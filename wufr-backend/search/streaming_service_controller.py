from rds_connect import rds_connect
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import youtube_title_parse
import requests
import os
import song_controller
import song_album_controller
import album_controller
import artist_album_controller
import artist_song_controller
import artist_controller
import playlist_controller
from util import create_response


# Function that gets all Streaming_Services in a Postgres DB with the attributes
# streaming_service_id (auto-incremented serial), name (text) , main_url (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Streaming_Service by it's iddef get_streaming_services():
def get_streaming_services():
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
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


# Function that gets an Streaming_Service in a Postgres DB with the attributes
# streaming_service_id (auto-incremented serial), name (text) , main_url (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Streaming_Service by it's id
def get_streaming_service(streaming_service_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
            query = f'SELECT * FROM "{table}" WHERE streaming_service_id = {streaming_service_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            if row is None:
                return create_response(
                    404, f"Streaming_Service {streaming_service_id} not found"
                )
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_streaming_services_by_name(name):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
            query = f"SELECT * FROM \"{table}\" WHERE name LIKE '%{name}%';"
            cursor.execute(query)
            rows = cursor.fetchall()
            # convert row to dict from tuple
            if rows is None:
                return create_response(404, f"Streaming_Service {name} not found")
            rows = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]

            return create_response(200, rows)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Streaming_Service in a Postgres DB with the attributes
# streaming_service_id (auto-incremented serial), name (text) , main_url (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Streaming_Service by it's id
def create_streaming_service(data):
    try:
        streaming_service_values = data
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
            for value in streaming_service_values.keys():
                streaming_service_values[value] = (
                    "'" + str(streaming_service_values[value]) + "'"
                )

            data["created_at"] = "CURRENT_TIMESTAMP"
            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(streaming_service_values.keys())
            # Get values from data
            values = ", ".join(streaming_service_values.values())
            # Get id of inserted row
            query = f'INSERT INTO public."{table}"({columns}) VALUES({values}) RETURNING streaming_service_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE streaming_service_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(404, f"Streaming_Service {insert_id} not found")
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))

            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that updates an Streaming_Service in a Postgres DB with the attributes
# streaming_service_id (auto-incremented serial), name (text) , main_url (text), artwork (text), created_at (timestamp), updated_at (timestamp)
# and then returns the created Streaming_Service by it's id
def update_streaming_service(data):
    try:
        streaming_service_values = data
        streaming_service_id = streaming_service_values["streaming_service_id"]
        streaming_service_values.pop("streaming_service_id")
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
            for value in streaming_service_values.keys():
                streaming_service_values[value] = (
                    "'" + str(streaming_service_values[value]) + "'"
                )

            data["updated_at"] = "CURRENT_TIMESTAMP"
            # Get columns from data
            columns = ", ".join(streaming_service_values.keys())
            # Get values from data
            values = ", ".join(streaming_service_values.values())
            # Get id of inserted row
            query = f'UPDATE public."{table}" SET ({columns}) = ({values}) WHERE streaming_service_id = {streaming_service_id} RETURNING streaming_service_id;'
            cursor.execute(query)
            row = cursor.fetchone()
            connection.commit()
            insert_id = row[0]
            query = f'SELECT * FROM "{table}" WHERE streaming_service_id = {insert_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that deletes an Streaming_Service in a Postgres DB with the attributes
def delete_streaming_service(streaming_service_id):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
            query = f'DELETE FROM public."{table}" WHERE streaming_service_id = {streaming_service_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200, f"Streaming_Service {streaming_service_id} deleted"
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# Function that creates an Streaming_Service in a Postgres DB with the attributes
def handle_external_search(term, list_of_services=["Spotify"]):
    response = []
    data_search_object = {
        "search_term": term,
        "search_type": "song",
    }
    for service in list_of_services:
        if service == "Spotify":
            response.append(plugin_spotify(data_search_object))
        if service == "YouTube":
            response.append(plugin_youtube(data_search_object))

    if response == []:
        return create_response(404, "No results found")
    else:
        return create_response(200, response)


