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
from collections import defaultdict
from sklearn.neighbors import KernelDensity
import sys

np.set_printoptions(threshold=sys.maxsize)

class MetricReadingError(Exception):
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

NEAREST_SEATS_BY_SENSOR = {
    '058bl2':['LH1', 'LH2', 'LI1'],
    '0559f3':['LH6', 'LH5', 'LI6', 'LI5'],
    '0520a5':['LE6', 'LF6', 'LE5', 'LF5'],
    '058ae6':['LB1', 'LC1', 'LB2', 'LC2'],
    '058ae2':['MH1', 'MH2', 'MI1', 'MI2'], # max 22nd
    '058ac8':['MC1', 'MC2', 'MD1', 'MD2'],
    '058b15':['MA3', 'MA4', 'MB3', 'MB4'],
    '058b19':['MF4', 'MF5', 'MG4', 'MG5'],
    '058ac0':['MG7', 'MG8', 'MH7', 'MH8'],
    '058ac6':['MB7', 'MB8', 'MC7', 'MC8'],
    '058ae4':['MF10', 'MF11', 'MG10', 'MG11'],
    '058b11':['MA11', 'MA12', 'MB11', 'MB12'],
    '058ae7':['MH13', 'MH14', 'MI13', 'MI14'],
    '058ac9':['ME13', 'ME14', 'MF13', 'MF14'], # max 24th
    '058ac3':['MC13', 'MC14', 'MD13', 'MD14'],
    '0559f2':['RH1', 'RG1'],
    '058b13':['RH6', 'RG6'],
    '058b14':['RE1', 'RF1'],
    '058b16':['RE6', 'RF6'],
    '058ac4':['RB1', 'RC1'],
    '058ac2':['RB6', 'RB5'],
    }

NEAREST_SENSOR_BY_SEAT = {}
for sensor in NEAREST_SEATS_BY_SENSOR:
    for seat in NEAREST_SEATS_BY_SENSOR[sensor]:
        NEAREST_SENSOR_BY_SEAT[seat] = sensor

def getMetricLim(metric):
    if metric == 'co2':
        return 300, 750
    if metric == 'temperature':
        return 18, 24
    else:
        return 0, 0

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
    boundedNodeDF : pd.DataFrame = getBoundedNodeDF(day, timeboundaries)

    # filter for values which contain the required seat
    targetSeatDF : pd.DataFrame = boundedNodeDF[boundedNodeDF['seats_occupied'].apply(lambda x: seat in x)]
    seatTS = targetSeatDF['acp_ts'] 
    return seatTS

def getSeatTSDensityPoints(seatTS, timeboundaries):
    seatTS = seatTS.to_numpy().reshape(-1, 1)
    kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(seatTS)
    ts_samples = np.linspace(timeboundaries[0], timeboundaries[1], len(seatTS)*10)
    ts_samples_2d = ts_samples.reshape(-1,1)
    density = np.exp(kde.score_samples(ts_samples_2d))
    return ts_samples, density

def getSeatTSDensityPointsEMA(timestamps, alpha=0.2):
    intervals = np.diff(timestamps) + 0.05
    print(timestamps[:20])
    print(intervals[:19])
    densities = 1 / intervals
    emaDensity = [0]
    for i in range(0, len(densities)):
        ema = alpha * densities[i] + (1 - alpha) * emaDensity[-1]
        emaDensity.append(ema)
    return emaDensity

def getSeatCounts(day, timeboundaries):
    boundedNodeDF = getBoundedNodeDF(day, timeboundaries)
    seatCounts = defaultdict(int)

    for _, row in boundedNodeDF.iterrows():
        for seat in row['seats_occupied']:
            seatCounts[seat] += 1
    return seatCounts

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
        raise MetricReadingError(f"No values of {metric} for {sensor} on this day")
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
        lo, up = getMetricLim(metric)
        plt.ylim(lo, up)

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

def getSensor1Points(sensor1s, day, timeboundaries, metric, num_plots):
    sensor1Points = {}
    acceptedSensor1s = []
    acceptedSensorIndecies = []
    i = 0
    for j, sensor1 in enumerate(sensor1s):
        try:
            sensor1Points[sensor1] = getSensorlevels(sensor1, day, timeboundaries, metric)
            acceptedSensor1s.append(sensor1)
            acceptedSensorIndecies.append(j)
            i += 1
        except MetricReadingError:
            print(f'no {metric} reading for {sensor1}, trying next sensor')
            continue
        if i >= num_plots:
            break
    return sensor1Points, acceptedSensor1s, acceptedSensorIndecies

