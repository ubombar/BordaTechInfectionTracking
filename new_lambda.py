#!/home/ubombar/torch/bin/python
from new_const import *
from new_algo import *
import json

# DIRECT LAMBDA FUNCTIONS
def register_contactv3(first:str, second:str, earliest:datetime, rssi:int): 
    if first < second: first, second = second, first # Sort
    DATABASE_CONTACTS.append({
        'FirstDevId': first, 
        'SecondDevId': second, 
        'EarliestDate': earliest.strftime(TIME_FORMAT), 
        'RSSI': rssi})
    
    # We may want to create the graph if there is a connection with root.
    trigger_alter_graph(first, second, earliest, rssi)
    trigger_alter_tree(first, second, earliest, rssi)

def register_info(devid:str, result:bool, date:datetime):
    DATABASE_INFO.append({
        'DevId': devid,
        'Result': result,
        'Date': date.strftime(TIME_FORMAT)
    }) 

    # trigger if there is some actively infected, get the connection data
    # starting from the earliest date that is greater that the earliest 
    # danger zone date? But this might cause other problems!
    if result:
        min_danger_date = date - INC_PERIOD
        trigger_alter_graph('root', devid, min_danger_date, 0)
        trigger_alter_tree('root', devid, min_danger_date, 0)


if __name__ == "__main__": # THOSE ALL ARE LAMBDA CALLS
    register_contactv3('dev01', 'dev04', datetime(2020, 1, 2), 50)
    register_contactv3('dev02', 'dev04', datetime(2020, 1, 6), 50)
    register_contactv3('dev03', 'dev04', datetime(2020, 1, 7), 50)
    register_contactv3('dev05', 'dev04', datetime(2020, 1, 2), 50)

    register_info('dev01', True, datetime(2020, 1, 16))
    register_info('dev02', True, datetime(2020, 1, 19))

    print(json.dumps(TREE_ROOT.to()))