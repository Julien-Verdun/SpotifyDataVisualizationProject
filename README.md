# SpotifyDataVisualizationProject

## Get your data

Get your data from your Spotify account [My Personnal Data](https://support.spotify.com/uk/article/data-rights-and-privacy-settings/).

You can get a ZIP file with a copy of most of your personal data by using the automated Download your data function on the Privacy Settings section of your account page.

The download includes information about your playlists, streaming history, searches, a list of items saved in Your Library, the number of followers you have, the number of accounts you follow, the names of the artists you follow, and your payment and subscription data.

## Data processing with Python

The data are stored on the `MyData` folder. There are several files `StreamingHistoryN.json`.

### Create a Spotify Developer account

You need a Spotify Developer Account in order to make some requests to the Spotify API. You can create one with the following link [Spotify Developer Account](https://developer.spotify.com/).

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

Then choose the folder you want to extract features from on the file `extract_songs_features.py`, for example
with `folder = "Julien"` you will get the features by all the songs listened by me.

Make sur you got all the required python librarires installed (especially **spotipy**) and then run `python extract_song_features.py`.

It can make some time and you need an internet connection to connect the Spotify API. The songs will be extracted from the StreamingHistory files and then their features will be requested to the Spotify API.

The file `{folder}/track_data.json` will then be created.
This file includes for every songs listened a list of features (float values) such as **danceability**,**energy**,**loudness**,**speechiness**,**acousticness**,**instrumentalness**,**liveness**,**valence**, **tempo**,**duration_ms**,**popularity** but also the artists and the album's name.

### Data normalization

The jupyteer notebook `my_spotify_data_enrichment.ipynb` allows you to normalize the data. It creates a json file `{folder}/track_data_normalized.json`. Make sure you set the right folder's name.

## Data Visualization

D3.js and Observable

Put the links of the notebook observable
