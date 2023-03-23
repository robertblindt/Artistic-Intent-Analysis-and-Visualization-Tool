import streamlit as st

from fpdf2_report_class import PDF

import pandas as pd
import numpy as np

import plotly.graph_objects as go


from database_query_module import discogs_verified_albums_query, create_album_artist_display_list, split_and_query
from prepare_and_quantify import create_album_list, column_list, create_resampled_line, duplicate_last_row\
   , create_time_alignment, flat_timeweighted_interpol, regression_line, descriptive_stats, calc_polynomial_regression\
   , calculate_tss, calc_poly_r_squared, features_to_albums, rank_r_square_fit\
   , features_stats_to_albums_stats, features_to_albums_df
from visualizations import create_legend_single_feature_compare, single_album_heatmap, create_color_list


DB = 'redesigned_music_database.db'

#Set page to widescreen mode and make main title
st.set_page_config(layout="wide")

# Eventually it may be better to query the database every once and a while to create this list, and not to create it every
# time the page loads.

# Query the database for the album names attached to that artists name.
artist_albums = discogs_verified_albums_query()

#Do this outside once the scrape is done. - Find a way to auto update this list when doing updates too...
label_list = create_album_artist_display_list(artist_albums)


with st.sidebar:
    st.markdown('''
    # Sections
    - [Data Entry](#data-entry)
    - [Album Heatmaps](#album-heatmaps)
    - [R-Squared Comparison Table](#r-squared-comparison-table)
    - [Feature Comparison](#feature-comparison)
    ''', unsafe_allow_html=True)
    skip_insig_line = st.checkbox(
        'Suppress the Interpolated Album Feature Lines for Albums that were not found to have significant regression fit',
        value=True)
    auto_scale_cof_graphs = st.checkbox(
        'Auto-scale Y axis to fit the line instead of the overall spectrum (Duration, Loudness, and Tempo always auto-scaled)',
        value=False)

    
st.header('Data Entry')
# Input Section to
with st.form("Header Info"):
   st.write("Please enter your name, purpose for comparison, and any additional notes in the boxes below.")
   user_name = st.text_input("Name")
   analysis_purpos = st.text_input("Purpose")
   notes = st.text_input("Notes")
   album_select = st.multiselect("What albums would you like to look at?", label_list)
   submitted_0 = st.form_submit_button("Submit")

if len(album_select) == 0:
    st.header('No Albums Selected')
    st.write('If you have selected albums, but can still see this message, press the "Select" button again.')
