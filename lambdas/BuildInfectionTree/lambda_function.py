import json
import boto3
from util import send
from datetime import datetime, timedelta
import structures
from boto3.dynamodb.conditions import Key, Attr
import collections
import ast

'''
not so easter but egg: https://cdn.discordapp.com/attachments/737267481906905151/748813138954158171/unknown.png
'''

INSERT_THE_JOKE_HERE = "Bat Soup"
ROOT_ID = "root"

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
INC_PERIOD = timedelta(days=14)
TIMELINE_TABLE = "academy2020-CovidTimeline"
TIMELINE_TABLE2 = "academy2020-CovidTimeline2"
INTERACTIONS_TABLE = "academy2020-InteractionTableLittle" # "InteractionTableDuplicatesRemoved"

REQUIRED_PARAMS = {"start_date"}
OPTIONAL_PARAMS = {
    "timeline": "real"
}

def lambda_handler(event, context):
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

    timeline = generate_timeline(database, http_params["start_date"], http_params['timeline'])
    useridmap = genrate_useridmap(rds_invoke)

    # get earliest date for filtering from  interaction table
    earliest_date = timeline.earliest(datetime.strptime(http_params['start_date'], TIME_FORMAT))
    http_params['earliest'] = earliest_date.strftime(TIME_FORMAT)
    timeline.register(ROOT_ID, datetime(2019, 1, 1), True) # mark patient zero as ill

    
    graph = generate_graph(database, http_params['earliest'], http_params['start_date'], timeline)

    tree = generate_tree(graph, http_params['earliest'], http_params['start_date'], useridmap, timeline)

    return send(200, json.dumps({
        "timeline": structures.timelinetodict(timeline, http_params['earliest'], http_params['start_date'], TIME_FORMAT, useridmap),
        "level": structures.Node.DICT,
        "tree": structures.nodetodict(tree)
    }))

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
        # This way we also remove the duplicates
    
    for (id1, id2), edge_list in temp_graph.edges.items():
        if len(edge_list) == 0: continue

        list_id1 = timeline.thefunction(id1, earliest, date)
        list_id2 = timeline.thefunction(id2, earliest, date)

        list_id1 = [(x[0], x[1]) for x in list_id1]
        list_id2 = [(x[0], x[1]) for x in list_id2]

        earliest_contact = {} # {(date1, date2): earliest date}

        for date1, date2 in structures.PeriodIterator(list_id1, list_id2):

            for edge_date, edge_rssi in edge_list:
                if edge_date < date1: 
                    continue

                if (date1, date2) in earliest_contact:
                    earliest_contact[(date1, date2)] = min(earliest_contact[(date1, date2)], (edge_date, edge_rssi))
                else:
                    earliest_contact[(date1, date2)] = (edge_date, edge_rssi)
        
        for _, (earliest_date, edge_rssi) in earliest_contact.items():
            graph.connect(id1, id2, (earliest_date, edge_rssi))


    for userid in timeline.lines.keys():
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

    root = structures.Node(ROOT_ID, INSERT_THE_JOKE_HERE, datetime(2019, 1, 1), True)
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
                
                node = structures.Node(node_id, useridmap[str(node_id)], edge_date, infectee_status=="I")
                node.attach(current_node)

                queue.append((node, last_date))
    return root




#### DEVELOPER DEBUG ZONE ####
development_mode = True

if __name__ == "__main__" and development_mode:
    event = {
        "queryStringParameters": {
            "start_date": "2020-09-01 14:36:00",
            "timeline": 'real' # optional
        }
    }
    response = lambda_handler(event, None)

    print(response["body"])