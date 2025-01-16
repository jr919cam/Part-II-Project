import asyncio
from collections import deque
import json

import numpy as np
from sanic import Websocket


class RollingSeatVarianceEngine():
    def __init__(self, seat, speed=1, chunkTime=20, windowSize=5):
        self.seat = seat
        self.speed = speed
        self.chunkTime = chunkTime
        self.windowSize= windowSize
        self.window = deque([], maxlen=windowSize)
        self.chunkCounter = 0
    
    async def startVarianceEngine(self, ws: Websocket, startTs:float):
        ts = startTs
        if self.seat != None:
            while True:
                await asyncio.sleep(self.chunkTime/self.speed)
                self.window.appendleft({"chunkCount": self.chunkCounter, "ts":ts + self.chunkTime/2})
                ts += self.chunkTime
                self.chunkCounter = 0
                if len(self.window) == self.windowSize:
                    variance = np.var([chunk["chunkCount"] for chunk in self.window])
                    varianceTs = np.mean([chunk["ts"] for chunk in self.window])
                    await ws.send(json.dumps({"acp_ts":varianceTs, "variance":variance, "type":"reading", "readingType": "variance"}))
                    self.window.pop()
    
    def incrementChunkCounter(self, seats_occupied):
        if self.seat in seats_occupied:
            self.chunkCounter += 1