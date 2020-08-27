import json
import structures
from datetime import datetime

def send(code:int, body:str):
    try:
        body = json.dumps(body) if not isinstance(body, str) else body
    except:
        body = str(body)
    return {
        "headers": {
            "Access-Control-Allow-Headers": 'Content-Type',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "statusCode": int(code),
        "body": body
    }

'''
def find_earliest(items, first_id, second_id, min_date, max_date, TIME_FORMAT):
    response = None, None
    for item in items:
        cdate = datetime.strptime(item["Date"], TIME_FORMAT)
        id1 = str(item["ContactID"])
        id2 = str(item["Id"])
        rssi = int(item["RSSI"])

        if first_id not in {id1, id2} or second_id not in {id1, id2}: continue
        
        if not (min_date < cdate < max_date): continue

        response = min(response, (cdate, rssi), key=lambda v: v[0])

    return response
'''

'''
for userid in timeline.lines.keys():
    for s, e in timeline.periods(userid, date):
        graph.connect(ROOT_ID, userid, (s, 0))
        early_contact = {} # {userid:earliest contact}

        for item in response["Items"]:
            cdate = datetime.strptime(item["Date"], TIME_FORMAT)
            id1 = str(item["ContactID"])
            id2 = str(item["Id"])
            rssi = int(item["RSSI"])

            if not userid in {id1, id2}: continue

            id1, id2 = (id2, id1) if userid == id2 else (id1, id2)

            print("invoked", id1, id2)

            if cdate < s or cdate > e: 
                
                continue

            if userid not in early_contact:
                early_contact[id2] = (cdate, rssi)
            else:
                ldate, _ = early_contact[id2]
                if ldate <= cdate: continue
                early_contact[id2] = (cdate, rssi)
        
        for id2, (cdate, rssi) in early_contact.items():
            graph.connect(userid, id2, (cdate, rssi))
'''


'''

def __generate_tree(graph, earliest, date, useridmap, timeline):
    root = structures.Node(ROOT_ID, datetime(2019, 1, 1), INSERT_THE_JOKE_HERE)
    visited = set()
    queue = [(root, root.date)]

    while len(queue) != 0:
        current_node, last_date = queue.pop(0) # act as a queue
        
        if current_node.id0 in visited: continue
        visited.add(current_node.id0)
         

        for child_id in graph.adj_nodes(current_node.id0):
            for cdate, rssi in graph.adj_edges(current_node.id0, child_id):
                pass # print(cdate)
            
            if gen_minimal:
                if child_id in visited: continue
                visited.add(child_id)
            
            # calculate things based on rssi?

            if contact_date < current_node.date: continue

            infector_status = timeline.lookup(current_node.id0, contact_date)
            infectee_status = timeline.lookup(child_id, contact_date)

            if infector_status == "H" and infectee_status == "H": continue
            if infector_status == "H" and infectee_status == "U": continue
            if infector_status == "H" and infectee_status == "I": continue

            if infector_status == "U" and infectee_status == "H": continue
            if infector_status == "U" and infectee_status == "U": pass
            if infector_status == "U" and infectee_status == "I": continue

            if infector_status == "I" and infectee_status == "H": continue
            if infector_status == "I" and infectee_status == "U": last_date = contact_date
            if infector_status == "I" and infectee_status == "I": 
                last_date = contact_date
                if current_node.id0 == ROOT_ID: pass # except root node
                else: continue

            if contact_date - last_date > INC_PERIOD: continue
        
            

            branch_passed = set()

            temp = current_node
            while temp is not None:
                branch_passed.add(temp.id0)
                temp = temp.parent
            
            if child_id in branch_passed: continue
            
            # name = useridmap[str(child_id)]
            child_node = structures.Node(child_id, contact_date, None)
            child_node.attach(current_node)

            queue.append((child_node, last_date))

    # print(visited)
    return root
'''