import json
from sqlalchemy.orm import Session

from app.settings import settings
from app.models import AnalyticsEvent


def track(db: Session, event: str, user_id: int | None, properties: dict | None = None) -> None:
    if not settings.enable_posthog or not settings.posthog_api_key:
        db.add(AnalyticsEvent(event=event, user_id=user_id, properties=json.dumps(properties or {})))
        db.commit()
        return
    # Placeholder for real PostHog
    db.add(AnalyticsEvent(event=event, user_id=user_id, properties=json.dumps({"forwarded": True, **(properties or {})})))
    db.commit()
