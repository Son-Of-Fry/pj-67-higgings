import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PJ-67 Kanban & Docs MCP"
    APP_ENV: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:////data/kanban.db"
    API_AUTH_TOKEN: str = ""
    ALLOWED_ORIGINS: str = "*"

    @property
    def sqlite_db_path(self) -> str:
        # Extraer la ruta de archivo desde sqlite:///ruta o usar fallback local
        url = self.DATABASE_URL
        if url.startswith("sqlite:///"):
            path = url.replace("sqlite:///", "")
        elif url.startswith("sqlite://"):
            path = url.replace("sqlite://", "")
        else:
            path = url

        # Si el directorio no existe (por ejemplo en desarrollo local fuera de Docker sin /data),
        # usar una carpeta local ./data
        p = Path(path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            return str(p)
        except (PermissionError, OSError):
            local_fallback = Path("./data/kanban.db")
            local_fallback.parent.mkdir(parents=True, exist_ok=True)
            return str(local_fallback)

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
