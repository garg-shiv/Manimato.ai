import logging
from pathlib import Path
import os
from app.core.config import config
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles



env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)
config.init()

# Sanity check for env loading
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL not found in environment variables!")

from app.middlewares.cors import add_cors_middleware
from app.middlewares.request_logger import add_request_logger_middleware
from app.routers.health import router as health_router
from app.routers.v1.router import router as v1_router






logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info(f"Loaded DATABASE_URL: {database_url}")

app = FastAPI(
    title="Manim Code Generator API",
    description="API for generating Manim animations from natural language prompts",
    version="1.0.0",
)

# Add CORS middleware
add_cors_middleware(app)
# Add request logger middleware
add_request_logger_middleware(app)

# Include V1 router
app.include_router(v1_router, prefix="/api")
# Add this line near your other `include_router` calls
app.include_router(health_router)
# TODO: to be removed later
app.mount("/videos", StaticFiles(directory="generated"), name="videos")
