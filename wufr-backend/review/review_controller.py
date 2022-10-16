from rds_connect import rds_connect
import json
from util import create_response

# Function that gets all Reviews in a Postgres DB with the attributes
# review_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Review by it's iddef get_reviews():
def get_reviews():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
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


# Function that gets an Review in a Postgres DB with the attributes
# review_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Review by it's id
def get_review(review_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
            query = f'SELECT * FROM "{table}" WHERE review_id = {review_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(404, f"Review {review_id} not found")
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_reviews_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
            query = f"SELECT * FROM \"{table}\" WHERE title LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"Review {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Review in a Postgres DB with the attributes
# review_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Review by it's id
def create_review(data):
    try:
        review_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
            for value in review_values.keys():
                review_values[value] = "'" + str(review_values[value]) + "'"

            data["created_at"] = "CURRENT_TIMESTAMP"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(review_values.keys())
            # Get values from data
            values = ", ".join(review_values.values())
            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING review_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE review_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"Review {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Review in a Postgres DB with the attributes
# review_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), user_id (serial), created_at (timestamp), updated_at (timestamp)
# and then returns the created Review by it's id
def update_review(data):
    try:
        review_values = data
        review_id = review_values["review_id"]
        review_values.pop("review_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
            for value in review_values.keys():
                review_values[value] = "'" + str(review_values[value]) + "'"

            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(review_values.keys())
            # Get values from data
            values = ", ".join(review_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE review_id = {review_id} RETURNING review_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE review_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Review in a Postgres DB with the attributes
def delete_review(review_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
            query = f'DELETE FROM public."{table}" WHERE review_id = {review_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Review {review_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Lambda handler function
def handler(event, context):

    print(event)
    print(context)
    if "requestContext" not in event:
        return create_response(400, event)

    if event["requestContext"]["http"]["method"] == "GET":

        if "queryStringParameters" in event:
            if "user_id" in event["queryStringParameters"]:
                response = get_review_by_user_id(
                    event["queryStringParameters"]["user_id"]
                )
                return create_response(200, response)
            elif "song_id" in event["queryStringParameters"]:
                # Get album media type review
                response = get_review_by_media_type_and_id(
                    "song", event["queryStringParameters"]["song_id"]
                )
                return create_response(200, response)
            elif "album_id" in event["queryStringParameters"]:
                # Get album media type review
                response = get_review_by_media_type_and_id(
                    "album", event["queryStringParameters"]["album_id"]
                )
                return create_response(200, response)
            elif "playlist_id" in event["queryStringParameters"]:
                # Get playlist media type review
                response = get_review_by_media_type_and_id(
                    "playlist", event["queryStringParameters"]["playlist_id"]
                )
                return create_response(200, response)
            else:
                return create_response(400, "Bad Request")

    if event["requestContext"]["http"]["method"] == "POST":
        try:
            if "queryStringParameters" in event:
                if "id" in event["queryStringParameters"]:
                    # Check if context autho sub id is the same as the user id
                    if (
                        "'"
                        + event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
                        + "'"
                    ) == event["queryStringParameters"]["id"]:
                        
                        response = create_review(json.loads(event["body"]))
                        return create_response(200, response)

                    else:
                        return create_response(401, "Unauthorized")
                else:
                    return create_response(400, "Bad Request")
            else:
                return create_response(400, "Bad Request")

        except Exception as e:
            pass
            return create_response(400, e)
    if event["requestContext"]["http"]["method"] == "DELETE":

        if "queryStringParameters" in event:
            if "review_id" in event["queryStringParameters"]:
                response = delete_review(
                    event["queryStringParameters"]["review_id"]
                )
                return create_response(200, response)
          
    return create_response(400, "Bad Request")


# Get Review by Media Type and ID
def get_review_by_media_type_and_id(media_type, media_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
            query = f'SELECT * FROM "{table}" WHERE media_type = \'{media_type}\' AND media_id = {media_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, [])
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")

# Get review by user id
def get_review_by_user_id(user_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Review"
            query = f'SELECT * FROM "{table}" WHERE user_id = {user_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, [])
                       # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")
