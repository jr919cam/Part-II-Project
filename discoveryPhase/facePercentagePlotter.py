'''

need to be able to select a seat and some selected CO2 sensors

with selected seat plot any positive detections as black lines and any negative detections as nothing

then plot the CO2 over time for the same time period for a sensor at the back of the room and near to the selected seat.

'''

from datetime import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class MetricReadingError(Exception):
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def getMetricLim(metric):
    if metric == 'co2':
        return 300
    if metric == 'temperature':
        return 20
    else:
        return 0

def getBoundedNodeDF(day, timeboundaries):
    with open(f'node_22-28Jan/cerberus-node-lt1_2024-01-{day}.txt', 'r') as file:
        nodeData = [json.loads(dataLine) for dataLine in file]
    nodeDataFrame = pd.DataFrame(nodeData)   

    # display full ts to 10dp
    pd.set_option('display.float_format', '{:.10f}'.format)
    nodeDataFrame['acp_ts'] = pd.to_numeric(nodeDataFrame['acp_ts'])

    # bound the data
    boundedNodeDF = nodeDataFrame[(nodeDataFrame['acp_ts'] >= timeboundaries[0]) & (nodeDataFrame['acp_ts'] <= timeboundaries[1])]

    return boundedNodeDF    


def getSeatTS(seat, day, timeboundaries):
    # first get df of times selected
    boundedNodeDF = getBoundedNodeDF(day, timeboundaries)

    # filter for values which contain the required seat
    targetSeatDF = boundedNodeDF[boundedNodeDF['seats_occupied'].apply(lambda x: seat in x)]
    seatTS = targetSeatDF['acp_ts'] 
    return seatTS

def getSensorlevels(sensor, day, timeboundaries, metric):
    # set up dataframe
    with open(f'jan2024SensorSample/elsys-co2-{sensor}/01/elsys-co2-{sensor}_2024-01-{day}.txt', 'r') as file:
        sensorData = [json.loads(dataLine) for dataLine in file]
    sensorDataFrame = pd.DataFrame(sensorData)

    # display full ts to 10dp
    pd.set_option('display.float_format', '{:.10f}'.format)
    sensorDataFrame['acp_ts'] = pd.to_numeric(sensorDataFrame['acp_ts'])
    
    # bound the data with co2 values in
    sensorDataFrameFiltered = sensorDataFrame[sensorDataFrame['payload_cooked'].apply(lambda x: metric in x)]
    if len(sensorDataFrameFiltered) == 0:
        raise MetricReadingError(f"No values of {metric} for this sensor on this day")
    sensorDataFrameTsBound = sensorDataFrameFiltered[(sensorDataFrameFiltered['acp_ts'] >= timeboundaries[0]) & (sensorDataFrameFiltered['acp_ts'] <= timeboundaries[1])]
    sensorDataFrameTsBound.reset_index(drop=True, inplace=True)

    return sensorDataFrameTsBound['acp_ts'], np.array([payload[metric] for payload in sensorDataFrameTsBound['payload_cooked']])


def plotMetricWithFaceDetectionFrequency(seat: str, sensor1: str, sensor2: str, day: int, timeboundaries: tuple[float, float], isSaved=False, metric='co2', vlineBoundary=2):
    seatTS = getSeatTS(seat, day, timeboundaries)
    print('seatTS', seatTS)
    sensor1TS, sensor1Levels = getSensorlevels(sensor1, day, timeboundaries, metric)
    sensor2TS, sensor2Levels = getSensorlevels(sensor2, day, timeboundaries, metric)
    closestSensor2val = np.interp(seatTS, sensor2TS, sensor2Levels) if vlineBoundary == 2 else np.interp(seatTS, sensor1TS, sensor1Levels)


    boundedNodeDF = getBoundedNodeDF(day, timeboundaries)
    crowdcountTS, crowdcount = boundedNodeDF['acp_ts'], boundedNodeDF['crowdcount']

    plt.figure(figsize=(20, 8))
    plt.bar(seatTS, closestSensor2val, width=5, align='center', color='black', alpha=0.75)

    xticksTS = np.linspace(timeboundaries[0], timeboundaries[1], int((timeboundaries[1]-timeboundaries[0]) / 3600) * 2 + 1)
    xticksLabels = np.array([datetime.fromtimestamp(tickTS).strftime('%H:%M') for tickTS in xticksTS])

    plt.xticks(xticksTS, xticksLabels, rotation=60)
    plt.xlim(timeboundaries)

    if metric == 'humidity':
        plt.ylim(24, 36)
    else:
        plt.ylim(getMetricLim(metric), 24)

    plt.xlabel('ACP timestamp')
    plt.ylabel(f'{metric} level')
    plt.title(f'times when {seat} was detected to be occupied with {metric} levels at {sensor1[-3:]} and {sensor2[-3:]}     ({day}/01/2024)')

    plt.plot(sensor1TS, sensor1Levels, color='w', linewidth=3)
    plt.plot(sensor1TS, sensor1Levels, color='r', label=f'{metric} at {sensor1[-3:]} (local)')
 
    plt.plot(sensor2TS, sensor2Levels, color='w', linewidth=3)
    plt.plot(sensor2TS, sensor2Levels, color='g', label=f'{metric} at {sensor2[-3:]} (global)')
    plt.legend(loc='upper right')

    ax2 = plt.gca().twinx()
    ax2.plot(crowdcountTS, crowdcount, color='w', linewidth=3)
    ax2.plot(crowdcountTS, crowdcount, color='orange', label='total crowdcount')
    ax2.set_ylabel('total crowdcount')
    ax2.set_ylim(0,150)
    ax2.tick_params(axis='y')
    ax2.legend(loc='upper left')

    plt.savefig(f'discoveryPhase/plots/second-facevisibilityPlots/{seat}-{metric}-{sensor1}-{sensor2}-{day}.png', format='png') if isSaved else plt.show()

if __name__ == '__main__':
    DAY = 24
    timeboundarystart = datetime.strptime(f'2024-1-{DAY} 08:30:00', "%Y-%m-%d %H:%M:%S").timestamp()
    timeboundaryend = datetime.strptime(f'2024-1-{DAY} 16:30:00', "%Y-%m-%d %H:%M:%S").timestamp()
    plotMetricWithFaceDetectionFrequency('MD14', '058ac3', '058aef', day=DAY, timeboundaries=(timeboundarystart, timeboundaryend), isSaved=True, metric='temperature', vlineBoundary=1)