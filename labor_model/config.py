from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    open_ai_key: str

    model_config = SettingsConfigDict(
        env_file=Path(Path(__file__).parent.parent, ".env"), env_file_encoding="utf-8"
    )
