# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 12:05:00 2022

@author: Robert
"""
# Database conversion

from sql_queries import run_inserts, run_query, run_command
#from make_database import make_database

#%%
#make_database()

#%% THSE TABEL CREATION COMMANDS ARE FOR WHEN I NEED TO CREATE A LOOP TO GRAB STUFF FROM DISCOGS
c3 = """
CREATE TABLE original_discogs_album(
    discog_album_master_id TEXT PRIMARY KEY,
    track_name TEXT,
    track_position_id TEXT,
    track_index_position INTEGER,
    track_id INTEGER,
    FOREIGN KEY(track_id) REFERENCES songs(track_id)
);
"""

insert_query5 = '''
                INSERT OR IGNORE INTO  spotify_features(
                    discog_album_master_id,
                    track_name,
                    track_position_id,
                    track_index_position,
                    track_id
                    )
                VALUES (?, ?, ?, ?, ?)
                '''

something = ''                

update1 = f'''UPDATE albums
        SET discog_album_master_id = '{something}'
        WHERE
        album_id == '{something}'; '''


c6 = """
CREATE TABLE error_handler(
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    spotify_album_id TEXT,
    discog_album_master_id TEXT,
    discog_track_list TEXT
);
"""

#%% First I need to turn the acoustic_features into servicable song references
insert_query1 = '''
                INSERT OR IGNORE INTO  spotify_features(
                    spotify_track_id,
                    spotify_track_name,
                    spotify_album_name,
                    spotify_artist,
                    spotify_album_id,
                    release_date,
                    acousticness,
                    danceability,
                    duration_ms,
                    energy,
                    instrumentalness,
                    key,
                    liveness,
                    loudness,
                    mode,
                    speechiness,
                    tempo,
                    time_signatues,
                    valence
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
insert_query2 = '''
                INSERT OR IGNORE INTO  songs(
                    spotify_track_id
                    )
                VALUES (?)
                '''                

#%% Second I need to turn the albums (top 200 lists) into a referencable set of albums by original release format info
# When initially transfering the data to the new DB, there will not be querying the discogs api at the same time, so skip 'discog_album_master_id'
insert_query3 = '''
                INSERT OR IGNORE INTO  albums(
                    album_name,
                    album_name_stripped,
                    artist,
                    artist_stripped
                    )
                VALUES (?, ?, ?, ?)
                '''
                

insert_query4 = '''
                INSERT OR IGNORE INTO  top200_lists(
                    lists_id,
                    date,
                    rank,
                    album_id
                    )
                VALUES (?, ?, ?, ?)
                '''

#%% 
DB = 'billboard-200-with-segments_Copy.db'
query_album_name_df = 'SELECT * FROM albums'
albums_urrything = run_query(DB, query_album_name_df)

#%%
for i in range(3):
    print(albums_urrything.iloc[i])

#%%
lists_id = albums_urrything.iloc[i]['id']
date = albums_urrything.iloc[i]['date']
artist = albums_urrything.iloc[i]['artist']
album_name = albums_urrything.iloc[i]['album']
rank = albums_urrything.iloc[i]['rank']


#%%
DB2 = 'DATABASE.db'
#%%
albums_that_exsist_list = []
album_names_query = 'SELECT album_name FROM albums'
names = run_query(DB2, album_names_query)
#names.iloc[0]
for i in range(len(names.values.tolist())):
    albums_that_exsist_list.append(names.iloc[i].values.tolist()[0])
    
print(albums_that_exsist_list)
    
#album_database_list
#%%
names.values
#%%
for i in range(5):
    if albums_urrything.iloc[i]['album'] == None:
        pass
    else:
        if albums_urrything.iloc[i]['album'] in albums_that_exsist_list:
            pass
        else:
            album_name = albums_urrything.iloc[i]['album']
            artist = albums_urrything.iloc[i]['artist']
            print(album_name)
            print(artist)
            
            run_inserts(DB2, insert_query3, (album_name,artist))
            album_id_query = f'SELECT album_id FROM albums WHERE album_name == "{album_name}"'
            album_id_db = run_query(DB2, album_id_query)
            album_id = album_id_db.iloc[0].tolist()[0]
            print(album_id)
            
            lists_id = int(albums_urrything.iloc[i]['id'])
            date = albums_urrything.iloc[i]['date']
            rank = int(albums_urrything.iloc[i]['rank'])
            
            # print(type(date))
            # print(rank)
            
            run_inserts(DB2, insert_query4, (lists_id,date,rank, album_id))
            albums_that_exsist_list.append(album_name)
        

#%%
len(albums_urrything)
#%% Transfer the Top 200 table into the new table
DB = 'billboard-200-with-segments_Copy.db'
query_album_name_df = 'SELECT * FROM albums'
albums_urrything = run_query(DB, query_album_name_df)

DB2 = 'new_music_database.db'

albums_that_exsist_list = []
album_names_query = 'SELECT album_name FROM albums'
names = run_query(DB2, album_names_query)
#names.iloc[0]
# for i in range(len(names.values.tolist())):
#     albums_that_exsist_list.append(names.iloc[i].values.tolist()[0])
    
# print(albums_that_exsist_list)

for i in range(len(albums_urrything)):
#for i in range(10000):
    if albums_urrything.iloc[i]['album'] == None:
        pass
    else:
        #if "'" in albums_urrything.iloc[i]['album']:   
        album_name = albums_urrything.iloc[i]['album']
        album_name_stripped = album_name.replace('"','').replace("'","")
        artist = albums_urrything.iloc[i]['artist']
        artist_stripped = artist.replace('"','').replace("'","")
        
        current_item = album_name_stripped + artist_stripped
        
        #print(album_name)
        #print(artist)
        
        if current_item in albums_that_exsist_list:
            pass
        else:
            run_inserts(DB2, insert_query3, (album_name,album_name_stripped,artist,artist_stripped))
        
        try:
            album_id_query = f'SELECT album_id FROM albums WHERE album_name_stripped == "{album_name_stripped}" AND artist_stripped == "{artist_stripped}"'
            album_id_db = run_query(DB2, album_id_query)
            album_id = album_id_db.iloc[0].tolist()[0]
        
        #IDK WHY IT ERRORS OUT OF 'Artist' by 'A Boogie Wit Da Hoodie'
        except:
            album_id_query = 'SELECT album_id FROM albums'
            album_id_db = run_query(DB2, album_id_query)
            album_id = album_id_db.iloc[-1].tolist()[0]

        
        lists_id = int(albums_urrything.iloc[i]['id'])
        date = albums_urrything.iloc[i]['date']
        rank = int(albums_urrything.iloc[i]['rank'])
        
        # print(type(date))
        # print(rank)
        
        run_inserts(DB2, insert_query4, (lists_id,date,rank, album_id))
        
        albums_that_exsist_list.append(current_item)
        
        # else:
        #     album_name = albums_urrything.iloc[i]['album']
        #     artist = albums_urrything.iloc[i]['artist']
        #     #print(album_name)
        #     #print(artist)
            
        #     run_inserts(DB2, insert_query3, (album_name,artist))
        #     album_id_query = f"""SELECT album_id FROM albums WHERE album_name == '{album_name}'"""
        #     album_id_db = run_query(DB2, album_id_query)
        #     album_id = album_id_db.iloc[0].tolist()[0]
        #     #print(album_id)
            
        #     lists_id = int(albums_urrything.iloc[i]['id'])
        #     date = albums_urrything.iloc[i]['date']
        #     rank = int(albums_urrything.iloc[i]['rank'])
            
        #     # print(type(date))
        #     # print(rank)
            
        #     run_inserts(DB2, insert_query4, (lists_id,date,rank, album_id))
        #     sting = album_name + ' by ' + artist
        #     albums_that_exsist_list.append(sting)
        
#%%
DB = 'billboard-200-with-segments_Copy.db'
query_album_name_df = 'SELECT * FROM acoustic_features'
features_urrything = run_query(DB, query_album_name_df)

DB2 = 'new_music_database_Copy.db'
#%%

features_urrything.keys()

#%%
spotify_track_id = features_urrything['id']
spotify_track_name = features_urrything['song']
spotify_album_name = features_urrything['album']
spotify_artist = features_urrything['artist']
spotify_album_id = features_urrything['album_id']
release_date = features_urrything['date']
acousticness = features_urrything['acousticness']
danceability = features_urrything['danceability']
duration_ms = features_urrything['duration_ms']
energy = features_urrything['energy']
instrumentalness = features_urrything['instrumentalness']
key = features_urrything['key']
loudness = features_urrything['loudness']
liveness = features_urrything['liveness']
mode = features_urrything['mode']
speechiness = features_urrything['speechiness']
tempo = features_urrything['tempo']
time_signatues = features_urrything['time_signature']
valence = features_urrything['valence']

#%%
#loudness

#run_inserts(DB2, insert_query1, (spotify_track_id,spotify_track_name,spotify_album_name,spotify_artist,spotify_album_id,release_date,acousticness,danceability,duration_ms,energy,instrumentalness,key,liveness,mode,speechiness,tempo,time_signatues,valence))

#%%
len(features_urrything)
features_urrything.iloc[0]['id']
#%% insert features back into new database
for i in range(len(features_urrything)):
    spotify_track_id = features_urrything.iloc[i]['id']
    spotify_track_name = features_urrything.iloc[i]['song']
    spotify_album_name = features_urrything.iloc[i]['album']
    spotify_artist = features_urrything.iloc[i]['artist']
    spotify_album_id = features_urrything.iloc[i]['album_id']
    release_date = features_urrything.iloc[i]['date']
    acousticness = features_urrything.iloc[i]['acousticness']
    danceability = features_urrything.iloc[i]['danceability']
    duration_ms = features_urrything.iloc[i]['duration_ms']
    energy = features_urrything.iloc[i]['energy']
    instrumentalness = features_urrything.iloc[i]['instrumentalness']
    key = features_urrything.iloc[i]['key']
    loudness = features_urrything.iloc[i]['loudness']
    liveness = features_urrything.iloc[i]['liveness']
    mode = features_urrything.iloc[i]['mode']
    speechiness = features_urrything.iloc[i]['speechiness']
    tempo = features_urrything.iloc[i]['tempo']
    time_signatues = features_urrything.iloc[i]['time_signature']
    valence = features_urrything.iloc[i]['valence']
    
    run_inserts(DB2, insert_query1, (spotify_track_id,spotify_track_name,spotify_album_name,spotify_artist,spotify_album_id,release_date,acousticness,danceability,duration_ms,energy,instrumentalness,key,liveness,mode,speechiness,tempo,time_signatues,valence))

#%% Insert spotify ids to make song table
features_urrything['id']
for i in range(len(features_urrything)):
    spotify_track_id = features_urrything.iloc[i]['id']
    
    run_inserts(DB2, insert_query2, (spotify_track_id))
    
#%% MAKE A NEW ROW CALLED 'cleaned_album_names' so I can do the compare against discogs output.

command = '''ALTER TABLE spotify_features ADD cleaned_album_names TEXT;'''

run_command(DB2, command)
#%% MAKE A NEW ROW CALLED 'cleaned_album_names' so I can do the compare against discogs output.

command = '''ALTER TABLE spotify_features ADD cleaned_artist_names TEXT;'''

run_command(DB2, command)

#%%
album_names_query = 'SELECT spotify_track_id, spotify_album_name, spotify_artist FROM spotify_features'
albums_names = run_query(DB2, album_names_query)

#%%
albums_names
#%%
len(albums_names)

#%%
albums_names.iloc[0]['spotify_album_name']

#%%
add_stripped_names = ''' INSERT or REPLACE INTO spotify_features(spotify_track_id,cleaned_album_names,cleaned_artist_names)
                         VALUES(?,?,?) '''


#%%
# update = f'''UPDATE spotify_features
# SET cleaned_album_names = {album_name_stripped},
# cleaned_artist_names = {artist_stripped}
# WHERE
# spotify_track_id == {spotify_id} '''

# '''INSERT INTO spotify_features(cleaned_album_names,cleaned_artist_names)
# VALUES(1, 'Pancakes', 75, 'OK');'''

#%%
for i in range(len(albums_names)):
    dirty_album_name = albums_names.iloc[i]['spotify_album_name']
    album_name_stripped = dirty_album_name.replace('"','').replace("'","")
    artist = albums_names.iloc[i]['spotify_artist']
    artist_stripped = artist.replace('"','').replace("'","")
    spotify_id = albums_names.iloc[i]['spotify_track_id']
    
    update = f'''UPDATE spotify_features
        SET cleaned_album_names = '{album_name_stripped}',
        cleaned_artist_names = '{artist_stripped}'
        WHERE
        spotify_track_id == '{spotify_id}'; '''
    
    
    
    run_inserts(DB2, update,())
    

#%% MAKE A NEW ROW CALLED 'cleaned_album_names' so I can do the compare against discogs output.

command = '''ALTER TABLE original_discogs_album ADD artist_name TEXT;'''

run_command(DB2, command) 
   
    #%% MAKE A NEW ROW CALLED 'cleaned_album_names' so I can do the compare against discogs output.

command = '''ALTER TABLE original_discogs_album ADD cleaned_track_name TEXT;'''

run_command(DB2, command)    
    
        
#%%
import discogs_client
import time
import re
import logging
from api_keys import discogs_api_token as token
#d = discogs_client.Client('Album Structure Academic Research : Retrieving original release tracklists for albums on Billboard Top 200', user_token=token)
d = discogs_client.Client('Acoustic Features Billboard Top 200 - Academic Research', user_token=token)
DB2 = 'new_music_database_Copy.db'

#%% USE THIS AS A BASE TO DO THE DISCOGS QUERY AND ERROR HANDLING STUFF
DB2 = 'new_music_database_Copy.db'

album_names_query = 'SELECT album_name, album_name_stripped, artist_stripped FROM albums'
album_names = run_query(DB2, album_names_query)

for i in range(len(album_names)):
    try:
        results = d.search(album_names.iloc[i]['album_name'], artist=album_names.iloc[i]['artist_stripped'], type='master,release')
        results.page(1)[0].tracklist
    except:
        results = d.search(album_names.iloc[i]['album_name'], type='master,release')
        results.page(1)[0].tracklist

    album_data = results.page(1)[0].data
    
    master_album_id = results.page(1)[0].id
    
    # REMEMBER YOU NEED TO RUN THE CHECKS AND DECIDE IF YOU WANT TO SAVE IT TO THE ACTUAL DATAFRAME FIRST!
    # STOP TRYING TO REMOVE IT! LOL
    song_list = []
    position = []
    num_list = []
    master_album_id_list = []
    
    count = 1

    
    for n in album_data['tracklist']:
        song_list.append(n['title'])
        position.append(n['position'])
        num_list.append(count)
        master_album_id_list.append(master_album_id)
        count += 1

    #QUERY FOR THE SPOTIFY NAME!
    album_song_query = f'SELECT spotify_track_name, spotify_track_id FROM spotify_features WHERE cleaned_album_names == "{album_names.iloc[i]["album_name_stripped"]}" AND cleaned_artist_names == "{album_names.iloc[i]["artist_stripped"]}"'
    album_song_df = run_query(DB2, album_song_query)
    
    dirty_list = [x for x in album_song_df['spotify_track_name']]
    
    
    album_index = 0
    match_container = []

    dirty_list_bool = [False for x in dirty_list]
    
    for m, title in enumerate(dirty_list):
        if re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower()) in re.sub(r'[^a-zA-Z0-9]', '', title.lower()) or re.sub(r'[^a-zA-Z0-9]', '', title.lower()) in re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower())):
            dirty_list_bool[m] = True                
            #I need to figure out how to auto scale this parsing progression
            album_index +=1
            if sum(dirty_list_bool) == len(song_list):
                album_index = 0
                match_container.append(dirty_list_bool)
                dirty_list_bool = [False for x in dirty_list]
                pass
        else:
            #I want this list to clear every time it does not fully make an album track list match
            # break
            album_index = 0
            dirty_list_bool = [False for x in dirty_list]
            pass
        
    if len(match_container) == 2:
        #go to pergatory
        print('2 lists!')
    elif len(match_container) == 1:
        print('YEAAAAAA!!!! Thats the whole album!')
    else:
        #go to pergatory
        print("Boohoo! it wasn't a match!")
    
    #DO LONG SLEEP TO START SO I CAN JUST STOP IT WHILE TROUBLESHOOTING
    time.sleep(15)
        



#%% USE THIS AS A BASE TO DO THE DISCOGS QUERY AND ERROR HANDLING STUFF
# Queries for this section
insert_query5 = '''
                INSERT OR IGNORE INTO  original_discogs_songs(
                    discog_song_master_id,
                    track_name,
                    track_position_id,
                    track_index_position,
                    discog_album_master_id,
                    track_id
                    )
                VALUES (?, ?, ?, ?, ?, ?)
                '''
          

insert_query6 = '''
                INSERT OR IGNORE INTO  original_discogs_album(
                    discog_album_master_id,
                    discog_album_name
                    )
                VALUES (?, ?)
                '''               
               
                
insert_query7 = '''
                INSERT OR IGNORE INTO  error_discogs_albums(
                    error_discog_album_id,
                    album_id,
                    retrieved_name
                    )
                VALUES (?, ?, ?)
                '''                


insert_query8 = '''
                INSERT OR IGNORE INTO  error_discogs_songs(
                    error_discog_song_id,
                    track_name,
                    track_position_id,
                    track_index_position,
                    error_discog_album_id
                    )
                VALUES (?, ?, ?, ?, ?)
                '''                
                                
# Set up
logging.basicConfig(filename='transfer_log.log', filemode='w')
DB2 = 'new_music_database_Copy.db'

# Set the start point based on the exsiting database
# error_album_id_set_list for excluding NULLs in main Query
error_album_ids = 'SELECT album_id FROM error_discogs_albums'
error_album_id_set_list = run_query(DB2, error_album_ids)

error_ids = []
[error_ids.append(int(error_album_id_set_list.iloc[x])) for x in range(len(error_album_id_set_list))]

error_album_id_set_list = tuple(set(error_ids))


album_names_query = f'''SELECT album_id, album_name, album_name_stripped, artist_stripped FROM albums 
                        WHERE discog_album_master_id IS NULL 
                        AND album_id NOT IN {error_album_id_set_list}
                        '''
album_names = run_query(DB2, album_names_query)


# Reset auto incriment Text naming scheme
not_found_count = 0
not_found_df_query = "SELECT album_id FROM error_discogs_albums WHERE error_discog_album_id LIKE '%XXX%'"
not_found_df = run_query(DB2, not_found_df_query)
try:
    not_found_count = len(not_found_df)
except:
    pass


# album_names dataframe is going into a system of loops to query the discogs databse for tracklists to match to spotify_feature tracklists.
for i in range(len(album_names)):
   
    # Query for Spotify song name.
    searched_album_title = album_names.iloc[i]['album_name']
    
    # Query for album id (internal to our database from AUTOINCRIMENTATION)
    album_id_forerror = int(album_names.iloc[i]['album_id'])
    
    # Query for list of songs from spotify_features table by the name from the albums table (originally the name used to query these items from Spotify) 
    album_song_query = f'''SELECT spotify_track_name, spotify_track_id FROM spotify_features 
                           WHERE cleaned_album_names == "{album_names.iloc[i]["album_name_stripped"]}" 
                           AND cleaned_artist_names == "{album_names.iloc[i]["artist_stripped"]}"
                           '''
    album_song_df = run_query(DB2, album_song_query)
    
    error_sl_list = []
    error_pos_list = []
    error_nl_list = []
    error_maid_list = []
    error_al_list = []
    
    song_list = []
    match_container = []
    
    # During the next system of Try Except blocks until the "finally" block, we are querying discogs API using a mix of 'Album + Artist and Album'
    # and 'Master and Release' options.  The try/except block is used because if a search is over contrained (artist is 'various' and therefore)
    # when you go to index into the ".page(1)[0]", there is no 0th index and it raises an error to commence to the next attempt with different
    # contraints.
    try:
        # Discogs API request
        results = d.search(album_names.iloc[i]['album_name'], artist=album_names.iloc[i]['artist_stripped'], type='master')
        # Add the tracklist to my result object
        results.page(1)[0].tracklist
        # retrieve and assign 'data' to variable
        album_data = results.page(1)[0].data
        # retrieve and assign discog ID to variable
        master_album_id = results.page(1)[0].id
        
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
            master_album_id_list.append('m' + str(master_album_id))
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
            
        # If there is 1 lists in the resulting container, print a visual indicator, and move onto the next step
        elif len(match_container) == 1:
            print('The whole album was found!')
        
        # If there is no match, append the lists created from Discogs onto a list container for potential later use in 
        # error logging.    
        else:
            error_sl_list.append(song_list)
            error_pos_list.append(position)
            error_nl_list.append(num_list)
            error_maid_list.append(master_album_id_list)
            error_al_list.append(retrieved_album_title)
            #go to pergatory
            print("No Match found using the master, album, and artist query.")
            raise Exception('Move on to next Query type')
    except:
        try:
            results = d.search(album_names.iloc[i]['album_name'], type='master')
            results.page(1)[0].tracklist
            album_data = results.page(1)[0].data
            master_album_id = results.page(1)[0].id
            
            # REMEMBER YOU NEED TO RUN THE CHECKS AND DECIDE IF YOU WANT TO SAVE IT TO THE ACTUAL DATAFRAME FIRST!
            # STOP TRYING TO REMOVE IT! LOL
            song_list = []
            position = []
            num_list = []
            master_album_id_list = []
            
            count = 1
            
            retrieved_album_title = album_data['title']
            
            for n in album_data['tracklist']:
                song_list.append(n['title'])
                position.append(n['position'])
                num_list.append(count)
                master_album_id_list.append('m' + str(master_album_id))
                count += 1

            dirty_list = [x for x in album_song_df['spotify_track_name']]
            
            
            album_index = 0
            match_container = []

            dirty_list_bool = [False for x in dirty_list]
            
            for m, title in enumerate(dirty_list):
                if re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower()) in re.sub(r'[^a-zA-Z0-9]', '', title.lower()) or re.sub(r'[^a-zA-Z0-9]', '', title.lower()) in re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower())):
                    dirty_list_bool[m] = True                
                    #I need to figure out how to auto scale this parsing progression
                    album_index +=1
                    if sum(dirty_list_bool) == len(song_list):
                        album_index = 0
                        match_container.append(dirty_list_bool)
                        dirty_list_bool = [False for x in dirty_list]
                        pass
                else:
                    #I want this list to clear every time it does not fully make an album track list match
                    # break
                    album_index = 0
                    dirty_list_bool = [False for x in dirty_list]
                    pass
                
            if len(match_container) >= 2:
                #go to pergatory
                print('2 or more lists found!')
            elif len(match_container) == 1:
                print('The the whole album!')

            else:
                error_sl_list.append(song_list)
                error_pos_list.append(position)
                error_nl_list.append(num_list)
                error_maid_list.append(master_album_id_list)
                error_al_list.append(retrieved_album_title)
                #go to pergatory
                print("No Match found using the master and album query.")
                raise Exception('Move on to next Query type')
        except:
            try:
                results = d.search(album_names.iloc[i]['album_name'], artist=album_names.iloc[i]['artist_stripped'], type='release')
                results.page(1)[0].tracklist
                album_data = results.page(1)[0].data
                
                #IF I WANT THIS TO DO ANYTHING, IT NEEDS TO BE BETWEEN MASTERS OR RELEASES, NOT THE BEGINNING OF RELEASES.
                master_album_id = results.page(1)[0].id
                if master_album_id in error_maid_list[0][0]:
                    print('YOU FOUND THE SAME ALBUM!')
                    print("No Match found using the release and album query.")
                else:
                    
                    # REMEMBER YOU NEED TO RUN THE CHECKS AND DECIDE IF YOU WANT TO SAVE IT TO THE ACTUAL DATAFRAME FIRST!
                    # STOP TRYING TO REMOVE IT! LOL
                    song_list = []
                    position = []
                    num_list = []
                    master_album_id_list = []
                    
                    count = 1
                    
                    retrieved_album_title = album_data['title']
                    
                    
                    for n in album_data['tracklist']:
                        song_list.append(n['title'])
                        position.append(n['position'])
                        num_list.append(count)
                        master_album_id_list.append('r' + str(master_album_id))
                        count += 1
    
                    dirty_list = [x for x in album_song_df['spotify_track_name']]
                    
                    
                    album_index = 0
                    match_container = []
    
                    dirty_list_bool = [False for x in dirty_list]
                    
                    for m, title in enumerate(dirty_list):
                        if re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower()) in re.sub(r'[^a-zA-Z0-9]', '', title.lower()) or re.sub(r'[^a-zA-Z0-9]', '', title.lower()) in re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower())):
                            dirty_list_bool[m] = True                
                            #I need to figure out how to auto scale this parsing progression
                            album_index +=1
                            if sum(dirty_list_bool) == len(song_list):
                                album_index = 0
                                match_container.append(dirty_list_bool)
                                dirty_list_bool = [False for x in dirty_list]
                                pass
                        else:
                            #I want this list to clear every time it does not fully make an album track list match
                            # break
                            album_index = 0
                            dirty_list_bool = [False for x in dirty_list]
                            pass
                        
                    if len(match_container) >= 2:
                        #go to pergatory
                        print('2 or more lists found!')
                    elif len(match_container) == 1:
                        print('The whole album was found!')
                    else:
                        error_sl_list.append(song_list)
                        error_pos_list.append(position)
                        error_nl_list.append(num_list)
                        error_maid_list.append(master_album_id_list)
                        error_al_list.append(retrieved_album_title)
                        #go to pergatory
                        print("No Match found using the release, album, and artist query.")
                        raise Exception('YOU SUCK')
            except:
                    try:
                        results = d.search(album_names.iloc[i]['album_name'], type='release')
                        results.page(1)[0].tracklist
                        album_data = results.page(1)[0].data
                        
                        master_album_id = results.page(1)[0].id
                        
                        # REMEMBER YOU NEED TO RUN THE CHECKS AND DECIDE IF YOU WANT TO SAVE IT TO THE ACTUAL DATAFRAME FIRST!
                        # STOP TRYING TO REMOVE IT! LOL
                        song_list = []
                        position = []
                        num_list = []
                        master_album_id_list = []
                        
                        count = 1
                        
                        retrieved_album_title = album_data['title']
                        
                        retrieved_album_title = album_data['title']
                        
                        for n in album_data['tracklist']:
                            song_list.append(n['title'])
                            position.append(n['position'])
                            num_list.append(count)
                            master_album_id_list.append('r' + str(master_album_id))
                            count += 1
    
                        dirty_list = [x for x in album_song_df['spotify_track_name']]
                        
                        
                        album_index = 0
                        match_container = []
    
                        dirty_list_bool = [False for x in dirty_list]
                        
                        for m, title in enumerate(dirty_list):
                            if re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower()) in re.sub(r'[^a-zA-Z0-9]', '', title.lower()) or re.sub(r'[^a-zA-Z0-9]', '', title.lower()) in re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower())):
                                dirty_list_bool[m] = True                
                                #I need to figure out how to auto scale this parsing progression
                                album_index +=1
                                if sum(dirty_list_bool) == len(song_list):
                                    album_index = 0
                                    match_container.append(dirty_list_bool)
                                    dirty_list_bool = [False for x in dirty_list]
                                    pass
                            else:
                                #I want this list to clear every time it does not fully make an album track list match
                                # break
                                album_index = 0
                                dirty_list_bool = [False for x in dirty_list]
                                pass
                            
                        if len(match_container) >= 2:
                            #go to pergatory
                            print('2 or more lists!')
                        elif len(match_container) == 1:
                            print('The whole album was found.')
                        else:
                            error_sl_list.append(song_list)
                            error_pos_list.append(position)
                            error_nl_list.append(num_list)
                            error_maid_list.append(master_album_id_list)
                            error_al_list.append(retrieved_album_title)
                            #go to pergatory
                            print("No Match found using the release and album query.")
                            raise Exception('Move on to next Query type')
                    except:
                        try:
                            results = d.search(album_names.iloc[i]['album_name'], type='release')
                            results.page(1)[1].tracklist
                            album_data = results.page(1)[0].data
                            
                            master_album_id = results.page(1)[0].id
                            
                            # REMEMBER YOU NEED TO RUN THE CHECKS AND DECIDE IF YOU WANT TO SAVE IT TO THE ACTUAL DATAFRAME FIRST!
                            # STOP TRYING TO REMOVE IT! LOL
                            song_list = []
                            position = []
                            num_list = []
                            master_album_id_list = []
                            
                            count = 1
                            
                            retrieved_album_title = album_data['title']
                            
                            for n in album_data['tracklist']:
                                song_list.append(n['title'])
                                position.append(n['position'])
                                num_list.append(count)
                                master_album_id_list.append('r' + master_album_id)
                                count += 1
                            
                            dirty_list = [x for x in album_song_df['spotify_track_name']]
                            
                            
                            album_index = 0
                            match_container = []
        
                            dirty_list_bool = [False for x in dirty_list]
                            
                            for m, title in enumerate(dirty_list):
                                if re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower()) in re.sub(r'[^a-zA-Z0-9]', '', title.lower()) or re.sub(r'[^a-zA-Z0-9]', '', title.lower()) in re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'[^a-zA-Z0-9]', '', song_list[album_index].lower())):
                                    dirty_list_bool[m] = True                
                                    #I need to figure out how to auto scale this parsing progression
                                    album_index +=1
                                    if sum(dirty_list_bool) == len(song_list):
                                        album_index = 0
                                        match_container.append(dirty_list_bool)
                                        dirty_list_bool = [False for x in dirty_list]
                                        pass
                                else:
                                    #I want this list to clear every time it does not fully make an album track list match
                                    # break
                                    album_index = 0
                                    dirty_list_bool = [False for x in dirty_list]
                                    pass
                                
                            if len(match_container) >= 2:
                                #go to pergatory
                                print('2 or more lists!')
                            elif len(match_container) == 1:
                                print('YEAAAAAA!!!! Thats the whole album!')
                            else:
                                error_sl_list.append(song_list)
                                error_pos_list.append(position)
                                error_nl_list.append(num_list)
                                error_maid_list.append(master_album_id_list)
                                error_al_list.append(retrieved_album_title)
                                #go to pergatory
                                print("No Match found using the release and album query.")
                        except:
                            print('I GUESS ITS REALLY NOT THERE!')
    finally:
        if len(match_container) >= 2:
            #go to pergatory
            print('2 or more lists!')
            logging.warning(f"2 lists were presant for {album_names.iloc[i]['album_name']}")      
            
            #CREATE A LOG FILE THAT LOGS THE NO PULLS (ERROR TABLE ADDS) AND 2 LIST ADDS!
            
            run_inserts(DB2, insert_query6,(master_album_id_list[0],retrieved_album_title))
            
            for p in range(len(song_list)):
                
                track_name = song_list[p]
                track_position_id = position[p]
                track_index_position = num_list[p]
                discog_album_master_id = master_album_id_list[0]
                discog_song_master_id = master_album_id_list[0] + 'T' + str(track_index_position)

                spotify_track_id = album_song_df.iloc[p]['spotify_track_id']
                song_name_query = f'SELECT track_id FROM songs WHERE spotify_track_id == "{spotify_track_id}"'
                track_id_df = run_query(DB2, song_name_query)
                track_id = track_id_df.iloc[0].to_list()[0]
                
                run_inserts(DB2, insert_query5, (discog_song_master_id, track_name, track_position_id, track_index_position, discog_album_master_id, track_id))
                
            update1 = f'''UPDATE albums
                SET discog_album_master_id = '{master_album_id_list[0][0]}'
                WHERE
                album_id == '{album_names.iloc[i]['album_id']}'; '''
            run_inserts(DB2, update1,())
            #DONT FORGET TO MAKE A LOG!!!!!! DONT FORGET TO MAKE A LOG!!!!! DONT FORGET TO MAKE A LOG!!!!!
            
        elif len(match_container) == 1:
            print('The whole album was found.')
            
            run_inserts(DB2, insert_query6,(master_album_id_list[0],retrieved_album_title))
            
            for p in range(len(song_list)):
                
                track_name = song_list[p]
                track_position_id = position[p]
                track_index_position = num_list[p]
                discog_album_master_id = master_album_id_list[p]
                discog_song_master_id = master_album_id_list[p] + 'T' + str(track_index_position)
                spotify_track_id = album_song_df.iloc[p]['spotify_track_id']
                song_name_query = f'SELECT track_id FROM songs WHERE spotify_track_id == "{spotify_track_id}"'
                track_id_df = run_query(DB2, song_name_query)
                track_id = track_id_df.iloc[0].to_list()[0]
                run_inserts(DB2, insert_query5, (discog_song_master_id, track_name, track_position_id, track_index_position, discog_album_master_id, track_id))
                
            update1 = f'''UPDATE albums
                SET discog_album_master_id = '{master_album_id_list[0]}'
                WHERE
                album_id == '{album_names.iloc[i]['album_id']}'; '''
            run_inserts(DB2, update1,())

            
        else:
            logging.warning(f"No match found for {album_names.iloc[i]['album_name']}")      
        #Create a log message here to say adding X number of albums from discogs
            try:
                album_id_forerror = int(album_names.iloc[i]['album_id'])
                for q in range(len(error_sl_list)):
                    for r in range(len(error_sl_list[q])):
                        song = error_sl_list[q][r]
                        position = error_pos_list[q][r]
                        number = error_nl_list[q][r]
                        discog_album_id = error_maid_list[q][r] + "SEARCH" + str(album_id_forerror)
                        discog_song_id = discog_album_id + 'T' + str(number)
                        # searched_album_title is just a single string!!!! No need to loop! Just use!
                        retrieved_album_title = error_al_list[q]
                        
                        
                        run_inserts(DB2, insert_query7, (discog_album_id, album_id_forerror, retrieved_album_title))
                        run_inserts(DB2, insert_query8, (discog_song_id, song,position, number,discog_album_id))
            except:                      
                 
                 logging.warning(f"NO SEARCH RESULT RETRIEVED FOR ANY QUERY FOR ALBUM: {album_names.iloc[i]['album_name']}")  
                 discog_album_id = f"XXX{not_found_count}"
                 retrieved_album_title = 'NOT FOUND!!!'
                 run_inserts(DB2, insert_query7, (discog_album_id, album_id_forerror, retrieved_album_title))
                 not_found_count += 1
                 pass
                    
                    
            #go to pergatory
            print("No match found!")
        
        #if album name is not in the newly created table, create an error log entry
        
                
        print('idk')
    
    
    #DO LONG SLEEP TO START SO I CAN JUST STOP IT WHILE TROUBLESHOOTING
    time.sleep(7)
        


#%%



    
    