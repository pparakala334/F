from uuid import uuid4
from sqlalchemy.orm import Session

from app.settings import settings
from app.models import Document


def create_signed_upload_url(filename: str) -> str:
    token = uuid4().hex[:12]
    if not settings.enable_s3 or not settings.aws_access_key_id:
        return f"http://localhost:8000/demo-upload/{token}?filename={filename}"
    return f"https://s3.{settings.aws_region}.amazonaws.com/{settings.aws_s3_bucket}/{token}/{filename}"


def complete_upload(db: Session, startup_id: int, doc_type: str, filename: str, storage_key: str) -> Document:
    doc = Document(startup_id=startup_id, doc_type=doc_type, filename=filename, storage_key=storage_key)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session, startup_id: int):
    return db.query(Document).filter(Document.startup_id == startup_id).all()
