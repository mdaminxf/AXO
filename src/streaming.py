import mss
import pygetwindow as gw
import numpy as np
import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame
import fractions
import time

class WindowCaptureTrack(VideoStreamTrack):
    """
    A video stream track that captures a specific window.
    """
    def __init__(self, window_title=None):
        super().__init__()
        self.window_title = window_title
        self.sct = mss.mss()
        self.last_frame = None

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        # Find the window
        windows = gw.getWindowsWithTitle(self.window_title) if self.window_title else None
        if windows:
            win = windows[0]
            if win.isMinimized:
                # Handle minimized window (maybe show a placeholder or last frame)
                if self.last_frame is not None:
                    frame = self.last_frame
                else:
                    # Black frame
                    img = np.zeros((480, 640, 3), dtype=np.uint8)
                    frame = VideoFrame.from_ndarray(img, format="bgr24")
            else:
                # Capture window region
                # win.left, win.top, win.width, win.height
                monitor = {
                    "top": win.top,
                    "left": win.left,
                    "width": win.width,
                    "height": win.height,
                }
                img = np.array(self.sct.grab(monitor))
                # Remove alpha channel
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                frame = VideoFrame.from_ndarray(img, format="bgr24")
                self.last_frame = frame
        else:
            # Fallback to full screen or black frame
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            frame = VideoFrame.from_ndarray(img, format="bgr24")

        frame.pts = pts
        frame.time_base = time_base
        return frame

def list_windows():
    return [w.title for w in gw.getAllWindows() if w.title]
