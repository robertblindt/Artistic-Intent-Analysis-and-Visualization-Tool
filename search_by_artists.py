import streamlit as st
from sql_queries import run_query
from lists import artist_list as al
import pandas as pd
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid_spec
import plotly.graph_objects as go



DB = 'billboard-200-with-segments_Copy.db'


#Set page to widescreen mode and make main title
st.set_page_config(layout="wide")

artist_list = st.multiselect('Select the artist you would like to look at.',al)

if len(artist_list) == 0:
    st.write('No Artist Selected')
elif len(artist_list) == 1:
    word = artist_list[0]
    query_album_name_df = f"SELECT * FROM albums WHERE artist = '{word}'"
    all_instances_of_artists_attendance = run_query(DB, query_album_name_df)

    query_album_name_df = f"SELECT * FROM acoustic_features WHERE artist = '{word}'"
    all_rated_song_features = run_query(DB, query_album_name_df)
else:
    query_album_name_df = f"SELECT * FROM albums WHERE artist IN {tuple(artist_list)}"
    all_instances_of_artists_attendance = run_query(DB, query_album_name_df)

    query_album_name_df = f"SELECT * FROM acoustic_features WHERE artist IN {tuple(artist_list)}"
    all_rated_song_features = run_query(DB, query_album_name_df)

missing_albums = []

sp_ave_list = []
ac_ave_list = []
dc_ave_list = []
en_ave_list = []
in_ave_list = []
lv_ave_list = []
va_ave_list = []

