# Artistic-Intent-Analysis-and-Visualization-Tool
 This repository contains analysis and visualization tools to look at song level acoustic features and album level feature flow pulled from Spotifys API.

In the scope of this project, the term 'artistic intent' is a reference to a quantitative statistical profile of selected albums that a creative would like to emulate some aspect of their production after. By exploring aspects of this project a creative can gain a feeling for how features intensities and trend relate to your actual intent with your production.

This is a repository containing a project that analyzes Spotify 'acoustic feature' flow, and a redesigned and verified version of the 'component.one' Spotify features database.  There is a detailed report about how everything works, and why I am treating the data the way I am called `Artistic-Intent-A-and-V-Tool.ipynb`.  

## Installation

In order to use the final app, you need to install the following packages into a Python 3.8 environment:

```bash
pip install pandas streamlit FPDF2 matplotlib plotly
```

If you would like to explore how the Spotify system interprets music that is not in the database, or multiple versions of the same song, you will need to sign up for a Spotify API key at https://developer.spotify.com/dashboard/login and:

```bash
pip install spotipy
```

Within the project I also interacted with the Discogs API, however unless you plan to expand the database with the same automated verification method you should not need to access it.  Nonetheless, you can sign up for an API key at https://www.discogs.com/developers/ and:

```bash
pip install discogs_api
```


## Usage
### **Final App:**

**Startup Streamlit app for `regression_report_app.py`:**

1) From the command line, type `Streamlit run regression_report_app.py`
2) Fill in your name, purpose, and notes (Information for self tracking reports)
3) Select Albums you would like to investigate
4) Hit "Submit" button to submit form
5) Investigate visualizations and change parameters in the side bar
6) Input desired PDF output file name
7) Press the export button to save the PDF to your local directory
    
### **Exploratory Data Analysis**

This section has three Streamlit apps.  Note that they do not have built-in capabilities to output reports.  

*When creating these apps, I did not bother to suppress the error outputs so that I could continue learning how to address things.  I did not fix this because these were not intended outputs of my project.  When opening and using these apps, users will see an error saying something like: 'list_name is empty', or 'list_name referenced before creation'.  However, it should work after adding data to the data entry fields.*

**Startup Streamlit app for `initial_spotify_api_exploration.py`:**

1) From the Command line, type `Streamlit run initial_spotify_api_exploration.py`
2) Type the name of an album or artist to investigate (The underlying search command defaults to searching by album name, but the Spotify search engine is forgiving.)
3) Select the albums you would like to see the features of (Checkbox)
4) Adjust Slider to add additional columns for comparison
5) Press "Submit" button (There are two select boxes to view data being passed into the graphs, but they do not add much value.)
6) Investigate the graphs in the containers

**Startup Streamlit app for `top200_timespan_features_singlepull.py`:**

1) From the command line, type `Streamlit run top200_timespan_features_singlepull.py`
2) Select a week to start your selection
3) Select a week to end your selection
4) Select the frequency to sample the database
5) Select how many of top 200 albums you would like to average between
6) After the graphs and statistics are generated, interpret and analyze the results.
   
**Startup Streamlit app for `search_by_artists.py`:**

1) From the command line, type `Streamlit run search_by_artists.py`
2) Select the artist(s) you want to investigate
3) After the graphs and statistics are generated, interpret and analyze the results.

## Contributing

Feel free to make improvements and changes or reach out if you have questions! This was a fun learning exercise and I hope to continue pushing the analysis to be more advanced and actionable, and streamline the Spotify API app into the final app, but I have some other things to do and learn before getting to that.  

## License

[MIT](https://choosealicense.com/licenses/mit/)