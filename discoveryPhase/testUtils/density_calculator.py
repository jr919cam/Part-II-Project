def getac0densities():    
    '''
    get the person density (num of detected people in the 3*3 area) around sensor ac0
    '''
    import json
    import numpy as np
    import pandas as pd


    indicies = {}
    rows = ['A','B','C','D','E','F','G','H','I','J','K','L']
    def getLeftIndicies():
        for i, row in enumerate(rows):
            for j in range(1,7):
                indicies['L'+row+str(j)] = (j-1,i*2 + 1)
    def getMiddleIndicies():
        for i, row in enumerate(rows[:9]):
            for j in range(1,15):
                indicies['M'+row+str(j)] = (8+j,i*2 + 1)
    def getRightIndicies():
        for i, row in enumerate(rows[:11]):
            for j in range(1,7):
                indicies['R'+row+str(j)] = (25+j,i*2 + 1)
    getLeftIndicies(); getMiddleIndicies(); getRightIndicies()

    with open(f'node_22-28Jan/cerberus-node-lt1_2024-01-24.txt', 'r') as file:
        nodeData = [json.loads(dataLine) for dataLine in file]
    nodeDataFrame = pd.DataFrame(nodeData)
    seatsOccupiedList = nodeDataFrame['seats_occupied']
    print(len(seatsOccupiedList))

    ac0densities = []
    for seatsOccupied in seatsOccupiedList:
        # I want to find the density for a given sensor, e.g AC0
        # AC0 located between indicies (14,13) & (15,13)
        #
        density = 0
        for seat in seatsOccupied:
            inds = indicies[seat]
            if inds[0] >= 11 and inds[0] <= 18 and inds[1] >= 10 and inds[1] <= 16:
                density += 1
        ac0densities.append(density)
    return np.array(ac0densities)