def plotMultipleMetricWithFaceDetectionFrequency(
        seats: list[str], 
        sensor1s: list[str], 
        sensor2s: list[str], 
        day: int, 
        timeboundaries: tuple[float, float], 
        isSaved=False, 
        metric='co2', 
        vlineBoundary=2, 
        num_plots=15, 
        isDensity=False
    ):
    sensor1Points, acceptedSensor1s, acceptedSensor1Indecies = getSensor1Points(sensor1s, day, timeboundaries, metric, num_plots)
    sensor2Points = {}
    for sensor2 in sensor2s:
        sensor2Points[sensor2] = getSensorlevels(sensor2, day, timeboundaries, metric)
    seatTSs = {}
    acceptedSeats = [seats[i] for i in acceptedSensor1Indecies]
    for seat in acceptedSeats:
        seatTSs[seat] = getSeatTS(seat, day, timeboundaries)
    
    boundedNodeDF = getBoundedNodeDF(day, timeboundaries)
    crowdcountTS, crowdcount = boundedNodeDF['acp_ts'], boundedNodeDF['crowdcount']

    fig, axs = plt.subplots(6, 3, figsize=(43, 27))
    fig.tight_layout(w_pad=15, h_pad=10)
    for ax, seat, sensor1, sensor2 in zip(axs.flatten(), acceptedSeats, acceptedSensor1s, sensor2s):

        xticksTS = np.linspace(timeboundaries[0], timeboundaries[1], int((timeboundaries[1]-timeboundaries[0]) / 3600) * 2 + 1)
        xticksLabels = np.array([datetime.fromtimestamp(tickTS).strftime('%H:%M') for tickTS in xticksTS])
        ax.set_xticks(xticksTS)
        ax.set_xticklabels(xticksLabels, rotation=60)
        ax.set_xlim(timeboundaries)
        ax.set_xlabel('ACP timestamp')
        ax.set_ylim(getMetricLim(metric))
        ax.set_ylabel(f'{metric} level')
        ax.set_title(f'{seat} occupancy density, {metric} levels at {sensor1[-3:]} and {sensor2[-3:]}     ({day}/01/2024)')

        axDensity = ax.twinx()
        axDensity.set_xlim(timeboundaries[0], timeboundaries[1])
        axDensity.set_yticks([])
        axDensity.set_yticklabels([])
        if isDensity:
            x, y = getSeatTSDensityPoints(seatTSs[seat], timeboundaries)
            x_interp = np.linspace(timeboundaries[0], timeboundaries[1], 1000)
            y_interp = np.interp(x_interp, x, y)
            axDensity.plot(x_interp, y_interp, color='black', label=f'seat occupancy density', zorder=-10)
        else:
            axDensity.set_ylim(getMetricLim(metric))
            closestSensorVals = np.interp(seatTSs[seat], sensor2Points[sensor2][0], sensor2Points[sensor2][1]) if vlineBoundary == 2 else np.interp(seatTSs[seat], sensor1Points[sensor1][0], sensor1Points[sensor1][1])
            axDensity.bar(seatTSs[seat], closestSensorVals, width=5, align='center', color='black', alpha=0.25)

        ax.plot(sensor1Points[sensor1][0], sensor1Points[sensor1][1], color='w', linewidth=3, zorder=9)
        ax.plot(sensor1Points[sensor1][0], sensor1Points[sensor1][1], color='r', label=f'{metric} at {sensor1[-3:]} (local)', zorder=10)
    
        ax.plot(sensor2Points[sensor2][0], sensor2Points[sensor2][1], color='w', linewidth=3, zorder=9)
        ax.plot(sensor2Points[sensor2][0], sensor2Points[sensor2][1], color='g', label=f'{metric} at {sensor2[-3:]} (global)', zorder=10)

        ax2 = ax.twinx()
        ax2.plot(crowdcountTS, crowdcount, color='w', linewidth=3, zorder=2)
        ax2.plot(crowdcountTS, crowdcount, color='orange', label='total crowdcount', zorder=3)
        ax2.set_ylabel('total crowdcount')
        ax2.set_ylim(0,150)
        ax2.tick_params(axis='y')

        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        handles3, labels3 = axDensity.get_legend_handles_labels()
        handles = handles1 + handles2 + handles3
        labels = labels1 + labels2 + labels3
        ax.legend(handles, labels, loc='upper left')
    save_path = f'discoveryPhase/plots/combinedFaceVisibilityPlots3/{metric}-{day}'
    if isDensity:
        save_path += '-density'
    plt.savefig(save_path + '.png', format='png') if isSaved else plt.show()

