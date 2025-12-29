from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ExitRequest

router = APIRouter()


@router.get("/")
def list_exits(db: Session = Depends(get_db)):
    exits = db.query(ExitRequest).all()
    return [
        {
            "exit_code": f"EXIT-{e.id:04d}",
            "window": e.window,
            "fee_bps": e.fee_bps,
            "status": e.status,
            "settlement": e.settlement,
        }
        for e in exits
    ]
