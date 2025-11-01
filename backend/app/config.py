from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Gemini API Key
    GEMINI_API_KEY: str

    # Google Application Credentials (for services like Gemini AI if using service account)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Report Recipient Email
    REPORT_RECIPIENT_EMAIL: Optional[str] = None

    # User Name for Reports
    USER_NAME: Optional[str] = None

    # Email Configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None

    # PostgreSQL Database Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fitness_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

settings = Settings()
