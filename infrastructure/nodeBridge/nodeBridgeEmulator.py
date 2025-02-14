import asyncio
from datetime import datetime
import time
import pandas as pd
from sanic import Sanic
from sanic import Websocket

from nodeStartSendLoop import nodeStartSendLoop
from nodeStartSkipperSendLoop import nodeStartSkipperSendLoop
from synopses import LectureBoundarySynopsis, PercentageConcentrationSynopsis, WholeRoomStabilitySynopsis, LeccentrationSynopsis, PeriodSynopsis
from co2BridgeEmulator import Co2BridgeEmulator

app = Sanic("nodeBridgeEmulator")

data = []

EMULATIONPERIODSPLIT = 10 * 60 # 10 min periods

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
    leccentrationSynopsis = LeccentrationSynopsis()

    co2BridgeEmulator = Co2BridgeEmulator(sensor, day, startTimestamp, endTimestamp, speed)

    nodeDf = getNodeDf(day, startTimestamp, endTimestamp)
    if(len(nodeDf) > 0):
        await nodeStartSkipperSendLoop(
            nodeDf, 
            co2BridgeEmulator, 
            startTimestamp, 
            endTimestamp, 
            speed, 
            ws, 
            percentageConcentrationSynopsis, 
            wholeRoomStabilitySynopsis, 
            leccentrationSynopsis,
            lectureBoundarySynopsis
        )
        # await asyncio.gather(
        #     co2BridgeEmulator.startSendLoop(ws),
        #     nodeStartSendLoop(percentageConcentrationSynopsis, wholeRoomStabilitySynopsis, leccentrationSynopsis, lectureBoundarySynopsis, nodeDf, startTimestamp, speed, ws)
        # )

        


if __name__ == "__main__":
    app.run(port=8002, auto_reload=True)