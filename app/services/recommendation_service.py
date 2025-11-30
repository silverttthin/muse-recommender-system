# app/services/recommendation_service.py
from sqlalchemy.orm import Session

from app.schemas.recommendation import PersonalRecResponse
from app.services.data_access import (
    fetch_user_ratings,
    fetch_rated_songs,
    fetch_candidate_songs,
)
from app.services.content_based import (
    build_user_preference_vector,
    score_candidates,
)


def recommend_for_user(
    db: Session,
    user_id: int,
    top_n: int = 30,
) -> PersonalRecResponse:
    """
    1. 유저의 rating 데이터 조회
    2. rating 남긴 곡들의 feature 조회 → 취향 벡터 생성
    3. 아직 평가 안 한 곡들(candidate)에 점수 매기기
    4. PersonalRecResponse로 반환
    """
    # 1) 유저가 매긴 평점
    ratings = fetch_user_ratings(db, user_id)

    # 2) 그 평점을 가진 곡들의 feature (취향 벡터용)
    rated_songs = fetch_rated_songs(db, user_id)

    # 3) 아직 이 유저가 평가하지 않은 곡들 (추천 후보)
    candidates = fetch_candidate_songs(db, user_id)

    # song_id → SongFeature 맵
    songs_by_id = {s.song_id: s for s in rated_songs}

    # 취향 벡터
    user_vec = build_user_preference_vector(ratings, songs_by_id)

    # rating이 거의 없거나 feature가 없어서 벡터 못 만들면 → 빈 추천
    if user_vec is None:
        return PersonalRecResponse(
            user_id=user_id,
            algorithm="content_based_v1",
            recommendations=[],
        )

    # 후보 곡들에 점수 매기기
    items = score_candidates(user_vec, candidates, top_n=top_n)

    return PersonalRecResponse(
        user_id=user_id,
        algorithm="content_based_v1",
        recommendations=items,
    )