def plugin_youtube(data_search_object):
    """
    Function to search for song in Youtube API using request api
    """
    print("\nSEARCHING YOUTUBE\n")
    # Create Spotify Streaming Service in Postgres DB if it doesn't exist
    streaming_service = get_streaming_services_by_name("YouTube")
    if streaming_service["body"] == "[]":
        streaming_service = create_streaming_service(
            {
                "name": "YouTube",
                "main_url": "https://www.youtube.com/",
                "artwork": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/1280px-YouTube_full-color_icon_%282017%29.svg.png",
            }
        )

    streaming_service = json.loads(streaming_service["body"])[0]

    # Get youtube api key from .env file
    api_key = os.environ.get("YOUTUBE_API_KEY")

    # Create youtube api url
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={data_search_object['search_term']}&key={api_key}"
    print(url)

    # Get response from youtube api
    response = requests.get(url)

    # Get json response
    videos = response.json()
    print(videos)
    if "error" in videos:
        return create_response(404, f"No results found/Passed limit {videos}")

    for video in videos["items"]:
        if "channelId" in video["id"]:
            # Search Object to return
            artists = create_youtube_artists(streaming_service, videos)

            search_object = {
                "song": [],
                "album": [],
                "artists": artists,
            }

            return search_object
        else:
            # Search Object to return
            artists = create_youtube_artists(streaming_service, videos)
            songs = create_youtube_songs(streaming_service, videos, artists)

            search_object = {
                "song": songs,
                "album": [],
                "artists": artists,
            }

            return search_object


def create_youtube_artists(streaming_service, videos):
    """
    ARTISTS
    """
    artist_list = []
    print(videos)
    for video in videos["items"]:
        # Get youtube api key from .env file
        artist_name_and_title_tuple = youtube_title_parse.get_artist_title(
            video["snippet"]["title"]
        )
        streaming_artist = get_streaming_service_media_by_external_id(
            streaming_service["streaming_service_id"],
            video["snippet"]["channelId"],
            "Artist",
        )

        status_code = streaming_artist["statusCode"]

        if status_code == 404:
            # Create artist in Postgres DB if they don't exist
            if artist_name_and_title_tuple is not None:
                # Fuzzy match for Artist
                artist_name = artist_name_and_title_tuple[0]
                new_artist = {
                    "full_name": artist_name,
                    "biography": "",
                    "artwork": json.dumps(video["snippet"]["thumbnails"]),
                }
            else:
                new_artist = {
                    "full_name": video["snippet"]["channelTitle"],
                    "biography": "",
                    "artwork": json.dumps(video["snippet"]["thumbnails"]),
                }

            does_artist_exist = match_media("artist", new_artist["full_name"])

            if does_artist_exist["statusCode"] == 200:
                new_artist = json.loads(does_artist_exist["body"])[0]
                print("Artist Found:\n")
            else:
                new_artist = artist_controller.create_artist(new_artist)
                print("Artist Created:\n")

            print(new_artist)
            print("\n")

            # # Link to Streaming Service
            streaming_service_link = {
                "streaming_service_id": streaming_service["streaming_service_id"],
                "media_id": new_artist["artist_id"],
                "external_id": video["snippet"]["channelId"],
                "external_url": f"https://www.youtube.com/channel/{video['snippet']['channelId']}",
            }
            link = link_streaming_service_to_media(
                streaming_service_link=streaming_service_link, media_type="Artist"
            )
            print(link)
            # Append new artist to list
            artist_list.append(new_artist)

        else:
            # Loads streaming_artist into artist
            artist = json.loads(streaming_artist["body"])
            print("Artist Found:\n")
            print(artist)
            print("\n")

            # Append existing artist to list
            artist_list.append(artist)


    return artist_list


