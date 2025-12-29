from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth.router import get_current_user
from app.db import get_db
from app.models import Round, Startup, TierOption, Investment, Contract, ExitRequest, Payout
from app.providers.payments import collect_investment
from app.settings import settings

router = APIRouter()


@router.get("/rounds")
def list_rounds(db: Session = Depends(get_db)):
    rounds = db.query(Round).filter(Round.status == "published").all()
    response = []
    for round_obj in rounds:
        startup = db.query(Startup).filter(Startup.id == round_obj.startup_id).first()
        raised = (
            db.query(func.coalesce(func.sum(Investment.amount_cents), 0))
            .filter(Investment.round_id == round_obj.id)
            .scalar()
        )
        response.append(
            {
                "round_code": f"RND-{round_obj.id:04d}",
                "startup_name": startup.name if startup else "Confidential",
                "max_raise_cents": round_obj.max_raise_cents,
                "tier_selected": round_obj.tier_selected,
                "raised_cents": raised,
            }
        )
    return response


@router.get("/rounds/{round_id}")
def round_detail(round_id: int, db: Session = Depends(get_db)):
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    tier = (
        db.query(TierOption)
        .filter(TierOption.round_id == round_id, TierOption.tier == round_obj.tier_selected)
        .first()
    )
    return {
        "round_code": f"RND-{round_obj.id:04d}",
        "max_raise_cents": round_obj.max_raise_cents,
        "tier": {
            "revenue_share_bps": tier.revenue_share_bps if tier else 0,
            "time_cap_months": tier.time_cap_months if tier else 0,
            "payout_cap_mult": float(tier.payout_cap_mult) if tier else 0,
            "min_hold_days": tier.min_hold_days if tier else 0,
            "exit_fee_bps_quarterly": tier.exit_fee_bps_quarterly if tier else 0,
            "exit_fee_bps_offcycle": tier.exit_fee_bps_offcycle if tier else 0,
        },
    }


class InvestRequest(BaseModel):
    round_id: int
    amount_cents: int


@router.post("/invest")
def invest(
    payload: InvestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == payload.round_id).first()
    if not round_obj or round_obj.status != "published":
        raise HTTPException(status_code=400, detail="Round not available")
    startup = db.query(Startup).filter(Startup.id == round_obj.startup_id).first()
    if settings.country_mode == "CA":
        if not startup or startup.country != "CA" or current_user.country != "CA":
            raise HTTPException(status_code=400, detail="Canada-only mode enforced")
    total = (
        db.query(func.coalesce(func.sum(Investment.amount_cents), 0))
        .filter(Investment.round_id == round_obj.id)
        .scalar()
    )
    if total + payload.amount_cents > round_obj.max_raise_cents:
        raise HTTPException(status_code=400, detail="Round fully subscribed")
    payment_id = collect_investment(db, current_user.id, round_obj.id, payload.amount_cents)
    investment = Investment(
        round_id=round_obj.id,
        investor_user_id=current_user.id,
        amount_cents=payload.amount_cents,
        payment_id=payment_id,
    )
    db.add(investment)
    db.commit()
    db.refresh(investment)
    tier = (
        db.query(TierOption)
        .filter(TierOption.round_id == round_obj.id, TierOption.tier == round_obj.tier_selected)
        .first()
    )
    payout_cap_cents = int(payload.amount_cents * float(tier.payout_cap_mult))
    contract = Contract(
        investment_id=investment.id,
        status="active",
        principal_cents=payload.amount_cents,
        payout_cap_cents=payout_cap_cents,
        revenue_share_bps=tier.revenue_share_bps,
        start_date=datetime.utcnow(),
        end_date_cap=datetime.utcnow() + timedelta(days=tier.time_cap_months * 30),
        paid_to_date_cents=0,
    )
    db.add(contract)
    db.commit()
    return {"investment_code": f"INV-{investment.id:04d}"}


@router.get("/portfolio")
def portfolio(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Forbidden")
    investments = db.query(Investment).filter(Investment.investor_user_id == current_user.id).all()
    data = []
    for investment in investments:
        contract = db.query(Contract).filter(Contract.investment_id == investment.id).first()
        data.append(
            {
                "investment_code": f"INV-{investment.id:04d}",
                "contract_code": f"CTR-{contract.id:04d}" if contract else None,
                "amount_cents": investment.amount_cents,
                "status": contract.status if contract else "active",
                "paid_to_date_cents": contract.paid_to_date_cents if contract else 0,
                "payout_cap_cents": contract.payout_cap_cents if contract else 0,
            }
        )
    return data


class ExitRequestCreate(BaseModel):
    contract_id: int
    exit_type: str


@router.post("/exits/request")
def request_exit(
    payload: ExitRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Forbidden")
    if payload.exit_type not in {"quarterly", "offcycle"}:
        raise HTTPException(status_code=400, detail="Invalid exit type")
    contract = db.query(Contract).filter(Contract.id == payload.contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    investment = db.query(Investment).filter(Investment.id == contract.investment_id).first()
    round_obj = db.query(Round).filter(Round.id == investment.round_id).first() if investment else None
    tier = (
        db.query(TierOption)
        .filter(TierOption.round_id == round_obj.id, TierOption.tier == round_obj.tier_selected)
        .first()
        if round_obj
        else None
    )
    if tier:
        min_hold_date = contract.start_date + timedelta(days=tier.min_hold_days)
        if datetime.utcnow() < min_hold_date:
            raise HTTPException(status_code=400, detail="Minimum holding period not satisfied")
    exit_req = ExitRequest(contract_id=contract.id, exit_type=payload.exit_type, status="requested")
    db.add(exit_req)
    db.commit()
    return {"exit_code": f"EXIT-{exit_req.id:04d}"}


@router.get("/payouts")
def payout_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Forbidden")
    investment_ids = [
        inv.id
        for inv in db.query(Investment).filter(Investment.investor_user_id == current_user.id).all()
    ]
    contract_ids = [
        contract.id
        for contract in db.query(Contract).filter(Contract.investment_id.in_(investment_ids)).all()
    ]
    payouts = db.query(Payout).filter(Payout.contract_id.in_(contract_ids)).all()
    return [
        {
            "payout_code": f"PO-{payout.id:04d}",
            "amount_cents": payout.amount_cents,
            "created_at": payout.created_at,
        }
        for payout in payouts
    ]
