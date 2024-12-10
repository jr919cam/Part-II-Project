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
    '''
        Exception raised when there is no reading of a specific metric in a given file
    '''
    pass

# selection of nearest seats to the sensors
NEAREST_SEATS_BY_SENSOR = {
    '058bl2':['LH1', 'LH2', 'LI1'],
    '0559f3':['LH6', 'LH5', 'LI6', 'LI5'],
    '0520a5':['LE6', 'LF6', 'LE5', 'LF5'],
    '058ae6':['LB1', 'LC1', 'LB2', 'LC2'],
    '058ae2':['MH1', 'MH2', 'MI1', 'MI2'], # max day 22nd in sample
    '058ac8':['MC1', 'MC2', 'MD1', 'MD2'],
    '058b15':['MA3', 'MA4', 'MB3', 'MB4'],
    '058b19':['MF4', 'MF5', 'MG4', 'MG5'],
    '058ac0':['MG7', 'MG8', 'MH7', 'MH8'],
    '058ac6':['MB7', 'MB8', 'MC7', 'MC8'],
    '058ae4':['MF10', 'MF11', 'MG10', 'MG11'],
    '058b11':['MA11', 'MA12', 'MB11', 'MB12'],
    '058ae7':['MH13', 'MH14', 'MI13', 'MI14'],
    '058ac9':['ME13', 'ME14', 'MF13', 'MF14'], # max day 24th in sample
    '058ac3':['MC13', 'MC14', 'MD13', 'MD14'],
    '0559f2':['RH1', 'RG1'],
    '058b13':['RH6', 'RG6'],
    '058b14':['RE1', 'RF1'],
    '058b16':['RE6', 'RF6'],
    '058ac4':['RB1', 'RC1'],
    '058ac2':['RB6', 'RB5'],
    }

# each seat's nearest sensor given by NEAREST_SEATS_BY_SENSOR
NEAREST_SENSOR_BY_SEAT = {}
for sensor in NEAREST_SEATS_BY_SENSOR:
    for seat in NEAREST_SEATS_BY_SENSOR[sensor]:
        NEAREST_SENSOR_BY_SEAT[seat] = sensor

def getMetricLim(metric: str) -> tuple[int, int]:
    '''
        returns basic y limits for given metrics when plotting
        Args:
            metric: metric of interest from sensor (e.g. 'co2')
        Returns:
            (ylim_lo, ylim_hi): y limits
    '''
    if metric == 'co2':
        return 300, 750
    if metric == 'temperature':
        return 18, 24
    else:
        return 0, 0

def getBoundedNodeDF(day: int, timeboundaries: tuple[str, str]) -> pd.DataFrame:
    '''
        for a given day and bounding timestamps, fetch the data from node which was published between the given times
        Args:
            day: the given day of interest
            timeboundaries: tuple of earliest and latest allowed timestamps
        Returns:
            seatTS: dataframe containing node readings between the timeboundaries on the given day
    '''
    
    with open(f'node_22-28Jan/cerberus-node-lt1_2024-01-{day}.txt', 'r') as file:
        nodeData = [json.loads(dataLine) for dataLine in file]
    nodeDataFrame = pd.DataFrame(nodeData)   

    # display full ts to 10dp for debugging purposes
    pd.set_option('display.float_format', '{:.10f}'.format)
    nodeDataFrame['acp_ts'] = pd.to_numeric(nodeDataFrame['acp_ts'])

    # bound the data
    boundedNodeDF = nodeDataFrame[(nodeDataFrame['acp_ts'] >= timeboundaries[0]) & (nodeDataFrame['acp_ts'] <= timeboundaries[1])]

    return boundedNodeDF    

# Assuming seatTS is a pandas Series
def save_seat_ts_to_json(seat_ts_dict, output_file):
    """
    Save the seatTS dictionary as a JSON file.

    Args:
        seat_ts_dict: Dictionary where keys are seat identifiers, and values are pandas Series.
        output_file: Path to the JSON file to save the data.
    """
    # Convert the dictionary to a JSON-serialisable format
    seat_ts_serialisable = {key: value.tolist() for key, value in seat_ts_dict.items()}

    # Save to a JSON file
    with open(output_file, 'w') as file:
        json.dump(seat_ts_serialisable, file, indent=4)

def save_timestamps_to_txt(timestamps, output_file):
    """
    Save a list of timestamps to a text file, each timestamp on a new line.
    
    Args:
        timestamps: List of timestamps to save.
        output_file: Path to the text file to save the timestamps.
    """
    with open(output_file, 'w') as file:
        for ts in timestamps:
            file.write(f"{ts}\n")


