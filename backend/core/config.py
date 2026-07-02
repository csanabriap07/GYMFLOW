"""
Configuración central del backend (core, según AGENTS.md).
Lee variables de entorno / .env vía pydantic-settings.

NOTA: verificar con Context7 la API exacta de pydantic-settings de la versión
instalada antes de mergear (puede diferir entre pydantic v1/v2).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    # Zona horaria del gimnasio, usada para calcular "día calendario" (RN-02) y
    # ventanas temporales (RN-04). Centralizada aquí según plan.md de 001.
    timezone: str = "America/Bogota"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
