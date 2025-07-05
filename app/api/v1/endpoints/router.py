from fastapi import APIRouter

from app.api.v1.endpoints import generate_video

router = APIRouter()
router.include_router(generate_video.router, tags=["video"])