def create_youtube_songs(streaming_service, videos, artists):
    """
    SONGS
    """
    song_list = []
    for video in videos["items"]:
        # Query satistics youtube api
        if "channelId" not in video["id"]:
            # Get youtube api key from .env file
            artist_name_and_title_tuple = youtube_title_parse.get_artist_title(
                video["snippet"]["title"]
            )
            streaming_song = get_streaming_service_media_by_external_id(
                streaming_service["streaming_service_id"],
                video["id"]["videoId"],
                "Song",
            )

            # create youtube url to video
            status_code = streaming_song["statusCode"]
        else:
            break

        print(streaming_song)
        if status_code == 404:
            if artist_name_and_title_tuple is not None:
                song = {
                    "title": artist_name_and_title_tuple[1],
                    "description": "",
                    "lyrics": [],
                    "color": "red",
                    "artwork": json.dumps(video["snippet"]["thumbnails"]),
                    "preview_url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                }
            else:
                song = {
                    "title": video["snippet"]["title"],
                    "description": "",
                    "lyrics": [],
                    "color": "red",
                    "artwork": json.dumps(video["snippet"]["thumbnails"]),
                    "preview_url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                }
            print(song)
            print("Fuzzy Search Album:\n")
            if artist_name_and_title_tuple is not None:
                fuzzy_match_album = match_artist_and_media(
                    "song",
                    artist_name_and_title_tuple[1],
                    artist_name_and_title_tuple[0],
                )
            else:
                fuzzy_match_album = match_artist_and_media(
                    "song", video["snippet"]["title"], video["snippet"]["channelTitle"]
                )

            if fuzzy_match_album["statusCode"] == 200:
                song = json.loads(fuzzy_match_album["body"])[0]
                print("Song Found:\n")
            else:
                song = json.loads(song_controller.create_song(song)["body"])
                print("Song Created:\n")
            print(song)
            print("\n")

            # # Link to Streaming Service
            streaming_service_link = {
                "streaming_service_id": streaming_service["streaming_service_id"],
                "media_id": song["song_id"],
                "external_id": video["id"]["videoId"],
                "external_url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
            }
            link = link_streaming_service_to_media(
                streaming_service_link=streaming_service_link, media_type="Song"
            )
            print(link)
            # Append new song to list
            song_list.append(song)
        song = json.loads(streaming_song["body"])

        print("Song Found:\n")
        print(song)
        print("\n")
        song_list.append(song)

    # Link artist to song
    for index, artist in enumerate(artists):
        link = artist_song_controller.link_artist_to_song(
            artist_id=artist["artist_id"], song_id=song_list[0]["song_id"], order=index
        )
        print("Song Artist Link Status:\n")
        print(link)
        print("\n")

    return song_list


def plugin_spotify(data_search_object, offset=0, limit=3):
    """
    Function to search for song in Spotify API
    and return {'status': 'Songs found: ' + song_id}'}
    """
    #     Function to search for song in Spotify API in try and catch
    #     and return {'status': 'Songs found: ' + song_id}'}
    print("\nSEARCHING SPOTIFY\n")
    try:
        print("Spotify Search Object:\n")
        print(data_search_object)
        # Create Spotify Streaming Service in Postgres DB if it doesn't exist
        streaming_service = get_streaming_services_by_name("Spotify")
        if streaming_service["body"] == "[]":
            streaming_service = create_streaming_service(
                {
                    "name": "Spotify",
                    "main_url": "https://open.spotify.com/",
                    "artwork": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/2048px-Spotify_logo_without_text.svg.png",
                }
            )

        streaming_service = json.loads(streaming_service["body"])[0]

        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

        # Spotify API
        spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

        if data_search_object["search_type"].lower() == "song":
            results = spotify.search(
                q=data_search_object["search_term"],
                type=["track", "artist", "album"],
                limit=limit,
                offset=offset,
                market="US",
            )

            results = results["tracks"]["items"]
            print("Spotify Results:\n")
            print(results)
            print("\n")
            search_results = []
            for result in results:

                # # Handle Albums from Spotify

                # print("album", json.loads(album['body']))

                # Handle Artists from Spotify
                artists = create_spotify_artists(
                    streaming_service=streaming_service,
                    artists=result["album"]["artists"],
                    spotify=spotify,
                )

                album = create_spotify_album(
                    streaming_service=streaming_service,
                    result=result,
                    spotify=spotify,
                    artists=artists,
                )

                # # Handle Songs from Spotify
                song = create_spotify_song(
                    streaming_service=streaming_service,
                    result=result,
                    album=album,
                    artists=artists,
                    spotify=spotify,
                )

                # Search Object to return
                new_search_object = {
                    "song": song,
                    "album": album,
                    "artists": artists,
                }
                print("Spotify Search Object:\n")
                print(new_search_object)

                search_results.append(new_search_object)

            return search_results
    except Exception as exception:
        print(exception)
        return {
            "status": f"Error searching for {data_search_object['search_type']}: "
            + str(exception)
        }


def create_spotify_album(streaming_service, result, spotify, artists):
    """
    ALBUMS
    """
    streaming_album = get_streaming_service_media_by_external_id(
        streaming_service["streaming_service_id"], result["album"]["uri"], "Album"
    )
    status_code = streaming_album["statusCode"]
    album = json.loads(streaming_album["body"])

    if status_code == 404:
        spotify_album = spotify.album(result["album"]["uri"])

        album = {
            "title": spotify_album["name"],
            "description": "",
            "released_date": spotify_album["release_date"],
            "artwork": json.dumps(spotify_album["images"]),
            "album_type": spotify_album["album_type"],
            "total_tracks": spotify_album["total_tracks"],
            "color": "red",
            "popularity": spotify_album["popularity"],
        }

        print("Fuzzy Search Album:\n")
        fuzzy_match_album = match_artist_and_media(
            "album", spotify_album["name"], spotify_album["artists"][0]["name"]
        )
        print(fuzzy_match_album)
        if fuzzy_match_album["statusCode"] == 200:

            album = json.loads(fuzzy_match_album["body"])[0]

            print("Album Found:\n")
        else:

            album = json.loads(album_controller.create_album(album)["body"])
            print("Album Created:\n")

        print(album)
        print("\n")

        streaming_service_link = {
            "streaming_service_id": streaming_service["streaming_service_id"],
            "media_id": album["album_id"],
            "external_id": spotify_album["uri"],
            "external_url": spotify_album["external_urls"]["spotify"],
        }

        link = link_streaming_service_to_media(
            streaming_service_link=streaming_service_link, media_type="Album"
        )

    print("Album Found:\n")
    print(album)
    print("\n")

    # Link artist to album
    for index, artist in enumerate(artists):
        link = artist_album_controller.link_artist_to_album(
            artist_id=artist["artist_id"], album_id=album["album_id"], order=index
        )
        print("Artist Album Link Status:\n")
        print(link)

    return album


def create_spotify_song(streaming_service, result, album, artists, spotify):
    """
    SONGS
    """
    spotify_song = spotify.track(result["uri"])

    # Create songs in Postgres DB if they don't exist
    streaming_song = get_streaming_service_media_by_external_id(
        streaming_service["streaming_service_id"], result["uri"], "Song"
    )

    status_code = streaming_song["statusCode"]
    song = json.loads(streaming_song["body"])

    if status_code == 404:
        song = {
            "title": spotify_song["name"],
            "description": "",
            "lyrics": [],
            "duration_ms": spotify_song["duration_ms"],
            "score": spotify_song["popularity"],
            "color": "red",
            "artwork": json.dumps(spotify_song["album"]["images"]),
            "released_date": spotify_song["album"]["release_date"],
            "popularity": spotify_song["popularity"],
            "preview_url": spotify_song["preview_url"],
        }

        print("Fuzzy Search Album:\n")
        fuzzy_match_album = match_artist_and_media(
            "song", spotify_song["name"], spotify_song["artists"][0]["name"]
        )
        print(fuzzy_match_album)
        if fuzzy_match_album["statusCode"] == 200:
            song = json.loads(fuzzy_match_album["body"])[0]
            print("Song Found:\n")
        else:
            song = json.loads(song_controller.create_song(song)["body"])
            print("Song Created:\n")
        print(song)
        print("\n")

        streaming_service_link = {
            "streaming_service_id": streaming_service["streaming_service_id"],
            "media_id": song["song_id"],
            "external_id": result["uri"],
            "external_url": result["external_urls"]["spotify"],
        }

        link = link_streaming_service_to_media(
            streaming_service_link=streaming_service_link, media_type="Song"
        )

        print(link)
        song = {**song, **streaming_service_link}

    print("Song Found:\n")
    print(song)
    print("\n")

    # Link artist to song
    for index, artist in enumerate(artists):
        link = artist_song_controller.link_artist_to_song(
            artist_id=artist["artist_id"], song_id=song["song_id"], order=index
        )
        print("Song Artist Link Status:\n")
        print(link)

    # Link song to album
    link = song_album_controller.link_song_to_album(
        song_id=song["song_id"],
        album_id=album["album_id"],
        order=result["track_number"],
    )
    print("\n")
    print("Song Album Link Status:\n")
    print(link)
    print("\n")

    return song


def create_spotify_artists(streaming_service, artists, spotify):
    """
    ARTISTS
    """

    artist_list = []

    for artist in artists:
        # search for artist in Spotify API using uri
        spotify_artist = spotify.artist(artist["uri"])
        streaming_artist = get_streaming_service_media_by_external_id(
            streaming_service["streaming_service_id"], spotify_artist["uri"], "Artist"
        )

        status_code = streaming_artist["statusCode"]

        if status_code == 404:

            # Create artist in Postgres DB if they don't exist
            new_artist = {
                "full_name": artist["name"],
                "biography": "",
                "artwork": json.dumps(spotify_artist["images"]),
                "popularity": spotify_artist["popularity"],
            }

            does_artist_exist = match_media("artist", new_artist["full_name"])

            if does_artist_exist["statusCode"] == 200:
                new_artist = json.loads(does_artist_exist["body"])[0]
                print("Artist Found:\n")
            else:
                new_artist = artist_controller.create_artist(new_artist)
                print("Artist Created:\n")

            print(new_artist)
            print("\n")

            # # Link to Streaming Service
            streaming_service_link = {
                "streaming_service_id": streaming_service["streaming_service_id"],
                "media_id": new_artist["artist_id"],
                "external_id": spotify_artist["uri"],
                "external_url": spotify_artist["external_urls"]["spotify"],
            }
            link = link_streaming_service_to_media(
                streaming_service_link=streaming_service_link, media_type="Artist"
            )
            print(link)
            # Append new artist to list
            artist_list.append(new_artist)

        else:
            # Loads streaming_artist into artist
            artist = json.loads(streaming_artist["body"])
            print("Artist Found:\n")
            print(artist)
            print("\n")
            artist_list.append(artist)

    return artist_list


def export_spotify_playlist(streaming_service, playlist):
    """
    PLAYLISTS
    """
    scope = "playlist-modify-public"
    username = "elbarros1996"

    token = SpotifyOAuth(scope=scope, username=username)
    sp = spotipy.Spotify(auth_manager=token)

    # Get external playlist

    streaming_playlist = get_streaming_service_media_by_external_id(
        streaming_service["streaming_service_id"],
        playlist["playlist_id"],
        "Playlist",
        "playlist_id",
    )
    print(streaming_playlist)
    status_code = streaming_playlist["statusCode"]
    print(status_code)
    if status_code == 404:
        # Create playlist in Spotify
        print("Creating Playlist in Spotify")
        spotify_playlist = sp.user_playlist_create(
            user=username,
            name=playlist["title"],
            public=True,
            description=playlist["description"],
        )
        spotify_playlist["external_id"] = spotify_playlist["id"]
        print(spotify_playlist)
        print("\n")

        streaming_service_link = {
            "streaming_service_id": streaming_service["streaming_service_id"],
            "media_id": spotify_playlist["playlist_id"],
            "external_id": spotify_playlist["id"],
            "external_url": spotify_playlist["external_urls"]["spotify"],
        }

        link = link_streaming_service_to_media(
            streaming_service_link=streaming_service_link, media_type="Playlist"
        )

        print("Streaming Service Link Status:\n")
        print(link)
        print("\n")

    else:
        # Loads streaming_playlist into playlist
        print("Playlist Found:\n")
        spotify_playlist = json.loads(streaming_playlist["body"])
        print(spotify_playlist)
        print("\n")

    # Get playlist songs
    playlist_songs = json.loads(
        playlist_controller.get_songs_from_playlist(playlist["playlist_id"])["body"]
    )
    spotify_playlist_songs = sp.playlist_tracks(spotify_playlist["external_id"])

    print("Playlist Songs:\n")
    print(playlist_songs)
    print("\n")

    print("Spotify Playlist Songs:\n")
    print(spotify_playlist_songs)
    print("\n")

    if "items" in spotify_playlist_songs:
        print("Spotify Playlist Songs Found:\n")
        playlist_track_ids = []
        for track in spotify_playlist_songs["items"]:
            if track["track"]["id"] not in playlist_track_ids:
                playlist_track_ids.append(track["track"]["id"])
        print(playlist_track_ids)
        sp.user_playlist_remove_all_occurrences_of_tracks(
            username, spotify_playlist["external_id"], playlist_track_ids
        )

    for song in playlist_songs:

        # Get external id for song
        streaming_song = get_streaming_service_media_by_external_id(
            streaming_service["streaming_service_id"],
            song["song_id"],
            "Song",
            "song_id",
        )
        status_code = streaming_song["statusCode"]
        print(status_code)
        # Check if song exists in Spotify, searches Spotify if not
        if status_code == 404:
            print("Song Not Found in Spotify")
            print("\n")
            loaded_song_artist = json.loads(
                artist_song_controller.get_artists_by_song(song["song_id"])["body"]
            )[0]
            print(loaded_song_artist)
            # loaded_artists = json.loads(song_controller.get_artists_from_song(song['song_id'])['body'])
            data_search_object = {
                "search_term": f"{loaded_song_artist['title']} {loaded_song_artist['full_name']}",
                "search_type": "Song",
            }
            print(data_search_object)
            # Search for song in Spotify
            external_id = json.loads(
                handle_external_search(
                    data_search_object=data_search_object, list_of_services=["Spotify"]
                )["body"]
            )[0]["song"]["external_id"]
            print(external_id)
            sp.playlist_add_items(
                playlist_id=spotify_playlist["external_id"], items=[external_id]
            )
            print("\n")
        else:
            print("Song Found in Spotify")
            streaming_song = json.loads(streaming_song["body"])
            print("\n")
            print(spotify_playlist)
            # Add song to playlist
            # print(streaming_song)
            sp.playlist_add_items(
                playlist_id=spotify_playlist["external_id"],
                items=[streaming_song["external_id"]],
            )
            print("\n")

    return playlist


# Function that links an Streaming_Service to an Media in a Postgres DB with the attributes by creating entry in junction table
# With external_id and external_url attribute
def link_streaming_service_to_media(
    streaming_service_link, media_type="Song",
):
    try:
        # Parse streaming_service_id, media_id, external_id, external_url from dict
        streaming_service_id = streaming_service_link["streaming_service_id"]
        media_id = streaming_service_link["media_id"]
        external_id = streaming_service_link["external_id"]
        external_url = streaming_service_link["external_url"]

        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = f"Streaming_Service_{media_type}"
            query = f'SELECT * FROM "{table}" WHERE streaming_service_id = {streaming_service_id} AND {media_type.lower()}_id = {media_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                return create_response(
                    409,
                    f"Streaming_Service {streaming_service_id} already linked to {media_type} {media_id}",
                )
            # Run SQL Query
            table = f'"Streaming_Service_{media_type}"'
            query = f"INSERT INTO {table} (streaming_service_id, {media_type.lower()}_id, external_url, external_id) VALUES ({streaming_service_id}, {media_id}, '{external_url}', '{external_id}');"
            cursor.execute(query)
            connection.commit()
            return create_response(
                200,
                f"Streaming_Service {streaming_service_id} linked to {media_type} {media_id} (id: {external_id})",
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def update_external_streaming_service_to_media(
    streaming_service_link, media_type="Song",
):
    try:
        # Parse streaming_service_id, media_id, external_id, external_url from dict
        streaming_service_id = streaming_service_link["streaming_service_id"]
        media_id = streaming_service_link["media_id"]
        external_id = streaming_service_link["external_id"]
        external_url = streaming_service_link["external_url"]

        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = f"Streaming_Service_{media_type}"
            query = f'SELECT * FROM "{table}" WHERE streaming_service_id = {streaming_service_id} AND {media_type.lower()}_id = {media_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404,
                    f"Streaming_Service {streaming_service_id} not linked to {media_type} {media_id}",
                )
            # Run SQL Query
            table = f"Streaming_Service_{media_type}"
            external_id = f"'{external_id}'"
            external_url = f"'{external_url}'"
            query = f'UPDATE "{table}" SET external_id = {external_id}, external_url = {external_url} WHERE streaming_service_id = {streaming_service_id} AND {media_type.lower()}_id = {media_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200,
                f"Streaming_Service {streaming_service_id} linked to {media_type} {media_id} (Order: {external_id})",
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def remove_link_streaming_service_to_media(streaming_service_id, media_id, media_type):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Check if row exists
            table = f"Streaming_Service_{media_type}"
            query = f'SELECT * FROM "{table}" WHERE streaming_service_id = {streaming_service_id} AND {media_type.lower()}_id = {media_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404,
                    f"Streaming_Service {streaming_service_id} not linked to {media_type} {media_id}",
                )
            # Run SQL Query
            table = f"Streaming_Service_{media_type}"
            query = f'DELETE FROM "{table}" WHERE streaming_service_id = {streaming_service_id} AND {media_type.lower()}_id = {media_id};'
            cursor.execute(query)
            connection.commit()
            return create_response(
                200,
                f"Streaming_Service {streaming_service_id} unlinked from {media_type} {media_id}",
            )
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


