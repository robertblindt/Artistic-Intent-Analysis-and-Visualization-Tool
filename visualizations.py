# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 18:04:41 2023

@author: Robert
"""
# Module: Visualizations

# Module for creating and returning figures for display on streamlit

#import matplotlib.pyplot as plt
#import pandas as pd
import plotly.express as px
#from prepare_and_quantify import resample_points
#import streamlit as st
#import fpdf as FPDF

#%% 
# Individual album graphed with regression line Moved


    
#%% Create compiled legend title list
def create_legend_single_feature_compare(album_names, options = 'All'):
    
    
    '''
    Input:
    album_names: a list of strings representing the names of the albums
    options: a string or list of integers representing the desired options for the legend (default value is 'All')
    
    Return Value:
    legend_list: a list of strings representing the items in the legend
    
    Function Description:
    This function generates a legend list based on the given album names and an option. If the 'options' parameter is set to 'All', the function will generate a list of legend items for all available options (interpolated, linear regression, 2nd degree polynomial regression, and 3rd degree polynomial regression) for each album in the album_names list.
    
    If the options parameter is not set to 'All', the function will generate a legend list based on just the best statistical fit. The options parameter should be a list of integers, where each integer represents an options best statstical fit:
    
    0: interpolated and linear regression
    1: interpolated and 2nd degree polynomial regression
    2: interpolated and 3rd degree polynomial regression
    3: interpolated and mean
    For each album in the album_names list, the function generates a list of legend items based on the specified options. The generated legend items are appended to the legend_list.
    
    The function returns the legend_list, which is a list of strings representing the items in the legend.
    '''

    legend_list = []
    if options == 'All':
        for name in album_names:
            one = name + ' Interpolated'
            two = name + ' Lin Regression'
            three = name + ' Poly 2 Regression'
            four = name + ' Poly 3 Regression'
            legend_list.append(one)
            legend_list.append(two)
            legend_list.append(three)
            legend_list.append(four)
    else:
        for n, option in enumerate(options):
            one = album_names[n] + ' Interpolated'
            two = album_names[n] + ' Lin Regression'
            three = album_names[n] + ' Poly 2 Regression'
            four = album_names[n] + ' Poly 3 Regression'
            five = album_names[n] + ' Mean'
            if option == 0:
                legend_list.append(one)
                legend_list.append(two)
            elif option == 1:
                legend_list.append(one)
                legend_list.append(three)
            elif option == 2:
                legend_list.append(one)
                legend_list.append(four)
            else:
                legend_list.append(one)
                legend_list.append(five)
    
    return legend_list
        
#%% Colors list
column_list = ''
o = 0

#%%
# Create Color list
def create_color_list(album_names, single_feature_list):
    """
    Create a list of colors for each album in album_names, to be used in graphing the single_feature_list data.

    Input:
    - album_names: a list of strings representing the names of the albums
    - single_feature_list: a list of lists containing feature data for each album

    Return Value:
    - color_list: a list of strings representing the colors to be used in graphing each album's data.
    """
    color_options = ['red','orange','green','blue','purple', 'black']
    multiplier = int(len(single_feature_list)/len(album_names))
    color_list = []
    [[color_list.append(color) for i in range(multiplier)] for color in color_options]
    return color_list

#%%
# Make Line List MOVED

#%% 
# Create a feature compared graph MOVED

#%%
# Graph Single Album with all features shown
def single_album_heatmap(single_album, name, resample_points):
    """
    Generate a heatmap of the acoustic features of a Spotify album.
   
   Parameters:
   -----------
   single_album : pandas DataFrame
       A DataFrame containing the acoustic features of each track in the album.
   name : str
       The name of the album to include in the plot title.
   resample_points : int
       The number of points to resample the x-axis to.
   
   Returns:
   --------
   fig : plotly.graph_objs._figure.Figure
       A Plotly figure object containing the heatmap.
   """
    ticks = resample_points-1
    xtick_point = [x*(ticks/4) for x in range(5)]
    fig = px.imshow(single_album, text_auto=True, aspect="auto",
                    labels = dict(x="Album Completeness", y="Spotify Feature", color = 'Coefficient'),
                    y=['Acousticness','Danceability','Energy','Instrumentalness','Liveness','Speechiness','Valence'],
                    title = f'{name} Spotify Acoustic Features',
                    color_continuous_scale='RdBu_r')    
    
    fig.update_layout(
            xaxis = dict(
            tickmode = 'array',
            showgrid = False,
            tickvals = xtick_point,
            ticktext = ['0%','25%','50%','75%','100%']
                         ),
            yaxis = dict(showgrid = False),
            title_x=0.5,
            title_font_color='#FA0000'
                        )
    return fig






