import graph
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import collections
import json
import algo

def generate_graph(contact_date):
    con_graph = graph.BordaGraph()

    for contact in contact_date:
        name1 = contact["Id"]
        name2 = contact["ContactID"]
        date = datetime.datetime.strptime(contact["Date"], algo.DTFORMAT)

        con_graph.add_edge(name1, name2, date)

    return con_graph

def get_data():
    '''
    dynamodb = boto3.resource("dynamodb")
    contacts_table = dynamodb.Table("ALGO_CONTACTS")
    info_table = dynamodb.Table("ALGO_INFO")
    dev_table = dynamodb.Table("ALGO_DEV")

    CONTACT_DATA = contacts_table.scan()["Items"]
    INFO_DATA = sorted(info_table.scan()["Items"], key=lambda item: item['Date']) # sort by date, fix might be needed
    DEV_DATA = dev_table.scan()["Items"]
    '''
    CONTACT_DATA = [
        {'ContactID': 'dev02', 'Date': '2020-08-04 09:30:00', 'RSSI': 50, 'Id': 'dev04'}, 
        {'ContactID': 'dev03', 'Date': '2020-08-06 09:00:00', 'RSSI': 50, 'Id': 'dev04'}, 
        {'ContactID': 'dev03', 'Date': '2020-08-03 11:30:00', 'RSSI': 50, 'Id': 'dev04'}, 
        {'ContactID': 'dev03', 'Date': '2020-08-01 09:00:00', 'RSSI': 50, 'Id': 'dev01'}, 
        {'ContactID': 'dev04', 'Date': '2020-08-02 09:30:00', 'RSSI': 50, 'Id': 'dev01'}, 
        {'ContactID': 'dev02', 'Date': '2020-08-05 10:30:00', 'RSSI': 50, 'Id': 'dev04'}, 
        {'ContactID': 'dev04', 'Date': '2020-08-03 09:00:00', 'RSSI': 50, 'Id': 'dev01'}
    ] 

    INFO_DATA = [
        {'Id': 'dev01', 'Covid': 'P', 'Date': '2020-07-31 10:00:00'},
        {'Id': 'dev02', 'Covid': 'N', 'Date': '2020-08-02 10:00:00'}
    ] 

    DEV_DATA = [
        {'Id': 'dev03', 'Name': 'Atahan Aksoy'}, 
        {'Id': 'dev04', 'Name': 'Feyza Aydoğan'}, 
        {'Id': 'dev02', 'Name': 'Erdem Ünlü'}, 
        {'Id': 'dev01', 'Name': 'Ufuk Bombar'}
    ]
    return CONTACT_DATA, INFO_DATA, DEV_DATA

def get_history_and_infected(info_data):
    info_history_devids = collections.defaultdict(list) # {devid : [(date, covid), ...]}

    for record in info_data:
        devid = record["Id"]
        date = datetime.datetime.strptime(record["Date"], algo.DTFORMAT)
        covid = record["Covid"] == "P"

        info_history_devids[devid].append((date, covid))

    any_infected = False
    for devid, history_list in info_history_devids.items():
        date, covid = history_list[-1]

        any_infected = any_infected or covid
    
    return info_history_devids, any_infected

def lambda_function(event, context):
    ''' 
        Creates the infected graph from scratch.
        PARAMS:
            MinDate: Earliest date to fetch data. (not implemented yet)
    '''
    CONTACT_DATA, INFO_DATA, DEV_DATA = get_data() # Get data from AWS

    interactions = generate_graph(CONTACT_DATA) # Generate graph

    history, infection = get_history_and_infected(INFO_DATA) # Get history per device and infection boolean

    if not infection: # Nobody is infected except patient zero
        return json.dumps({
            "Message": "Nobody is infected!", 
            "Tree": algo.PATIENT_ZERO.to()
        })
    
    ### 2 Infection detected! create a infection tree! ###
    root = algo.PATIENT_ZERO
    dev_name_dict = {x["Id"]: x["Name"] for x in DEV_DATA}

    for i, record in enumerate(INFO_DATA):
        date = datetime.datetime.strptime(record["Date"], algo.DTFORMAT)
        covid = record["Covid"].upper() == "P"
        devid = record["Id"]

        algo.iterate_for_data(interactions, root, (date, covid, devid), history, i, INFO_DATA, dev_name_dict)

    return json.dumps({"levels": graph.TreeNode.DICT, "tree": root.to()})



event = {"MinDate": "2020-07-20 10:00:00"}
context = None
print("Result of the infection tree algorithm: ", lambda_function(event, context)) # TEST
