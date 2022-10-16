from rds_connect import rds_connect
import json
from util import create_response

# Function that gets all Tags in a Postgres DB with the attributes
# tag_id (auto-incremented serial), name (text), score (integer), user_id (serial), created_at (timestamp), last_used_at (timestamp)
# and then returns the created Tag by it's iddef get_tags():
def get_tags():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            query = f'SELECT * FROM "{table}";'
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that gets an Tag in a Postgres DB with the attributes
# tag_id (auto-incremented serial), name (text), score (integer), user_id (serial), created_at (timestamp), last_used_at (timestamp)
# and then returns the created Tag by it's id
def get_tag(tag_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            query = f'SELECT * FROM "{table}" WHERE tag_id = {tag_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(404, f"Tag {tag_id} not found")
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_tags_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            query = f"SELECT * FROM \"{table}\" WHERE name LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"Tag {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Tag in a Postgres DB with the attributes
# tag_id (auto-incremented serial), name (text), score (integer), user_id (serial), created_at (timestamp), last_used_at (timestamp)
# and then returns the created Tag by it's id
def create_tag(data):
    try:
        tag_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            for value in tag_values.keys():
                tag_values[value] = "'" + str(tag_values[value]) + "'"

            data["created_at"] = "CURRENT_TIMESTAMP"
            data["last_used_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(tag_values.keys())
            # Get values from data
            values = ", ".join(tag_values.values())
            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING tag_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE tag_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"Tag {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Tag in a Postgres DB with the attributes
# tag_id (auto-incremented serial), name (text), score (integer), user_id (serial), created_at (timestamp), last_used_at (timestamp)
# and then returns the created Tag by it's id
def update_tag(data):
    try:
        tag_values = data
        tag_id = tag_values["tag_id"]
        tag_values.pop("tag_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            for value in tag_values.keys():
                tag_values[value] = "'" + str(tag_values[value]) + "'"

            data["last_used_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(tag_values.keys())
            # Get values from data
            values = ", ".join(tag_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE tag_id = {tag_id} RETURNING tag_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE tag_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Tag in a Postgres DB with the attributes
def delete_tag(tag_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            query = f'DELETE FROM public."{table}" WHERE tag_id = {tag_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Tag {tag_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Lambda handler function
def handler(event, context):

    if event["requestContext"]["http"]["method"] == "GET":
        if "queryStringParameters" not in event:
            return get_tags()
        else:
            if "id" in event["queryStringParameters"]:
                return get_tag(event["queryStringParameters"]["id"])
            elif "name" in event["queryStringParameters"]:
                return get_tags_by_name(event["queryStringParameters"]["name"])
            else:
                return create_response(400, "Bad Request")

    if event["requestContext"]["http"]["method"] == "POST":
        try:
            data = json.loads(event["body"])
            # data["user_id"] = event["requestContext"]["authorizer"]["jwt"]["claims"][
            #     "sub"
            # ]
            response = create_tag(data)

            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "PATCH":
        try:
            # return event
            data = json.loads(event["body"])
            # data["user_id"] = event["requestContext"]["authorizer"]["jwt"]["claims"][
            #     "sub"
            # ]

            response = update_tag(data)
            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "DELETE":

        id = event["queryStringParameters"]["id"]
        response = delete_tag(id)
        return response

    return create_response(404, "Resource Tag Found")


# Test apigateway event
event = {
    "requestContext": {"http": {"method": "GET"}},
    "queryStringParameters": {"id": "1"},
}

# Test apigateway event
event1 = {"requestContext": {"http": {"method": "GET"}}}
# Test apigateway event
event2 = {
    "requestContext": {"http": {"method": "POST"}},
    "body": '{"name": "test", "score": 3, "user_id": 5}',
}


context = {}
# Test Get one tag
print(handler(event, context))
# Test Get all tags
print(handler(event1, context))
# Test Create tag
created_tag = handler(event2, context)
print(created_tag)

body = created_tag["body"]
tag_id = json.loads(body)["tag_id"]

body = '{"tag_id": tag_id_placeholder,"name": "test", "score": 3, "user_id": 5}'.replace(
    "tag_id_placeholder", str(tag_id)
)

# Test apigateway event
event3 = {"requestContext": {"http": {"method": "PATCH"}}, "body": body}

# Test Update tag
print(handler(event3, context))
# Test apigateway event
event4 = {
    "requestContext": {"http": {"method": "DELETE"}},
    "queryStringParameters": {"id": f"{tag_id}"},
}

# Test Delete tag
# print(handler(event4, context))

# Test Get tags by name
event5 = {
    "requestContext": {"http": {"method": "GET"}},
    "queryStringParameters": {"name": "test"},
}

print(handler(event5, context))
