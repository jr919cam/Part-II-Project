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

class PercentageConcentrationSynopsis():
    def __init__(self, seat):
        self.seat = seat
        if seat == None:
            self.avg = None  
        else:
            self.avg = 0
        self.seatCount = 0
        self.readingsCount = 0
    
    def updateAverage(self, seats_occupied):
        if self.seat in seats_occupied:
            self.seatCount += 1
        self.readingsCount += 1
        self.avg = self.seatCount/self.readingsCount


class WholeRoomStabilitySynopsis():
    def __init__(self):
        self.prevSeatsOccupied = set()
        self.seatsOccupiedDiffCountTotal = 0
        self.seatsOccupiedDiffCount = 0

    def updateRoomStability(self, seatsOccupied):
        seatsOccupiedSet = set(seatsOccupied)
        self.seatsOccupiedDiffCountTotal += len(seatsOccupiedSet.symmetric_difference(self.prevSeatsOccupied))
        self.seatsOccupiedDiffCount = len(seatsOccupiedSet.symmetric_difference(self.prevSeatsOccupied))
        self.prevSeatsOccupied = seatsOccupiedSet


class LectureBoundarySynopsis():
    def __init__(self, EMA, alpha):
        self.EMA = EMA
        self.alpha = alpha
        self.timeSinceLastUpEvent = -1
        self.timeSinceLastDownEvent = -1
        self.timeDelta = 0

    def updateEMA(self, JSONDataList: list[dict], t:int):
        if t < 1:
            return
        crowdcountDelta = JSONDataList[t]['crowdcount'] - JSONDataList[t-1]['crowdcount']
        self.timeDelta = float(JSONDataList[t]['acp_ts']) - float(JSONDataList[t-1]['acp_ts'])
        self.EMA = self.alpha * crowdcountDelta + (1-self.alpha) * self.EMA

    def isEMALectureUpEvent(self, JSONDataList: list[dict], t:int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastUpEvent >= 0 and self.timeSinceLastUpEvent < 10 * 60:
            self.timeSinceLastUpEvent += self.timeDelta
            return False
        if (self.EMA * 9.5 / (np.log(JSONDataList[t]['crowdcount'] + 1) + 1)) < 1:
            return False
        self.timeSinceLastUpEvent = 0
        self.timeSinceLastDownEvent = -1
        return True
    
    def isEMALectureDownEvent(self, JSONDataList: list[dict], t:int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastDownEvent >= 0 and self.timeSinceLastDownEvent < 10 * 60:
            self.timeSinceLastDownEvent += self.timeDelta
            return False
        if (self.EMA * 7 / (np.log(JSONDataList[t]['crowdcount'] + 1) + 1)) > -1:
            return False
        self.timeSinceLastDownEvent = 0
        self.timeSinceLastUpEvent = -1
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

    lectureBoundarySynopsis = LectureBoundarySynopsis(0, alpha)
    percentageConcentrationSynopsis = PercentageConcentrationSynopsis(seat)
    wholeRoomStabilitySynopsis = WholeRoomStabilitySynopsis()

    # Optional variance engine for seat, does not sync correctly at high speeds
    # varianceEngine = RollingSeatVarianceEngine(seat, speed=speed)

    JSONDataList = getJSONDataList(day, startTimestamp, endTimestamp)
    async def sendLoop():
        try:
            for t, reading in enumerate(JSONDataList):
                startTime = time.time()
                acp_ts, acp_id, crowdcount, seats_occupied = reading.values()

                if percentageConcentrationSynopsis.seat != None:
                    percentageConcentrationSynopsis.updateAverage(seats_occupied)
                
                wholeRoomStabilitySynopsis.updateRoomStability(seats_occupied)

                formattedReading = {
                    "acp_ts":acp_ts,
                    "acp_id":acp_id, 
                    "payload_cooked": {
                        "crowdcount": crowdcount,
                        "seats_occupied": seats_occupied, 
                        "percent_concentration": percentageConcentrationSynopsis.avg, 
                        "seatsOccupiedDiffCountTotal":wholeRoomStabilitySynopsis.seatsOccupiedDiffCountTotal,
                        "seatsOccupiedDiffCount":wholeRoomStabilitySynopsis.seatsOccupiedDiffCount
                    },
                    "type":"reading", 
                    "readingType":"node"
                }

                # varianceEngine.incrementChunkCounter(seats_occupied)

                await ws.send(json.dumps(formattedReading))
                lectureBoundarySynopsis.updateEMA(JSONDataList, t)
                if lectureBoundarySynopsis.isEMALectureUpEvent(JSONDataList, t):
                    await ws.send(json.dumps({"acp_ts":acp_ts, "type":"event", "eventType": "lectureUp"}))
                if lectureBoundarySynopsis.isEMALectureDownEvent(JSONDataList, t):
                    await ws.send(json.dumps({"acp_ts":acp_ts, "type":"event", "eventType": "lectureDown"}))
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