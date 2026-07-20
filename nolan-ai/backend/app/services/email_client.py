"""SMTP email sending for Analytics Agent alerts (Resend/SendGrid or any
standard SMTP relay — all speak SMTP over TLS regardless of provider)."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import settings


class EmailNotConfiguredError(RuntimeError):
    pass


def send_alert_email(subject: str, body: str, *, to_address: str | None = None) -> None:
    recipient = to_address or settings.alert_recipient_email
    if not settings.smtp_host or not recipient:
        raise EmailNotConfiguredError(
            "SMTP not configured — set smtp_host/smtp_username/smtp_password/"
            "alert_recipient_email to enable email alerts."
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_address
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
