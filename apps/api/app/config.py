from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    database_url: str = "sqlite:///./data/royale.db"
    admin_password: str = "admin"
    secret_key: str = "change-me-in-production"
    mock_inference: bool = True
    cors_origins: str = "*"
    jwt_hours: int = 72
    match_pause_seconds: float = 1.1
    llm_timeout_seconds: float = 45.0

    @property
    def origins(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
