"""Configuration module for SRE RAG Incident Copilot.

Loads and manages environment configuration for LLM providers,
API settings, and file paths.
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration management for the SRE RAG Incident Copilot."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RUNBOOKS_DIR = DATA_DIR / "runbooks"
    SAMPLE_INCIDENTS_FILE = DATA_DIR / "sample_incidents.json"

    # LLM Provider settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4o-mini")
    GITHUB_MODELS_ENDPOINT = os.getenv(
        "GITHUB_MODELS_ENDPOINT",
        "https://models.github.ai/inference/chat/completions",
    )

    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Chunking settings
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

    # Search settings
    TOP_K_RESULTS = 3

    @classmethod
    def validate(cls) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid.
        """
        if cls.LLM_PROVIDER not in ("mock", "github_models"):
            raise ValueError(
                f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. "
                "Must be 'mock' or 'github_models'"
            )

        if cls.LLM_PROVIDER == "github_models" and not cls.GITHUB_TOKEN:
            raise ValueError(
                "GITHUB_TOKEN is required when LLM_PROVIDER=github_models"
            )

        if not cls.RUNBOOKS_DIR.exists():
            raise ValueError(f"Runbooks directory not found: {cls.RUNBOOKS_DIR}")

    @classmethod
    def load_from_env(cls, env_file: Optional[str] = None) -> None:
        """Load configuration from environment file.

        Args:
            env_file: Optional path to .env file.
        """
        if env_file and Path(env_file).exists():
            from dotenv import load_dotenv

            load_dotenv(env_file)
            # Reload class attributes after loading from file
            cls.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
            cls.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
            cls.GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4o-mini")
            cls.GITHUB_MODELS_ENDPOINT = os.getenv(
                "GITHUB_MODELS_ENDPOINT",
                "https://models.github.ai/inference/chat/completions",
            )
            cls.API_HOST = os.getenv("API_HOST", "0.0.0.0")
            cls.API_PORT = int(os.getenv("API_PORT", "8000"))
