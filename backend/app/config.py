import os
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")]
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "storage")

    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "sentence")
    LOCAL_EMBEDDING_MODEL: str = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    MOCK_COMPLETIONS: bool = os.getenv("MOCK_COMPLETIONS", "false").lower() == "true"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    os.makedirs(s.STORAGE_DIR, exist_ok=True)
    return s
