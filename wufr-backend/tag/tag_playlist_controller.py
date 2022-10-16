from rds_connect import rds_connect
from util import create_response

# Function that links an Tag to an Playlist in a Postgres DB with the attributes by creating entry in junction table
# With external_id and external_url attribute
def link_tag_to_playlist(tag_id, playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Tag_Playlist"
            query = f'SELECT * FROM "{table}" WHERE tag_id = {tag_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                return create_response(
                    409, f"Tag {tag_id} already linked to Playlist {playlist_id}"
                )
            # Run SQL Query
            table = '"Tag_Playlist"'
            query = f"INSERT INTO {table} (tag_id, playlist_id) VALUES ({tag_id}, {playlist_id});"
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Tag {tag_id} linked to Playlist {playlist_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(link_tag_to_playlist(1, 2))


def remove_link_tag_to_playlist(tag_id, playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Tag_Playlist"
            query = f'SELECT * FROM "{table}" WHERE tag_id = {tag_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            print(row)
            if row is None:
                return create_response(
                    404, f"Tag {tag_id} not linked to Playlist {playlist_id}"
                )
            # Run SQL Query
            table = "Tag_Playlist"
            query = f'DELETE FROM "{table}" WHERE tag_id = {tag_id} AND playlist_id = {playlist_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Tag {tag_id} unlinked from Playlist {playlist_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(remove_link_tag_to_playlist(8, 2))
# Function that gets all Playlists for an Tag in a Postgres DB using a junction
# and then returns all of the playlists for that tag (DOUBLE INNER JOIN)
def get_playlists_by_tag(tag_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            junction_table = "Tag_Playlist"
            second_table = "Playlist"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".tag_id = "{junction_table}".tag_id INNER JOIN "{second_table}" ON "{junction_table}".playlist_id = "{second_table}".playlist_id WHERE "{table}".tag_id = {tag_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Playlists for Tag {tag_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(get_playlists_by_tag(1))


def get_tags_by_playlist(playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist"
            junction_table = "Tag_Playlist"
            second_table = "Tag"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".playlist_id = "{junction_table}".playlist_id INNER JOIN "{second_table}" ON "{junction_table}".tag_id = "{second_table}".tag_id WHERE "{table}".playlist_id = {playlist_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(
                    404, f"Tags for Playlist {playlist_id} not found"
                )
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(get_tags_by_playlist(2))
