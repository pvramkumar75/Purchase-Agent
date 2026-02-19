import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import Optional

class EmailService:
    @staticmethod
    def draft_email(to: str, subject: str, body: str, tone: str = "polite"):
        """
        Creates a draft. In this local version, it returns the draft for approval.
        """
        return {
            "to": to,
            "subject": subject,
            "body": body,
            "tone": tone,
            "status": "pending_approval"
        }

    @staticmethod
    def send_email(to: str, subject: str, body: str):
        if not settings.GMAIL_USER or not settings.GMAIL_APP_PASSWORD:
            return {"error": "Email credentials not configured."}
        
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.GMAIL_USER
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
                server.send_message(msg)
            return {"status": "sent"}
        except Exception as e:
            return {"error": str(e)}

email_service = EmailService()
