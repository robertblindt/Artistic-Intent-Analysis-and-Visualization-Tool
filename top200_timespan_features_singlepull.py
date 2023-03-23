import streamlit as st
from sql_queries import run_query
from lists import date_list
import pandas as pd
from scipy.interpolate import interp1d
import numpy as np
import plotly.graph_objects as go



DB = 'starting_music_database.db'


#Set page to widescreen mode and make main title
st.set_page_config(layout="wide")

date_start = st.selectbox('Please select a week start your query from.', date_list)

date_end = st.selectbox('Please select a week to end your query at.', date_list, index = 1000)

frequency = st.number_input('How frequently would you like to sample the top 200 list? (Weeks)', min_value = 1, value = 4, step = 1)

number_requested = st.number_input('How many albums would you like to sample from each top 200 list? ', min_value = 1, max_value = 200, value = 5, step = 1)

date_start_index = date_list.index(date_start)
date_end_index = date_list.index(date_end)

# MAKE A IF ELSE USING DATE NAMES TO SWITCH TO 150 *!!!!!!!!
date_start_id = date_start_index * 200 + 2
date_end_id = date_end_index * 200 + 201


date_span = date_list[date_start_index:date_end_index:frequency]

#THIS IS TO CHECK TO MAKE SURE THE LIST WAS SLICING CORRECTLY!
#st.write(date_span)


# This queries every single album, and not specifically the jumps in dates.  This pull is only 10 seconds for the whole data base, so I said 'good enough for now'
query_album_name_df = f"SELECT * FROM albums WHERE id >= {date_start_id} AND id <= {date_end_id} AND length > 3 AND length < 30 AND rank <= {number_requested}"
all_selected_album_ratings = run_query(DB, query_album_name_df)

# Shows the list of albums
#st.write(all_selected_album_ratings)

# Look at the output of a single dates top X.
#st.write(list(all_selected_album_ratings.loc[all_selected_album_ratings['date'] == date_span[0]]['album']))


#Get list of albums in a list
list_of_dates = []
list_of_dates = [list(all_selected_album_ratings.loc[all_selected_album_ratings['date'] == date_span[x]]['album']) for x in range(len(date_span))]

#st.write(list_of_dates)
#st.write(len(list_of_dates))
#[st.write(x) for x in list_of_dates]

# Unpack a list of song names from a list of lists.
list_of_song_names = []
for x in list_of_dates:
    for y in x:
        list_of_song_names.append(y)

#st.write(list_of_song_names)
#st.write(all_selected_album_ratings['album'])


# Query all the songs from the acoustic_features table
query_album_name_df = f"SELECT * FROM acoustic_features WHERE album IN {tuple(list_of_song_names)}"
all_the_song_features = run_query(DB, query_album_name_df)

# Shows the list of songs from all the albums selected
#st.write(all_the_song_features)


# Create a list of album names for each year
album_lists = []
for n in date_span:
    album_lists.append(all_selected_album_ratings.loc[all_selected_album_ratings['date'] == n]['album'])
#st.write(album_lists)

# Create time positions and append, create a list of the dataframes.
song_frames_for_duration = []
missing_albums = []

# reasample length
xnew = np.linspace(0, 1, num=600, endpoint=True)
sp_list_sampled = []
ac_list_sampled = []
dc_list_sampled = []
en_list_sampled = []
in_list_sampled = []
lv_list_sampled = []
va_list_sampled = []

for n in album_lists:
    songs_for_week = []

    sp_list = []
    ac_list = []
    dc_list = []
    en_list = []
    in_list = []
    lv_list = []
    va_list = []

    for i in n:
        single_album_features = all_the_song_features.loc[all_the_song_features['album'] == i]
        #Need to do the time % stuff here...
        #st.write(single_album_features)
        song_locations = []
        previous_time = 0
        #st.write(i)
        for s in single_album_features['duration_ms']:
            #st.write(s)
            if len(song_locations) == 0:
                song_locations.append(float(previous_time))
                previous_time = previous_time + s / 2
            else:
                previous_time = previous_time + s / 2
                song_locations.append(float(previous_time))
                previous_time = previous_time + s / 2
        #st.write(song_locations)
        try:
            total_time = song_locations[-1]
            new_list = [x / total_time for x in song_locations]
            single_album_features = single_album_features.reset_index(drop = True)
            single_album_features = pd.concat([single_album_features, pd.Series(new_list, name = 'doneness')], axis = 1)

            #st.write(single_album_features)
        except:
            missing_albums.append(i)
            continue

        sp_list.append(
            (interp1d(single_album_features['doneness'], single_album_features['speechiness'], kind='linear'))(xnew))
        ac_list.append(
            (interp1d(single_album_features['doneness'], single_album_features['acousticness'], kind='linear'))(xnew))
        dc_list.append(
            (interp1d(single_album_features['doneness'], single_album_features['danceability'], kind='linear'))(xnew))
        en_list.append((interp1d(single_album_features['doneness'], single_album_features['energy'], kind='linear'))(xnew))
        in_list.append(
            (interp1d(single_album_features['doneness'], single_album_features['instrumentalness'], kind='linear'))(xnew))
        lv_list.append((interp1d(single_album_features['doneness'], single_album_features['liveness'], kind='linear'))(xnew))
        va_list.append((interp1d(single_album_features['doneness'], single_album_features['valence'], kind='linear'))(xnew))


        #st.write(single_album_features)
        songs_for_week.append(single_album_features.loc[single_album_features['album'] == i])
    #st.write((sp_list))
    try:
        # LOOK HERE FOR THE TUPLE instead of LIST!!!!
        ac_list_ave = sum(ac_list) / (len(ac_list))
        ac_list_sampled.append(ac_list_ave)

        dc_list_ave = sum(dc_list) / (len(dc_list))
        dc_list_sampled.append(dc_list_ave)

        en_list_ave = sum(en_list) / (len(en_list))
        en_list_sampled.append(en_list_ave)

        in_list_ave = sum(in_list) / (len(in_list))
        in_list_sampled.append(in_list_ave)

        lv_list_ave = sum(lv_list) / (len(lv_list))
        lv_list_sampled.append(lv_list_ave)

        va_list_ave = sum(va_list) / (len(va_list))
        va_list_sampled.append(va_list_ave)

        sp_list_ave = sum(sp_list) / (len(sp_list))
        sp_list_sampled.append(sp_list_ave)

        song_frames_for_duration.append(songs_for_week)
        #st.write(song_frames_for_duration)

    except:
        pass
