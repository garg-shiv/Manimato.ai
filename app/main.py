import logging
from pathlib import Path
import os
from app.core.config import config
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from error_handler.handler import add_error_handlers



env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)
config.init()


from app.middlewares.cors import add_cors_middleware
from app.middlewares.request_logger import add_request_logger_middleware
from app.routers.health import router as health_router
from app.routers.v1.router import router as v1_router


app = FastAPI(
    title="Manim Code Generator API",
    description="API for generating Manim animations from natural language prompts",
    version="1.0.0",
)

# Add CORS middleware
add_cors_middleware(app)
# Add request logger middleware
add_request_logger_middleware(app)


add_error_handlers(app)
# Include V1 router
app.include_router(v1_router, prefix="/api")
# Add this line near your other `include_router` calls
app.include_router(health_router)
# TODO: to be removed later
app.mount("/videos", StaticFiles(directory="generated"), name="videos")
