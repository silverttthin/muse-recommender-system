from typing import List, Dict, Tuple, Optional

import numpy as np

from ..schemas.recommendation import Rating, SongFeature, RecommendationItem, PersonalRecResponse


# 추천에 사용할 피쳐들
FEATURE_KEYS = ["energy", "danceability", "valence", "tempo"]


# 어떤 노래의 피쳐 중 추천 키들만을 float 리스트, 즉 벡터로 리턴하는 함수
def song_to_vector(song: SongFeature) -> np.ndarray:
    values: list[float] = []

    for key in FEATURE_KEYS:
        val = getattr(song, key, None) # song 객체에서 key 값을 가져오고 없다면 None을 반환
        if val is None:
            values.append(0.0)
        else:
            if key == "tempo":
                normalized_val = (float(val) - 35.226)/(228.571 - 35.226) # tempo 피쳐 데이터 중 최소, 최대 값
                values.append(normalized_val)
            else:
                values.append(float(val))
    
    return np.array(values, dtype=float)



def build_user_preference_vector(
    ratings: List[Rating], # 노래 id, 평점을 담은 객체
    songs_by_id: Dict[int, SongFeature], # 노래 id - 노래 피쳐 데이터 해시맵
    min_score_for_like: float = 4.0,
) -> Optional[np.ndarray]:

    # 유저 평점 기록 중 4점 이상만 추출
    liked = [r for r in ratings if r.score >= min_score_for_like]

    # 가중평균 =  각 값 * 각 가중치 / 전체 가중치 합
    def weighted_average(rs: List[Rating]) -> Optional[np.ndarray]:
        if not rs: return None

        vecs, weights = [], []

        for r in rs: # 평점 기록 하나하나마다
            song: SongFeature = songs_by_id.get(r.song_id) # 노래 피쳐 데이터를 얻어와서
            if not song: 
                continue

            vec = song_to_vector(song) # 해당 노래 벡터를 얻어
            vecs.append(vec) # vecs 배열에 넣고
            weights.append(float(r.score)) # weights 배열에 해당 노래에 유저가 매긴 평점을 삽입
        
        if not vecs:
            return None
        
        V = np.vstack(vecs) # 벡터 배열을 수직으로 쌓은 행렬 V를 얻는다
        w = np.array(weights) 
        w_sum = w.sum() # weights 배열의 합
        if w_sum == 0:
            return None

        # 0. 가져온 유저 평점 작성된 노래 개수가 3개라고 가정할 때
        # 1. w를 w[:,None]으로 두어 (3,)를 (3,1)로 변환, 즉 열벡터로 둔다. 각 행은 노래, 열은 별점이니 당연히 1개
        # 2. V는 (3,4)로 각 행은 노래, 열은 피쳐 개수이니 3,4
        # 3. 곱하면 3,1 * 3,4라 안맞지만 넘파이 브로드캐스팅 기능 지원으로 자동으로 3,4로 변환되어 곱해진다.
        #    이 곱하는 것의 의미는 각 노래마다 그 노래의 가중치 만큼 피쳐값들에 곱해지는 것이다.
        # 4. sum으로 합치되 axis=0 옵션을 주어 열 방향으로 합친다. 열은 피쳐였으므로 각 노래마다의 피쳐 속성끼리 합해진다. 템포끼리, 에너지끼리,...
        # 5. 이후 w_sum으로 나누면 이것이 가중평균값, 즉 피쳐 공간에서 유저의 선호도가 조합된 벡텨 결과물을 얻는다.
        #    w_sum으로 나누는 이유는 우리는 가중 평균 구하는 식에서 별점, 즉 rating을 가중치로 사용했기 때문에 그 가중치 합을 나눠줘야 한다.
        user_vec = (w[:, None] * V).sum(axis=0) / w_sum 
        return user_vec

    user_vec = weighted_average(liked)
    if user_vec is not None:
        return user_vec
    
    # liked가 비어있다 == 4점 이상 준 데이터가 없다 == 유저 선호도 벡터를 만들 수 없다
    # 그러므로 모든 노래에 대해 가중평균을 구하고 그 중 가장 높은 값을 가진 노래를 선택한다.
    user_vec = weighted_average(ratings)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None:
        return 0.0
    
    anorm = np.linalg.norm(a)
    bnorm = np.linalg.norm(b)
    if anorm < 1e-8 or bnorm < 1e-8:
        return 0.0

    return float(np.dot(a,b) / (anorm * bnorm))


def score_candidates(
    user_vec: np.ndarray,
    candidates: List[SongFeature],
    top_n: int = 30,
) -> List[RecommendationItem]:
    """
    유저 취향 벡터와 후보 곡 리스트를 받아,
    코사인 유사도 기준으로 Top-N 추천 결과를 반환.
    """
    scored: list[tuple[int, float]] = []

    for song in candidates:
        vec = song_to_vector(song)
        sim = cosine_similarity(user_vec, vec)
        scored.append((song.song_id, sim))

    scored.sort(key=lambda x: x[1], reverse=True)

    top = scored[:top_n]

    items = [
        RecommendationItem(song_id=song_id, score=score)
        for song_id, score in top
    ]
    return items



def build_content_based_recommendations(
    user_id: int,
    ratings: List[Rating],
    candidates: List[SongFeature],
    top_n: int = 10,
) -> PersonalRecResponse:
    """
    컨텐츠 기반 추천 전체 파이프라인:
    - 취향 벡터 만들기
    - 후보 곡에 점수 매기기
    - PersonalRecResponse 형태로 리턴
    """

    songs_by_id: dict[int, SongFeature] = {s.song_id: s for s in candidates}

    user_vec = build_user_preference_vector(ratings, songs_by_id)

    # 콜드 스타트 처리: rating이 전혀 없다면 그냥 빈 추천 반환
    if user_vec is None:
        return PersonalRecResponse(
            user_id=user_id,
            recommendations=[],
        )

    items = score_candidates(user_vec, candidates, top_n=top_n)
    return PersonalRecResponse(
        user_id=user_id,
        recommendations=items,
    )


