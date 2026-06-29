from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://music_explorer:music_explorer@localhost:5432/music_explorer"

    discogs_token: str = ""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    anthropic_api_key: str = ""
    genius_token: str = ""


settings = Settings()
