from rds_connect import rds_connect
from util import create_response

# Function that links an Song to an Album in a Postgres DB with the attributes by creating entry in junction table
# With optional order attribute
def link_song_to_album(song_id, album_id, order):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Song_Album"
            query = f'SELECT * FROM "{table}" WHERE song_id = {song_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                return create_response(
                    409,
                    f"Song {song_id} already linked to Album {album_id} (Order: {row[2]})",
                )
            # Run SQL Query
            table = "Song_Album"
            query = f'INSERT INTO "{table}" ("song_id", "album_id", "order") VALUES ({song_id}, {album_id}, {order});'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Song {song_id} linked to Album {album_id} (Order: {order})"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def update_order_song_to_album(song_id, album_id, order):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Song_Album"
            query = f'SELECT * FROM "{table}" WHERE song_id = {song_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404, f"Song {song_id} not linked to Album {album_id}"
                )
            # Run SQL Query
            table = "Song_Album"
            query = f'UPDATE "{table}" SET "order" = {order} WHERE song_id = {song_id} AND album_id = {album_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Song {song_id} linked to Album {album_id} (Order: {order})"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def remove_link_song_to_album(song_id, album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Song_Album"
            query = f'SELECT * FROM "{table}" WHERE song_id = {song_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404, f"Song {song_id} not linked to Album {album_id}"
                )
            # Run SQL Query
            table = "Song_Album"
            query = f'DELETE FROM "{table}" WHERE song_id = {song_id} AND album_id = {album_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Song {song_id} unlinked from Album {album_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(remove_link_song_to_album(8, 2))
# Function that gets all Albums for an Song in a Postgres DB using a junction
# and then returns all of the albums for that song (DOUBLE INNER JOIN)
def get_albums_by_song(song_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
            junction_table = "Song_Album"
            second_table = "Album"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".song_id = "{junction_table}".song_id INNER JOIN "{second_table}" ON "{junction_table}".album_id = "{second_table}".album_id WHERE "{table}".song_id = {song_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Albums for Song {song_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_songs_by_album(album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
            junction_table = "Song_Album"
            second_table = "Song"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".album_id = "{junction_table}".album_id INNER JOIN "{second_table}" ON "{junction_table}".song_id = "{second_table}".song_id WHERE "{table}".album_id = {album_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            print(rows)
            if rows == []:
                return create_response(404, f"Songs for Album {album_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function to check if a Song is already linked to an Album
def check_song_album(song_id, album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song_Album"
            query = f'SELECT * FROM "{table}" WHERE song_id = {song_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404, f"Song {song_id} not linked to Album {album_id}"
                )
            return create_response(200, f"Song {song_id} linked to Album {album_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")
