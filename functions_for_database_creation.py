# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 17:15:45 2023

@author: Robert
"""
import discogs_client
import re 
import time
from sql_queries import run_inserts, run_query, run_command
token = 'XHOfulIibqIxokieAdCmnqncmBxzCYZTgJQqgkHR'
#d = discogs_client.Client('Album Structure Academic Research : Retrieving original release tracklists for albums on Billboard Top 200', user_token=token)
d = discogs_client.Client('Acoustic Features Billboard Top 200 - Academic Research', user_token=token)
DB2 = 'new_music_database_Copy.db'


#%%
album_names_query = 'SELECT album_name, album_name_stripped, artist_stripped FROM albums'
album_names = run_query(DB2, album_names_query)


#%% Error handler lists

error_sl_list = []
error_pos_list = []
error_nl_list = []
error_maid_list = []
error_al_list = []

#%% search discogs and compare to our db

def search_discogs_compare_to_db(i, album_names, query_index, d = d, error_sl_list = error_sl_list, error_pos_list = error_pos_list, error_nl_list = error_nl_list, error_maid_list = error_maid_list, error_al_list = error_al_list):
    
    
    album_song_query = f'SELECT spotify_track_name, spotify_track_id FROM spotify_features WHERE cleaned_album_names == "{album_names.iloc[i]["album_name_stripped"]}" AND cleaned_artist_names == "{album_names.iloc[i]["artist_stripped"]}"'
    album_song_df = run_query(DB2, album_song_query)
    
    # Discogs API request
    if query_index == 0:
        results = d.search(album_names.iloc[i]['album_name'], artist=album_names.iloc[i]['artist_stripped'], type='master')
    elif query_index == 1:
        results = d.search(album_names.iloc[i]['album_name'], type='master')
    elif query_index == 2:
        results = d.search(album_names.iloc[i]['album_name'], artist=album_names.iloc[i]['artist_stripped'], type='release')
    else:
        results = d.search(album_names.iloc[i]['album_name'], type='release')

    # Add the tracklist to my result object
    results.page(1)[0].tracklist
    # retrieve and assign 'data' to variable
    album_data = results.page(1)[0].data
    # retrieve and assign discog ID to variable
    master_album_id = results.page(1)[0].id
    
    if query_index == 1:
        try:
            if master_album_id in error_maid_list[0][0]:
                print('YOU FOUND THE SAME ALBUM!')
                time.sleep(0.5)
                raise Exception('Move on to next Query type')
            else:
                pass
        except:
            pass
    elif query_index == 3:
        try:
            if master_album_id in error_maid_list[1][0]:
                print('YOU FOUND THE SAME ALBUM!')
                time.sleep(0.5)
                raise Exception('Move on to next Query type')
            else:
                pass
        except:
            pass
    else:
        pass
    
    # Set empty container for the lists of album_data results
    song_list = []
    position = []
    num_list = []
    master_album_id_list = []
    
    # Set an itterator to start at 1 for position
    count = 1
    
    # retrive and assign the title of the entry retrieved from Discogs
    retrieved_album_title = album_data['title']
    
    # Create the lists needed to compare 'album track lists' from the Discogs side
    for n in album_data['tracklist']:
        song_list.append(n['title'])
        position.append(n['position'])
        num_list.append(count)
        if query_index <=2:
           master_album_id_list.append('m' + str(master_album_id))
        else:
            master_album_id_list.append('r' + str(master_album_id))
        count += 1
    
    # Create a list of the track names from the spotify database (song_list above, but from my exisiting dataframe)
    # *** CHICKEN OR THE EGG!!!!  FUTURE CONSIDERATION FOR SPOTIFY PULLING SO THAT I CAN UTILIZE THIS CODE FOR LATER!!!
    dirty_list = [x for x in album_song_df['spotify_track_name']]
    
    # Create a counter so that I can itterate through the tracks in the comparison
    album_index = 0
    match_container = []
    
    dirty_list_bool = [False for x in dirty_list]
    
    # For loop to check if the songs in an track list pulled from discogs is the same as the one from spotify or visa versa
    for m, title in enumerate(dirty_list):
        if re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower()) in re.sub(r'[^a-zA-Z0-9]', '', title.lower()
      ) or re.sub(r'[^a-zA-Z0-9]', '', title.lower()) in re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'[^a-zA-Z0-9]', '', 
                                                                                     song_list[album_index].lower())):
            
            dirty_list_bool[m] = True                
            album_index +=1
            # This is the exit condition to create a second list of boolean statements
            if sum(dirty_list_bool) == len(song_list):
                album_index = 0
                match_container.append(dirty_list_bool)
                dirty_list_bool = [False for x in dirty_list]
                pass
        # If the name doesnt match, reset the counter to 0 and make the list fully false again.
        else:
            album_index = 0
            dirty_list_bool = [False for x in dirty_list]
            pass
       
    # If there are 2 or more lists in the resulting container, print a visual indicator, and move onto the next step
    if len(match_container) >= 2:
        #go to pergatory
        print('2 or more lists found!')
        return match_container, song_list, position, num_list, master_album_id_list, retrieved_album_title
    # If there is 1 lists in the resulting container, print a visual indicator, and move onto the next step
    elif len(match_container) == 1:
        print('The whole album was found!')
        return match_container, song_list, position, num_list, master_album_id_list, retrieved_album_title
    
    # If there is no match, append the lists created from Discogs onto a list container for potential later use in 
    # error logging.    
    else:
        # error_sl_list.append(song_list)
        # error_pos_list.append(position)
        # error_nl_list.append(num_list)
        # error_maid_list.append(master_album_id_list)
        # error_al_list.append(retrieved_album_title)
        
        #go to pergatory
        if query_index == 0:
            print("No Match found using the master, album, and artist query.")
        elif query_index == 1:
            print("No Match found using the master and album query.")
        elif query_index == 2:
            print("No Match found using the release, album, and artist query.")
        else:
            print("No Match found using the release and album query.")
        return match_container, song_list, position, num_list, master_album_id_list, retrieved_album_title
        # if query_index <= 3:
        #     query_index += 1
        #     time.sleep(0.5)
        #     raise Exception('Move on to next Query type')
            
#%%
i = 33
query_index = 0

#%%
(match_container, song_list, position, num_list, master_album_id_list, retrieved_album_title) = search_discogs_compare_to_db(i, album_names, query_index)

retrieved_album_title

#%%
master_album_id_list

#%%
match_container



