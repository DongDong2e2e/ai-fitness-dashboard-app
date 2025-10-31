import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

class Config:
    # Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    # Report Recipient Email
    REPORT_RECIPIENT_EMAIL = os.getenv("REPORT_RECIPIENT_EMAIL")

    # User Name for Reports
    USER_NAME = os.getenv("USER_NAME")

    # Email Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    try:
        SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    except (ValueError, TypeError):
        SMTP_PORT = 587
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    # PostgreSQL Database Configuration
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "fitness_db")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db") # Docker Compose 서비스 이름
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
