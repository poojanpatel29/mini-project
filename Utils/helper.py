import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
 
from core.config import settings
 
conf = ConnectionConfig(
    MAIL_USERNAME = settings.EMAIL_ADDRESS,
    MAIL_PASSWORD = settings.EMAIL_PASSWORD,
    MAIL_FROM = settings.EMAIL_ADDRESS,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
 
async def send_task_completion_email(email_to: str, task_name: str):
    html = f"""
    <p>Hello,</p>
    <p>The task <strong>{task_name}</strong> has been marked as <strong>Completed</strong>.</p>
    <p>Check your dashboard for details.</p>
    """
 
    message = MessageSchema(
        subject="Task Completed Notification",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )
 
    fm = FastMail(conf)
    await fm.send_message(message)