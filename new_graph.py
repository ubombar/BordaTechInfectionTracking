import collections
import datetime
import math
from datetime import datetime
from new_const import *

class BordaGraph(): # undirected graph
    def __init__(self):
        self.graph = collections.defaultdict(lambda: None) # {name:[names...]}
        self.edges = collections.defaultdict(lambda: []) # {(name1, name2):[edges...]}
    
    @staticmethod
    def sort(name1, name2):
        return tuple(sorted((name1, name2)))
    
    def get_child(self, name):
        self.add_vertex(name)
        return self.graph[name]
    
    def get_edge(self, name1, name2):
        self.add_vertex(name1)
        self.add_vertex(name2)

        return self.edges[(BordaGraph.sort(name1, name2))]
    
    def add_edge(self, name1, name2, edge):
        self.add_vertex(name1)
        self.add_vertex(name2)

        if len(self.edges[(BordaGraph.sort(name1, name2))]) == 0:
            self.graph[name1].append(name2)
            self.graph[name2].append(name1)

        self.edges[(BordaGraph.sort(name1, name2))] += [edge]

    def add_vertex(self, name):
        if name not in self.graph:
            self.graph[name] = []

class TreeNode():
    DICT = collections.defaultdict(lambda: 0)

    def __init__(self, devid, name, date, level=0, parent=None):
        self.parent = None

        if parent is not None:
            self.attach(parent)

        self.devid = devid
        self.date = date
        self.name = name
        self.__level = level
        self.__children = []

    def rm_all(self):
        for child_node in self.__children:
            child_node.detach()
        self.__children.clear()
    
    def add_child(self, node):
        self.__children.append(node)
        node.parent = self

    def rm_child(self, node):
        node.parent = None
        self.__children.remove(node)

    def detach(self):
        ''' Detaches itself from parent node '''
        self.parent.children.remove(self)
        self.parent = None
        self.level = 0

    def attach(self, parent):
        ''' Attaches itself to the parent node '''
        self.parent = parent
        self.parent.add_child(self)
        self.level = self.parent.level + 1

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.parent is None
    
    @property
    def level(self):
        return self.__level
    
    @level.setter
    def level(self, level):
        old_level = TreeNode.DICT[self.devid]

        if level != 0:
            if old_level == 0:
                TreeNode.DICT[self.devid] = level
            else:
                TreeNode.DICT[self.devid] = min(level, old_level)

        self.__level = level

    @property
    def children(self):
        return self.__children
    
    def to(self):
        return {
            # "pdevid": None if self.parent is None else self.parent.devid,
            "devid": self.devid,
            "level": self.level,
            # "name": self.name,
            "date": str(self.date),
            "children": [child.to() for child in self.__children]
        }

class TimePeriod():
    # I: Infected, H: Healthy, U: Unknown
    def __init__(self):
        # {devid:[(date, status)]}
        self.periods = collections.defaultdict(lambda: [(datetime(2019, 1, 1), "U")])

    def add_record(self, devid, date, covid):
        i = len(self.periods[devid]) - 1

        l_date, l_status = self.periods[devid][i]

        if covid:
            if l_status == "H":
                print("If you see this there is a problem...")
            elif l_status == "U":
                early_date = date - INC_PERIOD

                if l_date < early_date:
                    self.periods[devid][i] = (l_date, "H")
                    self.periods[devid].append((early_date, "I"))
                else:
                    self.periods[devid][i] = (l_date, "I")

            elif l_status == "I":
                pass 
        else:
            if l_status == "H":
                pass
            elif l_status == "U":
                self.periods[devid][i] = (l_date, "H")
                self.periods[devid].append((date, "U"))
            elif l_status == "I":
                # self.periods[devid][i] = (l_date, "I")
                self.periods[devid].append((date, "U"))

    def lookup(self, devid, date):
        return # I, H, U

    def to_str(self, devid):
        string = ""
        for date, status in self.periods[devid]:
            s = datetime.strftime(date, '%Y-%m-%d')
            string += f"'{s}:{status}'  "
        return string

dat = TimePeriod()

dat.add_record("dev01", datetime(2020, 8, 1), False)
dat.add_record("dev01", datetime(2020, 8, 2), False)
dat.add_record("dev01", datetime(2020, 8, 20), True)

print(dat.to_str("dev01"))

