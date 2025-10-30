import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
    REPORT_RECIPIENT_EMAIL: str = os.getenv("REPORT_RECIPIENT_EMAIL", "your_email@example.com")
    USER_NAME: str = os.getenv("USER_NAME", "사용자")
    RAW_DATA_SHEET_PREFIX: str = '운동데이터_'
    STRUCTURED_LOG_SHEET: str = 'structured_log'
    MAPPING_SHEET: str = '운동분류'
    INBODY_SHEET: str = 'Inbody_data'
    DEBOUNCE_TRIGGER_HANDLER: str = 'processDataUpdate' # This might be removed or re-purposed for a scheduler

    # Google Sheets Service Account Credentials
    GCP_TYPE: str = os.getenv("GCP_TYPE")
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID")
    GCP_PRIVATE_KEY_ID: str = os.getenv("GCP_PRIVATE_KEY_ID")
    GCP_PRIVATE_KEY: str = os.getenv("GCP_PRIVATE_KEY")
    GCP_CLIENT_EMAIL: str = os.getenv("GCP_CLIENT_EMAIL")
    GCP_CLIENT_ID: str = os.getenv("GCP_CLIENT_ID")
    GCP_AUTH_URI: str = os.getenv("GCP_AUTH_URI")
    GCP_TOKEN_URI: str = os.getenv("GCP_TOKEN_URI")
    GCP_AUTH_PROVIDER_X509_CERT_URL: str = os.getenv("GCP_AUTH_PROVIDER_X509_CERT_URL")
    GCP_CLIENT_X509_CERT_URL: str = os.getenv("GCP_CLIENT_X509_CERT_URL")
    GCP_UNIVERSE_DOMAIN: str = os.getenv("GCP_UNIVERSE_DOMAIN", "googleapis.com")

    # Google Spreadsheet Configuration
    SPREADSHEET_NAME: str = os.getenv("SPREADSHEET_NAME", "AI_Fitness_Dashboard") # Your Google Spreadsheet Name

    # Email Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "your_sender_email@example.com")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "your_email_password")