def plotMultipleFaceDetection(
        seats: list[str], 
        day: int, 
        timeboundaries: tuple[float, float], 
        isSaved=False,  
        isDensity=False,
        isEMA=False,
        isCombined=False
    ):
    seatTSs = {}
    for seat in seats:
        seatTSs[seat] = getSeatTS(seat, day, timeboundaries)
    
    boundedNodeDF = getBoundedNodeDF(day, timeboundaries)
    crowdcountTS, crowdcount = boundedNodeDF['acp_ts'], boundedNodeDF['crowdcount']

    fig, axs = plt.subplots(3, 1, figsize=(45, 15))
    fig.tight_layout(pad=10, w_pad=15, h_pad=10)
    for ax, seat in zip(axs.flatten(), seats[::15]):

        xticksTS = np.linspace(timeboundaries[0], timeboundaries[1], int((timeboundaries[1]-timeboundaries[0]) / 60) + 1)
        xticksLabels = np.array([datetime.fromtimestamp(tickTS).strftime('%H:%M') for tickTS in xticksTS])
        ax.set_xticks(xticksTS)
        ax.set_xticklabels(xticksLabels, rotation=60)
        ax.set_xlim(timeboundaries)
        ax.set_xlabel('ACP timestamp')
        ax.set_title(f'{seat} occupancy levels     ({day}/01/2024)')

        axDensity = ax.twinx()
        axDensity.set_xlim(timeboundaries[0], timeboundaries[1])
        axDensity.set_yticks([])
        axDensity.set_yticklabels([])
        if isDensity or isCombined:
            if isEMA:
                x = seatTSs[seat]
                y = getSeatTSDensityPointsEMA(seatTSs[seat])
            else:
                x, y = getSeatTSDensityPoints(seatTSs[seat], timeboundaries)
            axDensity.plot(x, y, color='black', label=f'seat occupancy density', zorder=-10)
            
            if isCombined:
                axDensity2 = axDensity.twinx()
                axDensity2.set_xlim(timeboundaries[0], timeboundaries[1])
                axDensity2.set_yticks([])
                axDensity2.set_yticklabels([])
                y = np.ones_like(seatTSs[seat])
                axDensity2.bar(seatTSs[seat], y, width=0.5, align='center', color='black', alpha=0.3)
        else:
            y = np.ones_like(seatTSs[seat])
            axDensity.bar(seatTSs[seat], y, width=1, align='center', color='black', alpha=0.1)

        ax2 = ax.twinx()
        ax2.plot(crowdcountTS, crowdcount, color='w', linewidth=3, zorder=2)
        ax2.plot(crowdcountTS, crowdcount, color='orange', label='total crowdcount', zorder=3)
        ax2.set_ylabel('total crowdcount')
        ax2.set_ylim(0,150)
        ax2.tick_params(axis='y')

        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        handles3, labels3 = axDensity.get_legend_handles_labels()
        handles = handles1 + handles2 + handles3
        labels = labels1 + labels2 + labels3
        ax.legend(handles, labels, loc='upper left')
    save_path = f'discoveryPhase/plots/combinedFaceVisibilityPlots4/{day}'
    if isCombined:
        save_path += '-single-combined-interval-EMA'
    elif isDensity:
        save_path += '-density'
        if isEMA:
            save_path += '-EMA'
    plt.savefig(save_path + '.png', format='png') if isSaved else plt.show()

def filterae2(day, seat):
    return not (NEAREST_SENSOR_BY_SEAT[seat] == '058ae2' and day > 22)

def filterac9(day, seat):
    return not (NEAREST_SENSOR_BY_SEAT[seat] == '058ac9' and day > 24)

def plotMultipleFaceDetectionFrequencyWithMetric(
        day: int, 
        timeboundaries: tuple[float, float], 
        isSaved=False, 
        metric='co2', 
        vlineBoundary=2, 
        num_plots=15, 
        isDensity=False
    ):
    faceDetectionSeatCounts = getSeatCounts(day, timeboundaries)
    sortedFaceDetectionSeats = sorted(faceDetectionSeatCounts, key=faceDetectionSeatCounts.get, reverse=True)
    near_seats = [seat for seats in NEAREST_SEATS_BY_SENSOR.values() for seat in seats]
    faceDetectionSeatsNearSensors = []
    for seat in sortedFaceDetectionSeats:
        if seat in near_seats:
            faceDetectionSeatsNearSensors.append(seat)
    faceDetectionSeatsNearSensors = list(filter(lambda x: filterac9(day, x) and filterae2(day, x), faceDetectionSeatsNearSensors))
    sensor1s = [NEAREST_SENSOR_BY_SEAT[seat] for seat in faceDetectionSeatsNearSensors]
    sensor2s = ['058ae3'] * num_plots
    plotMultipleMetricWithFaceDetectionFrequency(faceDetectionSeatsNearSensors, sensor1s, sensor2s, day, timeboundaries, isSaved, metric, vlineBoundary, num_plots, isDensity=isDensity)

def plotMultipleFaceDetectionFrequency(
        day: int, 
        timeboundaries: tuple[float, float], 
        isSaved=False, 
        isDensity=False,
        isEMA=False,
        isCombined=False,
    ):
    faceDetectionSeatCounts = getSeatCounts(day, timeboundaries)
    sortedFaceDetectionSeats = sorted(faceDetectionSeatCounts, key=faceDetectionSeatCounts.get, reverse=True)
    plotMultipleFaceDetection(sortedFaceDetectionSeats, day, timeboundaries, isSaved, isDensity, isEMA, isCombined=isCombined)


if __name__ == '__main__':
    for DAY in range(22, 27, 2):
        timeboundarystart = datetime.strptime(f'2024-1-{DAY} 9:20:00', "%Y-%m-%d %H:%M:%S").timestamp()
        timeboundaryend = datetime.strptime(f'2024-1-{DAY} 9:40:00', "%Y-%m-%d %H:%M:%S").timestamp() 
        print("plotting", "density + barcode", "on day", DAY)
        plotMultipleFaceDetectionFrequency(day=DAY, timeboundaries=(timeboundarystart, timeboundaryend), isSaved=True, isDensity=True, isEMA=True, isCombined=True)