import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
from structures import Graph, TimeLine, TreeNode
import ast
import collections

# constrains
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
INC_PERIOD = timedelta(days=14)
ROOT_ID = "root"

DB_TABLE_TIMELINE = "academy2020-CovidTimeline"
DB_TABLE_INTERACTIONS = "InteractionTableDuplicatesRemoved"
import json

def lambda_handler(event, context):
    '''
        req: 
            RESET(simid)
            ADD()
            REMOVE()
            COPY()
    '''
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }



event = {
    "queryStringParameters": {
        "request": "ADD",
        "simulation_id": "my simulation",

        # optional parameters

        "userid": "0",
        "covid19": "true",
        "date": "2020-08-20 15:42:00"
        }
    }

response = lambda_handler(event, None)

print(response)

