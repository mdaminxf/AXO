import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
import win32gui
from .network import MultiOSNode
from .streaming import list_windows, WindowCaptureTrack
import cv2

class MultiOS_UI:
    def __init__(self, root, host_ip="localhost"):
        self.root = root
        self.root.title(f"AXO Collaboration - Host: {host_ip}")
        self.root.geometry("400x500")
        
        self.host_ip = host_ip
        signaling_url = f"ws://{host_ip}:8888"
        self.node = MultiOSNode(room_id="default", signaling_url=signaling_url)
        self.loop = asyncio.new_event_loop()
        
        self._setup_style()
        self._create_widgets()
        
        # Start networking thread
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()
        
        # Connect to signaling
        self.loop.call_soon_threadsafe(lambda: asyncio.ensure_future(self.node.connect()))

    def _setup_style(self):
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))

    def _create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="AXO COLLABORATION", style="Header.TLabel").pack()
        ttk.Label(header_frame, text=f"Connected to: {self.host_ip}").pack()

        # Window Selection Frame
        selection_frame = ttk.LabelFrame(self.root, text="Step 1: Select Software to Share", padding=10)
        selection_frame.pack(fill="x", padx=10, pady=10)

        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(selection_frame, textvariable=self.window_var, state="readonly")
        self.window_combo.pack(fill="x", pady=5)
        
        btn_frame = ttk.Frame(selection_frame)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_windows).pack(side="left", padx=2)
        self.share_btn = ttk.Button(btn_frame, text="START SHARING", command=self.start_sharing)
        self.share_btn.pack(side="left", padx=2)

        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="System Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=10)
        self.status_label = ttk.Label(status_frame, text="Status: Ready", font=("Segoe UI", 9, "italic"))
        self.status_label.pack()

        self.refresh_windows()

    def refresh_windows(self):
        windows = list_windows()
        self.window_combo['values'] = windows
        if windows:
            self.window_combo.current(0)

    def start_sharing(self):
        win_title = self.window_var.get()
        if not win_title:
            messagebox.showwarning("Warning", "Please select a window first!")
            return
            
        self.status_label.config(text=f"Status: Sharing '{win_title}'...")
        # Run track addition on networking thread
        self.loop.call_soon_threadsafe(self.node.add_window_track, win_title)

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

def launch_ui(host_ip="localhost"):
    root = tk.Tk()
    app = MultiOS_UI(root, host_ip)
    
    # Receive video loop
    def check_for_tracks():
        @app.node.pc.on("track")
        def on_track(track):
            if track.kind == "video":
                async def display():
                    while True:
                        try:
                            frame = await track.recv()
                            img = frame.to_ndarray(format="bgr24")
                            cv2.imshow(f"AXO Remote Stream", img)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                        except: break
                    cv2.destroyWindow("AXO Remote Stream")
                asyncio.run_coroutine_threadsafe(display(), app.loop)
        root.after(1000, check_for_tracks) # Re-check for new tracks

    root.mainloop()
