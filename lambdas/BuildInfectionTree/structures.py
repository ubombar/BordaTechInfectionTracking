import collections
import datetime
import math
from datetime import datetime, timedelta
import json
import bisect
import sortedcontainers

class Graph():
    def __init__(self):
        self.__adjacent = collections.defaultdict(set) # {id: {ids...}}
        self.__edges = collections.defaultdict(list) # {(id1, id2):[edge]}

    def adj_nodes(self, id0):
        return self.__adjacent[id0]
    
    def adj_edges(self, id1, id2):
        if id1 > id2: id1, id2 = id2, id1 # (1, 2)

        return self.__edges[(id1, id2)]

    def connect(self, id1, id2, edge):
        self.__adjacent[id1].add(id2)
        self.__adjacent[id2].add(id1)

        if id1 > id2: id1, id2 = id2, id1 # (1, 2)

        self.__edges[(id1, id2)].append(edge)

class Timeline():
    def __init__(self):
        self.lines = collections.defaultdict(list) # {id:[(date, result)]}
    
    def status(self, id0, date:datetime, INCUB=timedelta(days=14)):
        lines = self.lines[id0]
        size = len(lines)

        if size == 0: return "U"
        if size == 1:
            fdate, fstatus = lines[0]
            if fstatus: return "H" if fdate - date > INCUB else "I"
            else: return "H" if fdate > date else "U"

        for i in range(size - 1):
            fdate, fstatus = lines[i]
            sdate, sstatus = lines[i + 1]

            if date < fdate: return "H"
            elif date < sdate:
                if not fstatus and sstatus: # N P
                    return "H" if sdate - date > INCUB else "I"
                return "I" if fstatus else "H"
        
        return "I" if sstatus else "U"

    def register(self, id0, date, result, INCUB=timedelta(days=14)): # O(N)
        '''
        line = self.lines[id0]
        size = len(line)

        if size == 0:
            line.append((date, result))
            return

        for i, (sdate, _) in enumerate(line):
            if not date < sdate: continue
            line.insert(i, (date, result))
            return
        line.append((date, result))
        '''
        bisect.insort(self.lines[id0], (date, result))

    def indexof(self, id0, date:datetime, INCUB=timedelta(days=14)):
        lines = self.lines[id0]
        size = len(lines)

        if size == 0: return -1

        for i, (tdate, _) in enumerate(lines):
            if date < tdate: 
                return i - 1
        return size - 1

    def periods(self, id0, date:datetime, INCUB=timedelta(days=14)):
        s = date
        L = self.lines[id0]
        if len(L) == 0: return []
        if len(L) == 1:
            time, result = L[0]
            if result:
                return [] if s + INCUB < time else [(time - INCUB, s)]# P
            else:
                return [] if s < time else [(time, s)]# N

        i, j = 0, 1
        period = []
        start, end = L[0][0] - INCUB, L[1][0]

        itime, jtime = start, end
        end_append = False

        if end > s: return []

        while jtime < s and j < len(L):
            itime, iresult = L[i] # first
            jtime, jresult = L[j] # second

            if iresult and jresult: # P P
                end_append = True
                end = jtime 
                j += 1
            elif iresult and not jresult: # P N
                end = jtime
                period.append((start, end))
                i = j
                j += 1
            elif not iresult and jresult: # N P
                start = max(itime, jtime - INCUB)
                end_append = True
                i += 1
                j += 1
            else: # N N
                i += 1
                j += 1

        if end_append:
            period.append((start, s))

        return period

        


        '''
        lines = self.lines[id0]
        size = len(lines)
        periods = []

        if size == 0: return []
        if size == 1:
            fdate, fstatus = lines[0]
            if fstatus and fdate - INCUB < date:
                return [(fdate - INCUB, date)]
            else:
                return []
        
        for i in range(size - 1):
            fdate, fstatus = lines[i]
            sdate, sstatus = lines[i + 1]

            if date < fdate: return periods

            if not fstatus and sstatus: # N P
                periods.append((max(fdate, sdate - INCUB), sdate))
            elif fstatus and not sstatus: # P N
                periods.append((fdate - INCUB, sdate)) # easy

        
        return periods
        '''
        
    def earliest(self, date:datetime, INCUB=timedelta(days=14)):
        def merge(times):
            saved = list(times[0])
            for st, en in sorted([sorted(t) for t in times]):
                if st <= saved[1]:
                    saved[1] = max(saved[1], en)
                else:
                    yield tuple(saved)
                    saved[0] = st
                    saved[1] = en
            yield tuple(saved)
        L = [self.periods(userid, date, INCUB) for userid, l in self.lines.items()]

        result = list(merge([j for sub in L for j in sub]))
        j = len(result) - 1
        while j >= 0:
            s, e = result[j]
            if e < date: j -= 1; continue
            return s
        
        return date

class Node():
    def __init__(self, id0, name, date):
        self.id0 = id0
        self.name = name 
        self.date = date

        self.parent = None
        self.level = 0
        self.children = []
    
    def attach(self, parent):
        self.parent = parent
        self.parent.children.append(self)
        self.level = parent.level + 1
    
    def detach(self):
        if self.parent is None: return
        self.parent.children.remove(self)
        self.parent = None
        self.level = 0
    