#
def getSeatTS(seat: str, day:str, timeboundaries:tuple[str, str]) -> pd.Series:
    '''
        for a given seat, day and bounding timestamps, gets the timestamps of whenever that seat was detected to be occupied
        Args:
            seat: the given seat of interest
            day: the given day of interest
            timeboundaries: tuple of earliest and latest allowed timestamps
        Returns:
            seatTS: timestamp series of when the seat was detected to be occupied by node
    '''

    # first get df of times selected
    boundedNodeDF : pd.DataFrame = getBoundedNodeDF(day, timeboundaries)

    # filter for values which contain the required seat
    targetSeatDF : pd.DataFrame = boundedNodeDF[boundedNodeDF['seats_occupied'].apply(lambda x: seat in x)]
    seatTS = targetSeatDF['acp_ts'] 
    return seatTS

def getSeatTSDensityPointsKDE(seatTS: pd.Series, timeboundaries: tuple[str, str]) -> tuple[np.ndarray, np.ndarray]:
    '''
        estimates the density function of seat occupancy timestamps using kernel density estimation
        Args:
            seatTS: the timestamps of detected occupancy for a given seat
            timeboundaries: tuple of earliest and latest allowed timestamps
        Returns:
            (ts_samples, density): the x and y values for the estimated function
    '''
    seatTS = seatTS.to_numpy().reshape(-1, 1)
    kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(seatTS)
    ts_samples = np.linspace(timeboundaries[0], timeboundaries[1], len(seatTS)*10)
    ts_samples_2d = ts_samples.reshape(-1,1)
    density = np.exp(kde.score_samples(ts_samples_2d))
    return ts_samples, density

def getSeatTSDensityPointsEMA(seatTS: pd.Series, alpha=0.2) -> np.ndarray:
    '''
        estimates the density function of seat occupancy timestamps using exponential mean average
        Args:
            seatTS: the timestamps of detected occupancy for a given seat
            alpha: smoothing factor of EMA
        Returns:
            EMAdensity: y values for the estimated function
    '''
    intervals = np.diff(seatTS) + 0.05
    densities = 1 / intervals
    emaDensity = [0]
    for i in range(0, len(densities)):
        ema = alpha * densities[i] + (1 - alpha) * emaDensity[-1]
        emaDensity.append(ema)
    return np.array(emaDensity)

def getSeatCounts(day: int, timeboundaries: tuple[str, str]) -> defaultdict[str, int]:
    '''
        gets the total number of occupancy counts for every seat on a given day between given time boundaries
        Args:
            day: the given day of interest
            timeboundaries: tuple of earliest and latest allowed timestamps
        Returns:
            seatCounts: dictionary of seats mapped to their total counts for the given time period
    '''
    boundedNodeDF = getBoundedNodeDF(day, timeboundaries)
    seatCounts = defaultdict(int)
    for _, row in boundedNodeDF.iterrows():
        for seat in row['seats_occupied']:
            seatCounts[seat] += 1
    return seatCounts

def getSensorlevels(sensor: str, day: int, timeboundaries: tuple[str, str], metric: str) -> tuple[pd.Series, np.ndarray]:
    '''
        get the readings of a given sensor in a given timeperiod for a given metric
        Args:
            sensor: the sensor of interest
            day: the given day of interest 
            timeboundaries: tuple of earliest and latest allowed timestamps
            metric: metric of interest from sensor (e.g. 'co2')
        Returns:
            (sensorTS, sensorReadings): a tuple containing the metric levels of the sensor and the timestamps at which they were recieved
    '''

    with open(f'jan2024SensorSample/elsys-co2-{sensor}/01/elsys-co2-{sensor}_2024-01-{day}.txt', 'r') as file:
        sensorData = [json.loads(dataLine) for dataLine in file]
    sensorDataFrame = pd.DataFrame(sensorData)

    pd.set_option('display.float_format', '{:.10f}'.format)
    sensorDataFrame['acp_ts'] = pd.to_numeric(sensorDataFrame['acp_ts'])

    sensorDataFrameFiltered = sensorDataFrame[sensorDataFrame['payload_cooked'].apply(lambda x: metric in x)]
    if len(sensorDataFrameFiltered) == 0:
        raise MetricReadingError(f"No values of {metric} for {sensor} on this day")
    sensorDataFrameTsBound = sensorDataFrameFiltered[(sensorDataFrameFiltered['acp_ts'] >= timeboundaries[0]) & (sensorDataFrameFiltered['acp_ts'] <= timeboundaries[1])]
    sensorDataFrameTsBound.reset_index(drop=True, inplace=True)

    return sensorDataFrameTsBound['acp_ts'], np.array([payload[metric] for payload in sensorDataFrameTsBound['payload_cooked']])


