from uuid import uuid4
from sqlalchemy.orm import Session

from app.settings import settings
from app.models import Document


def create_signed_upload_url(db: Session, user_id: int, filename: str, content_type: str) -> str:
    if not settings.enable_s3 or not settings.aws_access_key_id:
        doc = Document(startup_id=user_id, filename=filename, content_type=content_type, storage_url=None)
        db.add(doc)
        db.commit()
        return f"https://example.com/upload/{uuid4().hex}"
    return f"https://s3.{settings.aws_region}.amazonaws.com/{settings.aws_s3_bucket}/{uuid4().hex}/{filename}"


def list_documents(db: Session, startup_id: int):
    return db.query(Document).filter(Document.startup_id == startup_id).all()
