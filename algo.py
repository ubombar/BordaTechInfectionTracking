from graph import BordaGraph, TreeNode
import collections
from datetime import datetime

# CONSTANTS and CONSTRAINTS
DTFORMAT = '%Y-%m-%d %H:%M:%S'
PATIENT_ZERO_DATE = datetime.strptime("2019-07-01 10:00:00", DTFORMAT)
PATIENT_ZERO = TreeNode("root", "Patient Zero", PATIENT_ZERO_DATE, 0, None)

def algo_previous(node:TreeNode):
    ''' 
        Get all prevoius devids as a set
    '''
    array = set()
    trav = node 
    while trav is not None: # exclude patient zero
        array.add(trav.devid)
        trav = trav.parent
    return array - {None} # WELLDONE!

def stack_traverse(node : TreeNode, cgraph : BordaGraph, dev_name_dict, level=1):
    if node is None: return

    visited = algo_previous(node)

    # CREATE CHILDS USING THE GRAPH
    for contact_devid in cgraph.graph[node.devid]:
        if contact_devid in visited: continue
    
        date_list = cgraph.get_edge(contact_devid, node.devid)

        for date in date_list:
            if date < node.date: continue

            temp = TreeNode(contact_devid, dev_name_dict[contact_devid], date, level)
            temp.attach(node)

    for child_node in node.children:
        stack_traverse(child_node, cgraph, dev_name_dict, level + 1)

def traverse_tree_and_delete(node, r_devid):
    if node is None: return 

    if node.devid == r_devid:
        parent_tmp = node.parent
        node.detach()

        for child_node in node.children:
            parent_tmp.attach(child_node)

        node = parent_tmp

    for child_node in node.children:
        traverse_tree_and_delete(child_node, r_devid)

def process_record(cgraph, root, r_date, r_covid, r_devid, dev_name_dict):
    # CASE 1: ONLY ROOT EXISTS & COVID POSITIVE
    if root.is_leaf() and r_covid:
        treenode = TreeNode(r_devid, dev_name_dict[r_devid], r_date)
        treenode.attach(root)

        stack_traverse(treenode, cgraph, dev_name_dict)

    # CASE 2: TREE EXISTS & COVID POSITIVE

    # CASE 3: TREE EXISTS & COVID NEGATIVE
    if not root.is_leaf() and not r_covid:
        traverse_tree_and_delete(root, r_devid)





def iterate_for_data(cgraph, root, record, history, i, info_data, dev_name_dict):
    '''
        cgraph      : connection graph
        root        : root tree node
        record      : (date, covid, devid)
        history     : {devid:[date...]}
        i           : iteration
        info_data   : []
    '''
    date, covid, devid = record
    
    process_record(cgraph, root, date, covid, devid, dev_name_dict)
    
# DATE MERGING