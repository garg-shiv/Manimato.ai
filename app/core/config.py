from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Required environment variables (must be non-empty)
    DATABASE_URL: str = Field(..., description="Database connection URL")
    PYTHONPATH: str = Field(..., description="Python path")
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    GEMINI_API_KEY: str = Field(..., description="Gemini API key")
    OPENAI_LLM: str = Field(..., description="Which OpenAI LLM to use")
    OPENAI_API_BASE: str = Field(default="https://openrouter.ai/api/v1")

    # Fixed project paths - these are computed properties, not from env vars
    @property
    def PROJECT_ROOT(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @property
    def GENERATED_DIR(self) -> Path:
        return self.PROJECT_ROOT / "generated"

    @property
    def MEDIA_DIR(self) -> Path:
        return self.PROJECT_ROOT / "media"

    @field_validator(
        "DATABASE_URL",
        "PYTHONPATH",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_LLM",
        mode="before",
    )
    @classmethod
    def not_empty(cls, v: str, info):
        if not v or not v.strip():
            raise ValueError(
                f"Environment variable '{info.field_name}' is required and cannot be empty."
            )
        return v

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        self.MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    def init(self):
        """Initialize the configuration and create directories."""
        self.ensure_directories()
        print(" Environment validated successfully.")
        print("Created ./generated and ./media")

    class Config:
        # Optional: specify .env file location
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Case sensitivity for environment variables
        case_sensitive = True


def create_config() -> Settings:
    """Factory function to create and validate settings."""
    try:
        return Settings()  # type: ignore
    except Exception as e:
        print(f"Configuration error: {e}")
        print("Make sure all required environment variables are set:")
        print("- DATABASE_URL")
        print("- PYTHONPATH")
        print("- OPENAI_API_KEY")
        print("- GEMINI_API_KEY")
        print("- OPENAI_LLM")
        raise


# Instantiate this globally
config = create_config()
