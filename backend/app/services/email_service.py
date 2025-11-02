import smtplib
from email.mime.text import MIMEText
from app.config import settings

class EmailService:
    def send_email(self, subject: str, recipient: str, html_content: str):
        """Sends an email using the SMTP configuration from Config."""
        if not all([settings.SMTP_SERVER, settings.SENDER_EMAIL, settings.SENDER_PASSWORD]):
            print("SMTP 설정이 완전하지 않아 이메일을 발송할 수 없습니다.")
            raise ValueError("SMTP configuration is incomplete.")

        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = settings.SENDER_EMAIL
        msg['To'] = recipient

        try:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                smtp.send_message(msg)
            print(f"이메일을 성공적으로 발송했습니다: {recipient}")
        except Exception as e:
            print(f"이메일 발송 중 오류 발생: {e}")
            raise
