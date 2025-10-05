"""
Configuratiebeheer voor de MCP Document Processor.
"""
# SecretStr not currently used but available for API keys
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChunkingSettings(BaseSettings):
    """Configuratie voor tekst chunking."""
    model_config = SettingsConfigDict(env_prefix="CHUNKING_")
    DEFAULT_CHUNK_SIZE: int = 1000
    DEFAULT_CHUNK_OVERLAP: int = 200
    MAX_CHUNK_SIZE: int = 4000
    MIN_CHUNK_SIZE: int = 100
    AUTO_MODE_ENABLED: bool = True
    AUTO_MODE_SAFETY_FACTOR: float = 0.8  # Gebruik 80% van max context voor veiligheid


class OllamaSettings(BaseSettings):
    """Configuratie voor Ollama integratie."""
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")
    HOST: str = "http://localhost:11434"
    MODEL: str = "llama3:8b"
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
    chunking: ChunkingSettings = ChunkingSettings()
    # Voorbeeld van een geheim, bv. een API-sleutel
    # API_KEY: SecretStr


settings = AppSettings()
