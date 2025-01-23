from datetime import datetime
import json
import time
from sanic import Websocket
import asyncio
import pandas as pd


class Co2BridgeEmulator():

    def __init__(self, sensor, day, startTime, endTime, speed):
        self.sensor = sensor
        self.day = day
        self.startTime = startTime
        self.endTime = endTime
        self.speed = speed
        self.sensorReadingDf = pd.read_json(f"jan2024SensorSample/elsys-co2-{self.sensor}/01/elsys-co2-{self.sensor}_2024-01-{self.day}.txt", lines=True)
        self.baseReading = self.sensorReadingDf.loc[0]["payload_cooked"]["co2"]
        
    async def startSendLoop(self, ws: Websocket):
        self.sensorReadingDf = self.sensorReadingDf[(self.sensorReadingDf["acp_ts"] >= self.startTime) & (self.sensorReadingDf["acp_ts"] <= self.endTime)].reset_index()
        await asyncio.sleep(max((float(self.sensorReadingDf.loc[0]['acp_ts']) - self.startTime)/(self.speed), 0.1))
        for t, row in self.sensorReadingDf.iterrows():
            workStartTime = time.time()
            try:
                formattedReading = {
                    "acp_ts":row["acp_ts"],
                    "payload_cooked": {
                        "calibrated_co2": f"{(row['payload_cooked']['co2'] - self.baseReading) * 100/self.baseReading}"
                        # "calibrated_co2": f"{row['payload_cooked']['co2']}"
                    },
                    "type":"reading", 
                    "readingType":"sensor"
                }
                await ws.send(json.dumps(formattedReading))
            except KeyError:
                print("no co2 reading at: ", datetime.fromtimestamp(row["acp_ts"]).strftime('%H:%M:%S'))
                pass
            if t == len(self.sensorReadingDf) - 1:
                break
            time_delta = float(self.sensorReadingDf.loc[t+1]['acp_ts']) - float(row['acp_ts'])
            workEndTime = time.time()
            sleepTime = max((time_delta/self.speed) - (workEndTime - workStartTime),0)
            await asyncio.sleep(sleepTime)