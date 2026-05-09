import asyncio
import json
import logging
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
    AudioStreamTrack,
)
from aiortc.contrib.media import MediaRelay
from .streaming import WindowCaptureTrack
import cv2
import numpy as np

from .remote_control import RemoteControl

relay = MediaRelay()

import websockets

class MultiOSNode:
    def __init__(self, room_id, signaling_url="ws://89.58.31.246:8888"):
        self.room_id = room_id
        self.signaling_url = signaling_url
        self.pc = RTCPeerConnection()
        self.data_channel = None
        self.on_message_callback = None
        self.rc = RemoteControl()
        self.allow_remote_control = False
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.signaling_url)
        await self.ws.send(json.dumps({"type": "join", "room_id": self.room_id}))
        asyncio.ensure_future(self._signaling_loop())

    async def _signaling_loop(self):
        async for message in self.ws:
            data = json.loads(message)
            if data["type"] == "peer_joined":
                # When a peer joins, we create an offer
                offer = await self.pc.createOffer()
                await self.pc.setLocalDescription(offer)
                await self.ws.send(json.dumps({
                    "type": "offer",
                    "sdp": self.pc.localDescription.sdp,
                    "room_id": self.room_id
                }))
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
            elif data["type"] == "ice":
                # Handle ICE candidates if needed
                pass

    async def create_offer(self):
        # Kept for compatibility but usually handled by loop
        pass

    def _setup_datachannel(self, channel):
        self.data_channel = channel
        @self.data_channel.on("message")
        def on_message(message):
            try:
                data = json.loads(message)
                if data.get("type") == "control" and self.allow_remote_control:
                    self.rc.handle_command(data["payload"])
                else:
                    self._on_message(message)
            except:
                self._on_message(message)

    async def handle_answer(self, answer_sdp):
        answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
        await self.pc.setRemoteDescription(answer)

    def _on_message(self, message):
        if self.on_message_callback:
            self.on_message_callback(message)
        else:
            print(f"\n[Remote]: {message}")

    def send_message(self, message):
        if self.data_channel and self.data_channel.readyState == "open":
            self.data_channel.send(message)

    def add_window_track(self, window_title):
        track = WindowCaptureTrack(window_title)
        self.pc.addTrack(relay.subscribe(track))

    @property
    def connection_state(self):
        return self.pc.connectionState

    async def close(self):
        await self.pc.close()
