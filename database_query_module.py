# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:36:02 2023

@author: Robert
"""
# Module: prepare_and_quantify

# Module for Database Query functions

from sql_queries import run_query 
import pandas as pd

DB = 'new_music_database_Copy.db'

#%% discogs_verified_albums_query(DB = DB)
#Query for discogs verified albums

def discogs_verified_albums_query(DB = DB):
    """
    Query the database for the album names attached to the artists' name that have a verified Discogs album master ID.

    Parameters:
    - DB: a database connection object

    Return Value:
    - artist_albums: a Pandas DataFrame containing album names and artist names for albums with a verified Discogs album master ID
    """
    # Query the database for the album names attached to that artists name.
    query_album_name_df = "SELECT album_name, artist FROM albums WHERE discog_album_master_id IS NOT NULL"
    artist_albums = run_query(DB, query_album_name_df)
    return artist_albums
 
#%% create_album_artist_display_list(artist_albums)
#Create a list of artist albums and names using an unlikely devider for display

def create_album_artist_display_list(artist_albums):
    """
    Creates a list of album and artist names for display in a multi-select form field.

    Parameters:
    - artist_albums: a Pandas DataFrame containing album names and artist names

    Return Value:
    - label_list: a list of strings representing album and artist names for display in a multi-select form field
    """
    label_list = []
    # Creates a list of labels for the multi-select
    for i in range(len(artist_albums)):
        album = artist_albums['album_name'].iloc[i]
        artist = artist_albums['artist'].iloc[i]
        label = f"{album} --- {artist}"
        label_list.append(label)
    
    return label_list

#%% split_and_query(album_select, DB = DB)
#Split the selected names and query for discog ID

def split_and_query(album_select, DB = DB):
    """
    Input:
    
    album_select: a list of strings where each string contains the album name and artist name separated by ' --- '.
    DB: a database object. Default value is the global variable named 'DB'.
    Output:
    
    retrieved_database: a pandas dataframe object. The dataframe contains the following columns:
        'track_id': an integer that represents the track id.
        'track_name': a string that represents the name of the track.
        'track_index_position': an integer that represents the position of the track in the album.
        'spotify_track_id': a string that represents the Spotify ID of the track.
        'spotify_album_name': a string that represents the name of the album in Spotify.
        'acousticness': a float that represents the acousticness of the track.
        'danceability': a float that represents the danceability of the track.
        'duration_ms': an integer that represents the duration of the track in milliseconds.
        'energy': a float that represents the energy of the track.
        'instrumentalness': a float that represents the instrumentalness of the track.
        'liveness': a float that represents the liveness of the track.
        'loudness': a float that represents the loudness of the track.
        'speechiness': a float that represents the speechiness of the track.
        'valence': a float that represents the valence of the track.
        'tempo': a float that represents the tempo of the track.
    """
    discog_id_list = []
    # Splits the names aparts and removes the problematic characters for doing an SQL query. Then queries.
    for j in album_select:
        split_names = j.split(' --- ')
        album_name = split_names[0]
        artist_name = split_names[1]
    
        album_name_stripped = album_name.replace('"', '').replace("'", "")
        artist_name_stripped = artist_name.replace('"', '').replace("'", "")
        query_discog_id_df = f"SELECT discog_album_master_id FROM albums WHERE album_name_stripped = '{album_name_stripped}' AND artist_stripped = '{artist_name_stripped}'"
        discog_id_df = run_query(DB, query_discog_id_df)
        discog_id = discog_id_df.iloc[0][0]
        discog_id_list.append(discog_id)
        
    # Handles the different query formats needed for one vs 2+ items. Also handles a 0 entry Error    
    if len(discog_id_list) == 1:
        query_song_list = f"SELECT track_id, track_name, track_index_position from original_discogs_songs WHERE discog_album_master_id == '{discog_id_list[0]}'"
        song_list = run_query(DB, query_song_list)
    elif len(discog_id_list) == 0:
        # I DONT KNOW WHAT TO DO HERE TO BE USEFUL!
        # Right now, it will just raise an unhandled error trying to do the next query
        pass
    else:
        query_song_list = f"SELECT track_id, track_name, track_index_position from original_discogs_songs WHERE discog_album_master_id IN {tuple(discog_id_list)}"
        song_list = run_query(DB, query_song_list)
    
    query_song_spotify_id = f"SELECT spotify_track_id from songs WHERE track_id IN {tuple(song_list['track_id'])}"
    spotify_song_ids = run_query(DB, query_song_spotify_id)
    
    songs_df = pd.concat([song_list, spotify_song_ids], axis = 1, join = 'inner')
    
    query_song_features = f"SELECT spotify_track_id, spotify_album_name, acousticness, danceability, duration_ms, energy, instrumentalness, liveness, loudness, speechiness, valence, " \
                          f"tempo from spotify_features WHERE spotify_track_id IN {tuple(spotify_song_ids['spotify_track_id'])}"
    spotify_features = run_query(DB, query_song_features)
    retrieved_database=pd.merge(spotify_features, songs_df)
    
    return retrieved_database


#%% 






