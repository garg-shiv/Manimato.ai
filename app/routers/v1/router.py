from fastapi import APIRouter

from app.routers.v1.auth.routes import router as auth_router
from app.routers.v1.message import routes as message_router
from app.routers.v1.videos import routes as video_routes

router = APIRouter(prefix="/v1")

router.include_router(video_routes.router)

router.include_router(message_router.router)

router.include_router(auth_router)