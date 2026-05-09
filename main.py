import asyncio
import sys
import os

# Ensure 'src' is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui import launch_ui

def main():
    print("========================================")
    print("         AXO COLLABORATION SYSTEM")
    print("========================================")
    
    room_id = input("\nEnter Room ID to join/create (default: 'office'): ").strip()
    if not room_id:
        room_id = "office"
        
    print(f"\n[*] Connecting to AXO Global Server (89.58.31.246)...")
    print("[*] Launching Dashboard...")
    
    try:
        launch_ui(room_id)
    except KeyboardInterrupt:
        print("\n[!] System shutting down...")
    except Exception as e:
        print(f"\n[!] Error launching AXO: {e}")

if __name__ == "__main__":
    main()
