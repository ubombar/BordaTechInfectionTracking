from datetime import datetime, timedelta
from new_graph import BordaGraph, TreeNode, TimeLine
import collections
from new_const import *

DATABASE_CONTACTS = []
DATABASE_INFO = []

TREE_ROOT = TreeNode('root', 'Patient Zero', datetime(2019, 10, 1), 0)
GRAPH = BordaGraph()
TIMELINE = TimeLine()

# TRIGGER FUNCTIONS
def trigger_alter_graph(devid1, devid2, earliest, rssi):
    GRAPH.add_edge(devid1, devid2, (earliest, rssi))

def trigger_alter_timeline(devid, report_date, covid_result):
    TIMELINE.register(devid, report_date, covid_result)
    
def trigger_alter_tree(devid1, devid2, date, rssi):
    '''
        This will only be invoked when a new tree creation is requested!
    '''
    # if "root" not in {devid1, devid2}: return

    # devid = ({devid1, devid2} - {"root"}).pop() # dont judge me

    # newly_infected = TreeNode(devid, None, date)
    # newly_infected.attach(TREE_ROOT)

    TREE_ROOT.rm_all()

    # generate_full_tree_with_timeline(TREE_ROOT)
  
    generate_full_tree_with_timeline_14date(TREE_ROOT, date)

    # prune_tree(TREE_ROOT, [child_node.devid for child_node in TREE_ROOT.children] + ["root"])

# ALGO FUNCTIONS
def get_nodes_in_branch(node:TreeNode):
    visited = set()

    temp = node
    while temp is not None:
        visited.add(temp.devid)
        temp = temp.parent
    
    return visited

def generate_full_tree_with_timeline_14date(node:TreeNode, last_date:datetime):
    if node is None: return

    visited = get_nodes_in_branch(node)
    
    for contact_devid in GRAPH.graph[node.devid]:
        if contact_devid in visited: continue

        date_list = GRAPH.get_edge(contact_devid, node.devid)

        for contact_date, _ in date_list:
            if contact_date < node.date: continue

            infector_status = TIMELINE.lookup(node.devid, contact_date)
            infected_status = TIMELINE.lookup(contact_devid, contact_date)

            if infector_status in {"H"} or infected_status in {"H"}: continue
            if contact_date - last_date > INC_PERIOD: continue

            if infector_status == "I": last_date = contact_date
            
            child = TreeNode(contact_devid, None, contact_date)
            child.attach(node)
    
            generate_full_tree_with_timeline_14date(child, last_date)

'''
OLD VERSIONS
def generate_full_tree_with_timeline(node:TreeNode):
    if node is None: return

    visited = set()

    temp = node
    while temp is not None:
        visited.add(temp.devid)
        temp = temp.parent
    
    for contact_devid in GRAPH.graph[node.devid]:
        if contact_devid in visited: continue

        date_list = GRAPH.get_edge(contact_devid, node.devid)

        for contact_date, _ in date_list:
            if contact_date < node.date: continue

            infector_status = TIMELINE.lookup(node.devid, contact_date)
            infected_status = TIMELINE.lookup(contact_devid, contact_date)

            if infector_status in {"U", "I"} and infected_status in {"U", "I"}:
                child = TreeNode(contact_devid, None, contact_date)
                child.attach(node)
    
    for child in node.children:
        generate_full_tree_with_timeline(child)

def generate_trimmed_tree(node:TreeNode, inf_earliest:datetime):
    if node is None: return

    visited = set()
    
    
    temp = node
    while temp is not None:
        visited.add(temp.devid)
        temp = temp.parent

    devid_map = {}


    for contact_devid in GRAPH.graph[node.devid]:
        edge_list = GRAPH.get_edge(contact_devid, node.devid)


        min_date = None

        for earliest, _ in edge_list:
            if earliest > node.date and min_date is None:
                min_date = earliest
            elif earliest > node.date and min_date is not None:
                min_date = min(min_date, earliest)
        
        devid_map[contact_devid] = min_date
                
    for contact_devid, min_date in devid_map.items():
        if contact_devid in visited: continue
        if min_date is None: continue

        if min_date < node.date: continue

        child = TreeNode(contact_devid, None, min_date)
        child.attach(node)
    
    for child in node.children:
        generate_trimmed_tree(child, inf_earliest)

def generate_full_tree(node:TreeNode):
    if node is None: return

    visited = set()

    temp = node
    while temp is not None:
        visited.add(temp.devid)
        temp = temp.parent
    
    for contact_devid in GRAPH.graph[node.devid]:
        if contact_devid in visited: continue

        date_list = GRAPH.get_edge(contact_devid, node.devid)

        for earliest, _ in date_list:
            if earliest < node.date: continue

            child = TreeNode(contact_devid, None, earliest)
            child.attach(node)
    
    for child in node.children:
        generate_full_tree(child)

'''