try:
    for x in artist_list:
        band_album_df = all_rated_song_features.loc[all_rated_song_features['artist'] == x]
        band_album_list = list(set(band_album_df['album']))

        #st.write(band_album_list)
            # for y in band_album_list:
            #     artist_album_df = all_rated_song_features.loc[all_rated_song_features['album'] == y]

        xnew = np.linspace(0, 1, num=600, endpoint=True)
        sp_list = []
        ac_list = []
        dc_list = []
        en_list = []
        in_list = []
        lv_list = []
        va_list = []
        for i in band_album_list:

            single_album_features = band_album_df.loc[band_album_df['album'] == i]
            # Need to do the time % stuff here...
            # st.write(single_album_features)
            song_locations = []
            previous_time = 0
            # st.write(i)
            for s in single_album_features['duration_ms']:
                # st.write(s)
                if len(song_locations) == 0:
                    song_locations.append(float(previous_time))
                    previous_time = previous_time + s / 2
                else:
                    previous_time = previous_time + s / 2
                    song_locations.append(float(previous_time))
                    previous_time = previous_time + s / 2
            # st.write(song_locations)
            try:
                total_time = song_locations[-1]
                new_list = [x / total_time for x in song_locations]
                single_album_features = single_album_features.reset_index(drop=True)
                single_album_features = pd.concat([single_album_features, pd.Series(new_list, name='doneness')],
                                                  axis=1)

                # st.write(single_album_features)
            except:
                missing_albums.append(s)
                continue

            sp_list.append(
                (interp1d(single_album_features['doneness'], single_album_features['speechiness'], kind='linear'))(
                    xnew))
            ac_list.append(
                (interp1d(single_album_features['doneness'], single_album_features['acousticness'], kind='linear'))(
                    xnew))
            dc_list.append(
                (interp1d(single_album_features['doneness'], single_album_features['danceability'], kind='linear'))(
                    xnew))
            en_list.append(
                (interp1d(single_album_features['doneness'], single_album_features['energy'], kind='linear'))(xnew))
            in_list.append(
                (interp1d(single_album_features['doneness'], single_album_features['instrumentalness'],
                          kind='linear'))(xnew))
            lv_list.append(
                (interp1d(single_album_features['doneness'], single_album_features['liveness'], kind='linear'))(
                    xnew))
            va_list.append(
                (interp1d(single_album_features['doneness'], single_album_features['valence'], kind='linear'))(
                    xnew))
            #st.write(single_album_features)
        top_columns = ('col1', 'col2', 'col3')
        top_columns = st.columns(3)

        with top_columns[0]:
            fig, ax = plt.subplots()
            for i, s in enumerate(ac_list):
                ax = plt.plot(ac_list[i], color='pink')
            ac_list_ave = sum(ac_list) / (len(ac_list))
            ac_ave_list.append(ac_list_ave)
            ax = plt.plot(ac_list_ave, color='red')
            ax = plt.title(
                f'"Acousticness" progression on an Album by "{x}"\nthat was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
            st.pyplot(fig)

        with top_columns[1]:
            fig, ax = plt.subplots()
            for i, s in enumerate(dc_list):
                ax = plt.plot(dc_list[i], color='pink')
            dc_list_ave = sum(dc_list) / (len(dc_list))
            dc_ave_list.append(dc_list_ave)
            ax = plt.plot(dc_list_ave, color='red')
            ax = plt.title(
                f'"Danceability" progression on an Album by "{x}"\nthat was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
            st.pyplot(fig)

        with top_columns[2]:
            fig, ax = plt.subplots()
            for i, s in enumerate(en_list):
                ax = plt.plot(en_list[i], color='pink')
            en_list_ave = sum(en_list) / (len(en_list))
            en_ave_list.append(en_list_ave)
            ax = plt.plot(en_list_ave, color='red')
            ax = plt.title(
                f'"Energy" progression on an Album by "{x}"\nthat was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
            st.pyplot(fig)

        bottom_columns = ('col1', 'col2', 'col3', 'col4')
        bottom_columns = st.columns(4)

        with bottom_columns[0]:
            fig, ax = plt.subplots()
            for i, s in enumerate(in_list):
                ax = plt.plot(in_list[i], color='pink')
            in_list_ave = sum(in_list) / (len(in_list))
            in_ave_list.append(in_list_ave)
            ax = plt.plot(in_list_ave, color='red')
            ax = plt.title(
                f'"Instrumentalness" progression on an Album by "{x}"\nthat was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
            st.pyplot(fig)

        with bottom_columns[1]:
            fig, ax = plt.subplots()
            for i, s in enumerate(lv_list):
                ax = plt.plot(lv_list[i], color='pink')
            lv_list_ave = sum(lv_list) / (len(lv_list))
            lv_ave_list.append(lv_list_ave)
            ax = plt.plot(lv_list_ave, color='red')
            ax = plt.title(
                f'"Liveness" progression on an Album by "{x}"\nthat was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
            st.pyplot(fig)

        with bottom_columns[2]:
            fig, ax = plt.subplots()
            for i, s in enumerate(sp_list):
                ax = plt.plot(sp_list[i], color='pink')
            sp_list_ave = sum(sp_list) / (len(sp_list))
            sp_ave_list.append(sp_list_ave)
            ax = plt.plot(sp_list_ave, color='red')
            ax = plt.title(
                f'"Speechiness" progression on an Album by "{x}"\nthat was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
            st.pyplot(fig)

        with bottom_columns[3]:
            fig, ax = plt.subplots()
            for i, s in enumerate(va_list):
                ax = plt.plot(va_list[i], color='pink')
            va_list_ave = sum(va_list) / (len(va_list))
            va_ave_list.append(va_list_ave)
            ax = plt.plot(va_list_ave, color='red')
            ax = plt.title(
                f'"Valence" progression on an Album by "{x}"\nthat was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
            st.pyplot(fig)

        # PLOTLY RIDGELINE DOES NOT WORK!
        # import plotly.graph_objects as go
        # from plotly.colors import n_colors
        # import numpy as np
        #
        # # 12 sets of normal distributed random data, with increasing mean and standard deviation
        # data = (ac_list)  # ,ac_list,dc_list,en_list,in_list,lv_list,va_list)
        # data_len = len(data)
        # colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', data_len, colortype='rgb')
        # fig = go.Figure()
        # for data_line, color in zip(data, colors):
        #     fig.add_trace(go.Violin(x=data_line, line_color=color))
        #
        # fig.update_traces(orientation='h', side='positive', width=3, points=False)
        # fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False)
        # st.plotly_chart(fig)


    #st.write(all_instances_of_artists_attendance)
    #st.write(all_rated_song_features)
except:
    pass

lege_for_aves = artist_list
lege_for_aves.append('Average')

top_columns = ('col1', 'col2', 'col3')
top_columns = st.columns(3)
ave_for_ridge = []
with top_columns[0]:
    fig, ax = plt.subplots()
    for i, s in enumerate(ac_ave_list):
        ax = plt.plot(ac_ave_list[i], lw = 0.75)
    ac_list_ave_ave = sum(ac_ave_list) / (len(ac_ave_list))
    ave_for_ridge.append(ac_list_ave_ave)
    ax = plt.plot(ac_list_ave_ave, lw = 2.5)
    ax = plt.legend(lege_for_aves)
    ax = plt.title(
        f'"Acousticness" progression on an Artists Discography by the\ngroup selected that was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
    st.pyplot(fig)

with top_columns[1]:
    fig, ax = plt.subplots()
    for i, s in enumerate(dc_ave_list):
        ax = plt.plot(dc_ave_list[i], lw = 0.75)
    dc_list_ave_ave = sum(dc_ave_list) / (len(dc_ave_list))
    ave_for_ridge.append(dc_list_ave_ave)
    ax = plt.plot(dc_list_ave_ave, lw = 2.5)
    ax = plt.legend(lege_for_aves)
    ax = plt.title(
        f'"Dancability" progression on an Artists Discography by the\ngroup selected that was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
    st.pyplot(fig)

with top_columns[2]:
    fig, ax = plt.subplots()
    for i, s in enumerate(en_ave_list):
        ax = plt.plot(en_ave_list[i], lw = 0.75)
    en_list_ave_ave = sum(en_list) / (len(en_list))
    ave_for_ridge.append(en_list_ave_ave)
    ax = plt.plot(en_list_ave_ave, lw = 2.5)
    ax = plt.legend(lege_for_aves)
    ax = plt.title(
        f'"Energy" progression on an Artists Discography by the\ngroup selected that was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
    st.pyplot(fig)

top_columns = ('col1', 'col2', 'col3', 'col4')
top_columns = st.columns(4)

with top_columns[0]:
    fig, ax = plt.subplots()
    for i, s in enumerate(in_ave_list):
        ax = plt.plot(in_ave_list[i], lw = 0.75)
    in_list_ave_ave = sum(in_ave_list) / (len(in_ave_list))
    ave_for_ridge.append(in_list_ave_ave)
    ax = plt.plot(in_list_ave_ave, lw = 2.5)
    ax = plt.legend(lege_for_aves)
    ax = plt.title(
        f'"Instrumentalness" progression on an Artists Discography by the\ngroup selected that was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
    st.pyplot(fig)

with top_columns[1]:
    fig, ax = plt.subplots()
    for i, s in enumerate(lv_ave_list):
        ax = plt.plot(lv_ave_list[i], lw = 0.75)
    lv_list_ave_ave = sum(lv_ave_list) / (len(lv_ave_list))
    ave_for_ridge.append(lv_list_ave_ave)
    ax = plt.plot(lv_list_ave_ave, lw = 2.5)
    ax = plt.legend(lege_for_aves)
    ax = plt.title(
        f'"Liveness" progression on an Artists Discography by the\ngroup selected that was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
    st.pyplot(fig)

with top_columns[2]:
    fig, ax = plt.subplots()
    for i, s in enumerate(sp_ave_list):
        ax = plt.plot(sp_ave_list[i], lw = 0.75)
    sp_list_ave_ave = sum(sp_ave_list) / (len(sp_ave_list))
    ave_for_ridge.append(sp_list_ave_ave)
    ax = plt.plot(sp_list_ave_ave, lw = 2.5)
    ax = plt.legend(lege_for_aves)
    ax = plt.title(
        f'"Speechiness" progression on an Artists Discography by the\ngroup selected that was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
    st.pyplot(fig)

with top_columns[3]:
    fig, ax = plt.subplots()
    for i, s in enumerate(va_ave_list):
        ax = plt.plot(va_ave_list[i], lw = 0.75)
    va_list_ave_ave = sum(va_ave_list) / (len(va_ave_list))
    ave_for_ridge.append(va_list_ave_ave)
    ax = plt.plot(va_list_ave_ave, lw = 2.5)
    ax = plt.legend(lege_for_aves)
    ax = plt.title(
        f'"Valence" progression on an Artists Discography by the\ngroup selected that was on the Billboard top 200 Albums list \n Pink = Cloud of songs, Red = Average')
    st.pyplot(fig)

#st.write(ave_for_ridge)
features = ['acousticness', 'danceability', 'energy', 'instrumentalness',
            'liveness', 'speechiness', 'valence']
