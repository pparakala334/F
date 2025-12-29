from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db import get_db
from app.models import Investment, Round, TierOption, Contract, Startup, User
from app.providers.payments import collect_investment
from app.settings import settings

router = APIRouter()


class InvestRequest(BaseModel):
    investor_id: int
    round_id: int
    amount_cents: int


@router.post("/")
def invest(payload: InvestRequest, db: Session = Depends(get_db)):
    round_obj = db.query(Round).filter(Round.id == payload.round_id).first()
    if not round_obj or round_obj.status != "published":
        raise HTTPException(status_code=400, detail="Round not available")
    startup = db.query(Startup).filter(Startup.id == round_obj.startup_id).first()
    investor = db.query(User).filter(User.id == payload.investor_id).first()
    if settings.country_mode == "CA":
        if not investor or not startup or investor.country != "CA" or startup.country != "CA":
            raise HTTPException(status_code=400, detail="Canada-only mode enforced")

    with db.begin():
        total = db.scalar(
            select(func.coalesce(func.sum(Investment.amount_cents), 0)).where(Investment.round_id == payload.round_id)
        )
        if total + payload.amount_cents > round_obj.max_raise_cents:
            raise HTTPException(status_code=400, detail="Round fully subscribed")

        payment_id = collect_investment(db, payload.investor_id, payload.round_id, payload.amount_cents)
        investment = Investment(investor_id=payload.investor_id, round_id=payload.round_id, amount_cents=payload.amount_cents)
        db.add(investment)

    db.refresh(investment)

    option = db.query(TierOption).filter(TierOption.round_id == payload.round_id, TierOption.tier == round_obj.selected_tier).first()
    contract = Contract(
        investment_id=investment.id,
        payout_cap_multiple=float(option.multiple) if option else 1.5,
        months_cap=option.months if option else 30,
        min_hold_months=6,
        status="active",
        total_paid_cents=0,
    )
    db.add(contract)
    db.commit()

    return {
        "investment_code": f"INV-{investment.id:04d}",
        "payment_id": payment_id,
        "contract_status": contract.status,
    }


@router.get("/portfolio/{investor_id}")
def portfolio(investor_id: int, db: Session = Depends(get_db)):
    investments = db.query(Investment).filter(Investment.investor_id == investor_id).all()
    data = []
    for inv in investments:
        round_obj = db.query(Round).filter(Round.id == inv.round_id).first()
        startup = db.query(Startup).filter(Startup.id == round_obj.startup_id).first() if round_obj else None
        data.append(
            {
                "investment_code": f"INV-{inv.id:04d}",
                "startup_name": startup.name if startup else "Unknown",
                "amount_cents": inv.amount_cents,
                "status": inv.status,
            }
        )
    return data
