import json
import boto3
from util import send
from datetime import datetime, timedelta
import structures
from boto3.dynamodb.conditions import Key, Attr
import collections
import ast

INSERT_THE_JOKE_HERE = "Bat Soup"
ROOT_ID = "root"

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
INC_PERIOD = timedelta(days=14)
TIMELINE_TABLE = "academy2020-CovidTimeline"
TIMELINE_TABLE2 = "academy2020-CovidTimeline2"
INTERACTIONS_TABLE = "InteractionTableDuplicatesRemoved"

REQUIRED_PARAMS = {"date"}
OPTIONAL_PARAMS = {
    "timeline": "real"
}

def lambda_function(event, context):
    try:
        http_params = event["queryStringParameters"]

        if len(REQUIRED_PARAMS - set(http_params)) != 0: 
            raise Exception()
    except: return send(400, "Bad Request")

    for param in http_params:
        if http_params[param].lower() in {"true", "false"}:
            http_params[param] = http_params[param] == "true"
    
    for opt_param in OPTIONAL_PARAMS:
        if opt_param in http_params: continue
        http_params[opt_param] = OPTIONAL_PARAMS[opt_param]

    # Adjusting the arguments convert boolean strings to bools. Also 
    # Add the optional arguments.

    database = boto3.resource("dynamodb")
    rds_invoke = boto3.client('lambda')

    timeline = generate_timeline(database, http_params["date"], http_params['timeline'])
    useridmap = genrate_useridmap(rds_invoke)

    # get earliest date for filtering from  interaction table
    earliest_date = timeline.earliest(datetime.strptime(http_params['date'], TIME_FORMAT))
    http_params['earliest'] = earliest_date.strftime(TIME_FORMAT)
    timeline.register(ROOT_ID, datetime(2019, 1, 1), True) # mark patient zero as ill

    
    graph = generate_graph(database, http_params['earliest'], http_params['date'], timeline)

    tree = generate_tree(graph, http_params['earliest'], http_params['date'], useridmap, timeline)

    return send(200, json.dumps(structures.nodetodict(tree)))

### GENERATE TIMELINE ###
def generate_timeline(database, date:str, timeline_name:str):
    timeline_table = database.Table(TIMELINE_TABLE if timeline_name == 'real' else TIMELINE_TABLE2)
    response = timeline_table.scan(
        FilterExpression=Attr('SimulationId').eq(timeline_name) & Attr('Date').lt(date)) # FILTER OUT

    timeline = structures.Timeline()
    
    for item in response["Items"]:
        id0 = str(item["UserId"])
        covid = str(item["Covid19"]).lower() == 'true' # Covert to bool
        regdate = datetime.strptime(str(item["Date"]), TIME_FORMAT)

        timeline.register(id0, regdate, covid)
    
    return timeline

def generate_graph(database, earliest:datetime, date:datetime, timeline):
    graph = structures.Graph()
    temp_graph = structures.Graph()
    interaction_table = database.Table(INTERACTIONS_TABLE)
    response = interaction_table.scan(
        FilterExpression=Attr('Date').between(earliest, date)) # FILTER OUT

    earliest = datetime.strptime(earliest, TIME_FORMAT)
    date = datetime.strptime(date, TIME_FORMAT)

    for item in response["Items"]:
        cdate = datetime.strptime(item["Date"], TIME_FORMAT)
        id1 = str(item["ContactID"])
        id2 = str(item["Id"])
        rssi = int(item["RSSI"])
        temp_graph.connect(id1, id2, (cdate, rssi))
    
    for (id1, id2), edge_list in temp_graph.edges.items():
        if len(edge_list) == 0: continue

        list_id1 = timeline.periods(id1, date)
        list_id2 = timeline.periods(id2, date)

        if len(list_id1) == 0: list_id1 = [(earliest, date)]
        else: list_id1.insert(0, (earliest, list_id1[0][1]))

        if len(list_id2) == 0: list_id2 = [(earliest, date)]
        else: list_id2.insert(0, (earliest, list_id2[0][1]))

        if list_id1[-1][1] != date: list_id1.append((list_id1[-1][1], date))
        if list_id2[-1][1] != date: list_id2.append((list_id2[-1][1], date))

        if len({'56', '34'} - {id1, id2}) == 0:
            print(timeline.status('34', datetime(2020, 8, 26)))
            for date, _ in sorted(edge_list):
                print(f"'{str(date)}'")

            print("34", timeline.lines['34'])
            print("56", timeline.lines['56'])

        earliest_contact = {} # {(date1, date2): earliest date}

        for date1, date2 in structures.PeriodIterator(list_id1, list_id2):
            if len({'56', '34'} - {id1, id2}) == 0:
                print(date1, date2)

            for edge_date, edge_rssi in edge_list:
                if (date1, date2) in earliest_contact:
                    earliest_contact[(date1, date2)] = min(earliest_contact[(date1, date2)], (edge_date, edge_rssi))
                else:
                    earliest_contact[(date1, date2)] = (edge_date, edge_rssi)
        
        for _, (earliest_date, edge_rssi) in earliest_contact.items():
            graph.connect(id1, id2, (earliest_date, edge_rssi))


    for userid in timeline.lines.keys():
        # print(userid, timeline.periods(userid, date))
        for s, _ in timeline.periods(userid, date):
            
            graph.connect(ROOT_ID, userid, (s, 0))

    return graph

