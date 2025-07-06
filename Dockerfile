FROM python:3.11-slim-bookworm

# --- Env vars for clean builds and runtime ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# --- Install system + build dependencies for Manim + pycairo ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libcairo2-dev \
    libpango1.0-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    ffmpeg \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Install uv package manager ---
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# --- Copy dependency metadata ---
COPY pyproject.toml uv.lock ./

# --- Install all locked dependencies ---
RUN uv sync --frozen --no-cache

# --- Copy app source code ---
COPY . .

# --- Create non-root user for security ---
RUN adduser --disabled-password --gecos '' --shell /bin/bash user && \
    chown -R user:user /app

USER user

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
