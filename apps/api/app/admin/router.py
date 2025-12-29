from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import StartupApplication, Round, LedgerEntry, ExitRequest, Contract, LoanOffer

router = APIRouter()


@router.get("/applications")
def review_applications(db: Session = Depends(get_db)):
    apps = db.query(StartupApplication).all()
    return [
        {"application_code": f"APP-{app.id:04d}", "status": app.status, "company_name": app.company_name}
        for app in apps
    ]


@router.get("/rounds")
def review_rounds(db: Session = Depends(get_db)):
    rounds = db.query(Round).all()
    return [
        {"round_code": f"RND-{r.id:04d}", "status": r.status, "selected_tier": r.selected_tier}
        for r in rounds
    ]


@router.get("/ledger/metrics")
def ledger_metrics(db: Session = Depends(get_db)):
    entries = db.query(LedgerEntry).all()
    total = sum(entry.amount_cents for entry in entries)
    return {"entries": len(entries), "total_cents": total}


class ExitAction(BaseModel):
    contract_id: int
    window: str


@router.post("/demo/exit-request")
def create_exit_request(payload: ExitAction, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == payload.contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    fee_bps = 50 if payload.window == "quarterly" else 150
    exit_request = ExitRequest(contract_id=contract.id, window=payload.window, fee_bps=fee_bps, settlement="cash")
    db.add(exit_request)
    db.commit()
    return {"exit_code": f"EXIT-{exit_request.id:04d}", "fee_bps": fee_bps}


class ExitSettlement(BaseModel):
    exit_request_id: int
    settlement: str


@router.post("/demo/settle-exit")
def settle_exit(payload: ExitSettlement, db: Session = Depends(get_db)):
    exit_request = db.query(ExitRequest).filter(ExitRequest.id == payload.exit_request_id).first()
    if not exit_request:
        raise HTTPException(status_code=404, detail="Exit request not found")
    exit_request.status = "settled"
    exit_request.settlement = payload.settlement
    if payload.settlement == "loan":
        loan = LoanOffer(startup_id=1, amount_cents=100000, fee_cents=5000)
        db.add(loan)
        db.add(LedgerEntry(entry_type="loan_referral_fee", amount_cents=loan.fee_cents, currency="CAD", meta="simulated"))
    db.commit()
    return {"status": exit_request.status, "settlement": exit_request.settlement}
