from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "EstateGuard API"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://estateguard:estateguard@localhost:19002/estateguard"
    database_url_sync: str = "postgresql://estateguard:estateguard@localhost:19002/estateguard"
    redis_url: str = "redis://localhost:19003/0"
    secret_key: str = "dev-secret-change-in-production"
    github_webhook_secret: str = ""
    gitlab_webhook_secret: str = ""
    cors_origins: str = "http://localhost:19000"


settings = Settings()
