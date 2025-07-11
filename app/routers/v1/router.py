from fastapi import APIRouter

from app.routers.v1.auth import signin as signin_routes
from app.routers.v1.auth import signup as signup_routes
from app.routers.v1.videos import routes as video_routes

router = APIRouter(tags=["V1"])

router.include_router(video_routes.router)
router.include_router(signin_routes.router, tags=["auth"])
router.include_router(signup_routes.router, tags=["auth"])
