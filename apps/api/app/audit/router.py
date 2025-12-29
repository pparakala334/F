from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AuditLog

router = APIRouter()


@router.get("/")
def list_audit(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).all()
    return [
        {"audit_code": f"AUD-{log.id:04d}", "action": log.action, "details": log.details}
        for log in logs
    ]
