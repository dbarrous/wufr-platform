from rds_connect import rds_connect
from util import create_response


# Function that links an User to an Playlist in a Postgres DB with the attributes by creating entry in junction table
# With external_id and external_url attribute
def link_user_to_playlist(user_id, playlist_id, role):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "User_Playlist"
            query = f'SELECT * FROM "{table}" WHERE user_id = {user_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                return create_response(409, f"User {user_id} already linked to Playlist {playlist_id}")
            # Run SQL Query
            table = '"User_Playlist"'
            role = "'" + role + "'"
            query = f"INSERT INTO {table} (user_id, playlist_id, role) VALUES ({user_id}, {playlist_id}, {role});"
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"User {user_id} linked to Playlist {playlist_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")

print(link_user_to_playlist(3, 2, "owner"))

def update_user_playlist_role(user_id, playlist_id, role):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "User_Playlist"
            query = f'SELECT * FROM "{table}" WHERE user_id = {user_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"User {user_id} not linked to Playlist {playlist_id}")
            # Run SQL Query
            table = "User_Playlist"
            role = "'" + role + "'"
            query = f'UPDATE "{table}" SET role = {role} WHERE user_id = {user_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"User {user_id} role updated to {role} for Playlist {playlist_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")

print(update_user_playlist_role(3, 2, "admin"))

def remove_link_user_to_playlist(user_id, playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "User_Playlist"
            query = f'SELECT * FROM "{table}" WHERE user_id = {user_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            print(row)
            if row is None:
                return create_response(404, f"User {user_id} not linked to Playlist {playlist_id}")
            # Run SQL Query
            table = "User_Playlist"
            query = f'DELETE FROM "{table}" WHERE user_id = {user_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"User {user_id} unlinked from Playlist {playlist_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")

# print(remove_link_user_to_playlist(8, 2))
# Function that gets all Playlists for an User in a Postgres DB using a junction
# and then returns all of the playlists for that user (DOUBLE INNER JOIN)
def get_playlists_by_user(user_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "User"
            junction_table = "User_Playlist"
            second_table = "Playlist"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".user_id = "{junction_table}".user_id INNER JOIN "{second_table}" ON "{junction_table}".playlist_id = "{second_table}".playlist_id WHERE "{table}".user_id = {user_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Playlists for User {user_id} not found")
            # convert row to dict from tuple
            rows = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")

print(get_playlists_by_user(3))

def get_users_by_playlist(playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist"
            junction_table = "User_Playlist"
            second_table = "User"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".playlist_id = "{junction_table}".playlist_id INNER JOIN "{second_table}" ON "{junction_table}".user_id = "{second_table}".user_id WHERE "{table}".playlist_id = {playlist_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Users for Playlist {playlist_id} not found")
            # convert row to dict from tuple
            rows = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
            return create_response(200, rows)
        print(e)
        return create_response(432, f"Error in SQL Query {e}")

print(get_users_by_playlist(2))