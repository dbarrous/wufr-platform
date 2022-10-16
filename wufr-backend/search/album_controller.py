from multiprocessing import context
from rds_connect import rds_connect
from datetime import datetime
from util import create_response
import json


# Function that gets all Albums in a Postgres DB with the attributes
# album_id (auto-incremented serial), title (text) , description (text), color (text), artwork (text), released_date (date), created_at (timestamp), updated_at (timestamp)
# and then returns the created Album by it's iddef get_albums():
def get_albums():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
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


# Function that gets an Album in a Postgres DB with the attributes
# album_id (auto-incremented serial), title (text) , description (text), color (text), streaming_services (text), released_date (date), created_at (timestamp), updated_at (timestamp)
# and then returns the created Album by it's id
def get_album(album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
            query = f'SELECT * FROM "{table}" WHERE album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_albums_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
            query = f"SELECT * FROM \"{table}\" WHERE title LIKE '%{name}%';"
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


# Function that creates an Album in a Postgres DB with the attributes
# album_id (auto-incremented serial), title (text) , description (text), color (text), streaming_services (text), released_date (date), created_at (timestamp), updated_at (timestamp)
# and then returns the created Album by it's id
def create_album(data):
    try:
        album_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"

            for value in album_values.keys():
                # If string contains ' escape it for sql

                if isinstance(album_values[value], int):
                    album_values[value] = str(album_values[value])

                if isinstance(album_values[value], str) and "'" in album_values[value]:
                    album_values[value] = album_values[value].replace("'", "''")

                if isinstance(album_values[value], str) and value != "released_date":
                    album_values[value] = "'" + album_values[value] + "'"

                if value == "released_date":
                    if album_values[value] == "":
                        album_values[value] = "NULL"
                    if len(album_values[value]) == 4:
                        album_values[value] = f"01-01-{album_values['released_date']}"
                    else:
                        # Check if string is in format MM-DD-YYYY using datetime
                        try:
                            datetime.strptime(album_values[value], "%m-%d-%Y")
                        except ValueError:
                            print("Incorrect data format, should be MM-DD-YYYY - Album")
                            album_values[value] = datetime.strptime(
                                album_values[value], "%Y-%m-%d"
                            ).strftime("%m-%d-%Y")

                        album_values[value] = f"'{album_values[value]}'"

            data["created_at"] = "CURRENT_TIMESTAMP"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(album_values.keys())
            # Get values from data
            values = ", ".join(album_values.values())

            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING album_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE album_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Album in a Postgres DB with the attributes
# album_id (auto-incremented serial), title (text) , description (text), color (text), streaming_services (text), released_date (date), created_at (timestamp), updated_at (timestamp)
# and then returns the created Album by it's id
def update_album(data):
    try:
        album_values = data
        album_id = album_values["album_id"]
        album_values.pop("album_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
            for value in album_values.keys():
                album_values[value] = "'" + str(album_values[value]) + "'"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(album_values.keys())
            # Get values from data
            values = ", ".join(album_values.values())

            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE album_id = {album_id} RETURNING album_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE album_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Album in a Postgres DB with the attributes
def delete_album(album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
            query = f'DELETE FROM public."{table}" WHERE album_id = {album_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Album {album_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Lambda handler function
def handler(event, context):

    if event["requestContext"]["http"]["method"] == "GET":
        if "queryStringParameters" not in event:
            return get_albums()
        else:
            if "id" in event["queryStringParameters"]:
                return get_album(event["queryStringParameters"]["id"])
            elif "name" in event["queryStringParameters"]:
                return get_albums_by_name(event["queryStringParameters"]["name"])
            else:
                return create_response(400, "Bad Request")

    if event["requestContext"]["http"]["method"] == "POST":
        try:
            data = json.loads(event["body"])
            # data["user_id"] = event["requestContext"]["authorizer"]["jwt"]["claims"][
            #     "sub"
            # ]
            response = create_album(data)

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

            response = update_album(data)
            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "DELETE":

        id = event["queryStringParameters"]["id"]
        response = delete_album(id)
        return response

    return create_response(404, "Resource Album Found")
