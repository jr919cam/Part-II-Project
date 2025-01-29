import asyncio
from datetime import datetime
import time
import numpy as np
import pandas as pd
from sanic import Sanic
from sanic import Websocket
import json

from RollingSeatVarianceEngine import RollingSeatVarianceEngine
from synopses import LectureBoundarySynopsis, PercentageConcentrationSynopsis, WholeRoomStabilitySynopsis, WholeRoomAvgOccupancySynopsis, PeriodSynopsis
from co2BridgeEmulator import Co2BridgeEmulator

app = Sanic("nodeBridgeEmulator")

data = []

EMULATIONPERIODSPLIT = 15 * 60 # 15 min periods

def getNodeDf(day: int, startTimeStamp: int, endTimeStamp: int)->pd.DataFrame:
    if day[:4] == '2024':
        nodeDf = pd.read_json(f'node_22-28Jan/cerberus-node-lt1_{day}.txt', lines=True)
    else:
        nodeDf = pd.read_json(f'2025/2025/01/cerberus-node-lt1_{day}.txt', lines=True)
        payloadCookedDf = pd.DataFrame(list(nodeDf["payload_cooked"]))
        nodeDf["crowdcount"] = payloadCookedDf["crowdcount"]
        nodeDf["seats_occupied"] = payloadCookedDf["seats_occupied"].map(lambda d: list(d.keys()))

    return nodeDf[(nodeDf['acp_ts'] >= startTimeStamp) & (nodeDf['acp_ts'] <= endTimeStamp)].reset_index()

@app.websocket("/ws")
async def websocket_feed(request, ws: Websocket):
    alpha = float(request.args.get("alpha"))
    speed = float(request.args.get("speed"))
    day = request.args.get("day")
    startTime = request.args.get("startTime")
    endTime = request.args.get("endTime")
    seat = request.args.get("seat")
    sensor = request.args.get("sensor")

    startDateObj= datetime.strptime(f"{startTime} {day}", "%H:%M %Y-%m-%d")
    startTimestamp = int(time.mktime(startDateObj.timetuple()))
    
    endDateObj= datetime.strptime(f"{endTime} {day}", "%H:%M %Y-%m-%d")
    endTimestamp = int(time.mktime(endDateObj.timetuple()))

    lectureBoundarySynopsis = LectureBoundarySynopsis(0, alpha)
    percentageConcentrationSynopsis = PercentageConcentrationSynopsis(seat)
    wholeRoomStabilitySynopsis = WholeRoomStabilitySynopsis()
    wholeRoomAvgOccupancySynopsis = WholeRoomAvgOccupancySynopsis()
    crowdcountPeriodSynopsis = PeriodSynopsis(EMULATIONPERIODSPLIT, startTimestamp)

    co2BridgeEmulator = Co2BridgeEmulator(sensor, day, startTimestamp, endTimestamp, speed)

    # Optional variance engine for seat, does not sync correctly at high speeds
    # varianceEngine = RollingSeatVarianceEngine(seat, speed=speed)

    nodeDf = getNodeDf(day, startTimestamp, endTimestamp)
    if(len(nodeDf) > 0):
        async def nodeStartSendLoop():
            try:
                await asyncio.sleep(max((float(nodeDf.loc[0]['acp_ts']) - startTimestamp)/(speed), 0.1))
                for t, reading in nodeDf.iterrows():
                    workStartTime = time.time()

                    if percentageConcentrationSynopsis.seat != None:
                        percentageConcentrationSynopsis.updateAverage(reading["seats_occupied"])
                    
                    wholeRoomStabilitySynopsis.updateRoomStability(reading["seats_occupied"], t)
                    wholeRoomAvgOccupancySynopsis.updateRoomAvgOccupancy(reading["seats_occupied"])
                    

                    crowdcountPeriodSynopsis.resetIfPeriodEnd(reading['acp_ts'])
                    crowdcountPeriodSynopsis.updatePeriodMetrics(reading["crowdcount"])

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
                        # wholeRoomAvgOccupancySynopsis.reset()
                        await ws.send(json.dumps({"acp_ts":reading["acp_ts"], "type":"event", "eventType": "lectureUp"}))
                    if lectureBoundarySynopsis.isEMALectureDownEvent(reading, t):
                        # wholeRoomAvgOccupancySynopsis.reset()
                        await ws.send(json.dumps({"acp_ts":reading["acp_ts"], "type":"event", "eventType": "lectureDown"}))
                    if t == len(nodeDf) - 1:
                        break

                    time_delta = float(nodeDf.loc[t+1]['acp_ts']) - float(reading['acp_ts'])
                    
                    workEndTime = time.time()
                    sleepTime = max((time_delta/speed) - (workEndTime - workStartTime),0)
                    await asyncio.sleep(sleepTime)
                crowdcountPeriodSynopsis.resetIfPeriodEnd(np.infty)
                # print("facentration Avg:", "{:.1f}".format(wholeRoomAvgOccupancySynopsis.avg * 100) + "%", "\nfacentration stdDev:", "{:.1f}".format(wholeRoomAvgOccupancySynopsis.getStdDev() * 100) + "%")
                # print("quarterly means:",crowdcountPeriodSynopsis.periodMeans, "\nquarterly SDs:", crowdcountPeriodSynopsis.periodSDs)
            except Exception as e:
                print(f"WebSocket connection closed: {e}")
                raise e
            
        await asyncio.gather(
            # varianceEngine.startVarianceEngine(ws, startTimestamp),
            co2BridgeEmulator.startSendLoop(ws),
            nodeStartSendLoop()
        )

if __name__ == "__main__":
    app.run(port=8002, auto_reload=True)