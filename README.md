# AXO

Share your screen, voice, and files with your team instantly.

## 1. Setup
Install these tools first:
```bash
pip install aiortc mss pygetwindow opencv-python pywin32 sounddevice pyautogui av websockets
```

## 2. Run
**On your VPS:**
```bash
python signaling_server.py
```

**On your PC:**
```bash
python main.py
```

## 3. How to use
- Enter any **Room ID**.
- **Right-click** any app window to see the "Share to AXO" button.
- Click the button to start sharing!
