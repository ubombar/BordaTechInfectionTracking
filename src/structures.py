import collections
import datetime
import math
from datetime import datetime, timedelta
import json

class Graph(): # undirected graph
    def __init__(self, default_date=datetime.now()):
        self.graph = collections.defaultdict(lambda: set()) # {name:{names...}}
        self.edges = collections.defaultdict(lambda: None) # {(name1, name2):edge}
    
    @staticmethod
    def sort(name1, name2):
        return tuple(sorted((name1, name2)))
    
    def get_child(self, name):
        self.add_vertex(name)
        return self.graph[name]
    
    def get_edge(self, name1, name2):
        self.add_vertex(name1)
        self.add_vertex(name2)

        return self.edges[Graph.sort(name1, name2)]
    
    def set_edge(self, name1, name2, edge):
        self.add_vertex(name1)
        self.add_vertex(name2)

        # if len(self.edges[(Graph.sort(name1, name2))]) == 0:
        self.graph[name1].add(name2)
        self.graph[name2].add(name1)

        self.edges[Graph.sort(name1, name2)] = edge

    def add_vertex(self, name):
        if name not in self.graph:
            self.graph[name] = set()

    def to(self):
        return {
            "graph": [{"userid": userid, "adjacent": list(elements)} for userid, elements in self.graph.items()],
            "edges": [{"id1": id1, "id2": id2, "edge": {"date": str(edge[0]), "rssi": edge[1]}} for (id1, id2), edge in self.edges.items()]
        }

class TreeNode():
    DICT = collections.defaultdict(lambda: 0)

    def __init__(self, userid, date, level=0, parent=None):
        self.parent = None

        if parent is not None:
            self.attach(parent)

        self.userid = userid
        self.date = date
        self.__level = level
        self.__children = list()

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
        old_level = TreeNode.DICT[self.userid]

        if level != 0:
            if old_level == 0:
                TreeNode.DICT[self.userid] = level
            else:
                TreeNode.DICT[self.userid] = min(level, old_level)

        self.__level = level

    @property
    def children(self):
        return self.__children
    
    def to(self):
        return {
            "parentid": None if self.parent is None else self.parent.userid,
            "userid": self.userid,
            "level": self.level,
            "date": str(self.date),
            "children": [child.to() for child in self.__children]
        }

class TimeLine():
    def __init__(self):
        self.timeline = collections.defaultdict(lambda: [(datetime(2019, 1, 1), "U")])
        self.timeline["root"] = [(datetime(2019, 1, 1), "I")]

    def register(self, userid:str, date:datetime, covid:bool, INC_PERIOD):
        timeline:list = self.timeline[userid]

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
        
    def lookup(self, userid:str, date:datetime):
        timeline = self.timeline[userid]
        first_date, first_status = timeline[-1]

        if date < first_date: return "H"

        for i, (tl_date, tl_status) in enumerate(timeline):
            if i == 0: continue

            if date < tl_date: return first_status

            first_date, first_status = tl_date, tl_status
        
        return self.timeline[userid][-1][1] # last elements status
                
    def to(self):
        return {userid:[{    "Date": str(date), 
                            "Status": status 
                        } for date, status in timeline] for userid, timeline in self.timeline.items()}