import time, datetime
from tracemalloc import start
from dateutil.parser import parse as timeparse

def flattenIntervals(intervals):
    intervals.sort()
    i = 0
    ans = []
    while i < len(intervals):
        start = intervals[i][0]
        bound = intervals[i][1]
        i += 1
        while i < len(intervals) and intervals[i][0] <= bound:
            bound = max(intervals[i][1], bound)
            i += 1
        ans.append((start, bound))
        #print(ans)
    return ans

def plotAuras(startTime, endTime, intervals):
    t0 = timeparse(startTime)
    x0 = 0
    x1 = (timeparse(endTime) - t0).total_seconds()
    x_Left = [(timeparse(i[0]) - t0).total_seconds() for i in intervals]
    x_Width = [(timeparse(i[1]) - timeparse(i[0])).total_seconds() for i in intervals]
    return x0, x1, x_Left, x_Width
