from nodeBridgeEmulator import getNodeDf
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime

df = getNodeDf("2025-01-24", 1737707400 + 3600, 1737725400-7200)

x = df['acp_ts']
crowdcount = df['crowdcount']

diffs = [0, *np.diff(crowdcount)]

diffEMA = [0]

for diff in diffs:
    diffEMA.append(diffEMA[-1] + 0.1 * (diff - diffEMA[-1]))
diffEMA = diffEMA[1:]
scaleddiffEMA = [diffema * 50 for diffema in diffEMA]

ccEMA = [0]
sdEMA = [0]
for cc in crowdcount:
    ccEMA.append(ccEMA[-1] + 0.05 * (cc - ccEMA[-1]))
    sdEMA.append(sdEMA[-1] + 0.1 * (np.sqrt((ccEMA[-1] - cc)**2) - sdEMA[-1]))
ccEMA = ccEMA[1:]
sdEMA = sdEMA[1:]

# cc_window = []
# rolling_cc_sds = []

# for cc in crowdcount:
#     cc_window.append(cc)
#     if len(cc_window) > 8:
#         cc_window.pop(0)
#     rolling_cc_sds.append(np.std(cc_window))




# smoothEMA = [0]

# for diff in diffs:
#     smoothEMA.append(smoothEMA[-1] + 0.01 * (diff - smoothEMA[-1]))
# smoothEMA = smoothEMA[1:]
# scaledsmoothEMA = [(smoothema * 1000)/(np.log(cc) + 1) for smoothema, cc in zip(smoothEMA, crowdcount)]


plt.plot(x, crowdcount)
plt.plot(x, sdEMA)
# plt.plot(x, rolling_cc_sds)
# plt.plot(x, ccEMA)
# plt.plot(x, scaleddiffEMA)
# plt.plot(x, scaledsmoothEMA)
xticksLabels = np.array([datetime.fromtimestamp(tickTS).strftime('%H:%M') for tickTS in x])
plt.xticks(x[::1000], xticksLabels[::1000])
plt.ylim(-50, 150)
plt.show()