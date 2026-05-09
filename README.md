# Multi-OS Collaboration System

A "magic" low-latency, team collaboration tool. No manual setup or IP sharing required.

## Features
- **Magic Discovery:** Multiple users enter the same Room ID and connect automatically.
- **Global Right-Click:** Right-click any running software UI on your desktop to instantly share it with the team.
- **Voice Chat:** Seamless, low-latency audio for all connected members.
- **Window-Level Sharing:** Stream specific app UIs, not your whole screen.
- **Remote Control:** Let team members interact with your shared software.

## Setup
1. **Install Dependencies:**
   ```bash
   pip install aiortc mss pygetwindow opencv-python pywin32 sounddevice pyautogui av websockets
   ```
2. **Start Signaling Server (One person in the team):**
   ```bash
   python signaling_server.py
   ```
   *(Note: For remote teams, host this server on a public IP or use a tool like ngrok).*

## Usage
1. **Run the Tool:**
   ```bash
   python main.py
   ```
2. **Enter Room ID:** Everyone joins the same ID (e.g., `dev-team`).
3. **Share Apps:** 
   - **Method A:** Right-click any open window on your taskbar or desktop. A popup will ask to share.
   - **Method B:** Select from the dropdown in the Dashboard.
4. **Collaborate:** Talk, see shared windows, and grant remote control as needed.

## Security
- Connections are private to the Room ID.
- Remote control is opt-in only.
