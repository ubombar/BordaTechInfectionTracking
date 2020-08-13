from new_algo import *
import json

# DIRECT LAMBDA FUNCTIONS
def register_contactv3(first:str, second:str, start:datetime, end:datetime, rssi:int): 
    if first < second: first, second = second, first # Sort
    DATABASE_CONTACTS.append({
        'FirstDevId': first, 
        'SecondDevId': second, 
        'StartDate': start.strftime(TIME_FORMAT), 
        'EndDate': end.strftime(TIME_FORMAT), 
        'RSSI': rssi})
    trigger_alter_graph(first, second, start, end, rssi)
    trigger_alter_tree(first, second, start, end, rssi)

def register_info(devid:str, result:bool, date:datetime):
    DATABASE_INFO.append({
        'DevId': devid,
        'Result': result,
        'Date': date.strftime(TIME_FORMAT)
    }) 
    if result:
        register_contactv3('root', devid, date, date, 0)


if __name__ == "__main__":
    register_contactv3('dev01', 'dev02', datetime(2020, 1, 1), datetime(2020, 1, 1), 50)
    register_contactv3('dev01', 'dev03', datetime(2020, 1, 3), datetime(2020, 1, 3), 50)
    register_contactv3('dev02', 'dev03', datetime(2020, 1, 5), datetime(2020, 1, 5), 50)
    register_contactv3('dev03', 'dev04', datetime(2020, 1, 2), datetime(2020, 1, 2), 50)
    register_contactv3('dev03', 'dev04', datetime(2020, 1, 4), datetime(2020, 1, 4), 50)

    register_info('dev01', True, datetime(2020, 1, 3))

    print(json.dumps(TREE_ROOT.to()))