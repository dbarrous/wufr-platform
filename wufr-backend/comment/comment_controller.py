from rds_connect import rds_connect
import json
from util import create_response

# Function that gets all Comments in a Postgres DB with the attributes
# comment_id (auto-incremented serial), comment (text),  score (integer), comment_id (serial), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Comment by it's iddef get_comments():
def get_comments():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Comment"
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


# Function that gets an Comment in a Postgres DB with the attributes
# comment_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Comment by it's id
def get_comment(comment_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Comment"
            query = f'SELECT * FROM "{table}" WHERE comment_id = {comment_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(404, f"Comment {comment_id} not found")
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_comments_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Comment"
            query = f"SELECT * FROM \"{table}\" WHERE comment LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"Comment {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Comment in a Postgres DB with the attributes
# comment_id (auto-incremented serial), comment (text),  score (integer), comment_id (serial), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Comment by it's id
def create_comment(data):
    try:
        comment_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Comment"
            for value in comment_values.keys():
                comment_values[value] = "'" + str(comment_values[value]) + "'"

            data["created_at"] = "CURRENT_TIMESTAMP"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(comment_values.keys())
            # Get values from data
            values = ", ".join(comment_values.values())
            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING comment_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE comment_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"Comment {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Comment in a Postgres DB with the attributes
# comment_id (auto-incremented serial), comment (text),  score (integer), comment_id (serial), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Comment by it's id
def update_comment(data):
    try:
        comment_values = data
        comment_id = comment_values["comment_id"]
        comment_values.pop("comment_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Comment"
            for value in comment_values.keys():
                comment_values[value] = "'" + str(comment_values[value]) + "'"

            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(comment_values.keys())
            # Get values from data
            values = ", ".join(comment_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE comment_id = {comment_id} RETURNING comment_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE comment_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Comment in a Postgres DB with the attributes
def delete_comment(comment_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Comment"
            query = f'DELETE FROM public."{table}" WHERE comment_id = {comment_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Comment {comment_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Lambda handler function
def handler(event, context):

    if event["requestContext"]["http"]["method"] == "GET":
        if "queryStringParameters" not in event:
            return get_comments()
        else:
            if "id" in event["queryStringParameters"]:
                return get_comment(event["queryStringParameters"]["id"])
            elif "name" in event["queryStringParameters"]:
                return get_comments_by_name(event["queryStringParameters"]["name"])
            else:
                return create_response(400, "Bad Request")

    if event["requestContext"]["http"]["method"] == "POST":
        try:
            data = json.loads(event["body"])
            response = create_comment(data)

            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "PATCH":
        try:
            # return event
            data = json.loads(event["body"])

            response = update_comment(data)
            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "DELETE":

        id = event["queryStringParameters"]["id"]
        response = delete_comment(id)
        return response

    return create_response(404, "Resource Comment Found")
