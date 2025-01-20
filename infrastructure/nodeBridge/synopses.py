import numpy as np
from collections import defaultdict

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


class WholeRoomStabilitySynopsis():
    def __init__(self):
        self.prevSeatsOccupied = set()
        self.seatsOccupiedDiffCountTotal = 0
        self.seatsOccupiedDiffCount = 0

    def updateRoomStability(self, seatsOccupied):
        seatsOccupiedSet = set(seatsOccupied)
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
        self.avg = (sum(self.counts.values()) / self.readingsCount ) / len(self.counts)

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

    def updateEMA(self, JSONDataList: list[dict], t:int):
        if t < 1:
            return
        crowdcountDelta = JSONDataList[t]['crowdcount'] - JSONDataList[t-1]['crowdcount']
        self.timeDelta = float(JSONDataList[t]['acp_ts']) - float(JSONDataList[t-1]['acp_ts'])
        self.EMA = self.alpha * crowdcountDelta + (1-self.alpha) * self.EMA

    def isEMALectureUpEvent(self, JSONDataList: list[dict], t:int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastUpEvent >= 0 and self.timeSinceLastUpEvent < 10 * 60:
            self.timeSinceLastUpEvent += self.timeDelta
            return False
        if (self.EMA * 9.5 / (np.log(JSONDataList[t]['crowdcount'] + 1) + 1)) < 1:
            return False
        self.timeSinceLastUpEvent = 0
        self.timeSinceLastDownEvent = -1
        return True
    
    def isEMALectureDownEvent(self, JSONDataList: list[dict], t:int)->bool:
        if t < 1:
            return False
        if self.timeSinceLastDownEvent >= 0 and self.timeSinceLastDownEvent < 10 * 60:
            self.timeSinceLastDownEvent += self.timeDelta
            return False
        if (self.EMA * 7 / (np.log(JSONDataList[t]['crowdcount'] + 1) + 1)) > -1:
            return False
        self.timeSinceLastDownEvent = 0
        self.timeSinceLastUpEvent = -1
        return True