# print(remove_link_streaming_service_to_media(8, 2))
# Function that gets all Medias for an Streaming_Service in a Postgres DB using a junction
# and then returns all of the medias for that streaming_service (DOUBLE INNER JOIN)
def get_medias_by_streaming_service(streaming_service_id, media_type="Song"):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
            junction_table = f"Streaming_Service_{media_type}"
            second_table = f"{media_type}"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".streaming_service_id = "{junction_table}".streaming_service_id INNER JOIN "{second_table}" ON "{junction_table}".{media_type.lower()}_id = "{second_table}".{media_type.lower()}_id WHERE "{table}".streaming_service_id = {streaming_service_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(
                    404,
                    f"{media_type}s for Streaming_Service {streaming_service_id} not found",
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


# Function that gets all Medias for an Streaming_Service by streaming_service_id and external_id in a Postgres DB using a junction
# and then returns all of the songs for that streaming_service (DOUBLE INNER JOIN)
def get_streaming_service_media_by_external_id(
    streaming_service_id, external_id, media_type="Song", id_type="external_id",
):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = "Streaming_Service"
            junction_table = f"Streaming_Service_{media_type}"
            second_table = f"{media_type}"
            external_id = f"'{external_id}'"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".streaming_service_id = "{junction_table}".streaming_service_id INNER JOIN "{second_table}" ON "{junction_table}".{media_type.lower()}_id = "{second_table}".{media_type.lower()}_id WHERE "{table}".streaming_service_id = {streaming_service_id} AND "{junction_table}".{id_type} = {external_id};'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404,
                    f"{media_type} for Streaming_Service {streaming_service_id} with {id_type} {external_id} not found",
                )
            # convert row to dict from tuple
            row = dict(zip([column[0] for column in cursor.description], row))
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def get_streaming_services_by_media(media_id, media_type="Song"):
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = f"{media_type}"
            junction_table = f"Streaming_Service_{media_type}"
            second_table = "Streaming_Service"
            query = f'SELECT * FROM "{table}" INNER JOIN "{junction_table}" ON "{table}".{media_type.lower()}_id = "{junction_table}".{media_type.lower()}_id INNER JOIN "{second_table}" ON "{junction_table}".streaming_service_id = "{second_table}".streaming_service_id WHERE "{table}".{media_type.lower()}_id = {media_id};'
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                return create_response(
                    404, f"Streaming_Services for {media_type} {media_id} not found"
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


# Search Key for Media Type
SEARCH_KEY = {
    "song": "title",
    "artist": "full_name",
    "album": "title",
    "playlist": "title",
}


def match_artist_and_media(media_type, media_name, artist_name):
    """
    Function to match existing media in the database with
    the media name and artist name provided by the
    streaming service
    """
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = media_type.capitalize()
            media_name = media_name.replace("'", "''")
            artist_name = artist_name.replace("'", "''")
            query = f'SELECT * FROM "Artist" LEFT JOIN "Artist_{table}" ON "Artist".artist_id  = "Artist_{table}".artist_id LEFT JOIN "{table}" ON "Artist_{table}".{media_type.lower()}_id = "{table}".{media_type.lower()}_id  WHERE SIMILARITY("Artist".{SEARCH_KEY["artist"]}, \'{artist_name}\') > 0.4 AND SIMILARITY("{table}".{SEARCH_KEY[media_type]}, \'{media_name}\') > 0.4 ORDER BY "Artist".popularity ASC OFFSET 0 LIMIT 1;'
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404,
                    f"Streaming_Services for {media_type}: {media_name} - {artist_name} not found",
                )

            # convert row to dict from tuple
            row = [dict(zip([column[0] for column in cursor.description], row))]
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")


