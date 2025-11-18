from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from pprint import pprint

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())



def get_song_info(track_id):
    """
    주어진 트랙 id로 트랙 정보를 반환
    """
    track = sp.track(track_id)
    track.pop('available_markets', None)
    if 'album' in track:
        track['album'].pop('available_markets', None)
    
    artist_name = track['artists'][0]['name']
    artist_detail_url = track['artists'][0]['external_urls']['spotify']
    album_image_url = track['album']['images'][1].get('url', None)
    song_detail_url = track['external_urls']['spotify']

    return {
        'artist_name': artist_name,
        'artist_detail_url': artist_detail_url,
        'album_image_url': album_image_url,
        'song_detail_url': song_detail_url
    }


def get_chart_from_spotify():
    url = 'https://charts-spotify-com-service.spotify.com/public/v0/charts'

    response = requests.get(url)
    chart = []
    for idx, entry in enumerate(response.json()['chartEntryViewResponses'][0]['entries'], start=1):
        chart.append({
            "Rank": idx,
            "Artist": ', '.join([artist['name'] for artist in entry['trackMetadata']['artists']]),
            "TrackName": entry['trackMetadata']['trackName'],
        })
        if idx == 10:
            break
    
    return chart
