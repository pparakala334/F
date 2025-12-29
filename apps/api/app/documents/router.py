from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.providers.storage import create_signed_upload_url, list_documents

router = APIRouter()


class UploadRequest(BaseModel):
    user_id: int
    filename: str
    content_type: str


@router.post("/upload")
def upload(payload: UploadRequest, db: Session = Depends(get_db)):
    url = create_signed_upload_url(db, payload.user_id, payload.filename, payload.content_type)
    return {"upload_url": url}


@router.get("/startup/{startup_id}")
def list_startup_documents(startup_id: int, db: Session = Depends(get_db)):
    docs = list_documents(db, startup_id)
    return [
        {
            "filename": doc.filename,
            "content_type": doc.content_type,
            "storage_url": doc.storage_url,
        }
        for doc in docs
    ]
