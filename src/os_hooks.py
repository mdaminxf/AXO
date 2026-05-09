import win32gui
import win32api
import win32con
import threading
import time

class GlobalRightClickHook:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        # Poll right click state
        last_state = win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
        while self.running:
            current_state = win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
            if current_state != last_state:
                if current_state < 0: # Pressed
                    flags, hcursor, (x, y) = win32gui.GetCursorInfo()
                    hwnd = win32gui.WindowFromPoint((x, y))
                    
                    # Get top level parent
                    parent = hwnd
                    while win32gui.GetParent(parent):
                        parent = win32gui.GetParent(parent)
                    
                    title = win32gui.GetWindowText(parent)
                    if title:
                        self.callback(title)
                last_state = current_state
            time.sleep(0.05)