def plotMetricWithBarcode(seat: str, sensor1: str, sensor2: str, day: int, timeboundaries: tuple[float, float], isSaved=False, metric='co2', vlineBoundary=2) -> None:
    '''
        plots a seat detection barcode plot containing the local and global sensor values and total crowdcount timeseries
        Args:
            seat: seat of given interest
            sensor1: the local sensor
            sensor2: the global sensor
            day: the day of given interest
            timeboundaries: tuple of earliest and latest allowed timestamps
            isSaved: whether or not the plot will be saved to the repo or simply displayed
            metric: metric of interest from sensor (e.g. 'co2')
            vLineBoundary: which timeseries the barcode lines height matches
    '''
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

    plt.savefig(f'discoveryPhase/plots/barcodePlots/second-facevisibilityPlots/{seat}-{metric}-{sensor1}-{sensor2}-{day}.png', format='png') if isSaved else plt.show()

def getSensor1Points(sensor1s: list[str], day:int, timeboundaries:tuple[str, str], metric: str, num_plots: int) -> tuple[dict[str, tuple[pd.Series, np.ndarray]], list[str], list[int]]:
    '''
        get the x and y values for a list of local sensors handling any cases where there are no readings for the given metric
        Args:
            sensor1s: the list of local sensors to take readings from if data is available
            day: day of given interest
            timeboundaries: tuple of earliest and latest allowed timestamps
            metric: metric of interest from sensor (e.g. 'co2')
            num_plots: the amount of graphs being plotted
        Returns:
            sensor1Points: dict mapping a local sensor to its readings for the given metric
            acceptedSensor1s: the list of local sensors which had readings for the given metric
            acceptedSensorIndexes: list of indexes of sensor1s which were accepted
    '''
    sensor1Points = {}
    acceptedSensor1s = []
    acceptedSensorIndexes = []
    i = 0
    for j, sensor1 in enumerate(sensor1s):
        try:
            sensor1Points[sensor1] = getSensorlevels(sensor1, day, timeboundaries, metric)
            acceptedSensor1s.append(sensor1)
            acceptedSensorIndexes.append(j)
            i += 1
        except MetricReadingError:
            print(f'no {metric} reading for {sensor1}, trying next sensor')
            continue
        if i >= num_plots:
            break
    return sensor1Points, acceptedSensor1s, acceptedSensorIndexes

def plotMultipleMetricWithBarcodeGivenTargets(
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
    ) -> None:
    '''
        plots a collection of seat detection barcode plots containing the local and global sensor values and total crowdcount timeseries given target seats and sensors
        Args:
            seat: seat of given interest
            sensor1s: the local sensors
            sensor2s: the global sensors
            day: the day of given interest
            timeboundaries: tuple of earliest and latest allowed timestamps
            isSaved: whether or not the plot will be saved to the repo or simply displayed
            metric: metric of interest from sensor (e.g. 'co2')
            vLineBoundary: which timeseries the barcode lines height matches
            num_plots: the number of plots in the full image
            isDensity: whether or not the barcode lines should be replaced by their estimated density function
    '''
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
            x, y = getSeatTSDensityPointsKDE(seatTSs[seat], timeboundaries)
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
    save_path = f'discoveryPhase/plots/combinedBarcodePlots/combinedFaceVisibilityPlots3/{metric}-{day}'
    if isDensity:
        save_path += '-density'
    plt.savefig(save_path + '.png', format='png') if isSaved else plt.show()

