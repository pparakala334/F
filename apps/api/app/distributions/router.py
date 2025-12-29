from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Contract, Distribution
from app.providers.payments import payout_investor

router = APIRouter()


@router.post("/run-month")
def run_month(db: Session = Depends(get_db)):
    contracts = db.query(Contract).filter(Contract.status == "active").all()
    payouts = []
    for contract in contracts:
        amount_cents = 5000
        payout_id = payout_investor(db, contract.investment_id, amount_cents)
        distribution = Distribution(contract_id=contract.id, amount_cents=amount_cents)
        contract.total_paid_cents += amount_cents
        db.add(distribution)
        db.commit()
        payouts.append({"contract_id": contract.id, "payout_id": payout_id})
    return {"payouts": payouts}
