import json
from datetime import date, datetime

# Function that constructs response object
def create_response(code, body):
    response = {"statusCode": code, "body": json.dumps(body, default=json_serial)}

    return response


# Function that makes datetime serializable for JSON objects
def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
