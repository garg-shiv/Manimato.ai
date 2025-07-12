# FastAPI LLM Service

A FastAPI-based service for LLM interactions using Google's Gemini API and LangChain.

## Features

- **FastAPI Framework**: Modern, fast (high-performance) web framework
- **Gemini Integration**: Google's Gemini AI model integration
- **LangChain Support**: Advanced LLM chain operations
- **Async Operations**: Full async/await support
- **Request Logging**: Comprehensive request/response logging
- **Error Handling**: Custom exception handling
- **CORS Support**: Cross-origin resource sharing
- **Health Checks**: Built-in health check endpoints

## Project Structure

```
your_project/
├── app/
│   ├── api/                        # Entry point for HTTP APIs
│   │   ├── v1/
│   │   │   ├── endpoints/          # Route controllers
│   │   │   │   ├── chat.py
│   │   │   │   └── inference.py
│   │   │   └── router.py
│   ├── core/                       # Core system-wide functionality
│   │   ├── config.py               # Env + settings
│   │   ├── logger.py               # Logging setup
│   │   └── llm_provider.py         # Gemini/LangChain setup
│   ├── services/                   # Business logic layer
│   │   ├── chat_service.py
│   │   ├── chain_manager.py
│   │   └── prompt_templates.py
│   ├── schemas/                    # Pydantic request/response models
│   │   ├── chat.py
│   │   └── inference.py
│   ├── utils/                      # Shared utilities
│   │   ├── retry.py
│   │   └── helpers.py
│   ├── exceptions/                # Custom exception handlers
│   │   └── handlers.py
│   ├── middlewares/              # Custom middlewares (CORS, logging)
│   │   └── request_logger.py
│   ├── main.py                    # FastAPI app
│   └── deps.py                    # Shared dependencies
├── tests/                         # Unit & integration tests
│   ├── api/
│   └── services/
├── .env
├── requirements.txt
├── README.md
├── gunicorn_conf.py              # For production server
├── Dockerfile                    # Optional: for containerization
├── docker-compose.yml           # Optional: multi-service deploy
└── pyproject.toml                # Tooling config (black, isort, etc)
```

## Project Setup

This project uses [`uv`](https://github.com/astral-sh/uv) for fast Python dependency management and [`taskipy`](https://github.com/illBeRoy/taskipy) for running developer tasks.

---

### Prerequisites

- Python **3.12**
- Git
- [`pipx`](https://pypa.github.io/pipx/)
- [`uv`](https://github.com/astral-sh/uv)

---

### Step 1: Install `pipx` (One-Time Setup)

#### Linux / macOS

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Then restart your terminal or run:

    ```bash
    source ~/.bashrc   # or ~/.zshrc
    ```


#### Windows (PowerShell)

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```

Restart the terminal to apply the updated PATH.

### Step 2: Install uv with pipx

```bash
  pipx install uv
```

verify installation:

```bash
  uv --version
```

### Step 3: Set Up the Project

1. Clone the Repostiory

    ```bash
    git clone https://github.com/garg-shiv/Manimato.ai.git
    cd manimato.ai
    ```

2. Install System Dependencies (WSL/LINUX):
    ```bash
    sudo apt update
    sudo apt install -y libcairo2-dev libpango1.0-dev pkg-config python3-dev
    ```
2. Sync environment using uv: 

    This will install both main and development dependencies, and automatically create a virtual environment `(.venv)`:

    ```bash
      uv sync --group dev
    ```

3. Set up environment variables:

    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```

## Usage

### Development

Run the development server:

```bash
task dev
```

## API Endpoints

### Health Check

- `GET /health` - Health check endpoint

### Chat API

- `POST /api/v1/chat/chat` - Chat with the LLM

### Inference API

- `POST /api/v1/inference/inference` - Run LLM inference

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

Configuration is managed through environment variables. See `.env` file for available options:

- `ENVIRONMENT`: Environment (development/production)
- `DEBUG`: Enable debug mode
- `GEMINI_API_KEY`: Your Gemini API key
- `LLM_MODEL`: Gemini model to use
- `LOG_LEVEL`: Logging level

## Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app
```

## Development Tools

Format code:

```bash
black app/
isort app/
```

Lint code:

```bash
flake8 app/
```

## License

This project is licensed under the MIT License.
