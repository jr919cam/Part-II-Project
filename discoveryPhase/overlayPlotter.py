import matplotlib.pyplot as plt
from co2Plotter import getXYAndLabels as getXYAndLabelsco2
from crowdcountPlotter import getXYAndLabels as getXYAndLabelsCrowdcount
from density_calculator import getac0densities

SENSOR = 'ac0'
def main():
    fig, ax1 = plt.subplots(figsize=(12,6))
    ccx, ccy, labels, mask = getXYAndLabelsCrowdcount('24')
    y = getac0densities()
    ax1.plot(ccx, y[mask], color="r")
    ax1.set_ylabel('ac0 density', color='r')
    ax1.tick_params(axis='y', labelcolor='r') 

    ax2 = ax1.twinx()
    co2x, co2y, _ = getXYAndLabelsco2(SENSOR, '24')
    ax2.plot(co2x, co2y)
    ax2.set_xlabel('ACP timestamp')
    ax2.set_ylabel('co2 level', color='b')
    ax2.tick_params(axis='y', labelcolor='b')

    plt.xticks(labels, rotation=45)
    for label in labels:
        plt.axvline(x=label, color='grey', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(f'discoveryphase/plots/overlayPlots/overlay-{SENSOR}-density.png', format='png')

if __name__ == '__main__':
    main()