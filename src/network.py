import asyncio
import json
import logging
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
    RTCConfiguration,
    RTCIceServer,
    VideoStreamTrack,
    AudioStreamTrack,
)
from .streaming import WindowCaptureTrack
from .remote_control import RemoteControl
import cv2
import numpy as np
import websockets

# We'll avoid the global relay for now to simplify the connection
# relay = MediaRelay()

class MultiOSNode:
    def __init__(self, room_id, signaling_url="ws://89.58.31.246:8888"):
        self.room_id = room_id
        self.signaling_url = signaling_url
        self.pc = None
        self.ws = None
        self.data_channel = None
        self.on_message_callback = None
        self.rc = RemoteControl()
        self.allow_remote_control = False
        self.current_shared_window = None
        self.pending_candidates = [] # Store candidates until remote desc is set
        
        self._init_pc()

    def _init_pc(self):
        if self.pc:
            try: asyncio.ensure_future(self.pc.close())
            except: pass
            
        # Standard configuration with STUN
        config = RTCConfiguration(iceServers=[
            RTCIceServer(urls=["stun:stun.l.google.com:19302"]),
            RTCIceServer(urls=["stun:stun1.l.google.com:19302"])
        ])
        self.pc = RTCPeerConnection(configuration=config)
        self.pending_candidates = []
        
        @self.pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate and self.ws:
                try:
                    await self.ws.send(json.dumps({
                        "type": "ice",
                        "candidate": {
                            "candidate": candidate.candidate,
                            "sdpMid": candidate.sdpMid,
                            "sdpMLineIndex": candidate.sdpMLineIndex,
                        }
                    }))
                except: pass

        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"[*] AXO Connection State: {self.pc.connectionState}")
            if self.pc.connectionState == "failed":
                print("[!] Connection failed. Check firewall.")

    async def connect(self):
        try:
            print(f"[*] Connecting to server: {self.signaling_url}")
            self.ws = await websockets.connect(self.signaling_url)
            await self.ws.send(json.dumps({"type": "join", "room_id": self.room_id}))
            print("[+] Joined room.")
            asyncio.ensure_future(self._signaling_loop())
        except Exception as e:
            print(f"[!] Signaling connection failed: {e}")

    async def _negotiate(self):
        if self.pc.connectionState == "closed":
            self._init_pc()
            
        try:
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            if self.ws:
                await self.ws.send(json.dumps({
                    "type": "offer",
                    "sdp": self.pc.localDescription.sdp,
                    "room_id": self.room_id
                }))
        except Exception as e:
            print(f"Negotiation Error: {e}")

    async def _signaling_loop(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                
                if data["type"] == "peer_joined":
                    await self._negotiate()
                    
                elif data["type"] == "offer":
                    await self.pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type="offer"))
                    # Now we can add pending candidates
                    for cand in self.pending_candidates:
                        await self.pc.addIceCandidate(cand)
                    self.pending_candidates = []
                    
                    answer = await self.pc.createAnswer()
                    await self.pc.setLocalDescription(answer)
                    await self.ws.send(json.dumps({
                        "type": "answer",
                        "sdp": self.pc.localDescription.sdp,
                        "room_id": self.room_id
                    }))
                    
                elif data["type"] == "answer":
                    await self.pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type="answer"))
                    # Now we can add pending candidates
                    for cand in self.pending_candidates:
                        await self.pc.addIceCandidate(cand)
                    self.pending_candidates = []
                    
                elif data["type"] == "ice" and data.get("candidate"):
                    cand_data = data["candidate"]
                    candidate = RTCIceCandidate(
                        candidate=cand_data["candidate"],
                        sdpMid=cand_data["sdpMid"],
                        sdpMLineIndex=cand_data["sdpMLineIndex"]
                    )
                    
                    if self.pc.remoteDescription:
                        try:
                            await self.pc.addIceCandidate(candidate)
                        except Exception as e:
                            # Ignore specific aiortc index errors
                            if "list.index(x)" not in str(e):
                                print(f"ICE Add Error: {e}")
                    else:
                        self.pending_candidates.append(candidate)
                        
        except Exception as e:
            if "connection closed" not in str(e).lower():
                print(f"Signaling Loop Error: {e}")

    def add_window_track(self, window_title):
        self.current_shared_window = window_title
        try:
            track = WindowCaptureTrack(window_title)
            # Add track directly to PC (no relay) for maximum stability
            self.pc.addTrack(track)
            if self.ws:
                asyncio.ensure_future(self._negotiate())
        except Exception as e:
            print(f"Error sharing window: {e}")

    async def close(self):
        if self.pc: await self.pc.close()
        if self.ws: await self.ws.close()
