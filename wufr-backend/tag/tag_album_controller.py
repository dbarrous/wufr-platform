from rds_connect import rds_connect
from util import create_response

# Function that links an Tag to an Album in a Postgres DB with the attributes by creating entry in junction table
# With external_id and external_url attribute
def link_tag_to_album(tag_id, album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Tag_Album"
            query = f'SELECT * FROM "{table}" WHERE tag_id = {tag_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            print(row)
            if row is not None:
                return create_response(
                    409, f"Tag {tag_id} already linked to Album {album_id}"
                )
            # Run SQL Query
            table = '"Tag_Album"'
            query = (
                f"INSERT INTO {table} (tag_id, album_id) VALUES ({tag_id}, {album_id});"
            )
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Tag {tag_id} linked to Album {album_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(link_tag_to_album(1, 2))


def remove_link_tag_to_album(tag_id, album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = "Tag_Album"
            query = f'SELECT * FROM "{table}" WHERE tag_id = {tag_id} AND album_id = {album_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            print(row)
            if row is None:
                return create_response(
                    404, f"Tag {tag_id} not linked to Album {album_id}"
                )
            # Run SQL Query
            table = "Tag_Album"
            query = f'DELETE FROM "{table}" WHERE tag_id = {tag_id} AND album_id = {album_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(200, f"Tag {tag_id} unlinked from Album {album_id}")
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(remove_link_tag_to_album(8, 2))
# Function that gets all Albums for an Tag in a Postgres DB using a junction
# and then returns all of the albums for that tag (DOUBLE INNER JOIN)
def get_albums_by_tag(tag_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Tag"
            junction_table = "Tag_Album"
            second_table = "Album"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".tag_id = "{junction_table}".tag_id INNER JOIN "{second_table}" ON "{junction_table}".album_id = "{second_table}".album_id WHERE "{table}".tag_id = {tag_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Albums for Tag {tag_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(get_albums_by_tag(1))


def get_tags_by_album(album_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Album"
            junction_table = "Tag_Album"
            second_table = "Tag"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".album_id = "{junction_table}".album_id INNER JOIN "{second_table}" ON "{junction_table}".tag_id = "{second_table}".tag_id WHERE "{table}".album_id = {album_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(404, f"Tags for Album {album_id} not found")
            # convert row to dict from tuple
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


print(get_tags_by_album(2))
