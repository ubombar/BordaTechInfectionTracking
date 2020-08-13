import collections
import datetime
import math

'''
    author Bombique, all datatypes are for general use!
'''

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
    def __init__(self, devid, name, date, parent=None):
        self.parent = parent
        self.devid = devid
        self.date = date
        self.name = name
        self.__children = []
    
    def add_child(self, node):
        self.__children.append(node)
        node.parent = self

    def remove_child(self, node):
        node.parent = None
        self.__children.remove(node)

    def detach(self):
        ''' Detaches itself from parent node '''
        self.parent.children.remove(self)
        self.parent = None

    def attach(self, parent):
        ''' Attaches itself to the parent node '''
        self.parent = parent
        self.parent.add_child(self)

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.parent is None

    @property
    def children(self):
        return self.__children
    
    def to(self):
        return {
            # "pdevid": None if self.parent is None else self.parent.devid,
            "devid": self.devid,
            # "level": self.level,
            # "name": self.name,
            # "date": str(self.date),
            "children": [child.to() for child in self.__children]
        }