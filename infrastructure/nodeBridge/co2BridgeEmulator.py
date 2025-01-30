from datetime import datetime
import json
import time
import numpy as np
from sanic import Websocket
import asyncio
import pandas as pd
from synopses import PeriodSynopsis

METRIC = "co2"
SENSORSAMPLE = ['058ae3', '0559f3', '058ac8', '058ac6', '058b12', '058ac0', '058b16', '058ac4', '058ae6']
EMULATIONPERIODSPLIT = 15 * 60

class Co2BridgeEmulator():

    def __init__(self, sensor, day, startTime, endTime, speed):
        self.sensor = sensor
        self.day = day
        self.startTime = startTime
        self.endTime = endTime
        self.speed = speed
        self.isDisabled = self.day[:4] == '2025'
        if not self.isDisabled:
            self.sensorReadingDf = pd.read_json(f"jan2024SensorSample/elsys-co2-{self.sensor}/01/elsys-co2-{self.sensor}_{self.day}.txt", lines=True)
            self.baseReading = self.sensorReadingDf.loc[0]["payload_cooked"][METRIC]
            self.sensorSampleDfs = [pd.read_json(f"jan2024SensorSample/elsys-co2-{SENSOR}/01/elsys-co2-{SENSOR}_{self.day}.txt", lines=True) for SENSOR in SENSORSAMPLE]

    def getGlobalAverage(self, ts):
        count = 0
        for i, sensordf in enumerate(self.sensorSampleDfs):
            nearestRow = sensordf.iloc[(sensordf['acp_ts'] - ts).abs().argmin()]
            try:
                count += nearestRow['payload_cooked'][METRIC]
            except KeyError as e:
                print("no co2 reading for", SENSORSAMPLE[i], "at", nearestRow['acp_ts'])
        return count/len(SENSORSAMPLE)

        
    async def startSendLoop(self, ws: Websocket):
        if self.isDisabled:
            return
        co2PeriodSynopsis = PeriodSynopsis(EMULATIONPERIODSPLIT, self.startTime)
        self.sensorReadingDf = self.sensorReadingDf[(self.sensorReadingDf["acp_ts"] >= self.startTime) & (self.sensorReadingDf["acp_ts"] <= self.endTime)].reset_index()
        await asyncio.sleep(max((float(self.sensorReadingDf.loc[0]['acp_ts']) - self.startTime)/(self.speed), 0.1))
        for t, row in self.sensorReadingDf.iterrows():
            workStartTime = time.time()
            globalAvg = self.getGlobalAverage(row['acp_ts'])
            
            try:
                calibratedCo2 = (row['payload_cooked'][METRIC] - self.baseReading) + globalAvg
                if co2PeriodSynopsis.resetIfPeriodEnd(row['acp_ts']):
                    await ws.send((json.dumps({
                                "type":"event", 
                                "eventType": "quarterlyCo2", 
                                "quarterMean": co2PeriodSynopsis.periodMeans[-1], 
                                "quarterSD": co2PeriodSynopsis.periodSDs[-1], 
                            }
                        )))
                co2PeriodSynopsis.updatePeriodMetrics(calibratedCo2)
                formattedReading = {
                    "acp_ts":row["acp_ts"],
                    "payload_cooked": {
                        "calibrated_co2": f"{calibratedCo2}"
                        # "calibrated_co2": f"{row['payload_cooked']['co2']}"
                    },
                    "type":"reading", 
                    "readingType":"sensor"
                }
                await ws.send(json.dumps(formattedReading))
            except KeyError:
                print("no main co2 reading at: ", datetime.fromtimestamp(row["acp_ts"]).strftime('%H:%M:%S'))
                pass
            if t == len(self.sensorReadingDf) - 1:
                break
            time_delta = float(self.sensorReadingDf.loc[t+1]['acp_ts']) - float(row['acp_ts'])
            workEndTime = time.time()
            sleepTime = max((time_delta/self.speed) - (workEndTime - workStartTime),0)
            await asyncio.sleep(sleepTime)
        co2PeriodSynopsis.resetIfPeriodEnd(np.infty)
        await ws.send((json.dumps({
                            "type":"event", 
                            "eventType": "quarterlyCo2", 
                            "quarterMean": co2PeriodSynopsis.periodMeans[-1], 
                            "quarterSD": co2PeriodSynopsis.periodSDs[-1], 
                        }
                    )))