else:
    retrieved_database=split_and_query(album_select)

    album_names = create_album_list(retrieved_database)

    # Set resample point number
    # HOW DO I DEAL WITH THE REPRESENTATION OF COMPLETENESS IN MY STATS? - LOOK AT Notepad
    resample_points = 2000
    xnew = create_resampled_line(resample_points)

    # Create a list of lists for the resampled data for graphing as well as dataframes
    list_of_lines_list = [[], [], [], [], [], [], [], [], [], []]

    list_of_choices = [[], [], [], [], [], [], [], [], [], []]

    list_of_r_squared = [[], [], [], [], [], [], [], [], [], []]

    best_fit_list_of_lines_list = [[], [], [], [], [], [], [], [], [], []]

    list_of_stats_dfs = [[], [], [], [], [], [], [], [], [], []]

    empty_built_lists = []
    empty_built_lists_2 = []
    empty_built_lists_3 = []

    # Loop through each albums name to access the features of each album
    for i in album_names:
        # Selects the correct album
        empty_built_lists.append([])
        empty_built_lists_2.append([])
        empty_built_lists_3.append([])
        album_spotify_features = duplicate_last_row(i, retrieved_database)

        single_album_features = create_time_alignment(album_spotify_features)

        # Loop through each feature in the album
        for num, feature in enumerate(column_list):
            # Resamples the discrete points to time weighted points
            interpol_feature = flat_timeweighted_interpol(single_album_features, xnew, feature)

            # Creates regression line
            regression, regression_line_data = regression_line(interpol_feature, resample_points)

            fitpoints2, fitpoints3, polyfit2, polyfit3 = calc_polynomial_regression(xnew, interpol_feature)

            list_of_lines_list[num].append(interpol_feature)
            list_of_lines_list[num].append(regression_line_data)
            list_of_lines_list[num].append(fitpoints2)
            list_of_lines_list[num].append(fitpoints3)

            # Do descriptive stats
            df, static_stats = descriptive_stats(interpol_feature, regression, i)

            tss = calculate_tss(interpol_feature, static_stats.mean)

            poly_r_squared = calc_poly_r_squared(tss, polyfit2[1])

            poly_r_cubed = calc_poly_r_squared(tss, polyfit3[1])

            linear_r_squared = regression.rvalue ** 2

            list_of_r_squared[num].append(linear_r_squared)
            list_of_r_squared[num].append(poly_r_squared)
            list_of_r_squared[num].append(poly_r_cubed)

            # Create Ranked regression output
            #regression.rvalue ** 2, poly_r_squared, poly_r_cubed, static_stats
            resp, choice = rank_r_square_fit(linear_r_squared, poly_r_squared, poly_r_cubed, static_stats)
            list_of_choices[num].append(choice)

            if choice == 0:
                best_fit_list_of_lines_list[num].append(interpol_feature)
                best_fit_list_of_lines_list[num].append(regression_line_data)
                pass
            elif choice == 1:
                best_fit_list_of_lines_list[num].append(interpol_feature)
                best_fit_list_of_lines_list[num].append(fitpoints2)
                pass
            elif choice == 2:
                best_fit_list_of_lines_list[num].append(interpol_feature)
                best_fit_list_of_lines_list[num].append(fitpoints3)
                pass
            elif choice == 3:
                best_fit_list_of_lines_list[num].append(interpol_feature)
                mean_points = np.linspace(static_stats.mean,static_stats.mean, num = resample_points)
                best_fit_list_of_lines_list[num].append(mean_points)
                pass

            try:
                list_of_stats_dfs[num] = pd.concat([df,list_of_stats_dfs[num]], axis = 1)
            except:
                normalized_variance = static_stats.variance#(static_stats.variance/resample_points)*1000
                first_album_df = pd.DataFrame((static_stats.mean, normalized_variance, static_stats.skewness, static_stats.kurtosis,
                                   regression.slope
                                   , regression.intercept, regression.rvalue**2, regression.pvalue, regression.stderr,
                                   regression.intercept_stderr, poly_r_squared[0], poly_r_cubed[0])
                                  , columns=[f'{i}'],
                                  index=['Mean', 'Variance', 'Skewness', 'Kurtosis', 'Trend (Regression Slope)'
                                      , 'Regression Intercept', 'R-Squared Linear', 'P-value', 'Std Error', 'Intercept Std Error'
                                      ,   'R-Squared Poly 2nd', 'R-Squared Poly 3rd'])
                list_of_stats_dfs[num].append(first_album_df)


    # Create a bunch of handlers for different number of albums selected.
    # Create the columns of heatmaps for selected albums.
    album_built_lists = features_to_albums(list_of_lines_list, empty_built_lists, album_names)

    st.header("Album Heatmaps")
    heatmap_figure_list = []
    if len(album_names) <= 3:
        heatmap_columns = tuple(['col' + str(i) for i in range(len(album_names))])
        heatmap_columns = st.columns(len(album_names))
        for num, single_album in enumerate(album_built_lists):
            with heatmap_columns[num]:
                fig = single_album_heatmap(single_album, album_names[num], resample_points)
                heatmap_figure_list.append(fig)
                st.plotly_chart(fig)

    elif len(album_names) <= 6:
        heatmap_columns = tuple(['col' + str(i) for i in range(3)])
        heatmap_columns = st.columns(3)
        for num, single_album in enumerate(album_built_lists[0:3]):
            with heatmap_columns[num]:
                fig = single_album_heatmap(single_album, album_names[num], resample_points)
                heatmap_figure_list.append(fig)
                st.plotly_chart(fig)
        heatmap_columns = tuple(['col' + str(i) for i in range(3)])
        heatmap_columns = st.columns(3)
        for num, single_album in enumerate(album_built_lists[3:]):
            with heatmap_columns[num]:
                fig = single_album_heatmap(single_album, album_names[num+3], resample_points)
                heatmap_figure_list.append(fig)
                st.plotly_chart(fig)

    else:
        st.write('This app can only support comparing up to 6 albums.  Please reduce your search, and feel free to run multiple reports!')


    cap_list = []
    suppression_variable_0 = [[cap_list.append(i.capitalize()) for z in range(len(album_names))] for i in column_list]

    #feature to album df
    # NOT ACTUALLY USED
    empty_built_lists_3 = features_to_albums_df(list_of_stats_dfs, cap_list, empty_built_lists_3)

    # Create a text prompt that says something to the effect of:
        # "From the albums selected, there were some trends that we noticed! In the album 'album_name[i]', the features 'features[i]'...
        # {and 'duplicate for each album'} was found to have significant time correlation.  Below is a table that shows the compared
        # significance variables for each feature and regression degree completed.  Any item that could not be fit to one of
        # these regessions might be better described by its descriptive statistics. (Mean, Median, Skew, Kurtosis)"

    for lines_data in list_of_lines_list:
        fig = go.Figure()
        x_scale = np.linspace(0, resample_points - 1, num=resample_points)
        for oline in lines_data:
            fig.add_trace(go.Scatter(x=x_scale, y=oline,
                        mode='lines',
                        name='lines'))

    legend_list = create_legend_single_feature_compare(album_names)
    best_lists = []
    for o, single_feature_list in enumerate(best_fit_list_of_lines_list):
        legend_list_best = create_legend_single_feature_compare(album_names, list_of_choices[o])
        best_lists.append(legend_list_best)

    cap_list = []
    suppression_variable_0 = [[cap_list.append(i.capitalize()) for z in range(3)] for i in column_list]
    # TABLE OF R-SQUARED GOES HERE!
    regression_label = []
    regression_type = ['Linear', 'Quadratic', 'Cubic']
    suppression_variable_1 = [regression_label.append(regression_type[i%3]) for i in range(3*len(column_list))]

    arrays = [
        cap_list,
        regression_label,
             ]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=["Feature", "Data"])

    stats_out = features_stats_to_albums_stats(list_of_r_squared, empty_built_lists_2, album_names)

    df_list = []
    for y,album in enumerate(stats_out):
        s = pd.Series(stats_out[y], index=index, name = album_names[y])
        df_list.append(s.to_frame())

    for i, frames in enumerate(df_list):
        if i == 0:
            stats_df = frames
        else:
            stats_df = pd.concat([stats_df, frames], axis = 1)

    st.header('R-Squared Comparison Table')
    with st.expander('Comparison Table', expanded=True):
        st.dataframe(stats_df.style.background_gradient(cmap='RdYlGn', high = 0.25, vmin = 0.35, vmax = 0.715), width=1500)

    fig_name_list = []
    suppression_variable_2 = [fig_name_list.append(featurename+'fig') for featurename in column_list]


    st.header('Feature Comparison')
    cap_list = []
    suppression_variable_3 = [cap_list.append(column_list[o].capitalize()) for o in range(len(column_list))]
    tab_list = ['tab1', 'tab2', 'tab3', 'tab4', 'tab5', 'tab6', 'tab7', 'tab8', 'tab9', 'tab10']
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(cap_list)

    chart_state_list = []
    suppression_variable_4 = [chart_state_list.append('feature_state'+str(x)) for x in range(len(tab_list))]

    # Make the stats DF for the descriptive statistics of each 'non-regression' line.
    list_of_means = [[], [], [], [], [], [], [], [], [], []]
    for i, feature_titles in enumerate(best_lists):
        for name in feature_titles[1::2]:
            if 'Mean' in name:
                album_name = name.replace(' Mean', '')
                list_of_means[i].append(album_name)

    list_of_stat_indexes = [[], [], [], [], [], [], [], [], [], []]
    for i, means in enumerate(list_of_means):
        for name in means:
            number = album_names.index(name)
            list_of_stat_indexes[i].append(number)

    feature_dataframe_list = [[], [], [], [], [], [], [], [], [], []]
    #st.write(list_of_stats_dfs[0][0].loc[['Mean','Variance','Skewness','Kurtosis']])
    for i, index_list in enumerate(list_of_stat_indexes):
        for j, index in enumerate(index_list):
            if j == 0:
                feature_dataframe_list[i].append(list_of_stats_dfs[i][index].loc[['Mean','Variance','Skewness','Kurtosis']])
            else:
                temp_df = list_of_stats_dfs[i][index].loc[['Mean','Variance','Skewness','Kurtosis']]
                #st.write(temp_df)
                feature_dataframe_list[i][0] = pd.concat([feature_dataframe_list[i][0],temp_df], axis = 1)



    for o, single_feature_list in enumerate(list_of_lines_list):
        with eval(tab_list[o]):
            #if 'already_made' not in st.session_state:
            fig_name_list[o] = go.Figure()
            x_scale = np.linspace(0, resample_points - 1, num=resample_points)
            #st.write(legend_list)
            color_list = create_color_list(album_names, single_feature_list)
            #st.write(single_feature_list)
            for p, oline in enumerate(single_feature_list):
                if (p % 4) == 0:
                    line_weight = 2.5
                else:
                    line_weight = 1.5
                fig_name_list[o].add_trace(go.Scatter(x=x_scale, y=oline,
                                         line=(dict(color=color_list[p], width=line_weight)),
                                         mode='lines',
                                         name=legend_list[p]),
                                         )

            fig_name_list[o].for_each_trace(lambda trace: trace.update(visible="legendonly") if trace.name not in best_lists[o] else ())

            fig_name_list[o].update_xaxes(range=[0,2000])
            if auto_scale_cof_graphs == False:
                if o == 2 or o == 6 or o == 9:
                    pass
                else:
                    fig_name_list[o].update_yaxes(range=[0, 1])

            # This allows to suppress the Interpol lines for insigificant albums
            if skip_insig_line == True:
                fig_name_list[o].for_each_trace(lambda trace: trace.update(visible="legendonly") if trace.name.split('Interpolated')[0]+'Mean' in best_lists[o] else ())

            if skip_insig_line == True:
                legend_title = 'Default: First Regressionn with<br>R-Squared greater than 0.7<br>w/ Insignificant Albums suppressed'
            else:
                legend_title = 'Default: First Regressionn with<br>R-Squared greater than 0.7'

            fig_name_list[o].update_layout(title=f"Feature Comparison: {column_list[o].capitalize()}",
                                          # legend=dict(font = dict(size=10)),
                              legend_title_text=legend_title,
                              legend_font_color="#FA0000",
                                           height=700,
                              xaxis=dict(
                                  tickmode='array',
                                  tickvals= [x*((resample_points-1)/4) for x in range(5)],
                                  ticktext=['0%', '25%', '50%', '75%', '100%']),
                              #height=feature_graph_height,
                                           )
                #st.session_state.already_made = fig_name_list[o]

            st.subheader(f'{column_list[o].capitalize()}', anchor=column_list[o])
            st.plotly_chart(fig_name_list[o], use_container_width = True, theme = None)


    # THIS WORKS IN ITS OWN APP> WHATS UP WITH THAT? "WarnOnDeprecatedModuleAttributes" on FPDF()
    export_as_pdf = st.button("Export Report")
    file_name = st.text_input('What do you want to name your pdf',key=66)


    section_title = ['Heatmap', 'Feature Comparison', 'Stats Tables']

    heatmap_figure_names = ['heatmap_1.png','heatmap_2.png','heatmap_3.png','heatmap_4.png','heatmap_5.png','heatmap_6.png']
    feature_compare_file_list = ['acousticness_compare.png','danceability_compare.png','duration_comapre.png', 'energy_compare.png', 'instrumentalness_compare.png', 'liveness_compare.png', 'loudness_comapre.png', 'speechiness_compare.png', 'valence_compare.png', 'tempo_compare.png']
    trunc_list = heatmap_figure_names[:len(heatmap_figure_list)]

    #st.write(trunc_list)
    if export_as_pdf:
        # Save Heatmaps
        for i, fig in enumerate(heatmap_figure_list):
            fig.write_image(heatmap_figure_names[i])
        # Remove Legend and Save Features comparison plots
        for i, fig in enumerate(fig_name_list):
            fig.write_image(feature_compare_file_list[i])

        pdf = PDF()
        pdf.front_page(user_name, analysis_purpos, album_select, notes)
        pdf.print_image_chapter(1, f'{section_title[0]}', trunc_list)
        pdf.print_image_chapter(2, f'{section_title[1]}', feature_compare_file_list, table_bool=True, data_frame=feature_dataframe_list, table_header='TABLEHEADER')
        pdf.create_table_from_df(stats_df, table_header='R-Squared Comparison Table', index_count=2)

        pdf.output(file_name)
