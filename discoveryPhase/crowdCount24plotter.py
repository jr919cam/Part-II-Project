from datetime import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# extract crowdcount data from the sample data give
with open('node_22-28Jan/cerberus-node-lt1_2024-01-24.txt', 'r') as file:
    nodeData = [json.loads(dataLine) for dataLine in file]
nodeDataFrame = pd.DataFrame(nodeData)
crowdCount = np.array(nodeDataFrame["crowdcount"])

# extract and then format timestamp data
timeStamps = np.array(nodeDataFrame["acp_ts"])
hourMinuteStrings = np.array([datetime.fromtimestamp(float(ts)).strftime("%H:%M") for ts in timeStamps])
mask = (hourMinuteStrings >= "08:00") & (hourMinuteStrings <= "17:00")
boundedCrowdCount = crowdCount[mask]
boundedHourMinuteStrings = hourMinuteStrings[mask]

labels = [f"{i:02}:00" for i in range(8, 18)]

# plot data
plt.figure(figsize=(12, 6))
plt.plot(boundedHourMinuteStrings, boundedCrowdCount)
plt.xticks(labels, rotation=45)
for label in labels:
    plt.axvline(x=label, color='grey', linestyle='--', linewidth=0.5)
plt.xlabel('ACP timestamp')
plt.ylabel('LT1 crowd count')
plt.tight_layout()
plt.savefig('discoveryphase/plots/crowdCount24plot.png', format='png')