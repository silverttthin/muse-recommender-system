from fastapi import FastAPI
from app.api.v1.debug import router as debug_router
from app.api.v1.recommend.personal import router as recommend_router
from app.core.db import check_db_connection
from app.api.v1.profanity.profanity import router as profanity_router

app = FastAPI(
    title= "Music Recommendation API",
    version= "0.2.0",
)

app.include_router(debug_router, prefix="/api/v1")
app.include_router(recommend_router, prefix="/api/v1")
app.include_router(profanity_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    try:
        db_ok = check_db_connection()
    except Exception as e:
        return {
            "status": "error",
            "db": False,
            "detail": str(e),
        }
    return {
        "status": "ok" if db_ok else "error",
        "db": db_ok,
    }


