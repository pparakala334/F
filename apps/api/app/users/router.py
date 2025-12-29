from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

router = APIRouter()


@router.get("/")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {"user_code": f"USR-{user.id:04d}", "email": user.email, "role": user.role, "country": user.country}
        for user in users
    ]
