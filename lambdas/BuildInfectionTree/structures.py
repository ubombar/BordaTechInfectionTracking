import collections
import datetime
import math
from datetime import datetime, timedelta
import json
import bisect

class Graph():
    def __init__(self):
        self.__adjacent = collections.defaultdict(set) # {id: {ids...}}
        self.__edges = collections.defaultdict(list) # {(id1, id2):[edge]}

    @property
    def edges(self):
        return self.__edges

    def adj_nodes(self, id0):
        return self.__adjacent[id0]
    
    def adj_edges(self, id1, id2):
        if id1 > id2: id1, id2 = id2, id1 # (1, 2)

        return self.__edges[(id1, id2)]

    def connect(self, id1, id2, edge):
        # TODO: remove dupes? or create lambda
        self.__adjacent[id1].add(id2)
        self.__adjacent[id2].add(id1)

        if id1 > id2: id1, id2 = id2, id1 # (1, 2)

        self.__edges[(id1, id2)].append(edge)

class Timeline():
    def __init__(self):
        self.lines= collections.defaultdict(lambda: [(datetime(2019, 1, 1), False)])
        #self.lines = collections.defaultdict(list) # {id:[(date, result)]}
        
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
                return [] # if s < time else [(time, s)]# N

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

        if len(L) == 0: return date 

        result = list(merge([j for sub in L for j in sub]))
        j = len(result) - 1
        while j >= 0:
            s, e = result[j]
            if e < date: j -= 1; continue
            return s
        
        return date

    def thefunction(self, id0, start, end, INCUBATION=timedelta(days=14)):
        ''' by Erdem :) '''
        tuple_list = self.lines[id0]

        if len(tuple_list) == 0: return [(start, end, "U")]

        periods = [(start, start, "U")]
        counter = 0
        for day, covid in tuple_list:
            if start > day:
                continue
            if end <= day:
                break
            if covid:
                if periods[-1][1] >= (day - INCUBATION):
                    
                    status = (start, day, "I")
                    try:
                        periods[counter] = status
                    except:
                        periods.append(status)
                    counter += 1
                    #periods.append(status)
                else:
                    status = (start, day - INCUBATION, periods[-1][2])
                    try:
                        periods[counter] = status
                    except:
                        periods.append(status)
                    counter += 1
                    #periods.append(status)
                    status = (day - INCUBATION, day, "I")
                    try:
                        periods[counter] = status
                    except:
                        periods.append(status)
                    counter += 1
                    #periods.append(status)
                    
            else:
                if counter != 0:
                    if(tuple_list[counter - 1][1]):
                        status = (start, day, "I")
                    else:
                        status = (start, day, "H")
                else:
                    status = (start, day, "H")
                try:
                        periods[counter] = status
                except:
                        periods.append(status)
                counter += 1
                #periods.append(status)
            
            start = day
        try:
            if tuple_list[counter - 1][1]:
                status = (start, end, "I")
            else:
                status = (start, end, "U")
        except:
            if tuple_list[counter - 2][1]:
                status = (start, end, "I")
            else:
                status = (start, end, "U")
        periods.append(status)

        periods2 = []

        counter = 0
        while counter < len(periods):
            endControl = False
            while True:
                try:
                    if periods[counter][2] == periods[counter + 1][2]:
                        endControl = True
                        end = periods[counter + 1][1]
                        periods.pop(counter + 1)
                    else:
                        break
                except:
                    break
            if endControl:
                periods2.append((periods[counter][0], end, periods[counter][2]))
            else:
                periods2.append(periods[counter])
            counter += 1

        return periods2

class Node():
    DICT = collections.defaultdict(lambda: float('inf'))

    def __init__(self, id0, name, date, infected=False):
        self.id0 = id0
        self.name = name 
        self.date = date
        self.infected = infected

        self.parent = None
        self.level = 0
        self.children = []
    
    def attach(self, parent):
        self.parent = parent
        self.parent.children.append(self)
        self.level = parent.level + 1
        Node.DICT[self.id0] = min(Node.DICT[self.id0], self.level)
    
    def detach(self):
        if self.parent is None: return
        self.parent.children.remove(self)
        self.parent = None
        self.level = 0
    
def nodetodict(root, debug=False):
    if root is None: return
    if debug:
        return {
            "id": root.id0,
            "name": root.name,
            "date": str(root.date),
            "children": [nodetodict(node, debug) for node in root.children if node is not None]
        }
    
    if root.infected:
        return {
                "name": root.name,
                "nodeSvgShape": {"shapeProps": {"fill": "#d9376e","r": 10}},
                "attributes": {
                            "id": root.id0,
                            "date": str(root.date),
                            "level": root.level,
                            "parent": None if root.parent is None else root.parent.id0,
                        },
                "children": [nodetodict(node, debug) for node in root.children if node is not None]
            }
    else:
        return {
                "name": root.name,
                "attributes": {
                            "id": root.id0,
                            "date": str(root.date),
                            "level": root.level,
                            "parent": None if root.parent is None else root.parent.id0,
                        },
                "children": [nodetodict(node, debug) for node in root.children if node is not None]
            }

def timelinetodict(timeline:Timeline, start, end, TIME_FORMAT, useridmap):
    start = datetime.strptime(start, TIME_FORMAT)
    end = datetime.strptime(end, TIME_FORMAT)
    
    mapp = {}
    
    for userid, username in useridmap.items():
        dates = [{"Date": str(date), "Status": status} for date, _, status in timeline.thefunction(userid, start, end)]
        mapp[userid] = {"name": username, "dates": dates}
    
    return mapp
    
def merge(times):
    if len(times) == 0: return
    saved = list(times[0])
    for st, en in sorted([sorted(t) for t in times]):
        if st <= saved[1]:
            saved[1] = max(saved[1], en)
        else:
            yield tuple(saved)
            saved[0] = st
            saved[1] = en
    yield tuple(saved)


class PeriodIterator():
    def __init__(self, list1, list2):
        self.thelist = sorted({item for t in list1 + list2 for item in t})
        self.i = 1
        
    def __iter__(self):
        self.i = 1
        return self
    
    def __next__(self):
        if self.i < len(self.thelist):
            self.i += 1
            return self.thelist[self.i - 2], self.thelist[self.i - 1]
        raise StopIteration
