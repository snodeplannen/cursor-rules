"""
Configuratiebeheer voor de MCP Invoice Processor.
"""
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """Configuratie voor Ollama integratie."""
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")
    HOST: str = "http://localhost:11434"
    MODEL: str = "llama3"
    TIMEOUT: int = 120


class AppSettings(BaseSettings):
    """Definieert de applicatieconfiguratie via omgevingsvariabelen."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    LOG_LEVEL: str = "INFO"
    ollama: OllamaSettings = OllamaSettings()
    # Voorbeeld van een geheim, bv. een API-sleutel
    # API_KEY: SecretStr


settings = AppSettings()
