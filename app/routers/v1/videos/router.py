from fastapi import APIRouter

from app.routers.v1.videos import generate_video

router = APIRouter()
router.include_router(generate_video.router, tags=["video"])
