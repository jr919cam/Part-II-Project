import asyncio
from datetime import datetime
import time
import pandas as pd
from sanic import Sanic
from sanic import Websocket
import json

from RollingSeatVarianceEngine import RollingSeatVarianceEngine
from synopses import LectureBoundarySynopsis, PercentageConcentrationSynopsis, WholeRoomStabilitySynopsis, WholeRoomAvgOccupancySynopsis
from co2BridgeEmulator import Co2BridgeEmulator

app = Sanic("nodeBridgeEmulator")

data = []

def getNodeDf(day: int, startTimeStamp: int, endTimeStamp: int)->pd.DataFrame:
    nodeDf = pd.read_json(f'node_22-28Jan/cerberus-node-lt1_2024-01-{day}.txt', lines=True)
    return nodeDf[(nodeDf['acp_ts'] >= startTimeStamp) & (nodeDf['acp_ts'] <= endTimeStamp)].reset_index()

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
    wholeRoomAvgOccupancySynopsis = WholeRoomAvgOccupancySynopsis()

    co2BridgeEmulator = Co2BridgeEmulator('058ae3', day, startTimestamp, endTimestamp, speed)

    # Optional variance engine for seat, does not sync correctly at high speeds
    # varianceEngine = RollingSeatVarianceEngine(seat, speed=speed)

    nodeDf = getNodeDf(day, startTimestamp, endTimestamp)
    async def nodeStartSendLoop():
        try:
            await asyncio.sleep(max((float(nodeDf.loc[0]['acp_ts']) - startTimestamp)/(speed), 0.1))
            for t, reading in nodeDf.iterrows():
                workStartTime = time.time()

                if percentageConcentrationSynopsis.seat != None:
                    percentageConcentrationSynopsis.updateAverage(reading["seats_occupied"])
                
                wholeRoomStabilitySynopsis.updateRoomStability(reading["seats_occupied"], t)
                wholeRoomAvgOccupancySynopsis.updateRoomAvgOccupancy(reading["seats_occupied"])

                formattedReading = {
                    "acp_ts":reading["acp_ts"],
                    "acp_id":reading["acp_id"],
                    "payload_cooked": {
                        "crowdcount": reading["crowdcount"],
                        "seats_occupied": reading["seats_occupied"], 
                        "percent_concentration": percentageConcentrationSynopsis.avg, 
                        "seatsOccupiedDiffCountTotal":wholeRoomStabilitySynopsis.seatsOccupiedDiffCountTotal,
                        "seatsOccupiedDiffCount":wholeRoomStabilitySynopsis.seatsOccupiedDiffCount,
                        "roomAvgOccupancy": wholeRoomAvgOccupancySynopsis.avg
                    },
                    "type":"reading", 
                    "readingType":"node"
                }

                # varianceEngine.incrementChunkCounter(seats_occupied)

                await ws.send(json.dumps(formattedReading))
                lectureBoundarySynopsis.updateEMA(nodeDf, t)
                if lectureBoundarySynopsis.isEMALectureUpEvent(reading, t):
                    wholeRoomAvgOccupancySynopsis.reset()
                    await ws.send(json.dumps({"acp_ts":reading["acp_ts"], "type":"event", "eventType": "lectureUp"}))
                if lectureBoundarySynopsis.isEMALectureDownEvent(reading, t):
                    wholeRoomAvgOccupancySynopsis.reset()
                    await ws.send(json.dumps({"acp_ts":reading["acp_ts"], "type":"event", "eventType": "lectureDown"}))
                if t == len(nodeDf) - 1:
                    break

                time_delta = float(nodeDf.loc[t+1]['acp_ts']) - float(reading['acp_ts'])
                
                workEndTime = time.time()
                sleepTime = max((time_delta/speed) - (workEndTime - workStartTime),0)
                await asyncio.sleep(sleepTime)
        except Exception as e:
            print(f"WebSocket connection closed: {e}")
    await asyncio.gather(
        # varianceEngine.startVarianceEngine(ws, startTimestamp),
        
        co2BridgeEmulator.startSendLoop(ws),
        nodeStartSendLoop()
    )

if __name__ == "__main__":
    app.run(port=8002, auto_reload=True)