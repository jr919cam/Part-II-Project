import json
from enum import Enum
import pandas as pd

class seatEvent(Enum):
    Appear = 'Appear'
    Disappear = 'Disappear'

def main():
    print(getEvents(1706094300, 1706097300, ['MG4', 'MG5', 'MF4', 'MF5']))

def getEvents(startTime: float, endTime: float, seats: list[str] = []):
    '''
        hardcoded date and time period

        script which measures any change in seat occupancy given a selection of seats and time boundaries
        gives timestamps for each event
    '''
    with open('node_22-28Jan/cerberus-node-lt1_2024-01-24.txt', 'r') as file:
        nodeData = [json.loads(dataLine) for dataLine in file]
    nodeDataFrame = pd.DataFrame(nodeData)
    nodeDataFrame['acp_ts'] = pd.to_numeric(nodeDataFrame['acp_ts'])
    lectureDF = nodeDataFrame[(nodeDataFrame['acp_ts'] <= endTime) & (nodeDataFrame['acp_ts'] >= startTime)]
    current_seats = set()
    prev_seats = set()
    events = [] # list of dicts which contain 'acp_ts', 'seat' and 'seatEvent'

    seat_set = set(seats)

    for i, row in lectureDF.iterrows():
        prev_seats = current_seats
        current_seats = set(row['seats_occupied'])
        appeared = (current_seats - prev_seats) & seat_set
        disappeared = (prev_seats - current_seats) & seat_set
        for app in appeared:
            events.append({'acp_ts': row['acp_ts'], 'seat':app, 'seatEvent':seatEvent.Appear.value})
        for dis in disappeared:
            events.append({'acp_ts': row['acp_ts'], 'seat':dis, 'seatEvent':seatEvent.Disappear.value})
    return events

if __name__ == '__main__':
    main()
