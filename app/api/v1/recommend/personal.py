# app/api/v1/recommend.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.recommendation import PersonalRecResponse
from app.services.recommendation_service import recommend_for_user

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.get("/personal", response_model=PersonalRecResponse)
def get_personal_recommendations(
    user_id: int = Query(..., description="추천 대상 유저 ID"),
    top_n: int = Query(30, ge=1, le=100, description="추천 곡 개수"),
    db: Session = Depends(get_db),
):
    """
    컨텐츠 기반 개인화 추천 정식 엔드포인트.

    - 입력: user_id, top_n
    - 내부: DB 조회 + 취향 벡터 + cosine 기반 랭킹
    - 출력: PersonalRecResponse(JSON)
    """
    return recommend_for_user(db=db, user_id=user_id, top_n=top_n)
