from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Roleplay Training API"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    deepgram_api_key: str = ""

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_evaluator_model: str = "openai/gpt-4o-mini"
    openrouter_referer: str = "http://localhost:8501"
    openrouter_title: str = "AI Roleplay Trainer"

    azure_speech_key: str = ""
    azure_speech_region: str = ""
    azure_speech_voice: str = "en-US-AvaMultilingualNeural"

    simli_api_key: str = Field(default="", alias="SIMLI_API_KEY")
    simli_face_id: str = Field(default="", alias="SIMLI_FACE_ID")
    simli_base_url: str = Field(default="https://api.simli.ai", alias="SIMLI_BASE_URL")
    simli_max_session_length: int = Field(default=1800, alias="SIMLI_MAX_SESSION_LENGTH")
    simli_max_idle_time: int = Field(default=30, alias="SIMLI_MAX_IDLE_TIME")

    livekit_url: str = Field(default="", alias="LIVEKIT_URL")
    livekit_api_key: str = Field(default="", alias="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(default="", alias="LIVEKIT_API_SECRET")
    livekit_default_room: str = Field(default="roleplay-room", alias="LIVEKIT_DEFAULT_ROOM")
    livekit_agent_name: str = Field(default="roleplay-agent", alias="LIVEKIT_AGENT_NAME")

    frontend_backend_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
