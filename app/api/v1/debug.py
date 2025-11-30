from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.data_access import (
    fetch_user_ratings,
    fetch_candidate_songs,
    fetch_rated_songs,
)
from app.services.content_based import build_user_preference_vector

router = APIRouter(
    prefix="/debug",
    tags=["debug"],
)

@router.get("/user/{user_id}/ratings")
def get_user_ratings(user_id: int, db: Session = Depends(get_db)):
    ratings = fetch_user_ratings(db, user_id)
    return {
        "user_id": user_id,
        "ratings": [r.model_dump() for r in ratings],
    }


@router.get("/user/{user_id}/candidates")
def debug_user_candidates(user_id: int, db: Session = Depends(get_db)):
    songs = fetch_candidate_songs(db, user_id)
    # 디버깅용이라 50개만
    songs = songs[:50]
    return {"user_id": user_id, "count": len(songs), "songs": [s.model_dump() for s in songs]}


@router.get("/user/{user_id}/preference-vector")
def debug_user_preference_vector(user_id: int, db: Session = Depends(get_db)):
    # 1. 유저가 남긴 별점 곡들의 레이팅 갖고오기
    ratings = fetch_user_ratings(db, user_id)

    # 2. 유저가 rating 남긴 곡들의 피쳐 갖고오기
    rated_songs = fetch_rated_songs(db, user_id)

    # 3. id-songFeature 해시맵 만들기
    songs_by_id = {s.song_id: s for s in rated_songs}

    # 4. 취향 벡터 계산
    user_vec = build_user_preference_vector(ratings, songs_by_id)

    return {
        "user_id": user_id,
        "ratings": [r.model_dump() for r in ratings],
        "rated_songs": [s.model_dump() for s in rated_songs],
        "user_vector": user_vec.tolist() if user_vec is not None else None,
    }