def overlay_density_alt(ax, timestamps, timeboundaries, chunk_size=20, label='Occupancy density', color='blue', output_file=None):
    '''
    Overlay a density lineplot on the given axis based on timestamps within specified timeboundaries,
    and optionally save timestamps to a text file.
    Args:
        ax: Matplotlib axis to overlay the density plot
        timestamps: List or array of timestamps to calculate density
        timeboundaries: Tuple of (start_time, end_time) for the x-axis
        chunk_size: Size of time chunks (in seconds) for density calculation
        label: Label for the density plot in the legend
        color: Line color for the density plot
        output_file: File path to save the timestamps (optional)
    '''
    # Sort the timestamps and initialize variables
    timestamps = sorted(timestamps)
    density_x = []
    density_y = []

    # Save timestamps to a file if output_file is provided
    if output_file:
        with open(output_file, 'w') as f:
            f.writelines(f"{ts}\n" for ts in timestamps)

    # Start from the first timestamp and chunk data
    start_time = timestamps[0] if timestamps else timeboundaries[0]
    while start_time < timeboundaries[1]:
        end_time = start_time + chunk_size
        chunk_count = len([ts for ts in timestamps if start_time <= ts < end_time])
        density_x.append((start_time + end_time) / 2)  # Midpoint of the chunk
        density_y.append(chunk_count)
        print(chunk_count)
        start_time = end_time

    # Plot the density
    ax.plot(density_x, density_y, color=color, label=label, linestyle='--', linewidth=2)
    return density_x, density_y




def plotMultipleBarcodeGivenSeats(
        seats: list[str], 
        day: int, 
        timeboundaries: tuple[float, float], 
        isSaved=False,  
        isDensity=False,
        isEMA=False,
        isCombined=False,
        isDensityAlt=False
    ) -> None:
    '''
        Plots seat detection barcode plots containing the total crowdcount timeseries given the seats of interest.
        Args:
            seats: Seats of interest.
            day: The day of interest.
            timeboundaries: Tuple of earliest and latest allowed timestamps.
            isSaved: Whether or not the plot will be saved to the repo or displayed.
            isDensity: Whether barcode lines should be replaced by their estimated density function.
            isEMA: Whether EMA or KDE will be used for density estimation.
            isCombined: Whether both density and barcodes will be plotted.
            isDensityAlt: Whether to overlay a lineplot for density based on time chunking.
    '''
    seatTSs = {seat: getSeatTS(seat, day, timeboundaries) for seat in seats}
    print("Seats being processed:", list(seatTSs.keys()))

    boundedNodeDF = getBoundedNodeDF(day, timeboundaries)
    crowdcountTS, crowdcount = boundedNodeDF['acp_ts'], boundedNodeDF['crowdcount']

    # x_plots = 3
    # y_plots = 6
    # fig, axs = plt.subplots(y_plots, x_plots, figsize=(43, 27))
    x_plots = 3
    y_plots = 2
    fig, axs = plt.subplots(y_plots, x_plots, figsize=(43, 12))
    fig.tight_layout(pad=10, w_pad=15, h_pad=10)

    # Iterate over seats and axes
    for ax, seat in zip(axs.flatten(), seats[:x_plots * y_plots]):
        xticksTS = np.linspace(timeboundaries[0], timeboundaries[1], int((timeboundaries[1] - timeboundaries[0]) / 600) + 1)
        xticksLabels = [datetime.fromtimestamp(tickTS).strftime('%H:%M') for tickTS in xticksTS]
        ax.set_xticks(xticksTS)
        ax.set_xticklabels(xticksLabels, rotation=60)
        ax.set_xlim(timeboundaries)
        ax.set_xlabel('ACP timestamp')
        ax.set_title(f'{seat} occupancy levels ({day}/01/2024)')

        axDensity = ax.twinx()
        axDensity.set_xlim(timeboundaries[0], timeboundaries[1])
        axDensity.set_yticks([])
        axDensity.set_yticklabels([])

        # Plot barcode lines
        # y = np.ones_like(seatTSs[seat])
        # Increase the height of the barcode lines
        height = 10  # Adjust this to control the height
        y = np.full_like(seatTSs[seat], height)
        axDensity.bar(seatTSs[seat], y, width=1, align='center', color='black', alpha=0.1)
        
        # Save timestamps to .txt
        save_timestamps_to_txt(seatTSs[seat], f"{day}_{seat}_seatTS.txt")

        #  Save TS to debug
       # Example usage
        save_seat_ts_to_json(seatTSs, f'{day}_seatTS.json')

        # Overlay density plot if selected
        if isDensityAlt:
            print("DENSITY ALT SELECTED")
            overlay_density_alt(
            ax=ax, 
            timestamps=seatTSs[seat], 
            timeboundaries=(timeboundarystart, timeboundaryend), 
            chunk_size=60, 
            label='Occupancy density', 
            color='blue', 
            output_file=str(day)+"_"+str(seat)+'timestamps.txt'
        )

        print(seat)
        # print(seatTSs[seat])
        # print("y",y)
        # Crowdcount overlay
        ax2 = ax.twinx()
        ax2.plot(crowdcountTS, crowdcount, color='orange', label='Total crowdcount')
        ax2.set_ylabel('Total crowdcount')
        ax2.set_ylim(0, 150)
        ax2.tick_params(axis='y')

        # Combine legends
        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        handles3, labels3 = axDensity.get_legend_handles_labels()
        handles = handles1 + handles2 + handles3
        labels = labels1 + labels2 + labels3
        ax.legend(handles, labels, loc='upper left')

    # Hide unused axes
    for ax in axs.flatten()[len(seats[:x_plots * y_plots]):]:
        print("Hiding unused subplot")
        ax.axis('off')

    save_path = f'discoveryPhase/plots/combinedBarcodePlots/combinedFaceVisibilityPlots4/{day}'
    save_format = '.png'
    if isDensityAlt:
        save_path += '-density-alt'
    plt.savefig(save_path + save_format, format=save_format[1:]) if isSaved else plt.show()
    print(f"Saved in: {save_path}{save_format}")