def match_media(media_type, media_name):
    """
    Function to match existing media in the database with
    the media name provided by the
    streaming service
    """
    try:
        connection = rds_connect()
        with connection.cursor() as cursor:
            # Run SQL Query
            table = media_type.capitalize()
            query = f"SELECT * FROM \"{table}\" WHERE SIMILARITY(LOWER({SEARCH_KEY[media_type]}), LOWER('{media_name}')) > 0.5 ORDER BY popularity ASC OFFSET 0 LIMIT 1;"
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return create_response(
                    404, f"Streaming_Services for {media_type}: {media_name} not found"
                )

            # convert row to dict from tuple
            row = [dict(zip([column[0] for column in cursor.description], row))]
            return create_response(200, row)
    except Exception as e:
        print(e)
        return create_response(432, f"Error in SQL Query {e}")

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


# Lambda handler function
def handler(event, context):

    if "requestContext" not in event:
        return create_response(400, event)

    if event["requestContext"]["http"]["method"] == "GET":

        if "queryStringParameters" in event:
            if "term" in event["queryStringParameters"]:
                response = handle_external_search(
                    event["queryStringParameters"]["term"]
                )

                return create_response(200, response)
            if "streaming_search_term" in event["queryStringParameters"]:
                service = "Spotify" if event["queryStringParameters"]["streaming_service_id"] == 52 else "YouTube"
                response = handle_external_search(
                    event["queryStringParameters"]["streaming_search_term"], [service]
                )

                return create_response(200, response)
            elif "song_id" in event["queryStringParameters"]:
                response = song_controller.get_song(
                    event["queryStringParameters"]["song_id"]
                )
                return create_response(200, response)
            elif "artists_for_song_id" in event["queryStringParameters"]:
                response = artist_song_controller.get_artists_by_song(
                    event["queryStringParameters"]["artists_for_song_id"]
                )
                return create_response(200, response)
            elif "albums_for_song_id" in event["queryStringParameters"]:
                response = song_album_controller.get_albums_by_song(
                    event["queryStringParameters"]["albums_for_song_id"]
                )
                return create_response(200, response)
            elif "external_url_for_song_id" in event["queryStringParameters"]:
                streaming_song = get_streaming_service_media_by_external_id(
                    52,
                    event["queryStringParameters"]["external_url_for_song_id"],
                    "Song",
                    "song_id",
                )
                streaming_song2 = get_streaming_service_media_by_external_id(
                    55,
                    event["queryStringParameters"]["external_url_for_song_id"],
                    "Song",
                    "song_id",
                )
                return create_response(200, [streaming_song, streaming_song2])
            elif "external_url_for_album_id" in event["queryStringParameters"]:
                streaming_song = get_streaming_service_media_by_external_id(
                    52,
                    event["queryStringParameters"]["external_url_for_album_id"],
                    "Album",
                    "album_id",
                )
                return create_response(200, streaming_song)
            elif "artist_id" in event["queryStringParameters"]:
                response = artist_controller.get_artist(
                    event["queryStringParameters"]["artist_id"]
                )
                return create_response(200, response)
            elif "album_id" in event["queryStringParameters"]:
                response = album_controller.get_album(
                    event["queryStringParameters"]["album_id"]
                )
                return create_response(200, response)
            elif "playlist_id" in event["queryStringParameters"]:
                response = playlist_controller.get_playlist(
                    event["queryStringParameters"]["playlist_id"]
                )
                return create_response(200, response)
            else:
                return create_response(400, "Bad Request")

    return create_response(400, "Bad Request")

