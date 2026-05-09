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
from aiortc.contrib.media import MediaRelay
from .streaming import WindowCaptureTrack
from .remote_control import RemoteControl
import cv2
import numpy as np
import websockets
from .local_discovery import LocalDiscovery

relay = MediaRelay()

class MultiOSNode:
    def __init__(self, room_id, signaling_url="ws://89.58.31.246:8888"):
        self.room_id = room_id
        self.signaling_url = signaling_url
        
        config = RTCConfiguration(iceServers=[
            RTCIceServer(urls=["stun:stun.l.google.com:19302"]),
            RTCIceServer(urls=["stun:stun1.l.google.com:19302"])
        ])
        self.pc = RTCPeerConnection(configuration=config)
        
        self.data_channel = None
        self.on_message_callback = None
        self.rc = RemoteControl()
        self.allow_remote_control = False
        self.ws = None

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
                except:
                    pass

        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"[*] AXO Connection State: {self.pc.connectionState}")
            if self.pc.connectionState == "failed":
                print("[!] ICE Connection Failed. Possible Firewall/NAT issue.")

    async def connect(self):
        try:
            print(f"[*] Attempting VPS connection: {self.signaling_url}")
            self.ws = await asyncio.wait_for(websockets.connect(self.signaling_url), timeout=5)
            await self.ws.send(json.dumps({"type": "join", "room_id": self.room_id}))
            print("[+] Connected to AXO Signaling Server.")
            asyncio.ensure_future(self._signaling_loop())
        except Exception as e:
            print(f"[!] Signaling connection failed: {e}")

    async def _negotiate(self):
        if self.pc.connectionState == "closed":
            return
            
        try:
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
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
                    answer = await self.pc.createAnswer()
                    await self.pc.setLocalDescription(answer)
                    await self.ws.send(json.dumps({
                        "type": "answer",
                        "sdp": self.pc.localDescription.sdp,
                        "room_id": self.room_id
                    }))
                elif data["type"] == "answer":
                    await self.pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type="answer"))
                elif data["type"] == "ice" and data.get("candidate"):
                    cand = data["candidate"]
                    candidate = RTCIceCandidate(
                        candidate=cand["candidate"],
                        sdpMid=cand["sdpMid"],
                        sdpMLineIndex=cand["sdpMLineIndex"]
                    )
                    await self.pc.addIceCandidate(candidate)
        except Exception as e:
            print(f"Signaling Loop Error: {e}")

    def add_window_track(self, window_title):
        if self.pc.connectionState == "closed":
            print("[!] Cannot share: Connection is closed.")
            return

        try:
            track = WindowCaptureTrack(window_title)
            self.pc.addTrack(relay.subscribe(track))
            if self.ws:
                asyncio.ensure_future(self._negotiate())
        except Exception as e:
            print(f"Error sharing window: {e}")

    @property
    def connection_state(self):
        return self.pc.connectionState

    async def close(self):
        await self.pc.close()
        if self.ws:
            await self.ws.close()
