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
    
    host_ip = input("\nEnter Host IP (e.g. 89.58.31.246 or 192.168.x.x) [default: localhost]: ").strip()
    if not host_ip:
        host_ip = "localhost"
        
    print(f"\n[*] Connecting to AXO Server at {host_ip}...")
    print("[*] Launching Dashboard...")
    
    try:
        # Pass the host_ip to the UI
        launch_ui(host_ip=host_ip)
    except KeyboardInterrupt:
        print("\n[!] System shutting down...")
    except Exception as e:
        print(f"\n[!] Error launching AXO: {e}")

if __name__ == "__main__":
    main()
