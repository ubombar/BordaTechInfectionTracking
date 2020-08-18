import json
import boto3
from new_graph import *
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timedelta

DATABASE_TIMELINE = 'academy2020-CovidTimeline'
DATABASE_INTERACTION = 'InteractionTableDuplicatesRemoved' #  # 'academy2020-InteractionTableLittle' # 'academy2020-InteractionTableSmall' # 

TFORMAT = '%Y-%m-%d %H:%M:%S'
INC_PERIOD = timedelta(days=14)

# DATABASE_REGION="eu-central-1"

ROOT = TreeNode('root', 'Patient Zero', datetime(2019, 1, 1), 0)
GRAPH = BordaGraph()
TIMELINE = TimeLine()

def generate_graph(table, start_date, end_date, getall=False):
    start_date_str = datetime.strftime(start_date, TFORMAT)
    end_date_str = datetime.strftime(end_date, TFORMAT)
    
    expression = (Attr('Date').between(start_date_str, end_date_str)) if not getall else None
    
    result = table.scan()

    for item in result["Items"]:
        id1, id2, date, rssi = item["ContactID"], item["Id"], item["Date"], item["RSSI"]

        id1 = str(id1)
        id2 = str(id2)
        date = datetime.strptime(date, TFORMAT)
        rssi = int(rssi)
        
        GRAPH.add_edge(id1, id2, (date, rssi))

def generate_timeline(table, start_date, end_date, getall=False):
    start_date_str = datetime.strftime(start_date, TFORMAT)
    end_date_str = datetime.strftime(end_date, TFORMAT)
    
    # print(f"'{type(start_date)}', '{type(start_date_str)}'")
    
    expression = Attr('Date').between(start_date_str, end_date_str)
    
    result = sorted(table.scan()["Items"], key=lambda k: k["Date"])
    
    for item in result:
        userid = str(item["UserId"])
        report_date = datetime.strptime(item["Date"], TFORMAT)
        covid_result = bool(item["Covid19"])
        
        TIMELINE.register(userid, report_date, covid_result)

        GRAPH.add_edge(userid, "root", (report_date - INC_PERIOD, 0))

count = 0
total_time = timedelta(0)
user_set = set()

def generate_tree(node, last_date, requested_level=10, level=0):
    global count
    global total_time
    count += 1
    if node is None: return
    if requested_level < level: return

    visited = set()

    temp = node
    while temp is not None:
        visited.add(temp.userid)
        temp = temp.parent

    old = datetime.now()
    
    for contact_userid in GRAPH.graph[node.userid]:
        if contact_userid in visited: continue

        date_list = GRAPH.get_edge(contact_userid, node.userid)

        minimum_date = date_list[0][0] if len(date_list) != 0 else None

        # print(len(date_list))

        for date, _ in date_list:
            if date < minimum_date: minimum_date = date

        for contact_date, _ in [(minimum_date, 0)] if minimum_date is not None else []:
            if contact_date < node.date: continue

            infector_status = TIMELINE.lookup(node.userid, contact_date)
            infected_status = TIMELINE.lookup(contact_userid, contact_date)

            if infector_status == "H" and infected_status == "H": continue
            if infector_status == "H" and infected_status == "U": continue
            if infector_status == "H" and infected_status == "I": continue

            if infector_status == "U" and infected_status == "H": continue
            if infector_status == "U" and infected_status == "U": pass
            if infector_status == "U" and infected_status == "I": continue

            if infector_status == "I" and infected_status == "H": continue
            if infector_status == "I" and infected_status == "U": pass
            if infector_status == "I" and infected_status == "I": pass

            if infector_status in {"I"} and infected_status in {"U", "I"}: 
                last_date = contact_date

            if contact_date - last_date > INC_PERIOD: continue
            
            child = TreeNode(contact_userid, None, contact_date)
            child.attach(node)
    
            generate_tree(child, last_date, requested_level, level + 1)
    total_time += (datetime.now() - old)

def lambda_handler(event, condition):
    dynamodb = boto3.resource('dynamodb')
    
    table_interaction = dynamodb.Table(DATABASE_INTERACTION)
    table_timeline = dynamodb.Table(DATABASE_TIMELINE)
    
    html_args = event["queryStringParameters"]
    
    start_date = datetime.strptime(html_args["start_date"], TFORMAT)
    end_date = datetime.strptime(html_args["end_date"], TFORMAT)
    
    generate_graph(table_interaction, start_date, end_date) # DONE!
    
    generate_timeline(table_timeline, start_date, end_date) # DONE!

    old = datetime.now()
    
    generate_tree(ROOT, datetime(2019, 1, 1),  2)

    print("generate tree: ", (datetime.now() - old), "called ", count, " times", total_time, "total_time spent in graph edgs")
    print("userset", user_set)

    # print(GRAPH.graph['36'])
    # print(GRAPH.get_edge('root', '36'))
    # print(TIMELINE.lookup('36', datetime(2020, 8, 1)))    
    
    return json.dumps(ROOT.to())
    

if __name__ == "__main__":
    event = {
            "queryStringParameters": {
                "start_date": "2020-01-01 12:00:00",
                "end_date": "2021-01-01 12:00:00"
            }
        }
    
    print(lambda_handler(event, None))