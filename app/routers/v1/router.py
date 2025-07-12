from fastapi import APIRouter

from app.routers.v1.auth import signin as signin_routes
from app.routers.v1.auth import signup as signup_routes
from app.routers.v1.message import routes as message_router
from app.routers.v1.videos import routes as video_routes
from app.routers.v1.auth.routes import router as auth_router

router = APIRouter(prefix="/v1")

router.include_router(video_routes.router)
router.include_router(signin_routes.router, tags=["auth"])
router.include_router(signup_routes.router, tags=["auth"])
router.include_router(message_router.router)

router.include_router(auth_router)