from rds_connect import rds_connect
from util import create_response

# Function that links an Artist to an Song in a Postgres DB with the attributes by creating entry in junction table
# With optional order attribute
def link_artist_to_song(artist_id, song_id, order):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Artist_Song"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id} AND song_id = {song_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                return create_response(
                    409,
                    f"Artist {artist_id} already linked to Song {song_id} (Order: {row[2]})",
                )
            # Run SQL Query
            table = "Artist_Song"
            query = f'INSERT INTO "{table}" ("artist_id", "song_id", "order") VALUES ({artist_id}, {song_id}, {order});'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Artist {artist_id} linked to Song {song_id} (Order: {order})"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def update_order_artist_to_song(artist_id, song_id, order):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Artist_Song"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id} AND song_id = {song_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404, f"Artist {artist_id} not linked to Song {song_id}"
                )
            # Run SQL Query
            table = "Artist_Song"
            query = f'UPDATE "{table}" SET "order" = {order} WHERE artist_id = {artist_id} AND song_id = {song_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Artist {artist_id} linked to Song {song_id} (Order: {order})"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def remove_link_artist_to_song(artist_id, song_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Artist_Song"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id} AND song_id = {song_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404, f"Artist {artist_id} not linked to Song {song_id}"
                )
            # Run SQL Query
            table = "Artist_Song"
            query = f'DELETE FROM "{table}" WHERE artist_id = {artist_id} AND song_id = {song_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Artist {artist_id} unlinked from Song {song_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(remove_link_artist_to_song(8, 2))
# Function that gets all Songs for an Artist in a Postgres DB using a junction
# and then returns all of the songs for that artist (DOUBLE INNER JOIN)
def get_songs_by_artist(artist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"
            junction_table = "Artist_Song"
            second_table = "Song"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".artist_id = "{junction_table}".artist_id INNER JOIN "{second_table}" ON "{junction_table}".song_id = "{second_table}".song_id WHERE "{table}".artist_id = {artist_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Songs for Artist {artist_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_artists_by_song(song_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Song"
            junction_table = "Artist_Song"
            second_table = "Artist"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".song_id = "{junction_table}".song_id INNER JOIN "{second_table}" ON "{junction_table}".artist_id = "{second_table}".artist_id WHERE "{table}".song_id = {song_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Artists for Song {song_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")
