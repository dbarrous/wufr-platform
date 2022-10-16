from rds_connect import rds_connect
from util import create_response

# Function that gets all Artists in a Postgres DB with the attributes
# artist_id (auto-incremented serial), full_name (text) , birth_date (text), death_date (text), start_date (text), end_date (date), biography (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Artist by it's iddef get_artists():
def get_artists():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"
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


# Function that gets an Artist in a Postgres DB with the attributes
# artist_id (auto-incremented serial), full_name (text) , birth_date (text), death_date (text), start_date (text), end_date (date), biography (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Artist by it's id
def get_artist(artist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(404, f"Artist {artist_id} not found")
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_artists_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"
            query = f"SELECT * FROM \"{table}\" WHERE full_name LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"Artist {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Artist in a Postgres DB with the attributes
# artist_id (auto-incremented serial), full_name (text) , birth_date (text), death_date (text), start_date (text), end_date (date), biography (text), artwork (text), relea created_at (timestamp), updated_at (timestamp)
# and then returns the created Artist by it's id
def create_artist(data):
    try:
        artist_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"

            for value in artist_values.keys():
                artist_values[value] = "'" + str(artist_values[value]) + "'"
                if value == "released_date":
                    artist_values[value] = (
                        "to_date(" + artist_values[value] + ", 'YYYY-MM-DD')"
                    )
            data["created_at"] = "CURRENT_TIMESTAMP"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(artist_values.keys())
            # Get values from data
            values = ", ".join(artist_values.values())

            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING artist_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE artist_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"Artist {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            return row
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Artist in a Postgres DB with the attributes
# artist_id (auto-incremented serial), full_name (text) , birth_date (text), death_date (text), start_date (text), end_date (date), biography (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Artist by it's id
def update_artist(data):
    try:
        artist_values = data
        artist_id = artist_values["artist_id"]
        artist_values.pop("artist_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"
            for value in artist_values.keys():
                artist_values[value] = "'" + str(artist_values[value]) + "'"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(artist_values.keys())
            # Get values from data
            values = ", ".join(artist_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE artist_id = {artist_id} RETURNING artist_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE artist_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Artist in a Postgres DB with the attributes
def delete_artist(artist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"
            query = f'DELETE FROM public."{table}" WHERE artist_id = {artist_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Artist {artist_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Lambda handler function
def handler(event, context):

    if event["requestContext"]["http"]["method"] == "GET":
        if "queryStringParameters" not in event:
            return get_artists()
        else:
            if "id" in event["queryStringParameters"]:
                return get_artist(event["queryStringParameters"]["id"])
            elif "name" in event["queryStringParameters"]:
                return get_artists_by_name(event["queryStringParameters"]["name"])
            else:
                return create_response(400, "Bad Request")

    if event["requestContext"]["http"]["method"] == "POST":
        try:
            data = json.loads(event["body"])
            # data["user_id"] = event["requestContext"]["authorizer"]["jwt"]["claims"][
            #     "sub"
            # ]
            response = create_artist(data)

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

            response = update_artist(data)
            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "DELETE":

        id = event["queryStringParameters"]["id"]
        response = delete_artist(id)
        return response

    return create_response(404, "Resource Artist Found")
