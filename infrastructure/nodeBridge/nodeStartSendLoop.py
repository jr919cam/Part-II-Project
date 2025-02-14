import asyncio
import time
import json

async def nodeStartSendLoop(percentageConcentrationSynopsis, wholeRoomStabilitySynopsis, leccentrationSynopsis, lectureBoundarySynopsis, nodeDf, startTimestamp, speed, ws):
    try:
        await asyncio.sleep(max((float(nodeDf.loc[0]['acp_ts']) - startTimestamp)/(speed), 0.1))
        for t, reading in nodeDf.iterrows():
            workStartTime = time.time()

            if percentageConcentrationSynopsis.seat != None:
                percentageConcentrationSynopsis.updateAverage(reading["seats_occupied"])
            wholeRoomStabilitySynopsis.updateRoomStability(reading["seats_occupied"], t)
            leccentrationSynopsis.updateLeccentration(reading["seats_occupied"])

            await sendReading(reading, percentageConcentrationSynopsis, wholeRoomStabilitySynopsis, leccentrationSynopsis, ws)
            await handleLectureBoundaries(lectureBoundarySynopsis, reading, nodeDf, t, ws, leccentrationSynopsis)

            if t == len(nodeDf) - 1:
                break
            await sleepUntilNextReading(nodeDf, reading, t, speed, workStartTime)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
        raise e

async def sendReading(reading, percentageConcentrationSynopsis, wholeRoomStabilitySynopsis, leccentrationSynopsis, ws):
    formattedReading = {
        "acp_ts":reading["acp_ts"],
        "acp_id":reading["acp_id"],
        "payload_cooked": {
            "crowdcount": reading["crowdcount"],
            "seats_occupied": reading["seats_occupied"], 
            "percent_concentration": percentageConcentrationSynopsis.avg, 
            "seatsOccupiedDiffCountTotal":wholeRoomStabilitySynopsis.seatsOccupiedDiffCountTotal,
            "seatsOccupiedDiffCount":wholeRoomStabilitySynopsis.seatsOccupiedDiffCount,
            "roomAvgOccupancy": leccentrationSynopsis.leccentration
        },
        "type":"reading", 
        "readingType":"node"
    }
    await ws.send(json.dumps(formattedReading))

async def handleLectureBoundaries(lectureBoundarySynopsis, reading, nodeDf, t, ws, leccentrationSynopsis):
    lectureBoundarySynopsis.updateEMA(nodeDf, t)
    if lectureBoundarySynopsis.isEMALectureUpEvent(reading, t):
        if lectureBoundarySynopsis.wasLecture():
            await ws.send((json.dumps({
                    "type":"event", 
                    "eventType": "leccentration", 
                    "leccentration": leccentrationSynopsis.leccentration, 
                    "leccentrationSD": leccentrationSynopsis.getStdDev()
                }
            )))
            leccentrationSynopsis.reset()
        await ws.send(json.dumps({"acp_ts":reading["acp_ts"], "type":"event", "eventType": "lectureUp"}))
    if lectureBoundarySynopsis.hasEMAlectureSettled(reading, t):
        leccentrationSynopsis.reset()
        await ws.send(json.dumps({"acp_ts":reading["acp_ts"], "type":"event", "eventType": "lectureSettled"}))
    if lectureBoundarySynopsis.isEMALectureDownEvent(reading, t):
        if lectureBoundarySynopsis.wasLecture():
            await ws.send((json.dumps({
                    "type":"event", 
                    "eventType": "leccentration", 
                    "leccentration": leccentrationSynopsis.leccentration, 
                    "leccentrationSD": leccentrationSynopsis.getStdDev()
                }
            )))
            leccentrationSynopsis.reset()
        await ws.send(json.dumps({"acp_ts":reading["acp_ts"], "type":"event", "eventType": "lectureDown"}))

async def sleepUntilNextReading(nodeDf, reading, t, speed, workStartTime):
    time_delta = float(nodeDf.loc[t+1]['acp_ts']) - float(reading['acp_ts'])
    workEndTime = time.time()
    sleepTime = max((time_delta/speed) - (workEndTime - workStartTime),0)
    await asyncio.sleep(sleepTime)