from typing import List
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.recommendation import SongFeature, Rating


def fetch_user_ratings(db:Session, user_id:int) -> List[Rating]:
    # 특정 유저가 남긴 곡 평점 목록 조회

    sql = text("""
        SELECT song_id, score
        FROM song_ratings
        WHERE user_id = :user_id AND score IS NOT NULL
    """)
    rows = db.execute(sql, {"user_id": user_id}).mappings().all()
    return [Rating(song_id=r["song_id"], score=r["score"]) for r in rows]


def fetch_candidate_songs(db: Session, user_id: int) -> List[SongFeature]:
    """
    유저가 평가하지 않은 곡들 리턴. 이 곡들은 추천의 대상이 된다.
    """
    sql = text("""
        SELECT
            s.id           AS song_id,
            s.title        AS title,
            s.artist       AS artist,
            s.playlist_genre,
            s.energy,
            s.danceability,
            s.valence,
            s.tempo,
            s.loudness,
            s.speechiness,
            s.instrumentalness,
            s.acousticness,
            s.mode,
            s.duration_ms
        FROM songs s
        WHERE NOT EXISTS (
            SELECT 1
            FROM song_ratings r
            WHERE r.song_id = s.id
                AND r.user_id = :user_id
        )
    """)

    rows = db.execute(sql, {"user_id": user_id}).mappings().all()
    return [
        SongFeature(
            song_id=row["song_id"],
            title=row["title"],
            artist=row["artist"],
            playlist_genre=row["playlist_genre"],
            energy=row["energy"],
            danceability=row["danceability"],
            valence=row["valence"],
            tempo=row["tempo"],
            loudness=row["loudness"],
            speechiness=row["speechiness"],
            instrumentalness=row["instrumentalness"],
            acousticness=row["acousticness"],
            mode=row["mode"],
            duration_ms=row["duration_ms"],
        )
        for row in rows
    ]


def fetch_rated_songs(db: Session, user_id: int) -> List[SongFeature]:
    """
    유저가 평점을 남긴 곡들의 피쳐 조회. 유저 취향 벡터 만드는데 사용됨
    """
    sql = text("""
        SELECT
            s.id           AS song_id,
            s.title        AS title,
            s.artist       AS artist,
            s.playlist_genre,
            s.energy,
            s.danceability,
            s.valence,
            s.tempo,
            s.loudness,
            s.speechiness,
            s.instrumentalness,
            s.acousticness,
            s.mode,
            s.duration_ms
        FROM songs s
        JOIN song_ratings r
          ON r.song_id = s.id
        WHERE r.user_id = :user_id
    """)
    rows = db.execute(sql, {"user_id": user_id}).mappings().all()
    return [
        SongFeature(
            song_id=row["song_id"],
            title=row["title"],
            artist=row["artist"],
            playlist_genre=row["playlist_genre"],
            energy=row["energy"],
            danceability=row["danceability"],
            valence=row["valence"],
            tempo=row["tempo"],
            loudness=row["loudness"],
            speechiness=row["speechiness"],
            instrumentalness=row["instrumentalness"],
            acousticness=row["acousticness"],
            mode=row["mode"],
            duration_ms=row["duration_ms"],
        )
        for row in rows
    ]