from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import LoanOffer

router = APIRouter()


@router.get("/")
def list_loans(db: Session = Depends(get_db)):
    offers = db.query(LoanOffer).all()
    return [
        {"loan_code": f"LOAN-{o.id:04d}", "amount_cents": o.amount_cents, "fee_cents": o.fee_cents, "status": o.status}
        for o in offers
    ]
