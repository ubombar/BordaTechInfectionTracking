import json
import boto3
from util import send
from datetime import datetime, timedelta
import structures
from boto3.dynamodb.conditions import Key, Attr

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
INC_PERIOD = timedelta(days=14)
TIMELINE_TABLE = "academy2020-CovidTimeline"
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

    timeline = generate_timeline(database, http_params["date"], http_params['timeline'])

    print(timeline.lines)    

    return send(200, "All good chief")

### GENERATE TIMELINE ###
def generate_timeline(database, date:str, timeline_name:str):
    timeline_table = database.Table(TIMELINE_TABLE)
    response = timeline_table.scan(
        FilterExpression=Attr('SimulationId').eq(timeline_name) & Attr('Date').lt(date)) # FILTER OUT

    timeline = structures.Timeline()
    
    for item in response["Items"]:
        id0 = str(item["UserId"])
        covid = str(item["Covid19"]).lower() == 'true' # Covert to bool
        regdate = datetime.strptime(str(item["Date"]), TIME_FORMAT)

        timeline.register(id0, regdate, covid)
    
    return timeline













#### DEVELOPER DEBUG ZONE ####
development_mode = True

if __name__ == "__main__" and development_mode:
    event = {
        "queryStringParameters": {
            "date": "2020-08-21 17:30:00"
        }
    }
    response = lambda_function(event, None)

    print(response["body"])