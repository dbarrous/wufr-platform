from rds_connect import rds_connect
from util import create_response
# Function that links an Tag to an User in a Postgres DB with the attributes by creating entry in junction table
# With external_id and external_url attribute
def link_tag_to_user(tag_id, user_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Tag_User"
            query = f'SELECT * FROM "{table}" WHERE tag_id = {tag_id} AND user_id = {user_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                return create_response(
                    409, f"Tag {tag_id} already linked to User {user_id}"
                )
            # Run SQL Query
            table = '"Tag_User"'
            created_at = "CURRENT_TIMESTAMP"
            query = f"INSERT INTO {table} (tag_id, user_id, created_at) VALUES ({tag_id}, {user_id}, {created_at});"
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Tag {tag_id} linked to User {user_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(link_tag_to_user(1, 3))


def remove_link_tag_to_user(tag_id, user_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Tag_User"
            query = f'SELECT * FROM "{table}" WHERE tag_id = {tag_id} AND user_id = {user_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            print(row)
            if row is None:
                return create_response(
                    404, f"Tag {tag_id} not linked to User {user_id}"
                )
            # Run SQL Query
            table = "Tag_User"
            query = f'DELETE FROM "{table}" WHERE tag_id = {tag_id} AND user_id = {user_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Tag {tag_id} unlinked from User {user_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(remove_link_tag_to_user(8, 2))
# Function that gets all Users for an Tag in a Postgres DB using a junction
# and then returns all of the users for that tag (DOUBLE INNER JOIN)
def get_users_by_tag(tag_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            junction_table = "Tag_User"
            second_table = "User"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".tag_id = "{junction_table}".tag_id INNER JOIN "{second_table}" ON "{junction_table}".user_id = "{second_table}".user_id WHERE "{table}".tag_id = {tag_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Users for Tag {tag_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(get_users_by_tag(1))


def get_tags_by_user(user_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
            junction_table = "Tag_User"
            second_table = "Tag"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".user_id = "{junction_table}".user_id INNER JOIN "{second_table}" ON "{junction_table}".tag_id = "{second_table}".tag_id WHERE "{table}".user_id = {user_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Tags for User {user_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(get_tags_by_user(3))
