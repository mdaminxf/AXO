import asyncio
import sounddevice as sd
import numpy as np
from aiortc import AudioStreamTrack
from av import AudioFrame
import fractions

class MicrophoneStreamTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()
        self.samplerate = 48000
        self.channels = 1
        self.queue = asyncio.Queue()
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            callback=self._callback,
            dtype='int16'
        )
        self.stream.start()

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.queue.put_nowait(indata.copy())

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        data = await self.queue.get()
        
        # Create AudioFrame
        # aiortc expects S16 format
        frame = AudioFrame.from_ndarray(data.reshape(1, -1), format='s16', layout='mono')
        frame.sample_rate = self.samplerate
        frame.pts = pts
        frame.time_base = time_base
        
        return frame

    def stop(self):
        self.stream.stop()
        self.stream.close()