def filterae2(day, seat):
    '''
        filter function to remove sensor 058ae2 if the day is greater than 22
    '''
    return not (NEAREST_SENSOR_BY_SEAT[seat] == '058ae2' and day > 22)

def filterac9(day, seat):
    '''
        filter function to remove sensor 058ac9 if the day is greater than 24
    '''
    return not (NEAREST_SENSOR_BY_SEAT[seat] == '058ac9' and day > 24)

def plotMultipleMetricWithBarcode(
        day: int, 
        timeboundaries: tuple[float, float], 
        isSaved=False, 
        metric='co2', 
        vlineBoundary=2, 
        num_plots=15, 
        isDensity=False
    ):
    '''
        plots a collection of seat detection barcode plots containing the local and global sensor values and total crowdcount timeseries
        Args:
            day: the day of given interest
            timeboundaries: tuple of earliest and latest allowed timestamps
            isSaved: whether or not the plot will be saved to the repo or simply displayed
            metric: metric of interest from sensor (e.g. 'co2')
            vLineBoundary: which timeseries the barcode lines height matches
            num_plots: the number of plots in the full image
            isDensity: whether or not the barcode lines should be replaced by their estimated density function
    '''
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
    plotMultipleMetricWithBarcodeGivenTargets(faceDetectionSeatsNearSensors, sensor1s, sensor2s, day, timeboundaries, isSaved, metric, vlineBoundary, num_plots, isDensity=isDensity)

def plotMultipleBarcodes(
        day: int, 
        timeboundaries: tuple[float, float], 
        isSaved=False, 
        isDensity=False,
        isEMA=False,
        isCombined=False,
        isDensityAlt=False
    ) -> None:
    '''
        plots 3 seat detection barcode plots containing the total crowdcount timeseries given the seats of interest
        Args:
            day: the day of given interest
            timeboundaries: tuple of earliest and latest allowed timestamps
            isSaved: whether or not the plot will be saved to the repo or simply displayed
            isDensity: whether or not the barcode lines should be replaced by their estimated density function
            isEMA: whether EMA or KDE will be used for the density estimation function
            isCombined: whether or not both density and barcodes will be plotted
    '''
    faceDetectionSeatCounts = getSeatCounts(day, timeboundaries)
    sortedFaceDetectionSeats = sorted(faceDetectionSeatCounts, key=faceDetectionSeatCounts.get, reverse=True)
    print("Params:",timeboundaries, "|Saved:",isSaved,"|Density:", isDensity,"|Alt Density:", isDensityAlt,"|EMA:", isEMA, "|Combined:",isCombined)
    plotMultipleBarcodeGivenSeats(sortedFaceDetectionSeats, day, timeboundaries, isSaved, isDensity, isEMA, isCombined=isCombined, isDensityAlt=isDensityAlt)

if __name__ == '__main__':
    for DAY in range(22, 25, 2):
        timeboundarystart = datetime.strptime(f'2024-1-{DAY} 8:30:00', "%Y-%m-%d %H:%M:%S").timestamp()
        timeboundaryend = datetime.strptime(f'2024-1-{DAY} 13:30:00', "%Y-%m-%d %H:%M:%S").timestamp() 
        print("plotting", "density + barcode", "on day", DAY)
        plotMultipleBarcodes(day=DAY,
                             timeboundaries=(timeboundarystart,
                                             timeboundaryend),
                             isSaved=True,
                             isDensity=False,
                             isEMA=False,
                             isCombined=False,
                             isDensityAlt=True)

