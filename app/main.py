from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.v1.endpoints.router import router

app = FastAPI()
app.mount("/videos", StaticFiles(directory="generated"), name="videos")
app.include_router(router, prefix="/api/v1")
