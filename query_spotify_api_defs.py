# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 13:23:43 2022

@author: Robert
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as grid_spec

from sql_queries import run_inserts, run_command, run_query

from api_keys import client_id, client_secret


#%% Create Connection

def create_connection():
    
    '''
    sp = create_connection()
    
    Creates connection to my spotify API app location
    '''
    
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id,
                                                          client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace = False
    return sp

#%% --- Action Above
sp = create_connection()
#%%
for n in range(6,11):
    print(n)
    
#%% Search specific album
# Do I need to make a quick short and long range one if I want to do a drop down quick view to select and then a 20 album view if you do a full search?
# Add limit command to def?
def search_album(album_name, mod = 0):
    
    '''
    
    '''
    
    if len(sys.argv) > 1:
        album_query = ' '.join(sys.argv[1:])
    else:
        album_query = str(album_name)
    
    results = sp.search(q=album_query, offset = mod, type = 'album')
    
    num_shown_results = []
    num_possible_results = []
    offset_num = []
    
    num_shown_results.append(results['albums']['limit'])
    num_possible_results.append(results['albums']['total'])
    offset_num.append(results['albums']['offset'] )   
    
    album_type = []
    uris = []
    names = []
    release_date = []
    total_tracks = []
    images = []
    album_id = []
    artists = []
    
    
    for i, t in enumerate(results['albums']['items']):
        #print(' ', i, t['name'])
        uris.append(t['uri'])
        names.append(t['name'])
        release_date.append(str(t['release_date']))
        total_tracks.append(t['total_tracks'])
        images.append(t['images'])
        album_type.append(t['album_type'])
        album_id.append(t['id'])
        artists.append(t['artists'][0]['name']) 
        
    current_album_results = pd.DataFrame({'Album Name':names, 'Release Date':release_date, 'Total Tracks':total_tracks, 
                                          'Album Type':album_type, 'Album Images':images, 'Album ID':album_id, 'URI':uris,'Artists Names':artists,
                                        })
    #create dataframe
    
    #return album_search_df
    #print(artists)
    return current_album_results
        
#%% --- Action Above
current_album_results=search_album("Pink Floyd")
#%% --- View Head
current_album_results.head()

#%% --- Query column and row
current_album_results['URI'][0]

#%% --- Instatiate as a list (as if it came out of the selector that needs to be made)
album_uri_list = [current_album_results['URI'][0]]

#%% Ask user to select the correct one(s) from 'radio' 
# NEED TO TAKE THE OUTPUT OF search_albums TO POPULATE INFO AND IMAGE.
# Loop back to select album by name at that point, have exit condition on that page
def select_albums(current_album_results):
    #Display the results of 'search_albums' and use a radio select to say which one(s) is the right one to use.
    #Return the URI for the data parse.
    #maybe use a loop to go back to a page that says ('insert request or pass' or something like that)
    
    
    album_uri_list = current_album_results['URI']


#%%
album_name_list = list(current_album_results['Album Name'])

#%% Input album to grab info on each song in album and create database of that albums data.
def parse_tracks_info_from_album(album_uri_list, album_names_list):
    
    """
    intakes a list of album URIs and outputs a dataframe of the tracks information and their audio features
    """
    
    
    for i, aid in enumerate(album_uri_list): 
        
        track_name = []
        album_name = []
        disc_number = []
        track_id = []
        artist_name = []
        track_num = []
        track_uri_list = []
        popularity = []
        duration = []
        
        alb_tracks=sp.album_tracks(aid)['items']
                
        # Loop through track id list to find audio features for each track
        for track in alb_tracks:
            
            track_name.append(track['name'])
            album_name.append(album_names_list[i])
            disc_number.append(track['disc_number'])
            track_id.append(track['id'])            
            track_num.append(track['track_number'])
            track_uri_list.append(track['uri'])
            artist_name.append([artist['name'] for artist in track['artists']])
            duration.append(track['duration_ms'])

            track_info = sp.track(track_id=track['uri'])
            popularity.append(track_info['popularity'])
    
        album_track_info_df_temp = pd.DataFrame({'Track Name':track_name, 'Artist Name':artist_name, 'Album Name': album_name, 'Track ID':track_id,
                                              'Disk Number':disc_number, 'Track Number':track_num, 'Popularity':popularity, 'Duration (ms)':duration, 'URI':track_uri_list,
                                               })
        try:    
            album_track_info_df = pd.concat([album_track_info_df, album_track_info_df_temp])
        except:
            album_track_info_df = album_track_info_df_temp
    
    #SHOULD RETURN DATAFRAME.  PLACE HOLDER WHILE CREATING THE SMALLER FUNCTIONS BEFORE WORKING OUT DATAFRAME        
    return album_track_info_df

