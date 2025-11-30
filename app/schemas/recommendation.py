from typing import Optional, List
from pydantic import BaseModel

class Rating(BaseModel):
    song_id: int
    score: float


class SongFeature(BaseModel):
    song_id: int
    title: str
    artist: str
    playlist_genre: Optional[str] = None

    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    tempo: Optional[float] = None
    loudness: Optional[float] = None
    speechiness: Optional[float] = None
    instrumentalness: Optional[float] = None
    acousticness: Optional[float] = None
    mode: Optional[int] = None
    duration_ms: Optional[float] = None


class RecommendationItem(BaseModel):
    song_id: int
    score: float

class PersonalRecResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]