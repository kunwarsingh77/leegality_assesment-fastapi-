from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"

    # Database connection fields — stored separately to handle special chars in passwords
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""  # URL-encode special chars in .env e.g. @ → %40
    DB_NAME: str = "leegality_db"

    # Comma-separated origins allowed to call this API from a browser
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    # Max request body in bytes — default is 1MB
    MAX_REQUEST_BODY_SIZE: int = 1_048_576

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
