from datetime import datetime, timedelta
from new_graph import BordaGraph, TreeNode
import collections

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

INC_PERIOD = timedelta(days=14)

DATABASE_CONTACTS = []
DATABASE_INFO = []

TREE_ROOT = TreeNode('root', 'Patient Zero', datetime(2019, 10, 1), 1)
GRAPH = BordaGraph()

# TRIGGER FUNCTIONS
def trigger_alter_graph(devid1, devid2, earliest, rssi):
    GRAPH.add_edge(devid1, devid2, (earliest, rssi))
    
def trigger_alter_tree(devid1, devid2, earliest, rssi):
    if "root" not in {devid1, devid2}: return

    devid = devid1 if devid2 == "root" else devid2
    newly_infected = TreeNode(devid, None, earliest)
    newly_infected.attach(TREE_ROOT)

    # TREE_ROOT.rm_all()
    # generate_full_tree(newly_infected)
  
    generate_trimmed_tree(newly_infected, earliest)

# ALGO FUNCTIONS
def traverse_dfs(node:TreeNode, visited:set, max_size:int): # experimental only!
    if node is None: return

    if not node.is_leaf():
        for child_node in node.children:
            traverse_dfs(child_node, visited, max_size)
    else:
        pass



def generate_trimmed_tree(node:TreeNode, inf_earliest:datetime):
    '''
        Generate the trimmed tree. Data needs to be filtered. the connection data should start from
        the earliest date that is greater than the earliest active infection?
    '''
    if node is None: return

    visited = set()

    temp = node
    while temp is not None:
        visited.add(temp.devid)
        temp = temp.parent

    devid_map = {}

    for contact_devid in GRAPH.graph[node.devid]:
        edge_list = GRAPH.get_edge(contact_devid, node.devid)

        node.date
        min_date = None

        for earliest, _ in edge_list:
            if min_date is None and earliest > node.date: 
                min_date = earliest
            elif min_date is not None and earliest > node.date and earliest < min_date: 
                min_date = earliest 
        
        devid_map[contact_devid] = min_date
                
    for contact_devid, min_date in devid_map.items():
        if contact_devid in visited: continue
        if min_date is None: continue

        if min_date < node.date: continue

        child = TreeNode(contact_devid, None, earliest)
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