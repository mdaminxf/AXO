import asyncio
import sys
import os

# Add the current directory to sys.path to ensure 'src' is found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui import launch_ui

def main():
    print("========================================")
    print("    MULTI-OS COLLABORATION SYSTEM")
    print("========================================")
    
    room_id = input("\nEnter Room ID to join/create (default: 'office'): ").strip()
    if not room_id:
        room_id = "office"
        
    print(f"\n[*] Initializing all features for Room: {room_id}")
    print("[*] Launching Graphical Dashboard...")
    
    try:
        launch_ui(room_id)
    except KeyboardInterrupt:
        print("\n[!] System shutting down...")
    except Exception as e:
        print(f"\n[!] Error launching system: {e}")

if __name__ == "__main__":
    main()
