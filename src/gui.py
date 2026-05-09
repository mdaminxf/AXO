import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
from .network import MultiOSNode
from .streaming import list_windows
from .audio import MicrophoneStreamTrack
import cv2
import win32gui

from .os_hooks import GlobalRightClickHook

class MultiOS_UI:
    def __init__(self, root, host_ip="localhost"):
        self.root = root
        self.root.title(f"AXO Collaboration - Host: {host_ip}")
        self.root.geometry("400x550")
        
        self.host_ip = host_ip
        # Use default room_id for simplicity since we are now IP-focused
        signaling_url = f"ws://{host_ip}:8888"
        self.node = MultiOSNode(room_id="default", signaling_url=signaling_url)
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

    def _setup_style(self):
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("Status.TLabel", font=("Segoe UI", 9, "italic"))

    def _on_right_click(self, window_title):
        # This runs in the hook thread, so we must schedule on the main thread
        self.root.after(0, lambda: self._show_floating_share_button(window_title))

    def _show_floating_share_button(self, window_title):
        # Create a small, borderless window near the cursor
        x, y = win32gui.GetCursorPos()
        
        btn_win = tk.Toplevel(self.root)
        btn_win.overrideredirect(True) # Remove borders
        btn_win.attributes("-topmost", True) # Stay on top
        btn_win.geometry(f"+{x+10}+{y+10}") # Near cursor
        
        def share():
            # Run this on the loop thread to avoid asyncio loop mismatch
            self.loop.call_soon_threadsafe(self.node.add_window_track, window_title)
            self.status_label.config(text=f"Status: Sharing {window_title}")
            btn_win.destroy()

        btn = tk.Button(btn_win, text=f"Share '{window_title}' to AXO", 
                        bg="#0078d7", fg="white", font=("Segoe UI", 9, "bold"),
                        command=share, relief="flat", padx=10, pady=5)
        btn.pack()

        # Auto-destroy after 3 seconds if not clicked
        self.root.after(3000, lambda: btn_win.destroy() if btn_win.winfo_exists() else None)

    def _create_widgets(self):
        # Info Section
        info_frame = ttk.Frame(self.root, padding=10)
        info_frame.pack(fill="x")
        ttk.Label(info_frame, text=f"Connected to: {self.host_ip}", font=("Segoe UI", 12, "bold")).pack()
        ttk.Label(info_frame, text="AXO Magic: Right-click any app to share it!", foreground="#0078d7").pack()
        
        # Audio Section
        audio_frame = ttk.LabelFrame(self.root, text="Audio", padding=10)
        audio_frame.pack(fill="x", padx=10, pady=5)
        
        self.mic_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_frame, text="Microphone Enabled", variable=self.mic_var, command=self.toggle_mic).pack()
        
        # Status Section (Manual selection removed for 'Magic' experience)
        share_frame = ttk.LabelFrame(self.root, text="System Status", padding=10)
        share_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ttk.Label(share_frame, text="Status: Connected to Server", style="Status.TLabel")
        self.status_label.pack()
        
        # Remote Control Section
        rc_frame = ttk.LabelFrame(self.root, text="Permissions", padding=10)
        rc_frame.pack(fill="x", padx=10, pady=5)
        
        self.rc_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(rc_frame, text="Allow Remote Control", variable=self.rc_var, command=self.toggle_rc).pack()

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run_async(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def refresh_windows(self):
        windows = list_windows()
        # Note: window_list was removed in the magic update, but this method stayed.
        # Keeping it for now as a utility or for future use.
        pass

    def toggle_mic(self):
        # Implementation to mute/unmute
        pass

    def toggle_rc(self):
        self.node.allow_remote_control = self.rc_var.get()
        state = "Enabled" if self.node.allow_remote_control else "Disabled"
        self.status_label.config(text=f"Status: Remote Control {state}")

    def share_window(self):
        # This was for manual sharing, replaced by magic OS hook.
        pass

    def host_session(self):
        # Auto-handled by IP connection now
        pass

    def join_session(self):
        # Auto-handled by IP connection now
        pass

    def _get_input_dialog(self, title, prompt):
        # Kept for utility if needed
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

def launch_ui(host_ip="localhost"):
    root = tk.Tk()
    app = MultiOS_UI(root, host_ip)
    root.mainloop()
