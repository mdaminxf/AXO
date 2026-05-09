import asyncio
import sys
import os
import socket
import threading
import websockets
from src.gui import launch_ui
from signaling_server import handler as signaling_handler

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def start_internal_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def _start():
        async with websockets.serve(signaling_handler, "0.0.0.0", 8888):
            await asyncio.Future() # run forever
            
    loop.run_until_complete(_start())

def main():
    print("========================================")
    print("         AXO COLLABORATION SYSTEM")
    print("========================================")
    
    print("\n[1] HOST (Start a new room)")
    print("[2] JOIN (Connect to a friend)")
    
    choice = input("\nSelect an option [1/2]: ").strip()
    
    if choice == "1":
        my_ip = get_ip()
        print(f"\n[*] STARTING AXO SERVER...")
        print(f"[*] YOUR IP ADDRESS IS: {my_ip}")
        print(f"[*] Tell your team to connect to: {my_ip}")
        
        # Start server in background thread
        threading.Thread(target=start_internal_server, daemon=True).start()
        
        print("[*] Launching Dashboard...")
        launch_ui(host_ip="localhost") # Host connects to itself
        
    else:
        host_ip = input("\nEnter Host IP to connect to: ").strip()
        if not host_ip:
            host_ip = "localhost"
            
        print(f"\n[*] Connecting to AXO Host at {host_ip}...")
        print("[*] Launching Dashboard...")
        
        try:
            launch_ui(host_ip=host_ip)
        except KeyboardInterrupt:
            print("\n[!] System shutting down...")
        except Exception as e:
            print(f"\n[!] Error launching AXO: {e}")

if __name__ == "__main__":
    main()
