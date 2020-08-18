import collections
import datetime
import math
from datetime import datetime
from new_const import *
import json


class BordaGraph(): # undirected graph
    def __init__(self):
        self.graph = collections.defaultdict(lambda: []) # {name:[names...]}
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

class TimeLine():
    def __init__(self):
        self.timeline = collections.defaultdict(lambda: [(datetime(2019, 1, 1), "U")])
        self.timeline["root"] = [(datetime(2019, 1, 1), "I")]

    def register(self, devid:str, date:datetime, covid:bool):
        timeline:list = self.timeline[devid]

        prev_date, prev_status = timeline[-1]

        if prev_date > date:
            raise Exception("Given date cannot be lowev than the latest record!")

        size = len(timeline)

        if covid: # DONT CHANGE THIS IT IS COMPRESSED
            if prev_status == "U":
                early_date = date - INC_PERIOD
                if early_date < prev_date:
                    timeline[-1] = (prev_date, "I")
                else:
                    if size > 1 and timeline[-3][1] == "H":
                        timeline.append((early_date, "I"))
                        timeline.pop(-2)
                    else:
                        timeline[-1] = (prev_date, "H")
                        timeline.append((early_date, "I"))                    
        else:
            if prev_status == "U":
                timeline[-1] = (prev_date, "H")
                timeline.append((date, "U"))
                if size > 1 and timeline[-3][1] == "H":
                    timeline.pop(-2)
            elif prev_status == "I":
                timeline.append((date, "U"))
        
    def lookup(self, devid:str, date:datetime):
        timeline = self.timeline[devid]
        first_date, first_status = timeline[-1]

        if date < first_date: return "H"

        for i, (tl_date, tl_status) in enumerate(timeline):
            if i == 0: continue

            if date < tl_date: return first_status

            first_date, first_status = tl_date, tl_status
        
        return self.timeline[devid][-1][1] # last elements status
                
    def to(self):
        return {devid:[{    "Date": datetime.strftime(date, TIME_FORMAT), 
                            "Status": status 
                        } for date, status in timeline] for devid, timeline in self.timeline.items()}
