from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth.router import get_current_user
from app.db import get_db
from app.models import (
    Application,
    Document,
    Round,
    Startup,
    TierOption,
    RevenueReport,
    ExitRequest,
    Contract,
    Investment,
)
from app.providers.payments import charge_application_fee
from app.providers.storage import create_signed_upload_url, complete_upload
from app.algorithm.service import calculate_tiers

router = APIRouter()


class StartupCreate(BaseModel):
    name: str
    description: str
    country: str = "CA"
    website: str | None = None


@router.post("/startup")
def create_startup(
    payload: StartupCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = Startup(
        founder_user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        country=payload.country,
        website=payload.website,
        status="active",
    )
    db.add(startup)
    db.commit()
    db.refresh(startup)
    return {"startup_code": f"STP-{startup.id:04d}"}


@router.get("/startup")
def get_startup(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.founder_user_id == current_user.id).first()
    if not startup:
        return None
    return {
        "startup_code": f"STP-{startup.id:04d}",
        "id": startup.id,
        "name": startup.name,
        "description": startup.description,
        "country": startup.country,
        "website": startup.website,
    }


class ApplicationSubmit(BaseModel):
    startup_id: int
    fee_cents: int = 2500


@router.post("/application/submit")
def submit_application(
    payload: ApplicationSubmit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == payload.startup_id).first()
    if not startup or startup.founder_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Startup not found")
    payment_id = charge_application_fee(db, current_user.id, payload.fee_cents)
    application = Application(startup_id=startup.id, status="pending", fee_payment_id=payment_id)
    db.add(application)
    db.commit()
    return {"application_code": f"APP-{application.id:04d}", "status": application.status}


@router.get("/application")
def get_application(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.founder_user_id == current_user.id).first()
    if not startup:
        return None
    app = db.query(Application).filter(Application.startup_id == startup.id).first()
    if not app:
        return None
    return {"application_code": f"APP-{app.id:04d}", "status": app.status}


class DocumentPresign(BaseModel):
    filename: str
    doc_type: str


@router.post("/documents/presign")
def presign_document(
    payload: DocumentPresign,
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"upload_url": create_signed_upload_url(payload.filename)}


class DocumentComplete(BaseModel):
    startup_id: int
    filename: str
    doc_type: str
    storage_key: str


@router.post("/documents/complete")
def complete_document(
    payload: DocumentComplete,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    doc = complete_upload(db, payload.startup_id, payload.doc_type, payload.filename, payload.storage_key)
    return {"document_code": f"DOC-{doc.id:04d}"}


class RoundCreate(BaseModel):
    startup_id: int
    title: str
    max_raise_cents: int


@router.post("/rounds")
def create_round(
    payload: RoundCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = Round(
        startup_id=payload.startup_id,
        title=payload.title,
        max_raise_cents=payload.max_raise_cents,
        status="draft",
    )
    db.add(round_obj)
    db.commit()
    db.refresh(round_obj)
    return {"round_code": f"RND-{round_obj.id:04d}"}


@router.get("/rounds")
def list_rounds(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.founder_user_id == current_user.id).first()
    if not startup:
        return []
    rounds = db.query(Round).filter(Round.startup_id == startup.id).all()
    return [
        {
            "round_code": f"RND-{round_obj.id:04d}",
            "id": round_obj.id,
            "status": round_obj.status,
            "tier_selected": round_obj.tier_selected,
            "max_raise_cents": round_obj.max_raise_cents,
            "raised_cents": (
                db.query(func.coalesce(func.sum(Investment.amount_cents), 0))
                .filter(Investment.round_id == round_obj.id)
                .scalar()
            ),
        }
        for round_obj in rounds
    ]


class TierRequest(BaseModel):
    risk_level: str = "medium"
    baseline_monthly_revenue_cents: int | None = None
    stage: str = "seed"


@router.post("/rounds/{round_id}/tiers")
def run_tiers(
    round_id: int,
    payload: TierRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    tiers = calculate_tiers(
        round_obj.max_raise_cents,
        risk_level=payload.risk_level,
        baseline_monthly_revenue_cents=payload.baseline_monthly_revenue_cents,
        stage=payload.stage,
    )
    db.query(TierOption).filter(TierOption.round_id == round_id).delete()
    for tier in tiers:
        db.add(
            TierOption(
                round_id=round_id,
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
    return {"status": "ok"}


@router.get("/rounds/{round_id}/tiers")
def list_tiers(
    round_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    options = db.query(TierOption).filter(TierOption.round_id == round_id).all()
    return [
        {
            "tier": opt.tier,
            "revenue_share_bps": opt.revenue_share_bps,
            "time_cap_months": opt.time_cap_months,
            "payout_cap_mult": float(opt.payout_cap_mult),
            "min_hold_days": opt.min_hold_days,
            "exit_fee_bps_quarterly": opt.exit_fee_bps_quarterly,
            "exit_fee_bps_offcycle": opt.exit_fee_bps_offcycle,
            "explanation_json": opt.explanation_json,
        }
        for opt in options
    ]


@router.post("/rounds/{round_id}/select-tier")
def select_tier(
    round_id: int,
    tier: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj or round_obj.status != "draft":
        raise HTTPException(status_code=400, detail="Round not in draft")
    option = db.query(TierOption).filter(TierOption.round_id == round_id, TierOption.tier == tier).first()
    if not option:
        raise HTTPException(status_code=404, detail="Tier not found")
    round_obj.tier_selected = tier
    db.commit()
    return {"round_code": f"RND-{round_obj.id:04d}", "tier_selected": tier}


@router.post("/rounds/{round_id}/publish")
def publish_round(
    round_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj or round_obj.status != "draft" or not round_obj.tier_selected:
        raise HTTPException(status_code=400, detail="Select tier before publish")
    application = db.query(Application).filter(Application.startup_id == round_obj.startup_id).first()
    if not application or application.status != "approved":
        raise HTTPException(status_code=400, detail="Application not approved")
    round_obj.status = "published"
    round_obj.published_at = datetime.utcnow()
    db.commit()
    return {"round_code": f"RND-{round_obj.id:04d}", "status": round_obj.status}


class RevenueReportCreate(BaseModel):
    startup_id: int
    month: str
    gross_revenue_cents: int


@router.post("/revenue/report")
def report_revenue(
    payload: RevenueReportCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    report = RevenueReport(
        startup_id=payload.startup_id,
        month=payload.month,
        gross_revenue_cents=payload.gross_revenue_cents,
        reported_by=current_user.id,
    )
    db.add(report)
    db.commit()
    return {"report_code": f"REV-{report.id:04d}"}


@router.get("/exits")
def list_exits(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.founder_user_id == current_user.id).first()
    exits = []
    if startup:
        exits = (
            db.query(ExitRequest)
            .join(Contract)
            .join(Investment)
            .join(Round)
            .filter(Round.startup_id == startup.id)
            .all()
        )
    return [
        {
            "exit_code": f"EXIT-{exit_req.id:04d}",
            "status": exit_req.status,
            "exit_type": exit_req.exit_type,
            "settlement_method": exit_req.settlement_method,
        }
        for exit_req in exits
    ]


class ExitSettlement(BaseModel):
    settlement_method: str


@router.post("/exits/{exit_id}/settle")
def settle_exit(
    exit_id: int,
    payload: ExitSettlement,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    exit_req = db.query(ExitRequest).filter(ExitRequest.id == exit_id).first()
    if not exit_req:
        raise HTTPException(status_code=404, detail="Exit not found")
    exit_req.status = "settled"
    exit_req.settlement_method = payload.settlement_method
    exit_req.settled_at = datetime.utcnow()
    db.commit()
    return {"status": exit_req.status}
