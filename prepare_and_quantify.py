# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 16:28:13 2023

@author: Robert
"""
# Module: prepare_and_quantify

# Module for data preporation and wrangling (quantification sounds wrong)

import numpy as np
import pandas as pd
import scipy
#from scipy.interpolate import interp1d

#%% create_album_list(retrieved_database)
# Create album name list 

def create_album_list(retrieved_database):
    '''
    This function intakes the 'retrieved_database' dataframe from the database query module, and ouputs a list of album names.
    
    Input
    retrieved_database: The pandas dataframe containing the dataframe of Spotify Song features of the selected albums
    
    Output
    album_names: A list of selected albums
    '''
    album_names = list(set(retrieved_database['spotify_album_name'].to_list()))
    return album_names

#%% column_list
# List of columns used for data processing

# Create list of column names to iterate through df
column_list = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness', 'loudness',
               'speechiness', 'valence', 'tempo']

#%% resample_points
# Set a golbal or an imported resample point number

# This is the resample number points used to create the new x scale
resample_points = 2000

#%% create_resampled_line(resample_points = resample_points)
# Create a line for the later interpolation function to be applied to

def create_resampled_line(resample_points):
    '''
    This function intakes the desired number of points in your resampled lines, and outputs it as a numpy array.
    
    Input
    resample_points = Integer number of desired points in your resampled line
    
    Output
    xnew = np array for reampling
    '''
    xnew = np.linspace(0, 1, num=resample_points, endpoint=True)
    return xnew

#%% for i in album_names:
# A loop to start itterating through each album starts here

#%% duplicate_last_row(album_spotify_features, i, retrieved_database)
# duplicate the last entry for use in 'previous' interpolation
def duplicate_last_row(i, retrieved_database):
    '''
    This function intakes the 'retrieved_database' dataframe and the individual feature by the name 'i' to output a duplicate
    dataframe with teh final line doubled.
    
    Input
    i: individual feature name
    retrieved_database: The pandas dataframe containing the dataframe of Spotify Song features of the selected albums
    
    Output
    album_spotify_features: The duplicated dataframe with its final line duplicated
    '''
    # Selects the correct album
    album_spotify_features = retrieved_database.loc[retrieved_database['spotify_album_name'] == i].sort_values(by=['track_index_position'], ascending = True)

    # 1) Duplicate the final song entry to graphically display data time weighted
    album_spotify_features = pd.concat([album_spotify_features, pd.DataFrame(np.repeat(album_spotify_features.iloc[[-1]].values, 1,
                                                                           axis=0),columns=album_spotify_features.columns)]).reset_index(
                                                                           drop=True)
    return album_spotify_features

#%% create_time_alignment(album_spotify_features)
#Create a time aligned list of positional arguments for use in interpolation
def create_time_alignment(album_spotify_features):
    '''
    This function intakes the 'album_spotify_features' dataframe and outputs the same dataframe with the time weighted
    averaging weights appeneded.
    
    Input
    album_spotify_features: Dataframe of a single album with its final line duplicated
        
    Output
    single_album_features: Dataframe of a single album with the time weighting appended to it
    '''    
    song_locations = []
    previous_time = 0
    # Create a list of "start point locations"
    for s in album_spotify_features['duration_ms']:
        if len(song_locations) == 0:
            song_locations.append(float(previous_time))
            previous_time = previous_time + s
        else:
            song_locations.append(float(previous_time))
            previous_time = previous_time + s
    # Create a percentile location list that gets concatonated to the retrieved df
    total_time = song_locations[-1]
    new_list = [x / total_time for x in song_locations]
    single_album_features = album_spotify_features.reset_index(drop=True)
    single_album_features = pd.concat([single_album_features, pd.Series(new_list, name='doneness')], axis=1)
    
    return single_album_features


#%% for num, feature in enumerate(column_list)
# A loop to itterate through each feature starts here

#%% flat_timeweighted_interpol(single_album_features, xnew, feature)
# Interpolate using the 'previous' selection
def flat_timeweighted_interpol(single_album_features, xnew, feature):
    '''
    This function intakes the dataframe with time weighting, the number of points you want in your interpolated line, and
    the feature you would like to use create the line for and outputs a interpolated and resampled line.
    
    Input
    single_album_features: Dataframe of a single album with the time weighting appended to it
    xnew: np array for reampling
    feature: individual feature name
        
    Output
    interpol_feature: Interpolated time weighted array
    ''' 
    interpol_feature = scipy.interpolate.interp1d(single_album_features['doneness'], single_album_features[feature], kind='previous')(xnew)
    return interpol_feature


#%% regression_line(interpol_feature)
# Create a regression line and put it in a list
def regression_line(interpol_feature, resample_points):
    '''
    This function intakes the interpolated time weighted array and number of points in the line and outputs a regression
    line and information about it.
    
    Input
    interpol_feature: Interpolated time weighted array
        
    Output
    regression = Regression line array
    regression_line_data = Regression line information
    '''
    regression = scipy.stats.linregress(list(range(0, resample_points)), interpol_feature)
    regression_line_data = []
    for k in range(resample_points):
        regression_line_data.append(regression.slope * k + regression.intercept)
    return regression, regression_line_data

#%% descriptive_stats(interpol_feature, regression, i)
# Do descriptive stats and build df with regressional data
def descriptive_stats(interpol_feature, regression, i): 
    '''
    This function intakes the interpolated time weighted array, regression line, and individual feature name, and outputs
    a dataframe of the descriptive satistics and the descriptive stats with the regession line.
    
    Input
    interpol_feature: Interpolated time weighted array
    regression: Regression line array
    i: individual feature name
        
    Output
    df = 
    static_stats = 
    '''
    static_stats = scipy.stats.describe(interpol_feature, ddof=1, bias=False)
    df = pd.DataFrame((static_stats.mean, static_stats.variance, static_stats.skewness, static_stats.kurtosis, regression.slope
                     , regression.intercept, regression.rvalue, regression.pvalue, regression.stderr, regression.intercept_stderr)
                     , columns = [f'{i}'], index = ['Mean','Variance','Skewness','Kurtosis', 'Trend (Regression Slope)'
                     , 'Regression Intercept', 'R-value', 'P-value', 'Std Error', 'Intercept Std Error'])
    return df, static_stats

#%%
def features_to_albums_df(list_of_stats_dfs, cap_list, empty_built_lists_3):
    """
    Creates a summary DataFrame for each album feature in `list_of_stats_dfs`, combining the
    Mean, Variance, Skewness and Kurtosis statistics across all albums.

    Parameters:
    -----------
    list_of_stats_dfs : list of pandas.DataFrame
        A list of DataFrames containing summary statistics for each album feature.
    cap_list : list of str
        A list of column names to use for the output DataFrame.
    empty_built_lists_3 : list of list of pandas.DataFrame
        A nested list representing an empty DataFrame for each album feature.
        These DataFrames will be appended with the summary statistics for each album.

    Returns:
    --------
    list of list of pandas.DataFrame
        A nested list of DataFrames, where each inner list represents an album feature
        and contains summary statistics for all albums.
    """
    itterator = 0
    for feature_list_dfs in list_of_stats_dfs:
        for o, features_stats_df in enumerate(feature_list_dfs):
    
            single_album_descriptive_stats = features_stats_df.loc[['Mean','Variance','Skewness','Kurtosis']]
    
            single_album_descriptive_stats = single_album_descriptive_stats.rename(columns={single_album_descriptive_stats.columns[0]:cap_list[itterator]})
    
            itterator += 1
    
            if len(empty_built_lists_3[o]) != 0:
    
                empty_built_lists_3[o][0] = pd.concat([empty_built_lists_3[o][0],single_album_descriptive_stats], axis = 1)
                #empty_built_lists_3[o][0].join(single_album_descriptive_stats)
            else:
                empty_built_lists_3[o].append(single_album_descriptive_stats)
            
    return empty_built_lists_3

#%% 
# Calculate Residual
def calc_residual(interpol_feature, regression_line_data):
    residual = interpol_feature - regression_line_data
    return residual


#%%
#Calc polyfit
def calc_polynomial_regression(xnew, interpol_feature):
    """
    Calculates the 2nd and 3rd order polynomial regression fits for given x and y values.

    Parameters:
    -----------
    xnew: array-like
        The x values to use for polynomial regression fit.
    interpol_feature: array-like
        The y values to use for polynomial regression fit.

    Returns:
    --------
    fitpoints2: numpy.ndarray
        The fitted y values for the 2nd order polynomial regression.
    fitpoints3: numpy.ndarray
        The fitted y values for the 3rd order polynomial regression.
    polyfit2: tuple
        A tuple of NumPy arrays containing the polynomial coefficients, residuals,
        rank, singular values, and rcond of the 2nd order polynomial regression.
    polyfit3: tuple
        A tuple of NumPy arrays containing the polynomial coefficients, residuals,
        rank, singular values, and rcond of the 3rd order polynomial regression.
    """
    # Need to figure out the "goodness" stats on this stuff.
    polyfit2 = np.polyfit(xnew, interpol_feature, 2, full = True)
    polyfit3 = np.polyfit(xnew, interpol_feature, 3, full = True)
    fitpoints2 = np.poly1d(polyfit2[0])(xnew)
    fitpoints3 = np.poly1d(polyfit3[0])(xnew)
    return fitpoints2, fitpoints3, polyfit2, polyfit3
    
    
#%%
# Calculate TSS for calculating R-Squared for Polynomial Regression
def calculate_tss(interpol_feature, mean):
    """
    Calculates the total sum of squares (TSS) for a given feature and its mean.

    Parameters:
    -----------
    interpol_feature: array
        The feature for which to calculate the TSS.
    mean: float
        The mean value of the feature.

    Returns:
    --------
    tss: float
        The TSS value for the feature.
    """
    tss = 0
    for i in interpol_feature:
        tss += (i - mean)**2
    return tss


#%%
# Calculate R-squared for polynomial regression
def calc_poly_r_squared(tss,rss):
    """
    Calculates the R-squared value for a polynomial regression.
    
    Parameters:
    tss: float
        The total sum of squares.
    rss: float
        The residual sum of squares.
    
    Returns:
    poly_r_squared: float
        The R-squared value for the polynomial regression.
    """
    poly_r_squared = (tss-rss)/tss
    return poly_r_squared



#%% 
# Rank R-Squared Values
def rank_r_square_fit(linear_r_squared, poly_r_squared, poly_r_cubed, static_stats, threshold = 0.7):
    """
    Rank the goodness of fit for different types of regression models based on the R-squared values.
    
    Parameters:
    -----------
    linear_r_squared: float
        The R-squared value for the linear regression model.
    poly_r_squared: float
        The R-squared value for the 2nd order polynomial regression model.
    poly_r_cubed: float
        The R-squared value for the 3rd order polynomial regression model.
    static_stats: tuple
        A tuple containing the mean, variance, and skewness values of the data.
    threshold: float, optional (default=0.7)
        The threshold value for determining if a regression model is a good fit.
    
    Returns:
    --------
    resp: str
        A string indicating which regression model is a good fit based on the R-squared values.
    choice: int
        An integer indicating the choice of regression model based on the R-squared values.
        - 0: Linear Regression
        - 1: 2nd Order Polynomial Regression
        - 2: 3rd Order Polynomial Regression
        - 3: Average, Variance, and Skewness
    """
    if linear_r_squared >= threshold:
        resp = 'Linear Regression makes a good fit'
        choice = 0
    elif poly_r_squared >= threshold:
        resp = '2nd Order Polynomial regression is a good fit.'
        choice = 1
    elif poly_r_cubed >= threshold:
        resp = '3rd order Polynomial regression is a good fit.'
        choice = 2
    else:
        resp = 'Average, Varience, and Skew is probably your best fit.'
        choice = 3
        
    return resp, choice


#%%
# 


#%%
# Go from feature centric lists to album lists skipping non coef values
def features_to_albums(list_of_lists, empty_built_lists, album_names):
    """
    Parameters:
    -----------
    list_of_lists: list of lists
        The list of lists of features to be organized into albums.
    empty_built_lists: list of lists
        An empty list of lists to hold the organized data.
    album_names: list
        A list of album names to use for organizing the data.
    
    Returns:
    --------
    empty_built_lists: list of lists
        A list of lists of features organized into albums.    
    """
    for p, feature_list in enumerate(list_of_lists):
        divider = len(feature_list)/len(album_names)
        for o, line_data in enumerate(feature_list):
            #st.write(line_data)
            #st.write(o)
            if o == 0 or o % 4 == 0:
                if p == 2 or p == 9 or p == 6:
                    pass
                else:
                    if o == 0:
                        empty_built_lists[0].append(list(line_data))
                    else:
                        empty_built_lists[int(o/divider)].append(list(line_data))
            else:
                pass
    
    return empty_built_lists
    
    
#%%

def features_stats_to_albums_stats(list_of_r_squared, empty_built_lists, album_names):
    """
    Converts a list of lists of R-squared values (organised by feature) into a list of album-wise statistics.
    
    Parameters:
    -----------
    list_of_r_squared: list of lists
        A list of lists of R-squared values for each feature.
    empty_built_lists: list of lists
        A list of empty lists that will be populated with album-wise statistics.
    album_names: list
        A list of album names.
    
    Returns:
    --------
    empty_built_lists: list of lists
        A list of album-wise statistics populated with R-squared values.
    """ 

    for p, feature_stat_list in enumerate(list_of_r_squared):
        #divider = len(feature_stat_list)/len(album_names)
        for o, individual_r_squared in enumerate(feature_stat_list):
            #st.write(individual_r_squared)
            #st.write(o)
            # if o == 0:
            #     empty_built_lists[0].append(individual_r_squared)
            # else:
            empty_built_lists[int(o//3)].append(float(individual_r_squared))

    
    return empty_built_lists



