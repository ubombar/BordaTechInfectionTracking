import bisect
import collections

class Mapper():
    def __init__(self):
        self.d_map = collections.defaultdict(list) # {(id1, id2): [date1, date2 ...]}
    
    def append(self, id1, id2, date, INTERVAL):
        id1, id2 = tuple(sorted((id1, id2)))

        if self.has(id1, id2, date, INTERVAL):
            return False
        
        bisect.insort(self.d_map[(id1, id2)], date - INTERVAL)
        return True

    def custom_search(self, d_list, date, INTERVAL): # alright works well
        l, h = 0, len(d_list) - 1

        while l <= h:
            m = (l + h) // 2
            m_date = d_list[m]

            if  m_date <= date <= m_date + 2 * INTERVAL:
                return m_date
            elif m_date > date:
                h = m - 1
            else:
                l = m + 1
        
        return None

    def has(self, id1, id2, date, INTERVAL):
        id1, id2 = tuple(sorted((id1, id2)))

        n_date = self.custom_search(self.d_map[(id1, id2)], date, INTERVAL)
        return n_date is not None


'''
class Mapper():
    def __init__(self):
        self.d_list = list() # [date1, date2, date3 ...]
        self.d_map = collections.defaultdict(set) # {date: [(id1, id2) ...]}
    
    def append(self, id1, id2, date, INTERVAL):
        if self.has(id1, id2, date, INTERVAL):
            return
        
        id1, id2 = tuple(sorted((id1, id2)))
        n_date = date - INTERVAL
        bisect.insort(self.d_list, n_date)
        self.d_map[n_date].add((id1, id2))

    def custom_search(self, date, INTERVAL): # hmmm suspicious
        l, h = 0, len(self.d_list) - 1

        while l <= h:
            m = (l + h) // 2
            m_date = self.d_list[m]

            if  m_date <= date <= m_date + 2 * INTERVAL:
                return m_date
            elif m_date > date:
                h = m - 1
            else:
                l = m + 1
        
        return None

    def has(self, id1, id2, date, INTERVAL):
        n_date = self.custom_search(date, INTERVAL)
        if n_date is None: return False

        id1, id2 = tuple(sorted((id1, id2)))

        return (id1, id2) in self.d_map[n_date]
'''
test = Mapper()
INTERVAL = 2
test.append(10, 34, 10, INTERVAL)
test.append(34, 10, 12, INTERVAL)

for i in range(7, 15):
    print(i, test.has(10, 34, i, INTERVAL))