#%% --- Create individual URI in a list for next function
album_track_info_df = parse_tracks_info_from_album(album_uri_list,album_name_list[0:2])

track_id_list = album_track_info_df['URI']
           
#%% Take Trake list and output song features
def audio_features_from_track_id_list(track_id_list):                
        
    # Create empty lists to store audio feature values
    danceability = []
    energy = []
    loudness = []
    speechiness = []
    instrumentalness = []
    liveness = []
    valence = []
    tempo = []
        
    # Parse for audio features from the list 'track_id_list' created in prior loop
    for tid in track_id_list:
            
        # Append selected values to corresponding lists
        try:
            audio_features = sp.audio_features(tid)
            danceability.append(audio_features[0]["danceability"])
            energy.append(audio_features[0]["energy"])
            loudness.append(audio_features[0]["loudness"])
            valence.append(audio_features[0]["valence"])
            tempo.append(audio_features[0]["tempo"])
            speechiness.append(audio_features[0]["speechiness"])
            instrumentalness.append(audio_features[0]["instrumentalness"])
            liveness.append(audio_features[0]["liveness"])
            
        
        # Error results if there are no features available. Use try/except to set value to 0 when there is an error
        except TypeError:
            danceability.append(0)
            energy.append(0)
            loudness.append(0)
            valence.append(0)
            tempo.append(0)
            speechiness.append(0)
            instrumentalness.append(0)
            liveness.append(0)
    
    album_list_song_features = pd.DataFrame({'Danceability':danceability, 'Energy':energy,
                                          'Loudness':loudness, 'Valence':valence, 'Tempo':tempo, 
                                           'Speechiness':speechiness, 'Instrumentalness':instrumentalness, 'Liveness':liveness#,'Track ID':tid, 
                                        })  
    return album_list_song_features

#%% --- Action Above
#track_id_list = ['']
album_list_song_features = audio_features_from_track_id_list(track_id_list)
album_list_song_features

    
#%% --- Crate one big dataframe with all the data
#new_df = pd.concat([album_track_info_df,album_list_song_features], axis = 1)
new_df = album_track_info_df.merge(album_list_song_features, left_index = True, right_index = True)
#new_df['Artist Name']
new_df

#%%
album_names_list = list([current_album_results['Album Name'][0]])


#%%
album=new_df.loc[new_df['Album Name'] == 'The Wall']

#%% Graph Popularity of the albums selected
# def popularity_graph(album_df):
#     plt.figure(figsize=(24, 8), dpi=100)
#     x = list(np.arange(0,len(album_df)))
#     plt.plot(x, album_df['Popularity'], label = 'Popularity')
#     plt.xlabel('Track Name')
#     plt.ylabel('Popularity')
#     plt.xticks(ticks = list(np.arange(len(album_df))), labels = list(album_df['Track Name']),rotation = 60)
#     plt.grid(True)
        
#%%

def popularity_graph(album_df):
    fig, ax = plt.subplots(figsize=(16,6))
    x = list(np.arange(0,len(album_df)))
    ax.plot(x, album_df['Popularity'], label = 'Popularity')
    ax.set_xlabel('Track Name')
    ax.set_ylabel('Popularity')
    ax.set_xticks(ticks = list(np.arange(len(album_df))), labels = list(album_df['Track Name']),rotation = 90)
    ax.grid(True)
    return fig

