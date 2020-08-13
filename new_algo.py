from datetime import datetime, timedelta
from new_graph import BordaGraph, TreeNode

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

INC_PERIOD = timedelta(days=14)

DATABASE_CONTACTS = []
DATABASE_INFO = []

TREE_ROOT = TreeNode('root', 'Patient Zero', datetime(2019, 10, 1))
GRAPH = BordaGraph()

# TRIGGER FUNCTIONS
def trigger_alter_tree(devid1, devid2, start, end, rssi):
    if "root" not in {devid1, devid2}: return

    generate_tree(TREE_ROOT)

def trigger_alter_graph(devid1, devid2, start, end, rssi):
    GRAPH.add_edge(devid1, devid2, (start, end, rssi))

# ALGO FUNCTIONS
def generate_tree(node:TreeNode):
    if node is None: return

    visited = set()

    temp = node
    while temp is not None:
        visited.add(temp.devid)
        temp = temp.parent
    
    for contact_devid in GRAPH.graph[node.devid]:
        if contact_devid in visited: continue

        date_list = GRAPH.get_edge(contact_devid, node.devid)

        for _, end, _ in date_list:
            if end < node.date: continue

            child = TreeNode(contact_devid, None, end)
            child.attach(node)
    
    for child in node.children:
        generate_tree(child)