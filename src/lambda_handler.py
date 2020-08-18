import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from structures import Graph, TimeLine, TreeNode

# constrains
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
INC_PERIOD = timedelta(days=14)
ROOT_ID = "root"

DB_TABLE_TIMELINE = "academy2020-CovidTimeline"
DB_TABLE_INTERACTIONS = "InteractionTableDuplicatesRemoved"

def lambda_function(event, context):
    ''' Generate graph, timeline and tree '''
    database = boto3.resource('dynamodb')

    try:
        args = event["queryStringParameters"]

        # arguments
        start_date = datetime.strptime(args["start_date"], TIME_FORMAT)
        end_date = datetime.strptime(args["end_date"], TIME_FORMAT)
        allow_infected_pass = bool(args["allow_infected_pass"])
        depth_search = bool(args["depth_search"])
        gen_minimal = bool(args["gen_minimal"])
    except Exception:
        return json.dumps({
            "status": 400,
            "body": "Arguments are not correctly supplied to this function"
        })
        
    # generation
    graph = generate_graph(database, start_date, end_date)
    timeline = generate_timeline(database, graph, start_date, end_date)
    root = generate_tree(graph, timeline, start_date, end_date, allow_infected_pass, depth_search, gen_minimal)

    return json.dumps({
        "status": 200,
        "body": {
            "tree": root.to(),
            "timeline": timeline.to(),
            "graph": graph.to()
        }
    })

def generate_tree(graph:Graph, timeline:TimeLine, start_date, end_date, allow_infected_pass=False, depth_search=False, gen_minimal=False):
    '''
        graph:
            Connection graph only contains data from the given timespan. Only the oldest 
            interactions are stored in the graph.

        timeline:
            Holds the healty, infected and unknown info.

        start_time, end_time:
            the time span we want to generate the tree in. This span must be same
            as the generate_graph arguments.

        allow_infected_pass:false 
            When creating the tree, track interactions between already infected 
            users. Normally this is only allowed happens between infected people 
            and root.

        depth_search:false
            Apply depth first search on tree creation. Usually tree spreads horizontally
            but this is added for experimental reasons.

        gen_minimal:true
            This reduces the tree size to only connected users.
    '''
    root = TreeNode(ROOT_ID, start_date)
    visited = set()
    queue = [(root, start_date)]
    remove_index = -1 if depth_search else 0

    while len(queue) != 0:
        current_node, last_date = queue.pop(remove_index) # act as a queue

        if current_node.userid in visited: continue
        visited.add(current_node.userid)

        for child_id in graph.graph[current_node.userid]:
            contact_date, _ = graph.get_edge(current_node.userid, child_id)

            if gen_minimal and child_id in visited: continue

            # calculate things based on rssi?

            if contact_date < current_node.date: continue

            infector_status = timeline.lookup(current_node.userid, contact_date)
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
                if current_node.userid == ROOT_ID: pass # except root node
                else:
                    if allow_infected_pass: pass 
                    else: continue

            if contact_date - last_date > INC_PERIOD: continue

            branch_passed = set()

            temp = current_node
            while temp is not None:
                branch_passed.add(temp.userid)
                temp = temp.parent
            
            if child_id in branch_passed: continue

            child_node = TreeNode(child_id, contact_date)
            child_node.attach(current_node)

            queue.append((child_node, last_date))

    # print(visited)
    return root

def generate_timeline(database, graph, start_date, end_date):
    '''
        Generate timeline and also add interactions between currently sick 
        and patient zero.
    '''
    timeline = TimeLine()

    table = database.Table(DB_TABLE_TIMELINE)

    response = table.scan() # get all

    for item in response["Items"]:
        uid = str(item["UserId"])
        date = datetime.strptime(item["Date"], TIME_FORMAT)
        result = bool(item["Covid19"])

        timeline.register(uid, date, result, INC_PERIOD)

        if result and timeline.lookup(uid, start_date) == "I":
            graph.set_edge(uid, ROOT_ID, (start_date, 0))
    
    return timeline

def generate_graph(database, start_date, end_date):
    '''
        Generate graph with the connections insode the given timespan. 
        The oldest date between users are taken.
    '''
    graph = Graph(end_date)

    table = database.Table(DB_TABLE_INTERACTIONS)
    expression = Key('Date').between(
        datetime.strftime(start_date, TIME_FORMAT), 
        datetime.strftime(end_date, TIME_FORMAT))

    response = table.scan(FilterExpression=expression)

    for item in response["Items"]:
        id1 = str(item["ContactID"])
        id2 = str(item["Id"])
        date = datetime.strptime(item["Date"], TIME_FORMAT)
        rssi = int(item["RSSI"])

        old_tuple = graph.get_edge(id1, id2)

        if old_tuple is not None:
            old_date, old_rssi = old_tuple

            date, rssi = min([(old_date, old_rssi), (date, rssi)], key=lambda v: v[0]) 
            # get the oldest interaction

        graph.set_edge(id1, id2, (date, rssi))

    return graph

'''
    # Test

event = {
    "queryStringParameters": {
        "start_date": "2020-08-01 09:00:00", 
        "end_date": "2020-08-05 09:00:00",
        "allow_infected_pass": "false",
        "depth_search": "false",
        "gen_minimal": "false"
        }
    }

response = lambda_function(event, None)

print(response)

'''