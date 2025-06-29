from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints.router import router
import os
os.makedirs("generated", exist_ok=True)
app = FastAPI()
app.mount("/videos", StaticFiles(directory="generated"), name="videos")
app.include_router(router, prefix="/api/v1")
