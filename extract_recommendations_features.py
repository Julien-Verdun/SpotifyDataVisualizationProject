import requests
import spotipy
import ast
from typing import List
import json


def get_recommendations(path):
    with open(path, 'r', encoding='utf-8') as f:
        recommendations_json = json.load(f)
    return recommendations_json


# Remplacer par vos données
with open("my_spotify_dev_account.json", 'r', encoding='utf-8') as my_spotify_dev_account:
    my_spotify_dev_account = json.load(my_spotify_dev_account)

token = spotipy.util.prompt_for_user_token(username=my_spotify_dev_account["username"],
                                           scope=my_spotify_dev_account["scope"],
                                           client_id=my_spotify_dev_account["client_id"],
                                           client_secret=my_spotify_dev_account["client_secret"],
                                           redirect_uri=my_spotify_dev_account["redirect_uri"])

print("TOKEN : ", token)


def get_features(track_id: str, token: str) -> dict:
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


target_path = 'ProcessedData/User2'
recommendations_json = get_recommendations(
    target_path + '/recommendations.json')

unique_ids = []
for ids in recommendations_json:
    for id_reco in recommendations_json[ids]:
        if id_reco not in unique_ids:
            unique_ids.append(id_reco)


all_features = {}
for track_id in unique_ids:
    features = get_features(track_id, token)
    if features:
        all_features[track_id] = features


with open(target_path + '/recommendations_songs.json', 'w') as outfile:
    json.dump(all_features, outfile)
