import asyncio
import argparse
import sys
import os
from src.network import MultiOSNode
from src.streaming import list_windows
from src.filesystem import FileSystemManager
from src.audio import MicrophoneStreamTrack
import cv2
import sounddevice as sd
import numpy as np

from src.gui import launch_ui

async def main():
    parser = argparse.ArgumentParser(description="Multi-OS Collaboration System")
    parser.add_argument("--room", type=str, help="Room ID to join/create", default="default")
    parser.add_argument("--share-window", type=str, help="Window title to share")
    parser.add_argument("--send-file", type=str, help="Path to file to share")
    parser.add_argument("--list-windows", action="store_true", help="List available windows")
    parser.add_argument("--ui", action="store_true", help="Launch Graphical User Interface")
    
    args = parser.parse_args()

    if args.ui:
        launch_ui(args.room)
        return

    if args.list_windows:
        print("Available Windows:")
        for w in list_windows():
            print(f" - {w}")
        return

    node = MultiOSNode(args.room)
    fs = FileSystemManager()

    if args.send_file:
        print(f"[*] Quick share file: {args.send_file}")
        # In a real app, this would auto-connect to the room and send
        # For this prototype, we'll continue to main loop

    print(f"[*] Initializing room: {args.room}")
    
    mode = input("Select mode: [1] Host (Create Offer) [2] Join (Handle Offer): ")
    
    # Audio Setup
    mic_track = MicrophoneStreamTrack()
    node.pc.addTrack(mic_track)

    if mode == "1":
        if args.share_window:
            node.add_window_track(args.share_window)
        
        offer = await node.create_offer()
        print("\n--- COPY THIS OFFER ---")
        print(offer.sdp)
        print("--- END OFFER ---\n")
        
        answer_sdp = input("Paste the ANSWER here: ").strip()
        await node.handle_answer(answer_sdp)
    else:
        offer_sdp = input("Paste the OFFER here: ").strip()
        answer = await node.handle_offer(offer_sdp)
        print("\n--- COPY THIS ANSWER ---")
        print(answer.sdp)
        print("--- END ANSWER ---\n")

    print("[*] Connection establishing...")

    # Media handling
    output_stream = sd.OutputStream(samplerate=48000, channels=1, dtype='int16')
    output_stream.start()

    @node.pc.on("track")
    def on_track(track):
        print(f"[*] Received track: {track.kind}")
        if track.kind == "video":
            async def display_video():
                while True:
                    try:
                        frame = await track.recv()
                        img = frame.to_ndarray(format="bgr24")
                        cv2.imshow(f"Remote Stream - {args.room}", img)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    except Exception as e:
                        print(f"Video Error: {e}")
                        break
            asyncio.ensure_future(display_video())
        elif track.kind == "audio":
            async def play_audio():
                while True:
                    try:
                        frame = await track.recv()
                        data = frame.to_ndarray()
                        output_stream.write(data.T)
                    except Exception as e:
                        print(f"Audio Error: {e}")
                        break
            asyncio.ensure_future(play_audio())

    # CLI command loop
    print("\nCommands: 'send <msg>', 'ls', 'share <window>', 'exit'")
    try:
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, ">> ")
            if cmd.startswith("send "):
                msg = cmd[5:]
                node.send_message(msg)
            elif cmd == "ls":
                print("Local shared files:", fs.list_files())
            elif cmd.startswith("share "):
                win_title = cmd[6:]
                node.add_window_track(win_title)
                print(f"[*] Now sharing: {win_title}")
            elif cmd == "allow-rc":
                node.allow_remote_control = True
                print("[*] Remote control ENABLED. Be careful!")
            elif cmd == "deny-rc":
                node.allow_remote_control = False
                print("[*] Remote control DISABLED.")
            elif cmd == "exit":
                break
    except KeyboardInterrupt:
        pass
    finally:
        mic_track.stop()
        output_stream.stop()
        output_stream.close()
        await node.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
