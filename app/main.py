from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers.v1.endpoints.router import router as main_router
from app.routers.v1.auth.signup import router as signup_router
from app.routers.v1.auth.signin import router as signin_router
from app.middlewares.cors import add_cors_middleware
from app.middlewares.request_logger import add_request_logger_middleware

app = FastAPI()

# Add CORS middleware
add_cors_middleware(app)
# Add request logger middleware
add_request_logger_middleware(app)

# ✅ INCLUDE these as API routers:
app.include_router(signup_router, prefix="/auth")
app.include_router(signin_router, prefix="/auth")
app.include_router(main_router, prefix="/api/v1")

# ✅ Mount ONLY static files here:
app.mount("/videos", StaticFiles(directory="generated"), name="videos")
