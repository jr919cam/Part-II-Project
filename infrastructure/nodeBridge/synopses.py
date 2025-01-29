import numpy as np
from collections import defaultdict

import pandas as pd

class PercentageConcentrationSynopsis():
    def __init__(self, seat):
        self.seat = seat
        if seat == None:
            self.avg = None  
        else:
            self.avg = 0
        self.seatCount = 0
        self.readingsCount = 0
    
    def updateAverage(self, seats_occupied):
        if self.seat in seats_occupied:
            self.seatCount += 1
        self.readingsCount += 1
        self.avg = self.seatCount/self.readingsCount

class PeriodSynopsis():
    def __init__(self, period:int, startTS:float):
        '''
            #### Parameters:

            period: time in seconds for each measurement period
            startTS: starting timestamp
        '''
        self.period = period
        self.periodMeans = []
        self.periodSDs = []
        self.currents = {"count":0, "mean":0, "m2":0, "tsLimit":startTS + period}

    def updatePeriodMetrics(self, crowdcount:int):
        self.currents["count"] += 1
        delta = crowdcount - self.currents["mean"]
        self.currents["mean"] += delta/self.currents["count"]
        self.currents["m2"] += delta*(crowdcount - self.currents["mean"])
    
    def resetIfPeriodEnd(self, ts: float):
        if ts > self.currents["tsLimit"]:
            self.periodMeans.append("{:.1f}".format(self.currents['mean']))
            self.periodSDs.append("{:.1f}".format((self.currents['m2']/(self.currents["count"] - 1))**(0.5)))
            self.currents = {"count":0, "mean":0, "m2":0, "tsLimit": self.currents["tsLimit"] + self.period}

class WholeRoomStabilitySynopsis():
    def __init__(self):
        self.prevSeatsOccupied = set()
        self.seatsOccupiedDiffCountTotal = 0
        self.seatsOccupiedDiffCount = 0

    def updateRoomStability(self, seatsOccupied, t):
        seatsOccupiedSet = set(seatsOccupied)
        if t > 0:
            self.seatsOccupiedDiffCountTotal += len(seatsOccupiedSet.symmetric_difference(self.prevSeatsOccupied))
            self.seatsOccupiedDiffCount = len(seatsOccupiedSet.symmetric_difference(self.prevSeatsOccupied))
        self.prevSeatsOccupied = seatsOccupiedSet

class WholeRoomAvgOccupancySynopsis():
    def __init__(self):
        self.readingsCount = 0
        self.counts = defaultdict(int)
        self.avg = 0

    def updateRoomAvgOccupancy(self, seatsOccupied):
        self.readingsCount += 1
        for seat in seatsOccupied:
            self.counts[seat] += 1
        if self.readingsCount > 0 and len(self.counts) > 0:
            self.avg = (sum(self.counts.values()) / self.readingsCount ) / len(self.counts)
    
    def getStdDev(self):
        return np.sqrt(sum([(self.avg - count/self.readingsCount) ** 2 for count in self.counts.values()]) / len(self.counts))

    def reset(self):
        self.readingsCount = 0
        self.counts = defaultdict(int)
        self.avg = 0

class LectureBoundarySynopsis():
    def __init__(self, EMA, alpha):
        self.EMA = EMA
        self.alpha = alpha
        self.timeSinceLastUpEvent = -1
        self.timeSinceLastDownEvent = -1
        self.timeDelta = 0

    def updateEMA(self, nodeDf: pd.DataFrame, t:int):
        if t < 1:
            return
        crowdcountDelta = nodeDf.loc[t]['crowdcount'] - nodeDf.loc[t-1]['crowdcount']
        self.timeDelta = float(nodeDf.loc[t]['acp_ts']) - float(nodeDf.loc[t-1]['acp_ts'])
        self.EMA = self.alpha * crowdcountDelta + (1-self.alpha) * self.EMA

    def isEMALectureUpEvent(self, nodeReading: pd.Series, t: int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastUpEvent >= 0 and self.timeSinceLastUpEvent < 10 * 60:
            self.timeSinceLastUpEvent += self.timeDelta
            return False
        if (self.EMA * 13.5 / (np.log(nodeReading['crowdcount'] + 1) + 1)) < 1:
            return False
        self.timeSinceLastUpEvent = 0
        self.timeSinceLastDownEvent = -1
        return True
    
    def isEMALectureDownEvent(self, nodeReading: pd.Series, t:int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastDownEvent >= 0 and self.timeSinceLastDownEvent < 10 * 60:
            self.timeSinceLastDownEvent += self.timeDelta
            return False
        if (self.EMA * 12.5 / (np.log(nodeReading['crowdcount'] + 1) + 1)) > -1:
            return False
        self.timeSinceLastDownEvent = 0
        self.timeSinceLastUpEvent = -1
        return True