#%%
# Plotly gives a more interavive graph.  Does the checkbox thing
def audio_features_graph(album_df):
    fig, ax = plt.subplots(figsize=(16,6))
    x = list(np.arange(0,len(album_df)))
    ax.plot(x, album_df['Danceability'], label = 'Danceability')
    ax.plot(x, album_df['Energy'], label = 'Energy')
    ax.plot(x, album_df['Valence'], label = 'Valence')
    ax.plot(x, album_df['Speechiness'], label = 'Speechiness')
    ax.plot(x, album_df['Instrumentalness'], label = 'Instrumentalness')
    ax.plot(x, album_df['Liveness'], label = 'Liveness')
    ax.set_xticks(ticks = list(np.arange(len(album_df))), labels = list(album_df['Track Name']),rotation = 90)
    ax.set_xlabel('Track Name')
    ax.set_ylabel('Coeffient')
    ax.legend()
    ax.grid(True)
    return fig
    
    
#%%
def tempo_graph(album_df):
    fig, ax = plt.subplots(figsize=(16,6))
    x = list(np.arange(0,len(album_df)))
    ax.plot(x, album_df['Tempo'], label = 'Tempo')
    ax.set_xlabel('Track Number')
    ax.set_ylabel('Tempo (BPM)')
    ax.set_xticks(ticks = list(np.arange(len(album_df))), labels = list(album_df['Track Name']),rotation = 90)
    ax.grid(True)
    return fig



#%% RIDGELINE 
def plot_feature_ridgeline(single_week_albums_only_features, single_week_album_rating, n, date_select):
    features = ['acousticness', 'danceability','energy', 'instrumentalness',
            'liveness','speechiness', 'valence']
    gs = (grid_spec.GridSpec(len(features),1))
    
    colors = ['blueviolet', 'hotpink','royalblue', 'lime', 'brown', 'darkorange', 'red']
    
    fig = plt.figure(figsize=(8,6))
    
    i = 0
    
    #creating empty list
    ax_objs = []
    
    for feature in features:        
        
        ax_objs.append(fig.add_subplot(gs[i:i+1, 0:]))
    
        # plotting the distribution
        plot = (single_week_albums_only_features[feature].plot(ax=ax_objs[-1],color=colors[i], lw=0.75) # white line '#f0f0f0'  Hard line same color: colors[i]
                )
        
    
        # grabbing x and y data from the kde plot - NOT A KDE ANYMORE SO WHAT DOES IT DO?
        x = plot.get_children()[0]._x
        y = plot.get_children()[0]._y
    
        # filling the space beneath the distribution
        ax_objs[-1].fill_between(x,y,facecolor=colors[i], alpha = .25)
    
        # setting uniform x and y lims
        ax_objs[-1].set_xlim(0, len(single_week_albums_only_features)-1)
        ax_objs[-1].set_ylim(0,1)
        gs.update(hspace= -0.75)
        # make background transparent
        rect = ax_objs[-1].patch
        rect.set_alpha(0)
        
        # remove borders, axis ticks, and labels
        ax_objs[-1].set_yticklabels([])
        ax_objs[-1].set_ylabel('')
        ax_objs[-1].tick_params(left = False, bottom = False)
    
        
        if i == len(features)-1:
            ax_objs[-1].set_xticks(ticks = list(np.arange(len(single_week_albums_only_features))), labels = list(single_week_albums_only_features['song']),rotation = 90)
        else:
            ax_objs[-1].set_xticklabels([])
        
        spines = ["top","right","left","bottom"]
        for s in spines:
            ax_objs[-1].spines[s].set_visible(False)
            
        
        #feature = feature.replace(" ","\n")
        ax_objs[-1].text(-0.02,0,feature.capitalize(),fontweight="bold",fontsize=10,ha="center", color= colors[i])
        i += 1
        
    ax_objs[1].set_title(f"#{single_week_album_rating.iloc[n]['rank']} rated song from {date_select}\n" + single_week_album_rating['album'][n] + ' by ' + single_week_album_rating['artist'][n])
        
    
    
    
    #plt.tight_layout()
    return fig

#%%
DB = 'billboards-200-with-segments.db'
#%% NAHHHHT USED!!!!
#  MAYBE LOOK AT THIS LATER?
def unify_time_and_average(album_list, DB = DB):
    features = ['acousticness', 'danceability','energy', 'instrumentalness',
            'liveness','speechiness', 'valence']
    
    for n in album_list:
        query_album_name_df = f'SELECT * FROM acoustic_features WHERE album == "{album_list[n]}"'
        single_week_albums_only_features = run_query(DB, query_album_name_df)
        
        for feature in features:
            single_week_albums_only_features[feature]
        





