# Spotify Data Visualization Project

This project has been developped by **Théo Malka-Lacombe**, **Maxime Peter** and **Julien Verdun** within the scope of a data visualization class at Ecole Centrale Lyon.

This repository includes the files required to process personnal data received from Spotify.

The data are explored and drew on different **Observable notebook** available [here](https://observablehq.com/@julien-verdun/spotify-data-visualization-project).

The **main visualization** of the project is a dashboard [Spotify project](https://theo-malka.github.io/). It has been deployed with Github Pages. The code is stored on the repository [the-malka.github.io](https://github.com/theo-malka/theo-malka.github.io).

It is a dashboard of someone Spotify personnal data with 3 charts, a scatter plot, a radar plot and a bar chart.
Anyone can upload its own personnal data and analyze them with the 3 charts.

In order to get your personnal data, please follow the instructions below.

## Get your data

Get your data from your Spotify account [My Personnal Data](https://support.spotify.com/uk/article/data-rights-and-privacy-settings/).

You can get a ZIP file with a copy of most of your personal data by using the automated Download your data function on the Privacy Settings section of your account page.

The download includes information about your playlists, streaming history, searches, a list of items saved in Your Library, the number of followers you have, the number of accounts you follow, the names of the artists you follow, and your payment and subscription data.

### Data processing with Python

The data are stored on the `MyData` folder. There are one folder per user and several files `StreamingHistoryN.json` per user's folder.

### Create a Spotify Developer account

You need a Spotify Developer Account in order to make some requests to the Spotify API. You can create one with the following link [Spotify Developer Account](https://developer.spotify.com/).

Make sure to create a new application, you will need your application keys for the following steps.

### Features extraction

Create a json file `my_spotify_dev_account.json` on this folder with the keys and values :

```
{
    "username": "your_user_name",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uri": "http://localhost:7777/callback",
    "scope": "user-read-recently-played"
}
```

Required Python libraries :

- sklearn
- spotipy
- numpy
- pandas
- ...

Then, open a command line, make sure you have Python installed with all the required libraries (cf the list above) and add the redirect_uti `http://localhost:7777/callback` in the white-listed redirect-URI list in your app settings. Then run the following command line :

```
python my_spotify_history_enrichment.py data_folder processed_data_folder
```

with `data_folder = "MyData/User3"` and `processed_data_folder = "ProcessedData/User3"` as follows :

```
python my_spotify_history_enrichment.py "MyData/User3" "ProcessedData/User3"
```

It can take some time and you need an internet connection to connect the Spotify API. The songs are extracted from the StreamingHistory files and then their features are requested to the Spotify API.

The files `{folder}/track_data.json` is created.
This file includes for every songs listened a list of features (float values) such as **danceability**, **energy**, **loudness**, **speechiness**, **acousticness**, **instrumentalness**, **liveness**, **valence**, **tempo**, **duration_ms**, **popularity** but also the artists and the album's name.

Then some requests to the Spotify API searchs for every user listened songs a list of recommendations. The files `{folder}/recommendations_songs.json` includes for every recommended songs the list of its features.

Both data, users data and recommendations, are processed by Python.

First, the **data are normalized** using sklearn MinMaxScaler algorithm.

Then, songs are **clustered** using sklearn **KMeans** algorithm.

The dimension of the data (11 numerical dimensions) is reduced by performing a **PCA** with sklearn. The PCA allows to reduce the dimension to 2 dimensions with **60% of explained data variability**. It allows us to project the songs on a 2D space and to visualize the distance between them.

The cluster and the new coordinates of each song are stored with songs' features in the json file `songs_json.json` for recommendations and in the json file `user_songs_json.json` for user listened songs.

Both json file `songs_json.json` and `user_songs_json.json` are used to create a recommendation visualization.

## Upload your data on the visualization

You can now go on the dashboard [Spotify project](https://theo-malka.github.io/), upload the different files, the streaming history files on the first selector, the user songs on the second one and the songs on the last one, and validate.
The dashboard will be updated with your personnal data.
