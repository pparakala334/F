from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import LedgerEntry

router = APIRouter()


@router.get("/")
def list_entries(db: Session = Depends(get_db)):
    entries = db.query(LedgerEntry).all()
    return [
        {"entry_code": f"LED-{e.id:04d}", "type": e.entry_type, "amount_cents": e.amount_cents, "currency": e.currency}
        for e in entries
    ]
