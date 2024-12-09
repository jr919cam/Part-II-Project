from datetime import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from discoveryPhase.testUtils.faceEvent import getEvents

def getXYAndLabels(sensor, day):
    with open(f'jan2024SensorSample/elsys-co2-{sensor}/01/elsys-co2-{sensor}_2024-01-{day}.txt', 'r') as file:
        ac6Data = [json.loads(dataLine) for dataLine in file]
    ac6DataFrame = pd.DataFrame(ac6Data)
    ac6DataFrame['acp_ts'] = pd.to_numeric(ac6DataFrame['acp_ts'])
    ac6DataFrameFiltered = ac6DataFrame[ac6DataFrame['payload_cooked'].apply(lambda x: 'co2' in x)]
    ac6DataFrameFiltered.reset_index(drop=True, inplace=True)
    ac6DataFrameTsBound = ac6DataFrameFiltered[(ac6DataFrameFiltered['acp_ts'] % 86400 >= 11*3600) & (ac6DataFrameFiltered['acp_ts'] % 86400 <= 12*3600)]
    ac6DataFrameTsBound.reset_index(drop=True, inplace=True)

    timestamps = np.array(pd.to_numeric(ac6DataFrameTsBound["acp_ts"]))
    co2 = np.array([payload['co2'] for payload in ac6DataFrameTsBound['payload_cooked']])
    labels = [f"11:{i*10:02}" for i in range(7)]
    return  timestamps, co2, labels

def plotData(sensor, day, events = pd.DataFrame(), title = ''):
    x, y, labels = getXYAndLabels(sensor, day)
    plt.figure(figsize=(12, 6))
    plt.plot(x, y)
    labelXValues = np.linspace(x[0], x[-1], 7)
    plt.xticks(labelXValues, labels, rotation=45)
    for labelx in labelXValues:
        plt.axvline(x=labelx, color='grey', linestyle='--', linewidth=0.5)
    for _, event in events.iterrows():
        event_color = 'lime' if event['seatEvent'] == 'Appear' else 'red'
        plt.axvline(x=event['acp_ts'], color=event_color, linestyle='--', label='late arrival', linewidth=1)

    plt.xlim(x[0], x[-1])
    plt.xlabel('ACP timestamp')
    plt.ylabel(f'{sensor} sensor co2 levels')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f'discoveryphase/plots/{sensor}-co2-{day}11-12plot.png', format='png')

def main():
    events = pd.DataFrame(getEvents(1706094300, 1706097300, ['RE1', 'RE2', 'RF1', 'RF2', 'RD1', 'RD2']))
    print(events)
    title = 'co2 at ae7 with seatEvents from RE1, RE2, RF1, RF2, RD1, RD2 marked'
    plotData('058b14', '24', events, title)

if __name__ == '__main__':
    main()