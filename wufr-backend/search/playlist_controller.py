from rds_connect import rds_connect
from util import create_response

# Function that gets all Playlists in a Postgres DB with the attributes
# playlist_id (auto-incremented serial), title (text) , description (text), recommendation (text), color (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Playlist by it's iddef get_playlists():
def get_playlists():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist"
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


# Function that gets an Playlist in a Postgres DB with the attributes
# playlist_id (auto-incremented serial), title (text) , description (text), score (integer), color (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Playlist by it's id
def get_playlist(playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist"
            query = f'SELECT * FROM "{table}" WHERE playlist_id = {playlist_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(404, f"Playlist {playlist_id} not found")
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_playlists_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist"
            query = f"SELECT * FROM \"{table}\" WHERE title LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"Playlist {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Playlist in a Postgres DB with the attributes
# playlist_id (auto-incremented serial), title (text) , description (text), recommendation (text), color (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Playlist by it's id
def create_playlist(playlist_values):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            songs = playlist_values.pop("songs")

            # Run SQL Query
            table = "Playlist"
            for value in playlist_values.keys():
                if "'" in str(playlist_values[value]):
                    playlist_values[value] = playlist_values[value].replace("'", "''")

                playlist_values[value] = "'" + str(playlist_values[value]) + "'"

            playlist_values["created_at"] = "CURRENT_TIMESTAMP"
            playlist_values["updated_at"] = "CURRENT_TIMESTAMP"

            # Get columns from data
            columns = ", ".join(playlist_values.keys())
            # Get values from data
            values = ", ".join(playlist_values.values())

            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING playlist_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            print(row)
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE playlist_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"Playlist {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            for song in songs:
                link = link_song_to_playlist(insert_id, song["song_id"], song["order"])
                print(link)

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Playlist in a Postgres DB with the attributes
# playlist_id (auto-incremented serial), title (text) , description (text), recommendation (text), color (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Playlist by it's id
def update_playlist(playlist_values):
    try:
        # Run SQL Query
        songs = playlist_values.pop("songs")
        playlist_id = playlist_values["playlist_id"]
        playlist_values.pop("playlist_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist"
            for value in playlist_values.keys():
                if "'" in str(playlist_values[value]):
                    playlist_values[value] = playlist_values[value].replace("'", "''")

                playlist_values[value] = "'" + str(playlist_values[value]) + "'"

            playlist_values["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(playlist_values.keys())
            # Get values from data
            values = ", ".join(playlist_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE playlist_id = {playlist_id} RETURNING playlist_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE playlist_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            unlink_all_songs_from_playlist(insert_id)
            for song in songs:
                link = link_song_to_playlist(insert_id, song["song_id"], song["order"])
                print(link)
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Playlist in a Postgres DB with the attributes
def delete_playlist(playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist"
            query = f'DELETE FROM public."{table}" WHERE playlist_id = {playlist_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Playlist {playlist_id} deleted")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Attach song to playlist (playlist_id, song_id, order, user_id)
def link_song_to_playlist(playlist_id, song_id, order):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist_Song"
            query = f'INSERT INTO public."{table}" ("playlist_id", "song_id", "order") VALUES ({playlist_id}, {song_id}, {order}) RETURNING playlist_id, song_id, "order";'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Remove song from playlist (playlist_id, song_id)
def unlink_song_from_playlist(playlist_id, song_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist_Song"
            query = f'DELETE FROM public."{table}" WHERE playlist_id = {playlist_id} AND song_id = {song_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Song {song_id} removed from Playlist {playlist_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Get all songs from playlist (playlist_id)
def get_songs_from_playlist(playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist_Song"
            query = f'SELECT * FROM public."{table}" WHERE playlist_id = {playlist_id};'
            cursor.execute(query)
            row = cursor.fetchall()
            connection.commit()
            # convert row to dict from tuple
            row = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in row
            ]
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Unlink all songs from playlist (playlist_id)
def unlink_all_songs_from_playlist(playlist_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Playlist_Song"
            query = f'DELETE FROM public."{table}" WHERE playlist_id = {playlist_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"All songs removed from Playlist {playlist_id}"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")
