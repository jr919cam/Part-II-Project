import asyncio
from datetime import datetime
import time
from sanic import Sanic
from sanic import Websocket
import json
import numpy as np
from collections import deque

app = Sanic("nodeBridgeSimulator")

data = []

class LectureBoundarySynopsis():
    def __init__(self, EMA, alpha):
        self.EMA = EMA
        self.alpha = alpha
        self.timeSinceLastEvent = -1

    def isEMALectureEvent(self, JSONDataList: list[dict], t:int)->bool:
        if t < 1:
            return False
        crowdcountDelta = JSONDataList[t]['crowdcount'] - JSONDataList[t-1]['crowdcount']
        timeDelta = float(JSONDataList[t]['acp_ts']) - float(JSONDataList[t-1]['acp_ts'])
        self.EMA = self.alpha * crowdcountDelta + (1-self.alpha) * self.EMA
        if self.timeSinceLastEvent >= 0 and self.timeSinceLastEvent < 10 * 60:
            self.timeSinceLastEvent += timeDelta
            return False
        if abs(self.EMA < 1):
            return False
        self.timeSinceLastEvent = 0
        return True
    
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

def getJSONDataList(day: int, startTimeStamp: int)->list[dict]:
    with open(f'node_22-28Jan/cerberus-node-lt1_2024-01-{day}.txt', 'r') as file:
        JSONDataList = [json.loads(dataLine[:-1]) for dataLine in file]
        for i, reading in enumerate(JSONDataList):
            if float(reading["acp_ts"]) >= startTimeStamp:
                return JSONDataList[i:]
        return []

@app.websocket("/ws")
async def websocket_feed(request, ws: Websocket):
    alpha = float(request.args.get("alpha"))
    speed = float(request.args.get("speed"))
    day = request.args.get("day")
    startTime = request.args.get("startTime")

    startDateObj= datetime.strptime(f"{startTime} {day}/{1}/{2024}", "%H:%M %d/%m/%Y")
    startTimestamp = int(time.mktime(startDateObj.timetuple()))

    synopsis = LectureBoundarySynopsis(0, alpha)
    varianceEngine = RollingSeatVarianceEngine("MA9", speed=speed)

    JSONDataList = getJSONDataList(day, startTimestamp)
    async def sendLoop():
        try:
            for t, reading in enumerate(JSONDataList):
                acp_ts, acp_id, crowdcount, seats_occupied = reading.values()
                formattedReading = {"acp_ts":acp_ts,"acp_id":acp_id, "payload_cooked":{"crowdcount": crowdcount, "seats_occupied": seats_occupied}, "type":"reading", "readingType":"node"}
                varianceEngine.incrementChunkCounter(seats_occupied)
                
                # print(f'sending: {formattedReading}')
                await ws.send(json.dumps(formattedReading))
                if synopsis.isEMALectureEvent(JSONDataList, t):
                    # print(f'\n\nsending lecture EVENT\n\n')
                    await ws.send(json.dumps({"acp_ts":acp_ts, "type":"event"}))
                if t == len(JSONDataList) - 1:
                    break
                time_delta = float(JSONDataList[t+1]['acp_ts']) - float(formattedReading['acp_ts'])
                await asyncio.sleep(time_delta/speed)
        except Exception as e:
            print(f"WebSocket connection closed: {e}")
    await asyncio.gather(
        varianceEngine.startVarianceEngine(ws, startTimestamp),
        sendLoop()
    )

if __name__ == "__main__":
    app.run(port=8002, auto_reload=True)