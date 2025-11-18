from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


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

    return {
        'artist_name': artist_name,
        'artist_detail_url': artist_detail_url,
        'album_image_url': album_image_url
    }
