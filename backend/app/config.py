import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")


def configured_path(name: str, default: str) -> Path:
    value = Path(os.getenv(name, default))
    return value if value.is_absolute() else BACKEND_DIR / value


def database_path() -> Path:
    return configured_path("DATABASE_PATH", "data/questions.db")


def question_bank_path() -> Path:
    return configured_path("QUESTION_BANK_PATH", "question_bank")


def frontend_origins() -> list[str]:
    return [item.strip() for item in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if item.strip()]
