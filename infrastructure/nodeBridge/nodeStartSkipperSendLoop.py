import asyncio
from datetime import datetime
import json

from nodeStartSendLoop import handleLectureBoundaries, sendReading


async def nodeStartSkipperSendLoop(
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
    ):
    co2Info = {
        "inLecture": False,  
        "wasLecture": False, 
        "count": 0,
        "mean": 0,
        "m2": 0}
    
    currentTimeStamp = startTimestamp
    t = 0
    while True:
        if currentTimeStamp > endTimestamp:
            break
        currentNodeReadings = nodeDf[(nodeDf['acp_ts'] >= currentTimeStamp) & (nodeDf['acp_ts'] <= min(currentTimeStamp + speed, endTimestamp))]
        currentCo2Readings = co2BridgeEmulator.sensorReadingDf[
            (co2BridgeEmulator.sensorReadingDf['acp_ts'] >= currentTimeStamp) 
            & (co2BridgeEmulator.sensorReadingDf['acp_ts'] <= min(currentTimeStamp + speed, endTimestamp))]
        for i, reading in currentNodeReadings.iterrows():
            if percentageConcentrationSynopsis.seat != None:
                percentageConcentrationSynopsis.updateAverage(reading["seats_occupied"])
            wholeRoomStabilitySynopsis.updateRoomStability(reading["seats_occupied"], t)
            leccentrationSynopsis.updateLeccentration(reading["seats_occupied"])
            await sendReading(reading, percentageConcentrationSynopsis, wholeRoomStabilitySynopsis, leccentrationSynopsis, ws)
            await handleLectureBoundaries(lectureBoundarySynopsis, reading, nodeDf, t, ws, leccentrationSynopsis, co2Info)
            t += 1
        for i, row in currentCo2Readings.iterrows():
            globalAvg = co2BridgeEmulator.getGlobalAverage(row['acp_ts'])
            try:
                calibratedCo2 = (row['payload_cooked']['co2'] - co2BridgeEmulator.baseReading) + globalAvg

                if co2Info["inLecture"]:
                    co2Info["count"] += 1
                    delta = calibratedCo2 - co2Info["mean"]
                    co2Info["mean"] += delta/co2Info["count"]
                    co2Info["m2"] += delta*(calibratedCo2 - co2Info["mean"])
                else:
                    if co2Info["wasLecture"]:
                        co2Info["wasLecture"] = False
                        await ws.send(json.dumps({
                                "type":"event", 
                                "eventType": "lectureCo2", 
                                "co2Avg": round(co2Info["mean"]), 
                                "co2SD": round((co2Info["m2"]/(co2Info["count"] - 1))**(0.5))
                            }
                        ))
                    co2Info["count"] = 0
                    co2Info["mean"] = 0
                    co2Info["m2"] = 0
                    
                formattedReading = {
                    "acp_ts":row["acp_ts"],
                    "payload_cooked": {
                        "calibrated_co2": f"{calibratedCo2}"
                    },
                    "type":"reading", 
                    "readingType":"sensor"
                }
                await ws.send(json.dumps(formattedReading))
            except KeyError:
                print("no main co2 reading at: ", datetime.fromtimestamp(row["acp_ts"]).strftime('%H:%M:%S'))
        await asyncio.sleep(1/speed)
        currentTimeStamp += speed