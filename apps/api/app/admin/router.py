from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.router import get_current_user
from app.db import get_db
from app.models import (
    Application,
    Document,
    Round,
    LedgerEntry,
    RevenueReport,
    Distribution,
    Contract,
    Investment,
    Payout,
    ExitRequest,
    User,
)
from app.providers.payments import payout_investor
from app.auth.security import hash_password
from app.algorithm.service import calculate_tiers
from app.models import TierOption, Startup

router = APIRouter()


def require_admin(current_user):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/applications")
def applications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    apps = db.query(Application).all()
    return [
        {
            "application_code": f"APP-{app.id:04d}",
            "status": app.status,
            "startup_code": f"STP-{app.startup_id:04d}",
            "name": app.name,
            "application_type": app.application_type,
            "requested_limit_cents": app.requested_limit_cents,
            "documents": [
                {"doc_type": doc.doc_type, "filename": doc.filename}
                for doc in db.query(Document).filter(Document.startup_id == app.startup_id).all()
            ],
        }
        for app in apps
    ]


class ApplicationDecision(BaseModel):
    notes: str | None = None


@router.post("/applications/{application_id}/approve")
def approve_application(application_id: int, payload: ApplicationDecision, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app or app.status != "submitted":
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "approved"
    app.reviewed_at = datetime.utcnow()
    app.reviewer_id = current_user.id
    app.admin_notes = payload.notes
    db.add(LedgerEntry(entry_type="application_approved", actor_user_id=current_user.id, startup_id=app.startup_id, amount_cents=0))
    db.commit()
    return {"status": app.status}


@router.post("/applications/{application_id}/deny")
def deny_application(application_id: int, payload: ApplicationDecision, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app or app.status != "submitted":
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "rejected"
    app.reviewed_at = datetime.utcnow()
    app.reviewer_id = current_user.id
    app.admin_notes = payload.notes
    db.commit()
    return {"status": app.status}


@router.get("/rounds")
def rounds(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    rounds = db.query(Round).all()
    return [
        {
            "round_code": f"RND-{round.id:04d}",
            "status": round.status,
            "tier_selected": round.tier_selected,
        }
        for round in rounds
    ]


@router.post("/rounds/{round_id}/close")
def close_round(round_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    round_obj.status = "closed"
    db.commit()
    return {"status": round_obj.status}


@router.get("/ledger")
def ledger(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    entries = db.query(LedgerEntry).all()
    return [
        {
            "entry_code": f"LED-{entry.id:04d}",
            "type": entry.entry_type,
            "amount_cents": entry.amount_cents,
        }
        for entry in entries
    ]


class DistributionRun(BaseModel):
    startup_id: int
    month: str


@router.post("/distributions/run")
def run_distribution(payload: DistributionRun, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    contracts = (
        db.query(Contract)
        .join(Investment)
        .join(Round)
        .filter(Round.startup_id == payload.startup_id, Contract.status == "active")
        .all()
    )
    distribution = Distribution(
        startup_id=payload.startup_id,
        month=payload.month,
        total_distributed_cents=0,
        created_by=current_user.id,
    )
    db.add(distribution)
    db.commit()
    total = 0
    for contract in contracts:
        payout_amount = int(contract.principal_cents * 0.02)
        if contract.paid_to_date_cents >= contract.payout_cap_cents:
            contract.status = "completed"
            continue
        payout_id = payout_investor(db, contract.id, payout_amount)
        payout = Payout(
            contract_id=contract.id,
            distribution_id=distribution.id,
            amount_cents=payout_amount,
            payout_id=payout_id,
        )
        contract.paid_to_date_cents += payout_amount
        total += payout_amount
        db.add(payout)
    distribution.total_distributed_cents = total
    reports = db.query(RevenueReport).filter(RevenueReport.startup_id == payload.startup_id, RevenueReport.month == payload.month).all()
    for report in reports:
        report.distribution_status = "distributed"
    db.commit()
    return {"distribution_code": f"DIST-{distribution.id:04d}"}


class RevenueSimulate(BaseModel):
    startup_id: int
    month: str
    gross_revenue_cents: int


@router.post("/revenue/simulate")
def simulate_revenue(payload: RevenueSimulate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    report = RevenueReport(
        startup_id=payload.startup_id,
        month=payload.month,
        gross_revenue_cents=payload.gross_revenue_cents,
        reported_by=current_user.id,
        distribution_status="pending",
    )
    db.add(report)
    db.commit()
    return {"report_code": f"REV-{report.id:04d}"}


@router.post("/exits/{exit_id}/settle")
def settle_exit(exit_id: int, settlement_method: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    exit_req = db.query(ExitRequest).filter(ExitRequest.id == exit_id).first()
    if not exit_req:
        raise HTTPException(status_code=404, detail="Exit not found")
    exit_req.status = "settled"
    exit_req.settlement_method = settlement_method
    exit_req.settled_at = datetime.utcnow()
    db.commit()
    return {"status": exit_req.status}


@router.post("/demo/seed")
def seed_demo(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    if db.query(User).count() > 1:
        return {"status": "already_seeded"}
    founder = User(email="founder@demo.com", hashed_password=hash_password("password"), role="founder", country="CA")
    investor = User(email="investor@demo.com", hashed_password=hash_password("password"), role="investor", country="CA")
    db.add_all([founder, investor])
    db.commit()
    startup = Startup(
        founder_user_id=founder.id,
        legal_name="Steelman Industries",
        operating_name="Steelman",
        country="CA",
        incorporation_type="Corp",
        incorporation_date="2021-01-01",
        website="https://steelman.example",
        logo_key=None,
        industry="Fintech",
        sub_industry="Revenue share",
        short_description="Compliance-first revenue-share platform.",
        long_description="A revenue-share marketplace for aligned capital.",
        current_monthly_revenue="$25k-$50k",
        revenue_model="SaaS",
        revenue_consistency="Stable",
        revenue_stage="Stable",
        existing_debt=0,
        existing_investors=1,
        intended_use_of_funds=json.dumps(["Hiring", "Product"]),
        target_funding_size="$250k-$1M",
        preferred_timeline="3-6 months",
        status="draft",
    )
    db.add(startup)
    db.commit()
    application = Application(
        startup_id=startup.id,
        name="Initial Funding Application",
        application_type="Initial Funding Application",
        requested_limit_cents=5000000,
        risk_preference="medium",
        status="approved",
        reviewed_at=datetime.utcnow(),
        reviewer_id=current_user.id,
    )
    db.add(application)
    db.commit()
    round_obj = Round(
        startup_id=startup.id,
        application_id=application.id,
        title="Revenue Share Round",
        max_raise_cents=5000000,
        status="published",
        tier_selected="medium",
        published_at=datetime.utcnow(),
    )
    db.add(round_obj)
    db.commit()
    tiers = calculate_tiers(round_obj.max_raise_cents)
    for tier in tiers:
        db.add(
            TierOption(
                round_id=round_obj.id,
                tier=tier.name,
                revenue_share_bps=tier.revenue_share_bps,
                time_cap_months=tier.time_cap_months,
                payout_cap_mult=tier.payout_cap_mult,
                min_hold_days=tier.min_hold_days,
                exit_fee_bps_quarterly=tier.exit_fee_bps_quarterly,
                exit_fee_bps_offcycle=tier.exit_fee_bps_offcycle,
                explanation_json=tier.explanation_json,
            )
        )
    db.commit()
    return {"status": "seeded"}
