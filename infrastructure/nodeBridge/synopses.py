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
    
    def resetIfPeriodEnd(self, ts: float) -> bool:
        isPastLimit = ts > self.currents["tsLimit"]
        if isPastLimit:
            self.periodMeans.append("{:.1f}".format(self.currents['mean']))
            self.periodSDs.append("{:.1f}".format((self.currents['m2']/(self.currents["count"] - 1))**(0.5)))
            self.currents = {"count":0, "mean":0, "m2":0, "tsLimit": self.currents["tsLimit"] + self.period}
        return isPastLimit

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

class LeccentrationSynopsis():
    def __init__(self):
        self.readingsCount = 0
        self.counts = defaultdict(int)
        self.leccentration = 0

    def updateLeccentration(self, seatsOccupied):
        self.readingsCount += 1
        for seat in seatsOccupied:
            self.counts[seat] += 1
        if self.readingsCount > 0 and len(self.counts) > 0:
            self.leccentration = (sum(self.counts.values()) / self.readingsCount ) / len(self.counts)
    
    def getStdDev(self):
        if len(self.counts) == 0: return 0
        return np.sqrt(sum([(self.leccentration - count/self.readingsCount) ** 2 for count in self.counts.values()]) / len(self.counts))

    def reset(self):
        self.readingsCount = 0
        self.counts = defaultdict(int)
        self.leccentration = 0

class LectureBoundarySynopsis():
    def __init__(self, diffEMA, alpha):
        self.diffEMA = diffEMA
        self.alpha = alpha
        self.timeSinceLastUpEvent = -1
        self.timeSinceLastDownEvent = -1
        self.timeDelta = 0

        self.isLectureEntering = False
        self.isLectureExiting = False
        self.inLecture = False
        self.ccEMA = 0
        self.varEMA = 0

    def updateEMA(self, nodeDf: pd.DataFrame, t:int):
        if t < 1:
            return
        crowdcountDelta = nodeDf.loc[t]['crowdcount'] - nodeDf.loc[t-1]['crowdcount']
        self.timeDelta = float(nodeDf.loc[t]['acp_ts']) - float(nodeDf.loc[t-1]['acp_ts'])
        self.diffEMA = self.alpha * crowdcountDelta + (1-self.alpha) * self.diffEMA

        self.ccEMA = 0.05 * (nodeDf.loc[t]['crowdcount']) + (1-0.05) * self.ccEMA
        self.varEMA = 0.1 * np.sqrt((nodeDf.loc[t]['crowdcount'] - self.ccEMA)**2) + (1-0.1) * self.varEMA

    def isEMALectureUpEvent(self, nodeReading: pd.Series, t: int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastUpEvent >= 0 and self.timeSinceLastUpEvent < 10 * 60:
            self.timeSinceLastUpEvent += self.timeDelta
            return False
        if (self.diffEMA * 13.5 / (np.log(nodeReading['crowdcount'] + 1) + 1)) < 1:
            return False
        self.timeSinceLastUpEvent = 0
        self.timeSinceLastDownEvent = -1
        self.isLectureEntering = True
        return True
    
    def hasEMAlectureSettled(self, nodeReading: pd.Series, t: int)->bool:
        if t < 1:
            return False
        if not self.isLectureEntering and not self.isLectureExiting:
            return False
        print(self.varEMA)
        if self.varEMA < 1.5:
            self.isLectureEntering = False
            self.isLectureExiting = False
            if nodeReading['crowdcount'] < 5:
                return False
            self.inLecture = True
            return True
        return False

    def isEMALectureDownEvent(self, nodeReading: pd.Series, t:int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastDownEvent >= 0 and self.timeSinceLastDownEvent < 10 * 60:
            self.timeSinceLastDownEvent += self.timeDelta
            return False
        if (self.diffEMA * 12.5 / (np.log(nodeReading['crowdcount'] + 1) + 1)) > -1:
            return False
        self.timeSinceLastDownEvent = 0
        self.timeSinceLastUpEvent = -1
        self.isLectureExiting = True
        return True
    
    def wasLecture(self):
        if not self.inLecture: 
            return False
        self.inLecture = False
        return True