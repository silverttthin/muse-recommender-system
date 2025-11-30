# app/api/v1/recommend.py
from fastapi import APIRouter, Query

from utils import check_profanity
import urllib.parse


router = APIRouter(prefix="/profanity", tags=["profanity"])

@router.get("/check")
def check_profanity_api(text: str = Query(..., description="프로파니티 체크할 텍스트")):
    return check_profanity(urllib.parse.unquote(text))
