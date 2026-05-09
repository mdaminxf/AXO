import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
from .network import MultiOSNode
from .streaming import list_windows
from .audio import MicrophoneStreamTrack
import cv2

from .os_hooks import GlobalRightClickHook

class MultiOS_UI:
    def __init__(self, root, room_id="default"):
        self.root = root
        self.root.title(f"Multi-OS Collaboration - Room: {room_id}")
        self.root.geometry("400x550")
        
        self.room_id = room_id
        self.node = MultiOSNode(room_id)
        self.loop = asyncio.new_event_loop()
        
        # Right Click Hook
        self.hook = GlobalRightClickHook(self._on_right_click)
        self.hook.start()
        
        self._setup_style()
        self._create_widgets()
        
        # Start asyncio loop in a separate thread
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()
        
        # Auto-connect to signaling server
        self._run_async(self.node.connect())

    def _on_right_click(self, window_title):
        # This runs in the hook thread, so we must schedule on the main thread
        self.root.after(0, lambda: self._handle_right_click_discovery(window_title))

    def _handle_right_click_discovery(self, window_title):
        if messagebox.askyesno("Share App?", f"Do you want to share '{window_title}' with the room?"):
            self.node.add_window_track(window_title)
            self.status_label.config(text=f"Status: Sharing {window_title}")

    def _create_widgets(self):
        # Info Section
        info_frame = ttk.Frame(self.root, padding=10)
        info_frame.pack(fill="x")
        ttk.Label(info_frame, text=f"Active Room: {self.room_id}", font=("Segoe UI", 12, "bold")).pack()
        ttk.Label(info_frame, text="Tip: Right-click any app to share it instantly!").pack()
        
        # Audio Section
        audio_frame = ttk.LabelFrame(self.root, text="Audio", padding=10)
        audio_frame.pack(fill="x", padx=10, pady=5)
        
        self.mic_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_frame, text="Microphone Enabled", variable=self.mic_var, command=self.toggle_mic).pack()
        
        # Screen Sharing Section
        share_frame = ttk.LabelFrame(self.root, text="Software Sharing", padding=10)
        share_frame.pack(fill="x", padx=10, pady=5)
        
        self.window_list = ttk.Combobox(share_frame, state="readonly")
        self.window_list.pack(fill="x", pady=5)
        self.refresh_windows()
        
        ttk.Button(share_frame, text="Refresh Windows", command=self.refresh_windows).pack(side="left", padx=5)
        ttk.Button(share_frame, text="Share Selected", command=self.share_window).pack(side="left", padx=5)
        
        # Remote Control Section
        rc_frame = ttk.LabelFrame(self.root, text="Permissions", padding=10)
        rc_frame.pack(fill="x", padx=10, pady=5)
        
        self.rc_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(rc_frame, text="Allow Remote Control", variable=self.rc_var, command=self.toggle_rc).pack()
        
        # Status
        self.status_label = ttk.Label(self.root, text="Status: Idle", style="Status.TLabel")
        self.status_label.pack(side="bottom", anchor="w", padx=10, pady=5)

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run_async(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def refresh_windows(self):
        windows = list_windows()
        self.window_list['values'] = windows
        if windows:
            self.window_list.current(0)

    def toggle_mic(self):
        # Implementation to mute/unmute
        pass

    def toggle_rc(self):
        self.node.allow_remote_control = self.rc_var.get()
        state = "Enabled" if self.node.allow_remote_control else "Disabled"
        self.status_label.config(text=f"Status: Remote Control {state}")

    def share_window(self):
        win_title = self.window_list.get()
        if win_title:
            self.node.add_window_track(win_title)
            self.status_label.config(text=f"Status: Sharing {win_title}")

    def host_session(self):
        async def _host():
            offer = await self.node.create_offer()
            # In a real app, this would use a signaling server
            # For this prototype, we show a popup to copy SDP
            self.root.clipboard_clear()
            self.root.clipboard_append(offer.sdp)
            messagebox.showinfo("Offer Created", "Offer SDP copied to clipboard. Send it to your peer.")
            
            # Simple dialog to get answer
            answer_sdp = self._get_input_dialog("Join Session", "Paste peer's Answer SDP:")
            if answer_sdp:
                await self.node.handle_answer(answer_sdp)
                self.status_label.config(text="Status: Connected")

        self._run_async(_host())

    def join_session(self):
        async def _join():
            offer_sdp = self._get_input_dialog("Join Session", "Paste peer's Offer SDP:")
            if offer_sdp:
                answer = await self.node.handle_offer(offer_sdp)
                self.root.clipboard_clear()
                self.root.clipboard_append(answer.sdp)
                messagebox.showinfo("Answer Created", "Answer SDP copied to clipboard. Send it back to the host.")
                self.status_label.config(text="Status: Connected")

        self._run_async(_join())

    def _get_input_dialog(self, title, prompt):
        # Very simple input dialog for SDP
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        ttk.Label(dialog, text=prompt).pack(padx=10, pady=5)
        text_area = tk.Text(dialog, height=10, width=50)
        text_area.pack(padx=10, pady=5)
        
        result = [None]
        def ok():
            result[0] = text_area.get("1.0", "end-1c").strip()
            dialog.destroy()
        
        ttk.Button(dialog, text="OK", command=ok).pack(pady=5)
        self.root.wait_window(dialog)
        return result[0]

def launch_ui(room_id="default"):
    root = tk.Tk()
    app = MultiOS_UI(root, room_id)
    root.mainloop()
