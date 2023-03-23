import streamlit as st
import pandas as pd
from query_spotify_api_defs import create_connection, search_album, parse_tracks_info_from_album, audio_features_from_track_id_list, popularity_graph, audio_features_graph, tempo_graph

#Set page to widescreen mode and make main title
st.set_page_config(layout="wide")
st.title("Query Spotify's API to output album songs feature data.")

#Create empty list to be used to keep track of albums you want to query (NEEDS TO BE ADDRESSED!)
albums_to_compare = []

#Make container that requests text input for Query
with st.container():
    album_query = st.text_input('What is the name of the album you would like to add to your database to compare?')
    st.write('If the album happens to have a common name and is not initially listed, add the artists name to the search!')
    st.write(' ')
    #Currently does not update with below selections.  Maybe just take out in the short term
    #st.write(f'Your current list of albums selected is {albums_to_compare}')

    create_connection()

#Make Line
st.markdown('''<hr style="height:10px;border:none;color:#777;background-color:#777;" />''', unsafe_allow_html = True)


#Create list of booleans to be modified by the checkboxes
compare_select=[False for i in range(10)]

#I Should have a try/except in here, but I cant get the except to handle the SpotifyException for some reason...
#There may be more than one type of error within it, so that could be why, but I dont know how to address that
#try:
# except SpotifyException:
#     st.error(f'Please ensure you have entered an album name before expecting an output.')

#Create container with first 5 album results
with st.container():
    try:
        current_album_results = search_album(album_query)
        top_columns = ('col1', 'col2', 'col3', 'col4', 'col5')
        top_columns = st.columns(5)

        for i in range(5):
            with top_columns[i]:
                st.subheader(current_album_results['Album Name'][i])

                total_images = len(current_album_results['Album Images'][i])
                tabs_list = ['tab'+str(n+1) for n in range(total_images)]
                tuple_tabs = tuple(tabs_list)
                image_list_titles = ['Album Art ' + str(n + 1) for n in range(total_images)]
                tuple_tabs = st.tabs(image_list_titles)
                for n in range(len(image_list_titles)):
                    with tuple_tabs[n]:
                        #st.header(image_list_titles[n])
                        st.image(current_album_results['Album Images'][i][n]['url'])

                st.write(f'Total Tracks : {current_album_results["Total Tracks"][i]}')
                st.write(f'Release Date : {current_album_results["Release Date"][i]}')
                st.write(f'Album Type : {current_album_results["Album Type"][i]}')
                st.write(f'Artists Names : {current_album_results["Artists Names"][i]}')
                compare_select[i] = st.checkbox('Compare', key=f'check_box_{i}')
    except:
        pass

#Create container with albums 6-10
with st.container():
    try:
        current_album_results = search_album(album_query)
        bottom_columns = ('col1', 'col2', 'col3', 'col4', 'col5')
        bottom_columns = st.columns(5)

        for i in range(5):
            with bottom_columns[i]:
                st.header(current_album_results['Album Name'][i+5])

                total_images = len(current_album_results['Album Images'][i+5])
                tabs_list = ['tab' + str(n + 1) for n in range(total_images)]
                tuple_tabs = tuple(tabs_list)

                image_list_titles = ['Album Art ' + str(n + 1) for n in range(total_images)]

                tuple_tabs = st.tabs(image_list_titles)

                for n in range(len(image_list_titles)):
                    with tuple_tabs[n]:
                        #st.header(image_list_titles[n])
                        st.image(current_album_results['Album Images'][i+5][n]['url'])

                st.write(f'Total Tracks : {current_album_results["Total Tracks"][i+5]}')
                st.write(f'Release Date : {current_album_results["Release Date"][i+5]}')
                st.write(f'Album Type : {current_album_results["Album Type"][i+5]}')
                st.write(f'Artists Names : {current_album_results["Artists Names"][i+5]}')
                compare_select[i+5] = st.checkbox('Compare', key=f'check_box_{i+5}')
    except:
        pass

