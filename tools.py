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
