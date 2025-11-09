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
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    # JWT Settings
    # IMPORTANT: In production, this should be set via an environment variable
    # You can generate a new secret with: openssl rand -hex 32
    SECRET_KEY: str = "65ce745718013f4202449c06b8cc084147dfbd474e02ba1c7ed98d3bac3cc934"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