#Create container button to initiate the polling of information from the page that you want to store
#@st.cache(persist=True)
with st.container():
    if st.button(label='Add Checked Items to Comparison List', key= 'button_1'):
        #st.write(compare_select)
        for i, bool in enumerate(compare_select):
            if bool == True:
                try:
                    #Write function to do @st.cache on top of these blocks.
                    #Turn these blocks into function and use the st.cache above it.
                    temp_series = current_album_results.iloc[i]
                    temp_df = pd.DataFrame({'Album Name': temp_series[0], 'Release Date': temp_series[1], 'Total Tracks': temp_series[2],
                                  'Album Type': temp_series[3], 'Album Images': {0: temp_series[4][0]['url']}, 'Album ID': temp_series[5], 'URI': temp_series[6],
                                  'Artists Names': temp_series[7],
                                  })
                    compare_select_df = pd.concat([compare_select_df,temp_df])
                    albums_to_compare.append(compare_select_df.iloc[-1].loc['Album Name'])
                    #st.write(albums_to_compare, compare_select_df)

                except:
                    temp_series = current_album_results.iloc[i]
                    compare_select_df = pd.DataFrame(
                        {'Album Name': temp_series[0], 'Release Date': temp_series[1], 'Total Tracks': temp_series[2],
                         'Album Type': temp_series[3], 'Album Images': {0: temp_series[4][0]['url']}, 'Album ID': temp_series[5],
                         'URI': temp_series[6],
                         'Artists Names': temp_series[7],
                         })
                    albums_to_compare.append(compare_select_df.iloc[0].loc['Album Name'])
                    #albums_to_compare.append(compare_select_df.loc['Album Name'])

            else:
                pass

    else:
        st.write('Please press the button when you have selected if you would like to compare any of these albums.')
    st.write(f'Your current list of albums selected is {albums_to_compare}')
    try:
        album_vis = st.checkbox('Album DataFrame Visibility', key='album_visibility')
        if album_vis == True:
            st.write(compare_select_df)
        else:
            pass

    except:
        pass

    try:
        album_songs_df = parse_tracks_info_from_album(list(compare_select_df['URI']),list(compare_select_df['Album Name']))
        album_songs_features_df = audio_features_from_track_id_list(album_songs_df['URI'])
        #st.write(album_songs_features_df)
        #st.write(album_songs_df)
        #drops the album index number so the sequential features grab can just be joined to it.
        album_songs_df.reset_index(drop = True, inplace = True)
        album_songs_df = album_songs_df.join(album_songs_features_df)



    except:
        #st.write('No Album URIs submitted for search yet')
        pass

    album_song_vis = st.checkbox('Album Song DataFrame Visibility', key='album_song_visibility')
    if album_song_vis == True:
        try:
            st.write(album_songs_df)
        except:
            st.write('No songs requested yet.')
    else:
        pass

        # st.write(album_songs_features_df_temp)
        # st.write(album_songs_df_temp_2)

# Slider for num of columns to compare
with st.container():
    compare_columns = st.slider('How many albums would you like to compare?', min_value=1,max_value=5,step=1)

# Select box to see the graphical output of the features.
with st.container():
    graph_vis = st.checkbox('Album Song Graph Visibility', key='graph_visibility', value = True)
    if graph_vis == True:
        try:
            columns = tuple(['col' + str(i) for i in range(compare_columns)])
            columns = st.columns(compare_columns)
            for i in range(compare_columns):
                with columns[i]:
                    total_albums = len(albums_to_compare)
                    tabs_list = list(['tab' + str(n + 1) for n in range(len(albums_to_compare))])
                    try:
                        tuple_tabs = tuple(tabs_list)
                        tuple_tabs = st.tabs(albums_to_compare)
                        for n in range(len(albums_to_compare)):
                            with tuple_tabs[n]:
                                # How do this in tabs?
                                album = album_songs_df.loc[album_songs_df['Album Name'] == albums_to_compare[n]]
                                # album = album_songs_df.loc[album_songs_df['Album Name'][album_list_titles[n]]]
                                # st.write(album)
                                st.pyplot(popularity_graph(album))
                                st.pyplot(audio_features_graph(album))
                                st.pyplot(tempo_graph(album))
                    except:
                        pass
        except:
            st.write('No songs requested yet.')
    else:
        pass


with st.container():
    try:
        insert_col_num = len(albums_to_compare)
        col_names = []
        col_names = ['col'+ str(n) for n in range(insert_col_num)]
        col_names_tup = tuple(col_names)
        columns = st.columns(insert_col_num)
        for i in range(insert_col_num):
            with columns[i]:
                st.header(albums_to_compare[i])
                #How do I itterate the naem of this slider variable? can I use the key as the output name?
                songs_to_add_ = st.slider("Select the range of the album that you would like to add to your database:", value=(0, int(compare_select_df.iloc[i]['Total Tracks'])), max_value=int(compare_select_df.iloc[i]['Total Tracks']), key=('select'+str(i)))
    except:
        pass

    #something = st.selectbox('some_crap', options=[1,2,3,4,5], key = 'selectbox_one')
    #another_something = st.checkbox('some_checkbox', key = 'some_checkbox')
    #text = st.text_input('How many song do you want?')



    #
    #         total_images = len(current_album_results['Album Images'][i + 5])
    #         tabs_list = ['tab' + str(n + 1) for n in range(total_images)]
    #         tuple_tabs = tuple(tabs_list)
    #
    #         image_list_titles = ['Album Art ' + str(n + 1) for n in range(total_images)]
    #
    #         tuple_tabs = st.tabs(image_list_titles)
    #
    #         for n in range(len(image_list_titles)):
    #             with tuple_tabs[n]:
    #                 # st.header(image_list_titles[n])
    #                 st.image(current_album_results['Album Images'][i + 5][n]['url'])
    # if st.button(label='Add Selected Items to Database'):
    #     pass


