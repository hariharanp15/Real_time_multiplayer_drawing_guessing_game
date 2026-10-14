from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./sketch_guess.db"
    cors_origins: str = "http://localhost:5173"
    round_seconds: int = 75
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
