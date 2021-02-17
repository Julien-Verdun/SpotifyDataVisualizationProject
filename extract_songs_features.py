import requests
import spotipy
import ast
from typing import List
from os import listdir
import json

"""
Credentials to : 
https://towardsdatascience.com/get-your-spotify-streaming-history-with-python-d5a208bbcbd3

Spotify data places on the folder MyData
"""


def get_streamings(path: str = 'MyData/User1') -> List[dict]:

    files = [path + '/' + x for x in listdir(path)
             if x.split('.')[0][:-1] == 'StreamingHistory']

    all_streamings = []

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            all_streamings = json.load(f)
    return all_streamings


# Remplacer par vos données
with open("my_spotify_dev_account.json", 'r', encoding='utf-8') as my_spotify_dev_account:
    my_spotify_dev_account = json.load(my_spotify_dev_account)

token = spotipy.util.prompt_for_user_token(username=my_spotify_dev_account["username"],
                                           scope=my_spotify_dev_account["scope"],
                                           client_id=my_spotify_dev_account["client_id"],
                                           client_secret=my_spotify_dev_account["client_secret"],
                                           redirect_uri=my_spotify_dev_account["redirect_uri"])

print("TOKEN : ", token)


def get_id(track_name: str, token: str) -> str:
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer ' + token
    }
    params = [('q', track_name), ('type', 'track')]
    try:
        response = requests.get('https://api.spotify.com/v1/search',
                                headers=headers, params=params, timeout=5)
        json = response.json()
        first_result = json['tracks']['items'][0]
        track_id = first_result['id']
        track_artist = []
        for artist in first_result['artists']:
            track_artist.append(artist["name"])
        track_album = first_result["album"]["name"]
        popularity = first_result["popularity"]
        return [track_id, track_artist, track_album, popularity]
    except:
        return [None, None, None, None]


def get_features(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([track_id])
        return features[0]
    except:
        return None


def get_recommendations(track_names, token):
    headers = {
        'Authorization': f'Bearer ' + token
    }
    params = [('seed_tracks', ",".join(track_names)),
              ('seed_artists', ",".join([])), ('seed_genres', ",".join([]))]
    try:
        response = requests.get('https://api.spotify.com/v1/recommendations',
                                headers=headers, params=params, timeout=5)
        json = response.json()
        recommendations = []
        for track in json["tracks"]:
            recommendations.append(track["id"])
        return recommendations
    except:
        return None


folder_path = 'MyData/User2'
target_path = 'ProcessedData/User2'
streamings = get_streamings(folder_path)
# streamings = streamings[0:1]
unique_tracks = list(set([streaming['trackName']
                          for streaming in streamings]))

all_features = {}
all_recommendations = {}
for track in unique_tracks:
    [track_id, track_artist, track_album, popularity] = get_id(track, token)
    features = get_features(track_id, token)
    if features:
        features["id"] = track_id
        features["artist"] = track_artist
        features["album"] = track_album
        features["popularity"] = popularity
        all_features[track] = features
        all_recommendations[track_id] = get_recommendations([track_id], token)


with open(target_path + '/track_data.json', 'w') as outfile:
    json.dump(all_features, outfile)


with open(target_path + '/recommendations.json', 'w') as outfile:
    json.dump(all_recommendations, outfile)
