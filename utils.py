from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from pprint import pprint
from contextlib import contextmanager

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())



def get_song_info(ids):
    res = sp.tracks(ids) 

    artist_detail_urls = []
    album_image_urls = []

    track_list = res['tracks']
    for track in track_list:
        artist_detail_url = track["album"]["artists"][0]["external_urls"]["spotify"]
        album_image_url = track["album"]["images"][1]["url"]
        
        artist_detail_urls.append(artist_detail_url)
        album_image_urls.append(album_image_url)
    
    return artist_detail_urls, album_image_urls



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


if __name__ == "__main__":
    from dotenv import load_dotenv
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    load_dotenv()

    DATABASE_URL = "postgresql+psycopg2://postgres:1533@localhost:5432/muse"
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=True,
    )

    SessionLocal  = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @contextmanager
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    
    with get_db() as db:
        # 1. songs 데이터 갖고오기
        songs = db.execute(text("SELECT spotify_id FROM songs")).fetchall()

        # 2. batch 50개마다 ids로 묶어서 get_song_info 함수 호출(tracks api 최대 인풋 id개수가 50개임)
        for song_batch_start_idx in range(0, len(songs), 50):
            ids = [song[0] for song in songs[song_batch_start_idx:song_batch_start_idx+50]]
            artist_detail_urls, album_image_urls = get_song_info(ids)

            import time
            time.sleep(2) # 3. api 너무 연속으로 호출하면 429 뜰것 같아서

            # 4. 각 spotify_id로 찾은 열의 artist_detail_url과 album_image_url을 songs 테이블에 업데이트
            for song_idx in range(len(ids)):
                db.execute(text("update songs set artist_detail_url = :artist_detail_url, album_image_url = :album_image_url where spotify_id = :spotify_id"), {
                    "artist_detail_url": artist_detail_urls[song_idx],
                    "album_image_url": album_image_urls[song_idx],
                    "spotify_id": ids[song_idx],
                })

            db.commit()



        
            
            




            
            
            
