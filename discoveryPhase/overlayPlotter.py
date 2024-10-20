import matplotlib.pyplot as plt
from co2Plotter import boundedHourMinuteStrings as co2x, boundedco2 as co2y, labels
from crowdcountPlotter import boundedHourMinuteStrings as ccx, boundedCrowdCount as ccy

fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(ccx, ccy, color="r")
ax1.set_ylabel('crowd count', color='r')
ax1.tick_params(axis='y', labelcolor='r') 

ax2 = ax1.twinx()
ax2.plot(co2x, co2y)
ax2.set_xlabel('ACP timestamp')
ax2.set_ylabel('co2 level', color='b')
ax2.tick_params(axis='y', labelcolor='b')

plt.xticks(labels, rotation=45)
for label in labels:
    plt.axvline(x=label, color='grey', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig('discoveryphase/plots/overlay.png', format='png')
