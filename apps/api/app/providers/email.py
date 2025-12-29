from uuid import uuid4
from sqlalchemy.orm import Session

from app.settings import settings
from app.models import EmailOutbox


def send_email(db: Session, to: str, subject: str, html: str) -> str:
    if not settings.enable_resend or not settings.resend_api_key:
        message_id = f"sim_email_{uuid4().hex[:8]}"
        db.add(EmailOutbox(to_address=to, subject=subject, html=html, provider_message_id=message_id))
        db.commit()
        print(f"[email][demo] {to} {subject}")
        return message_id
    return f"resend_{uuid4().hex[:8]}"
