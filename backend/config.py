import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# On Vercel (serverless), the filesystem is read-only except /tmp
IS_VERCEL = os.environ.get("VERCEL", False)

if IS_VERCEL:
    DATA_DIR = Path("/tmp")
else:
    DATA_DIR = BASE_DIR

UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DATA_DIR / 'adaptive_quiz.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-prod")
    UPLOAD_FOLDER = str(UPLOAD_DIR)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
