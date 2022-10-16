from rds_connect import rds_connect
from datetime import datetime
from util import create_response
import json

# Function that gets all Songs in a Postgres DB with the attributes
# song_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), artwork (text), lyrics (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Song by it's iddef get_songs():
def get_songs():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
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


# Function that gets an Song in a Postgres DB with the attributes
# song_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Song by it's id
def get_song(song_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
            query = f'SELECT * FROM "{table}" WHERE song_id = {song_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(404, f"Song {song_id} not found")
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_songs_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
            query = f"SELECT * FROM \"{table}\" WHERE title LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"Song {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Song in a Postgres DB with the attributes
# song_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Song by it's id
def create_song(data):
    try:
        song_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
            for value in song_values.keys():
                # If string contains ' escape it for sql
                if "'" in str(song_values[value]) and value != "released_date":
                    song_values[value] = song_values[value].replace("'", "''")

                if value == "released_date":
                    if song_values[value] == "":
                        song_values[value] = "NULL"
                    if len(song_values[value]) == 4:
                        song_values[value] = f"01-01-{song_values['released_date']}"
                    else:
                        # Check if string is in format MM-DD-YYYY using datetime
                        try:
                            datetime.strptime(song_values[value], "%m-%d-%Y")
                        except ValueError:
                            print("Incorrect data format, should be MM-DD-YYYY - Song")

                            song_values[value] = datetime.strptime(
                                song_values[value], "%Y-%m-%d"
                            ).strftime("%m-%d-%Y")

                song_values[value] = f"'{song_values[value]}'"

            data["created_at"] = "CURRENT_TIMESTAMP"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(song_values.keys())
            # Get values from data
            values = ", ".join(song_values.values())
            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING song_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE song_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"Song {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Song in a Postgres DB with the attributes
# song_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), artwork (text), lyrics (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Song by it's id
def update_song(data):
    try:
        song_values = data
        song_id = song_values["song_id"]
        song_values.pop("song_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
            for value in song_values.keys():
                song_values[value] = "'" + str(song_values[value]) + "'"

            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(song_values.keys())
            # Get values from data
            values = ", ".join(song_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE song_id = {song_id} RETURNING song_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE song_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Song in a Postgres DB with the attributes
def delete_song(song_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
            query = f'DELETE FROM public."{table}" WHERE song_id = {song_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Song {song_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Lambda handler function
def handler(event, context):

    if event["requestContext"]["http"]["method"] == "GET":
        if "queryStringParameters" not in event:
            return get_songs()
        else:
            if "id" in event["queryStringParameters"]:
                return get_song(event["queryStringParameters"]["id"])
            elif "name" in event["queryStringParameters"]:
                return get_songs_by_name(event["queryStringParameters"]["name"])
            else:
                return create_response(400, "Bad Request")

    if event["requestContext"]["http"]["method"] == "POST":
        try:
            data = json.loads(event["body"])
            # data["user_id"] = event["requestContext"]["authorizer"]["jwt"]["claims"][
            #     "sub"
            # ]
            response = create_song(data)

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

            response = update_song(data)
            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "DELETE":

        id = event["queryStringParameters"]["id"]
        response = delete_song(id)
        return response

    return create_response(404, "Resource Song Found")


# # Test apigateway event
# event = {
#     "requestContext": {"http": {"method": "GET"}},
#     "queryStringParameters": {"id": "1"},
# }

# # Test apigateway event
# event1 = {"requestContext": {"http": {"method": "GET"}}}
# # Test apigateway event
# event2 = {
#     "requestContext": {"http": {"method": "POST"}},
#     "body": '{"title": "test", "description": "test", "lyrics": "test", "score": 3, "color": "test", "artwork": "test", "released_date": "2020-01-01"}',
# }


# context = {}
# # Test Get one song
# # print(handler(event, context))
# # Test Get all songs
# # print(handler(event1, context))
# # Test Create song
# # created_song = handler(event2, context)
# # print(created_song)

# body = created_song["body"]
# song_id = json.loads(body)["song_id"]

# body = '{"song_id": song_id_placeholder, "title": "test", "description": "test", "lyrics": "test", "score": 3, "color": "test", "artwork": "test", "released_date": "2020-01-01"}'.replace(
#     "song_id_placeholder", str(song_id)
# )

# # Test apigateway event
# event3 = {"requestContext": {"http": {"method": "PATCH"}}, "body": body}

# # Test Update song
# print(handler(event3, context))
# # Test apigateway event
# event4 = {
#     "requestContext": {"http": {"method": "DELETE"}},
#     "queryStringParameters": {"id": f"{song_id}"},
# }

# # Test Delete song
# # print(handler(event4, context))

# # Test Get songs by name
# event5 = {
#     "requestContext": {"http": {"method": "GET"}},
#     "queryStringParameters": {"name": "test"},
# }

# print(handler(event5, context))
