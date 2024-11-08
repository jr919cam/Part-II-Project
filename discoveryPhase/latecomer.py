import json
import pandas as pd

def main():
    with open('node_22-28Jan/cerberus-node-lt1_2024-01-24.txt', 'r') as file:
        nodeData = [json.loads(dataLine) for dataLine in file]
    nodeDataFrame = pd.DataFrame(nodeData)
    nodeDataFrame['acp_ts'] = pd.to_numeric(nodeDataFrame['acp_ts'])
    lecture1DF = nodeDataFrame[(nodeDataFrame['acp_ts'] <= 1706097300) & (nodeDataFrame['acp_ts'] >= 1706094300)]
    lecture1DF.reset_index(drop=True, inplace=True)
    lateness = {}
    order = []
    for i in range(len(lecture1DF)):
        current_ts = lecture1DF['acp_ts'][i]
        for seat in lecture1DF['seats_occupied'][i]:
            if seat not in lateness:
                lateness[seat] =  current_ts - 1706094300
                order.append(seat)
    
    for seat in order:
        print(seat, lateness[seat])

if __name__ == '__main__':
    main()