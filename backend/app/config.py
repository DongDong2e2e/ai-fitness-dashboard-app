from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Gemini API Key
    GEMINI_API_KEY: str

    # Report Recipient Email
    REPORT_RECIPIENT_EMAIL: str | None = None

    # User Name for Reports
    USER_NAME: str | None = None

    # Email Configuration
    SMTP_SERVER: str | None = None
    SMTP_PORT: int = 587
    SENDER_EMAIL: str | None = None
    SENDER_PASSWORD: str | None = None

    # PostgreSQL Database Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fitness_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    class Config:
        env_file = ".env"

settings = Settings()
