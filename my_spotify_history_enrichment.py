from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import requests
import spotipy
from typing import List
from os import listdir
import json
import sys
from tqdm import tqdm


"""
Credentials to : 
https://towardsdatascience.com/get-your-spotify-streaming-history-with-python-d5a208bbcbd3

Spotify data places on the folder MyData
"""

# python my_spotify_history_enrichment.py "MyData/User3" "ProcessedData/User3"

if len(sys.argv) >= 3:
    folder_path = sys.argv[1]
    target_path = sys.argv[2]
else:
    folder_path = 'MyData/User3'
    target_path = 'ProcessedData/User3'


def get_streamings(path: str = folder_path) -> List[dict]:

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


def get_user_features(track_id: str, token: str) -> dict:
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


streamings = get_streamings(folder_path)
unique_tracks = list(set([streaming['trackName']
                          for streaming in streamings]))

print("Getting all listened songs features")
all_features = {}
all_recommendations = {}
for i in tqdm(range(len(unique_tracks))):
    track = unique_tracks[i]
    [track_id, track_artist, track_album, popularity] = get_id(track, token)
    features = get_user_features(track_id, token)
    if features:
        features["id"] = track_id
        features["artist"] = track_artist
        features["album"] = track_album
        features["popularity"] = popularity
        all_features[track] = features
        all_recommendations[track_id] = get_recommendations([track_id], token)


with open(target_path + '/track_data.json', 'w') as outfile:
    json.dump(all_features, outfile)


