from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    LOG_INGEST_URL: str = "http://localhost:8003"
    SEMANTIC_URL: str = "http://localhost:8004"
    INTENT_URL: str = "http://localhost:8002"
    MITRE_URL: str = "http://localhost:8001"
    
    ORCHESTRATOR_TIMEOUT: float = 5.0
    ORCHESTRATOR_LOG_LEVEL: str = "INFO"

    class Config:
        # Load from parent directory (project root) if not found locally
        # src/orchestrator/config.py -> src/orchestrator -> src -> orchestrator -> CCE (root)
        # But simpler is just to look for .env in CWD or parent dirs
        env_file = ".env"
        extra = "ignore" 

@lru_cache()
def get_settings():
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Explicitly load from root .env
    # src/config.py -> src -> orchestrator -> CCE (root)
    env_path = Path(__file__).resolve().parents[2] / '.env'
    load_dotenv(dotenv_path=env_path)
    
    return Settings()

settings = get_settings()