def genrate_useridmap(rds_invoke):
    useridmap = collections.defaultdict(lambda: "unknown name")
    dbpayload = {"process":"get_raw", "sql":f"SELECT ID, Name, Surname FROM Users"}
    request = rds_invoke.invoke(FunctionName="academy2020-RDSConnection", InvocationType="RequestResponse", Payload=json.dumps(dbpayload))
    response = ast.literal_eval(request['Payload'].read().decode())
    
    for row in response:
        userid, name, surname = tuple(row)
        useridmap[str(userid)] = f"{name} {surname}"
    
    return useridmap

def generate_tree(graph, earliest, date, useridmap, timeline):
    earliest = datetime.strptime(earliest, TIME_FORMAT)
    date = datetime.strptime(date, TIME_FORMAT)

    root = structures.Node(ROOT_ID, INSERT_THE_JOKE_HERE, datetime(2019, 1, 1))
    visited = set()
    queue = [(root, earliest)]

    while len(queue) != 0:
        current_node, last_date = queue.pop(0) # act as a queue

        if current_node.id0 in visited: continue
        visited.add(current_node.id0)
        

        for node_id in graph.adj_nodes(current_node.id0):
            for edge_date, _ in graph.adj_edges(current_node.id0, node_id):
                if edge_date < current_node.date: continue
                if node_id in visited: continue

                infector_status = timeline.status(current_node.id0, edge_date)
                infectee_status = timeline.status(node_id, edge_date)

                if infector_status == "H" and infectee_status == "H": continue
                if infector_status == "H" and infectee_status == "U": continue
                if infector_status == "H" and infectee_status == "I": continue

                if infector_status == "U" and infectee_status == "H": continue
                if infector_status == "U" and infectee_status == "U": pass
                if infector_status == "U" and infectee_status == "I": continue

                if infector_status == "I" and infectee_status == "H": continue
                if infector_status == "I" and infectee_status == "U": last_date = edge_date; pass
                if infector_status == "I" and infectee_status == "I": 
                    if current_node.id0 == ROOT_ID: last_date = edge_date; pass
                    else: continue

                
                
                if edge_date - last_date > INC_PERIOD: continue

                
                branch_passed = set()

                temp = current_node
                while temp is not None:
                    branch_passed.add(temp.id0)
                    temp = temp.parent
                
                if node_id in branch_passed: continue

                duplicate = False
                for other_node in current_node.children:
                    if other_node.id0 == node_id and other_node.date == edge_date:
                        duplicate = True
                        break
                
                if duplicate: continue
                
                node = structures.Node(node_id, useridmap[str(node_id)], edge_date)
                node.attach(current_node)

                queue.append((node, last_date))
    return root




#### DEVELOPER DEBUG ZONE ####
development_mode = True

if __name__ == "__main__" and development_mode:
    event = {
        "queryStringParameters": {
            "date": "2020-08-27 14:36:00",
            "timeline": 'real'
        }
    }
    response = lambda_function(event, None)

    print(response["body"])