def get_songs_features(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([track_id])[0]
        track_features = sp.track(track_id)
        features["name"] = track_features["name"]
        features["popularity"] = track_features["popularity"]
        features["artists"] = [track_features["artists"][k]["name"]
                               for k in range(len(track_features["artists"]))]
        features["album"] = track_features["album"]["name"]
        return features
    except:
        return None


print("Getting all recommended songs")

unique_ids = []
for i in tqdm(range(len(list(all_recommendations.keys())))):
    ids = list(all_recommendations.keys())[i]
    for id_reco in all_recommendations[ids]:
        if id_reco not in unique_ids:
            unique_ids.append(id_reco)

print("Getting all features from recommended songs")

all_features = {}
for i in tqdm(range(len(unique_ids))):
    track_id = unique_ids[i]
    features = get_songs_features(track_id, token)
    if features:
        all_features[track_id] = features


with open(target_path + '/recommendations_songs.json', 'w') as outfile:
    json.dump(all_features, outfile)


print("Data processing")

recommendations_data = pd.read_json(
    target_path + '/recommendations_songs.json').T

numerical_features = ["danceability", "energy", "loudness", "speechiness",
                      "acousticness", "instrumentalness", "liveness", "valence", "tempo", "popularity"]
other_features = ["mode", "key", "id", "duration_ms",
                  "artists", "name", "id", "artists", "album"]

numerical_recommendations_data = recommendations_data[numerical_features]


track_np = np.array(numerical_recommendations_data.values)


print("Data normalization")

minMaxScaler = MinMaxScaler().fit(track_np)
track_np = minMaxScaler.transform(track_np)

track_data_normalized = pd.DataFrame(
    track_np, columns=numerical_features, index=recommendations_data.index)

for feature in other_features:
    track_data_normalized[feature] = recommendations_data[feature]


print("Data clustering")
n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(track_np)


kmeans_cluster_labels = kmeans.labels_

kmeans_cluster_centers = kmeans.cluster_centers_

track_data_normalized["kmeans_cluster"] = kmeans_cluster_labels


# sub-clusterisation : each cluster is divided into small clusters
n_sub_clusters = 10
track_data_normalized["kmeans_subcluster"] = 0

for i in range(n_clusters):
    num_track_data_np = np.array(
        track_data_normalized[track_data_normalized["kmeans_cluster"] == i][numerical_features])

    subkmeans = KMeans(n_clusters=n_sub_clusters,
                       random_state=0).fit(num_track_data_np)

    track_data_normalized.loc[track_data_normalized["kmeans_cluster"]
                              == i, "kmeans_subcluster"] = subkmeans.labels_


print("Dimension reduction with PCA")
pca = PCA(n_components=2)
pca.fit(track_np)

track_np_pca = pca.transform(track_np)

track_data_normalized["x"] = track_np_pca[:, 0]
track_data_normalized["y"] = track_np_pca[:, 1]


cluster_centers_pca = pca.transform(kmeans_cluster_centers)


def comput_dist(x, y, cluster):
    return 1000*np.sqrt((x-cluster_centers_pca[cluster][0])**2 + (y-cluster_centers_pca[cluster][1])**2)


track_data_normalized["dist"] = track_data_normalized.apply(
    lambda x: comput_dist(x['x'], x['y'], x['kmeans_cluster']), axis=1)


songs_df = track_data_normalized[["name", "kmeans_cluster", "kmeans_subcluster",
                                  "x", "y", "dist", "id", "artists", "album"]+numerical_features]


songs_df.T.to_json(target_path+'/songs_json.json')

track_data = pd.read_json(target_path+'/track_data.json')
track_data = track_data.loc[["danceability", "energy", "loudness", "speechiness", "acousticness",
                             "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "popularity", "artist", "album", "id"]].T


track_np_user = np.array(track_data[numerical_features].values)

track_np_user = minMaxScaler.transform(track_np_user)

track_data_normalized = pd.DataFrame(
    track_np_user, columns=numerical_features, index=track_data.index)


track_data_normalized["artist"] = track_data["artist"]
track_data_normalized["album"] = track_data["album"]
track_data_normalized["id"] = track_data["id"]
track_data_normalized["name"] = track_data.index
track_data_normalized["duration_ms"] = track_data["duration_ms"]


files = [folder_path + '/' + x for x in listdir(folder_path)
         if x.split('.')[0][:-1] == 'StreamingHistory']

streaming_history_df = pd.read_json(files[0])
if len(files) > 1:
    for file_path in files[1:]:
        streaming_history_df = pd.concat(
            (streaming_history_df, pd.read_json(file_path)))

countPerTrack = pd.value_counts(streaming_history_df["trackName"])

msPlayedSum = streaming_history_df.groupby(
    "trackName").agg({"msPlayed": ["sum"]})

track_data_normalized["name"] = track_data_normalized.index


def trackCount(x):
    if countPerTrack.loc[x["name"]]:
        return countPerTrack.loc[x["name"]]
    return 0


track_data_normalized["countPerTrack"] = track_data_normalized.apply(
    lambda x: trackCount(x), axis=1)


def trackMsPlayed(x):
    if msPlayedSum.loc[x["name"]][0]:
        return msPlayedSum.loc[x["name"]][0]
    return 0


track_data_normalized["msPlayedSum"] = track_data_normalized.apply(
    lambda x: trackMsPlayed(x), axis=1)


def get_reco(x, recommendations=all_recommendations):
    if x["id"] in recommendations:
        return recommendations[x["id"]]
    else:
        return []


track_data_normalized["recommendations"] = track_data_normalized.apply(
    lambda x: get_reco(x), axis=1)


user_track_data = track_data_normalized

numerical_user_track_data = user_track_data[numerical_features]

user_track_np = np.array(numerical_user_track_data.values)


user_cluster = kmeans.predict(user_track_np)
user_track_np_pca = pca.transform(user_track_np)


user_track_data_normalized = pd.DataFrame(
    user_track_np, columns=numerical_features, index=user_track_data.index)


for feature in ["duration_ms", "artist", "album", "countPerTrack", "msPlayedSum", "id", "recommendations"]:
    user_track_data_normalized[feature] = user_track_data[feature]


user_track_data_normalized["kmeans_cluster"] = user_cluster


user_track_data_normalized["x"] = user_track_np_pca[:, 0]
user_track_data_normalized["y"] = user_track_np_pca[:, 1]


user_track_data_normalized["dist"] = user_track_data_normalized.apply(
    lambda x: comput_dist(x['x'], x['y'], x['kmeans_cluster']), axis=1)


user_track_data_normalized["name"] = user_track_data_normalized.index


user_songs_df = user_track_data_normalized[["name", "artist", "album", "kmeans_cluster", "x",
                                            "y", "dist", "countPerTrack", "msPlayedSum", "id", "recommendations"] + numerical_features]
user_songs_df.reset_index(drop=True)


user_songs_df.T.to_json(target_path + "/user_songs_json.json")
