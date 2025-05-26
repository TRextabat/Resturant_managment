from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from smtplib import SMTPException
from pydantic import BaseModel, EmailStr
from src.core.settings import settings
from loguru import logger
class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    body: str

# Configure SMTP settings for Gmail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_FROM,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,  
    MAIL_SSL_TLS=False,  
    USE_CREDENTIALS=True
)

async def send_email(email: EmailSchema):
    """
    Send an email using SMTP with exception handling.
    Runs as a background task.
    """
    message = MessageSchema(
        subject=email.subject,
        recipients=[email.email],
        body=email.body,
        subtype=MessageType.plain
    )
    logger.info(f"✉️ Sending email to {email.email}")
    logger.info(f"✉️ Email: {email}")
    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"✅ Email sent successfully to {email.email}")

    except SMTPException as smtp_error:
        logger.error(f"❌ SMTP error while sending email to {email.email}: {smtp_error}")

    except ConnectionError:
        logger.error("❌ Failed to connect to the email server.")

    except Exception as e:
        logger.error(f"❌ Unexpected error while sending email: {e}")