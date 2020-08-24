import json
import structures

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

