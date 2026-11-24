import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env da raiz do projeto
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "oscar_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "oscar_secret")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "oscar_tracker")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))

    TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
    OMDB_API_KEY: str = os.getenv("OMDB_API_KEY", "")

    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
