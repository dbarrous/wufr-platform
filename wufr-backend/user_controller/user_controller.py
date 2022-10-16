from rds_connect import rds_connect
import json
import logging
from util import create_response


# Function that gets all Users in a Postgres DB with the attributes
# user_id (auto-incremented serial), full_name (text), username (text), birth_date (text), email (text), color (text), profile_pic (text), activated (Boolean), phone (text), autho_id (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created User by it's iddef get_users():
def get_users():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
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


# Function that gets an User in a Postgres DB with the attributes
# user_id (auto-incremented serial), full_name (text) , birth_date (text), death_date (text), start_date (text), end_date (date), biography (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created User by it's id
def get_user(user_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
            query = f'SELECT * FROM "{table}" WHERE user_id = {user_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(404, f"User {user_id} not found")
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_users_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
            query = f"SELECT * FROM \"{table}\" WHERE full_name LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"User {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function to get user by autho id
def get_user_by_autho_id(external_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
            query = f'SELECT * FROM "{table}" WHERE autho_id = {external_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(
                    404,
                    {
                        "message": f"User with autho id: {external_id} not found",
                        "user": None,
                    },
                )
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(
                200,
                {"message": f"User with autho id: {external_id} found", "user": row},
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an User in a Postgres DB with the attributes
# user_id (auto-incremented serial), full_name (text) , birth_date (text), death_date (text), start_date (text), end_date (date), biography (text), artwork (text), relea created_at (timestamp), updated_at (timestamp)
# and then returns the created User by it's id
def create_user(data):
    try:
        user_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"

            for value in user_values.keys():
                user_values[value] = "'" + str(user_values[value]) + "'"
            data["created_at"] = "CURRENT_TIMESTAMP"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(user_values.keys())
            # Get values from data
            values = ", ".join(user_values.values())

            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING user_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE user_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"User {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an User in a Postgres DB with the attributes
# user_id (auto-incremented serial), full_name (text), username (text), birth_date (text), email (text), color (text), profile_pic (text), activated (Boolean), phone (text), autho_id (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created User by it's id
def update_user(data):
    try:
        user_values = data
        user_id = user_values["user_id"]
        user_values.pop("user_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
            for value in user_values.keys():
                user_values[value] = "'" + str(user_values[value]) + "'"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(user_values.keys())
            # Get values from data
            values = ", ".join(user_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE user_id = {user_id} RETURNING user_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE user_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an User in a Postgres DB with the attributes
def delete_user(user_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
            query = f'DELETE FROM public."{table}" WHERE user_id = {user_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"User {user_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Lambda handler function
def handler(event, context):

    print(event)
    print(context)
    if "requestContext" not in event:
        logging.error("Invalid request:")
        logging.error(event)
        return create_response(400, event)

    if event["requestContext"]["http"]["method"] == "GET":

        if "queryStringParameters" in event:
            if "id" in event["queryStringParameters"]:
                # Check if context autho sub id is the same as the user id
                if (
                    "'"
                    + event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
                    + "'"
                ) == event["queryStringParameters"]["id"]:
                    return get_user_by_autho_id(event["queryStringParameters"]["id"])
                else:
                    return create_response(401, "Unauthorized")
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
                        user = get_user_by_autho_id(
                            event["queryStringParameters"]["id"]
                        )
                        if user["statusCode"] == 200:
                            return create_response(400, user)
                        else:
                            create_user(json.loads(event["body"]))
                            user = get_user_by_autho_id(
                                event["queryStringParameters"]["id"]
                            )
                            return create_response(200, user)

                    else:
                        return create_response(401, "Unauthorized")
                else:
                    return create_response(400, "Bad Request")
            else:
                return create_response(400, "Bad Request")

        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "PATCH":
        try:
            # return event
            data = json.loads(event["body"])

            response = update_user(data)
            return response
        except Exception as e:
            pass
            return create_response(400, e)

    if event["requestContext"]["http"]["method"] == "DELETE":

        id = event["queryStringParameters"]["id"]
        response = delete_user(id)
        return response

    return create_response(404, "Invalid Request")


# # # # Test apigateway event
# event = {
#     "requestContext": {"http": {"method": "GET"}},
#     "queryStringParameters": {"id": "1"},
# }

# # Test apigateway event
# event1 = {"requestContext": {"http": {"method": "GET"}}}
# # Test apigateway event
# event2 = {
#     "requestContext": {"http": {"method": "POST"}},
#     "body": '{"full_name": "Test User", "username": "testuser", "birth_date": "1990-01-01", "email": "damianbarrous@gmail.com", "color": "blue", "profile_pic": "url", "activated": "true", "phone": "", "autho_id": "1234567890"}',
# }


# context = {}
# # Test Get one user
# print(handler(event, context))
# # Test Get all users
# print(handler(event1, context))
# # Test Create user
# created_user = handler(event2, context)
# print(created_user)

# body = created_user["body"]
# user_id = json.loads(body)["user_id"]

# body = '{"user_id": user_id_placeholder,"full_name": "Test User", "username": "testuser", "birth_date": "1990-01-01", "email": "damianbarrous@gmail.com", "color": "blue", "profile_pic": "url", "activated": "true", "phone": "", "autho_id": "1234567890"}'.replace(
#     "user_id_placeholder", str(user_id)
# )

# # Test apigateway event
# event3 = {"requestContext": {"http": {"method": "PATCH"}}, "body": body}

# # Test Update user
# print(handler(event3, context))
# # Test apigateway event
# event4 = {
#     "requestContext": {"http": {"method": "DELETE"}},
#     "queryStringParameters": {"id": f"{user_id}"},
# }

# # Test Delete user
# # print(handler(event4, context))

# # Test Get users by name
# event5 = {
#     "requestContext": {"http": {"method": "GET"}},
#     "queryStringParameters": {"name": "Test"},
# }

# print(handler(event5, context))
