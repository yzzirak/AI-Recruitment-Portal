"""
email_utils.py
Sends the reset email using SMTP. If SMTP is not configured,
returns False and the app falls back to demo mode.
"""
import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST")          # e.g. smtp.gmail.com
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")          # your email
SMTP_PASS = os.getenv("SMTP_PASS")          # Gmail App Password


def smtp_configured() -> bool:
    return all([SMTP_HOST, SMTP_USER, SMTP_PASS])


def send_reset_email(to_email: str, token: str) -> bool:
    if not smtp_configured():
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = "HireFast - Password reset code"
        msg["From"]    = SMTP_USER
        msg["To"]      = to_email
        msg.set_content(
            f"Your password reset code (valid for 15 minutes):\n\n{token}\n\n"
            "If you did not request this, ignore this email."
        )
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email send failed:", e)
        return False