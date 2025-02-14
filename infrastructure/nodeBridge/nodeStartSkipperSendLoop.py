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
    currentTimeStamp = startTimestamp
    t = 0
    while True:
        if currentTimeStamp > endTimestamp:
            break
        currentNodeReadings = nodeDf[(nodeDf['acp_ts'] >= currentTimeStamp) & (nodeDf['acp_ts'] <= currentTimeStamp + speed)]
        currentCo2Readings = co2BridgeEmulator.sensorReadingDf[
            (co2BridgeEmulator.sensorReadingDf['acp_ts'] >= currentTimeStamp) 
            & (co2BridgeEmulator.sensorReadingDf['acp_ts'] <= currentTimeStamp + speed)]
        for i, reading in currentNodeReadings.iterrows():
            if percentageConcentrationSynopsis.seat != None:
                percentageConcentrationSynopsis.updateAverage(reading["seats_occupied"])
            wholeRoomStabilitySynopsis.updateRoomStability(reading["seats_occupied"], t)
            leccentrationSynopsis.updateLeccentration(reading["seats_occupied"])
            await sendReading(reading, percentageConcentrationSynopsis, wholeRoomStabilitySynopsis, leccentrationSynopsis, ws)
            await handleLectureBoundaries(lectureBoundarySynopsis, reading, nodeDf, t, ws, leccentrationSynopsis)
            t += 1
        for i, row in currentCo2Readings.iterrows():
            globalAvg = co2BridgeEmulator.getGlobalAverage(row['acp_ts'])
            try:
                calibratedCo2 = (row['payload_cooked']['co2'] - co2BridgeEmulator.baseReading) + globalAvg
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
        currentTimeStamp += speed