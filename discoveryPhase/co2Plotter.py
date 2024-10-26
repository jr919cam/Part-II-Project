from datetime import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def getXYAndLabels(sensor, day):
    with open(f'jan2024SensorSample/elsys-co2-058{sensor}/01/elsys-co2-058{sensor}_2024-01-{day}.txt', 'r') as file:
        ac6Data = [json.loads(dataLine) for dataLine in file]
    ac6DataFrame = pd.DataFrame(ac6Data)
    payloads = np.array(ac6DataFrame['payload_cooked'])
    missing_indecies = []
    co2 = []
    for i, payload in enumerate(payloads):
        try:
            co2.append(payload['co2'])
        except KeyError:
            if len(co2) > 0:
                co2.append(co2[-1])
            else:
                co2.append(0)
            missing_indecies.append(i)
    co2 = np.array(co2)

    timeStamps = np.array(ac6DataFrame["acp_ts"])
    hourMinuteStrings = np.array([datetime.fromtimestamp(float(ts)).strftime("%H:%M") for ts in timeStamps])
    mask = (hourMinuteStrings >= "08:00") & (hourMinuteStrings <= "17:00")
    boundedco2 = co2[mask]
    boundedHourMinuteStrings = hourMinuteStrings[mask]

    labels = [f"{i:02}:00" for i in range(8, 18)]
    return  boundedHourMinuteStrings, boundedco2, labels

def plotData():
    x, y, labels = getXYAndLabels('ac6', '24')
    plt.figure(figsize=(12, 6))
    plt.plot(x, y)
    plt.xticks(labels, rotation=45)
    for label in labels:
        plt.axvline(x=label, color='grey', linestyle='--', linewidth=0.5)
    plt.xlabel('ACP timestamp')
    plt.ylabel('AC6 sensor co2 levels')
    plt.tight_layout()
    plt.savefig('discoveryphase/plots/ac6-co2-24plot.png', format='png')