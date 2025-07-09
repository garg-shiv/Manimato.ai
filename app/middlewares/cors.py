from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(app):
    """Add CORS middleware to the FastAPI app. Allow all origins for dev; restrict in prod."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 