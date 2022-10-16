from rds_connect import rds_connect
from util import create_response

# Function that links an Artist to an Album in a Postgres DB with the attributes by creating entry in junction table
# With optional order attribute
def link_artist_to_album(artist_id, album_id, order):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Artist_Album"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                return create_response(
                    409,
                    f"Artist {artist_id} already linked to Album {album_id} (Order: {row[2]})",
                )
            # Run SQL Query
            table = "Artist_Album"
            query = f'INSERT INTO "{table}" ("artist_id", "album_id", "order") VALUES ({artist_id}, {album_id}, {order});'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Artist {artist_id} linked to Album {album_id} (Order: {order})"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(link_artist_to_album(8, 2, 6))


def update_order_artist_to_album(artist_id, album_id, order):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Artist_Album"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # print(row)
            if row is None:
                return create_response(
                    404, f"Artist {artist_id} not linked to Album {album_id}"
                )
            # Run SQL Query
            table = "Artist_Album"
            query = f'UPDATE "{table}" SET "order" = {order} WHERE artist_id = {artist_id} AND album_id = {album_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Artist {artist_id} linked to Album {album_id} (Order: {order})"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(update_order_artist_to_album(8, 2, 3))


def remove_link_artist_to_album(artist_id, album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Artist_Album"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # print(row)
            if row is None:
                return create_response(
                    404, f"Artist {artist_id} not linked to Album {album_id}"
                )
            # Run SQL Query
            table = "Artist_Album"
            query = f'DELETE FROM "{table}" WHERE artist_id = {artist_id} AND album_id = {album_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Artist {artist_id} unlinked from Album {album_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(remove_link_artist_to_album(8, 2))
# Function that gets all Albums for an Artist in a Postgres DB using a junction
# and then returns all of the albums for that artist (DOUBLE INNER JOIN)
def get_albums_by_artist(artist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist"
            junction_table = "Artist_Album"
            second_table = "Album"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".artist_id = "{junction_table}".artist_id INNER JOIN "{second_table}" ON "{junction_table}".album_id = "{second_table}".album_id WHERE "{table}".artist_id = {artist_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Albums for Artist {artist_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(get_albums_by_artist(8))


def get_artists_by_album(album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
            junction_table = "Artist_Album"
            second_table = "Artist"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".album_id = "{junction_table}".album_id INNER JOIN "{second_table}" ON "{junction_table}".artist_id = "{second_table}".artist_id WHERE "{table}".album_id = {album_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Artists for Album {album_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(get_artists_by_album(2))
def check_artist_album(artist_id, album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Artist_Album"
            query = f'SELECT * FROM "{table}" WHERE artist_id = {artist_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404, f"Artist {artist_id} not linked to Album {album_id}"
                )
            return create_response(
                200, f"Artist {artist_id} linked to Album {album_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")
