from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
)

fm = FastMail(conf)


async def send_verification_email(email: str, token: str):
    base = (settings.FRONT_URL or "").rstrip("/")
    # Link hacia el frontend
    link = f"{settings.FRONT_URL}/auth/verify?token={token}"
    msg = MessageSchema(
        subject="Verifica tu cuenta - Cibercity",
        recipients=[email],
        body=f"Hola,\n\nConfirma tu cuenta con este enlace:\n{link}\n\nSi no fuiste tu, ignora este mensaje",
        subtype="plain"
    )
    await fm.send_message(msg)

async def send_reset_email(email: str, token: str):
    base = (settings.FRONT_URL or "").rstrip("/")
    link = f"{base}/auth/reset-password?token={token}"
    msg = MessageSchema(
        subject="Recupera tu contraseña - Cibercity",
        recipients=[email],
        body=f"Hola,\n\nRestablece tu contraseña aqui (15m):\n{link}\n\nSi no fuiste tu, ignora este mensaje",
        subtype="plain"
    )

    await fm.send_message(msg)