#st.write(ac_list_sampled)
xaxis = [i/600 for i in range(0,600)]
z1 = ac_list_sampled

fig = go.Figure(data=[
    go.Surface(x=(xaxis),
                y=date_span,
                z=z1),
                ])
fig.update_layout( title = f'Acousticness averages from {date_start} to {date_end} sampled at {frequency} weeks',
        scene = {
            'camera_eye': {"x": -2.25, "y": -1.5, "z": 1},
            "aspectratio": {"x": 1, "y": 2, "z": 1},
                    'xaxis_title':'Album Progression (0 start, 1 end)',
                    'yaxis_title':'Time',
                    'zaxis_title':'Cof'})


st.plotly_chart(fig)


z1 = dc_list_sampled

fig = go.Figure(data=[
    go.Surface(x=(xaxis),
               y=date_span,
               z=z1),
])
fig.update_layout( title = f'Danceability averages from {date_start} to {date_end} sampled at {frequency} weeks',
        scene = {
            'camera_eye': {"x": -2.25, "y": -1.5, "z": 1},
            "aspectratio": {"x": 1, "y": 2, "z": 1},
            'xaxis_title': 'Album Progression (0 start, 1 end)',
            'yaxis_title': 'Time',
            'zaxis_title': 'Cof'})


st.plotly_chart(fig)


z1 = en_list_sampled

fig = go.Figure(data=[
    go.Surface(x=(xaxis),
                y=date_span,
                z=z1),
                ])
fig.update_layout( title = f'Energy averages from {date_start} to {date_end} sampled at {frequency} weeks',
        scene = {
            'camera_eye': {"x": -2.25, "y": -1.5, "z": 1},
            "aspectratio": {"x": 1, "y": 2, "z": 1},
            'xaxis_title': 'Album Progression (0 start, 1 end)',
            'yaxis_title': 'Time',
            'zaxis_title': 'Cof'})


st.plotly_chart(fig)


z1 = in_list_sampled

fig = go.Figure(data=[
    go.Surface(x=(xaxis),
               y=date_span,
               z=z1),
])
fig.update_layout( title = f'Instrumentalness averages from {date_start} to {date_end} sampled at {frequency} weeks',
        scene = {
            'camera_eye': {"x": -2.25, "y": -1.5, "z": 1},
            "aspectratio": {"x": 1, "y": 2, "z": 1},
            'xaxis_title': 'Album Progression (0 start, 1 end)',
            'yaxis_title': 'Time',
            'zaxis_title': 'Cof'})


st.plotly_chart(fig)


z1 = lv_list_sampled

fig = go.Figure(data=[
    go.Surface(x=(xaxis),
               y=date_span,
               z=z1),
])
fig.update_layout( title = f'Liveness averages from {date_start} to {date_end} sampled at {frequency} weeks',
        scene = {
            'camera_eye': {"x": -2.25, "y": -1.5, "z": 1},
            "aspectratio": {"x": 1, "y": 2, "z": 1},
            'xaxis_title': 'Album Progression (0 start, 1 end)',
            'yaxis_title': 'Time',
            'zaxis_title': 'Cof'})


st.plotly_chart(fig)


z1 = sp_list_sampled

fig = go.Figure(data=[
    go.Surface(x=(xaxis),
               y=date_span,
               z=z1),
])
fig.update_layout( title = f'Speechiness averages from {date_start} to {date_end} sampled at {frequency} weeks',
        scene = {
            'camera_eye': {"x": -2.25, "y": -1.5, "z": 1},
            "aspectratio": {"x": 1, "y": 2, "z": 1},
            'xaxis_title': 'Album Progression (0 start, 1 end)',
            'yaxis_title': 'Time',
            'zaxis_title': 'Cof'})


st.plotly_chart(fig)


z1 = va_list_sampled

fig = go.Figure(data=[
    go.Surface(x=(xaxis),
               y=date_span,
               z=z1),
])
fig.update_layout( title = f'Valence averages from {date_start} to {date_end} sampled at {frequency} weeks',
        scene = {
            'camera_eye': {"x": -2.25, "y": -1.5, "z": 1},
            "aspectratio": {"x": 1, "y": 2, "z": 1},
            'xaxis_title': 'Album Progression (0 start, 1 end)',
            'yaxis_title': 'Time',
            'zaxis_title': 'Cof'})


st.plotly_chart(fig)
