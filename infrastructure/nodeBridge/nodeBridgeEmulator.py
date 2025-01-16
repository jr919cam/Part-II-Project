import asyncio
from datetime import datetime
import time
from sanic import Sanic
from sanic import Websocket
import json
import numpy as np

from RollingSeatVarianceEngine import RollingSeatVarianceEngine

app = Sanic("nodeBridgeEmulator")

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
        if abs((self.EMA * 5 / (np.log(JSONDataList[t]['crowdcount'] + 1) + 1))) < 1:
            return False
        self.timeSinceLastEvent = 0
        return True

def getJSONDataList(day: int, startTimeStamp: int, endTimeStamp: int)->list[dict]:
    with open(f'node_22-28Jan/cerberus-node-lt1_2024-01-{day}.txt', 'r') as file:
        JSONDataList = [json.loads(dataLine[:-1]) for dataLine in file]
        startIndex = None
        for i, reading in enumerate(JSONDataList):
            if startIndex == None and float(reading["acp_ts"]) >= startTimeStamp:
                startIndex = i
            if float(reading["acp_ts"]) >= endTimeStamp:
                return JSONDataList[startIndex:i]
        return []

@app.websocket("/ws")
async def websocket_feed(request, ws: Websocket):
    alpha = float(request.args.get("alpha"))
    speed = float(request.args.get("speed"))
    day = request.args.get("day")
    startTime = request.args.get("startTime")
    endTime = request.args.get("endTime")
    seat = request.args.get("seat")

    startDateObj= datetime.strptime(f"{startTime} {day}/{1}/{2024}", "%H:%M %d/%m/%Y")
    startTimestamp = int(time.mktime(startDateObj.timetuple()))
    
    endDateObj= datetime.strptime(f"{endTime} {day}/{1}/{2024}", "%H:%M %d/%m/%Y")
    endTimestamp = int(time.mktime(endDateObj.timetuple()))

    synopsis = LectureBoundarySynopsis(0, alpha)

    # Optional variance engine for seat, does not sync correctly at high speeds
    # varianceEngine = RollingSeatVarianceEngine(seat, speed=speed)

    JSONDataList = getJSONDataList(day, startTimestamp, endTimestamp)
    async def sendLoop():
        try:
            for t, reading in enumerate(JSONDataList):
                startTime = time.time()
                acp_ts, acp_id, crowdcount, seats_occupied = reading.values()
                formattedReading = {"acp_ts":acp_ts,"acp_id":acp_id, "payload_cooked":{"crowdcount": crowdcount, "seats_occupied": seats_occupied}, "type":"reading", "readingType":"node"}
                
                # varianceEngine.incrementChunkCounter(seats_occupied)

                await ws.send(json.dumps(formattedReading))
                if synopsis.isEMALectureEvent(JSONDataList, t):
                    await ws.send(json.dumps({"acp_ts":acp_ts, "type":"event"}))
                if t == len(JSONDataList) - 1:
                    break
                time_delta = float(JSONDataList[t+1]['acp_ts']) - float(formattedReading['acp_ts'])
                endTime = time.time()
                sleepTime = max(time_delta - (endTime - startTime),0)
                await asyncio.sleep(sleepTime/speed)
        except Exception as e:
            print(f"WebSocket connection closed: {e}")
    await asyncio.gather(

        # varianceEngine.startVarianceEngine(ws, startTimestamp),
        
        sendLoop()
    )

if __name__ == "__main__":
    app.run(port=8002, auto_reload=True)