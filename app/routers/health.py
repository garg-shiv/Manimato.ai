# app/routers/health.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "0.1.0"}
