from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Startup

router = APIRouter()


@router.get("/")
def list_startups(db: Session = Depends(get_db)):
    startups = db.query(Startup).all()
    return [
        {"startup_code": f"STP-{s.id:04d}", "name": s.name, "country": s.country, "status": s.status}
        for s in startups
    ]
