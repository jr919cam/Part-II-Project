import json
import numpy as np
import pandas as pd
from river import tree
from river import metrics
from river import preprocessing
import matplotlib.pyplot as plt



def main():
    with open('jan2024SensorSample/elsys-co2-058ac6/01/elsys-co2-058ac6_2024-01-24.txt', 'r') as file:
        ac6Data = [json.loads(dataLine) for dataLine in file]
    ac6DataFrame = pd.DataFrame(ac6Data)
    readings = ac6DataFrame['payload_cooked']
    clean_readings = [reading for reading in readings if 'co2' in reading]
    model = (
        preprocessing.StandardScaler() |
        tree.HoeffdingAdaptiveTreeRegressor()
    )
    metric = metrics.MAE()

    clean_readings = clean_readings[400:1200]
    co2_preds = [clean_readings[0]['co2']]

    for i in range(1, len(clean_readings)):
        x = {
            'temperature': clean_readings[i - 1]['temperature'],        
            'co2': clean_readings[i - 1]['co2']                  
        }
        y = clean_readings[i]['co2']

        y_pred = model.predict_one(x)
        model.learn_one(x, y)

        metric.update(y, y_pred)
        if y_pred is not None:
            print(f'True: {y:.2f}, Predicted: {y_pred:.2f}, Error: {metric.get():.4f}')
            co2_preds.append(y_pred)
        
    

    print(f'Final Mean Absolute Error (MAE): {metric.get():.4f}')
    co2 = [clean_reading['co2'] for clean_reading in clean_readings]
    n_co2 = len(co2)
    x = np.linspace(0, n_co2, n_co2)
    plt.plot(x, co2, label="co2 level")
    plt.plot(x, co2_preds, color="r", label="predicted co2 level")
    plt.ylim(350, 600)
    plt.ylabel('AC6 sensor co2 levels')
    plt.legend()
    plt.text(0, -0.2, f'MAE = {metric.get()}', 
        horizontalalignment='center', verticalalignment='center', 
        transform=plt.gca().transAxes)
    plt.tight_layout()
    plt.savefig(f'discoveryphase/plots/hoeffdingplots/hoeffding_+temp_co2t+1_pred.png', format='png')
    plt.close()

    



if __name__ == '__main__':
    main()
    