<a href="#english-version">English</a>

## 추천 서버

muse의 추천 서버입니다.

이 서버는 muse와 동일한 PostgreSQL 데이터베이스에 접근하지만
read-only role만 부여받은 계정으로 연결됩니다.

```
postgresql+psycopg2://rec_engine:<Password>@localhost:5432/muse
```

이를 통해 불필요한 데이터 조작을 원천적으로 방지하며, 추천 계산에 필요한 조회 쿼리만 수행합니다.


## 기능

### 1. 컨텐츠 기반 추천 로직

- 사용자가 평점을 남긴 노래들을 기반으로 가중 평균을 계산하여 **사용자 취향 벡터**를 생성합니다.
- 아직 평가하지 않은 나머지 노래들도 벡터화합니다.
- 1번과 2번에서 벡터로 만들 때 쓰는 노래 features는 energy, danceability, valence, tempo입니다.
    - 이 때 tempo(35\~228)는 나머지 값(0\~1)들과 스케일이 다르기 때문에 정규화를 먼저 진행합니다.
    - 이 피쳐들만으로도 노래의 전반적인 분위기 표현엔 적당하다 판단해 개발의 용이성을 위해 전체 피쳐 12개 중 4개만 추천 기준으로 활용했습니다
* 사용자 벡터와 후보 벡터 간의 코사인 유사도를 계산하여
  상위 50곡 추천 풀을 생성합니다. (홈 화면에선 이 풀에서 랜덤 10개를 선정해 띄웁니다)
  

### 2. 욕설 필터링

* 사용자가 muse 서비스 내에서 남기는 모든 텍스트에 대해 비속어 포함 여부를 검사합니다.
* 키워드 기반 욕설 감지 라이브러리 [korcen](https://github.com/Tanat05/korcen/tree/main)을 활용하여 빠르고 가벼운 필터링을 수행합니다.

---

<div id="english-version"></div>


# Recommendation Server

This is the recommendation engine for the **muse** service.

The server accesses the same PostgreSQL database as the main muse application but connects using an account granted a **read-only role**.

```
postgresql+psycopg2://rec_engine:<Password>@localhost:5432/muse

```

This architecture inherently prevents unnecessary data manipulation and ensures the server only performs the read queries required for recommendation calculations.

---

## Features

### 1. Content-Based Filtering Logic

* **User Preference Vectoring**: Generates a user preference vector by calculating a weighted average of songs the user has rated.
* **Candidate Vectoring**: Converts unrated songs into vectors for comparison.
* **Feature Selection & Normalization**: Recommendations are based on four key song features: `energy`, `danceability`, `valence`, and `tempo`.
* **Normalization**: Since `tempo` (35–228) operates on a different scale compared to the other features (0–1), it is normalized before processing.
* **Optimization**: To ensure development efficiency while maintaining accuracy in capturing a song's overall atmosphere, these 4 features were selected from the total 12 available.


* **Similarity Calculation**: Calculates the **Cosine Similarity** between the user vector and candidate vectors to generate a recommendation pool of the top 50 songs.
* *Note: The home screen randomly selects and displays 10 songs from this pool.*



### 2. Profanity Filtering

* **Text Validation**: Scans all user-generated text within the muse service for profanity or abusive language.
* **Library Integration**: Utilizes [korcen](https://github.com/Tanat05/korcen/tree/main), a keyword-based profanity detection library, to perform fast and lightweight filtering.
