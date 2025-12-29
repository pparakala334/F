from datetime import datetime
import json
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
    Distribution,
    ExitRequest,
    Contract,
    Investment,
    AuditLog,
    LedgerEntry,
)
from app.providers.payments import charge_application_fee
from app.providers.storage import create_signed_upload_url, complete_upload
from app.algorithm.service import calculate_tiers
from app.settings import settings

router = APIRouter()


class StartupCreate(BaseModel):
    legal_name: str
    operating_name: str | None = None
    country: str = "CA"
    incorporation_type: str
    incorporation_date: str
    website: str | None = None
    logo_key: str | None = None
    industry: str
    sub_industry: str | None = None
    short_description: str
    long_description: str
    current_monthly_revenue: str
    revenue_model: str
    revenue_consistency: str
    revenue_stage: str
    existing_debt: bool
    existing_investors: bool
    intended_use_of_funds: list[str]
    target_funding_size: str
    preferred_timeline: str


@router.get("/startups")
def list_startups(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startups = db.query(Startup).filter(Startup.founder_user_id == current_user.id).all()
    data = []
    for startup in startups:
        total_raised = (
            db.query(func.coalesce(func.sum(Investment.amount_cents), 0))
            .join(Round, Round.id == Investment.round_id)
            .filter(Round.startup_id == startup.id)
            .scalar()
        )
        active_round = db.query(Round).filter(Round.startup_id == startup.id, Round.status == "published").first()
        last_report = (
            db.query(RevenueReport)
            .filter(RevenueReport.startup_id == startup.id)
            .order_by(RevenueReport.created_at.desc())
            .first()
        )
        status = startup.status
        if active_round:
            status = "live"
        elif db.query(Application).filter(Application.startup_id == startup.id, Application.status == "submitted").first():
            status = "application_pending"
        elif db.query(Application).filter(Application.startup_id == startup.id, Application.status == "approved").first():
            status = "approved"
        data.append(
            {
                "startup_code": f"STP-{startup.id:04d}",
                "id": startup.id,
                "name": startup.operating_name or startup.legal_name,
                "industry": startup.industry,
                "country": startup.country,
                "status": status,
                "total_raised_cents": total_raised,
                "active_round": bool(active_round),
                "last_revenue_reported": last_report.month if last_report else None,
            }
        )
    return data


@router.post("/startups")
def create_startup(payload: StartupCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    country = payload.country
    if settings.country_mode == "CA":
        country = "CA"
    startup = Startup(
        founder_user_id=current_user.id,
        legal_name=payload.legal_name,
        operating_name=payload.operating_name,
        country=country,
        incorporation_type=payload.incorporation_type,
        incorporation_date=payload.incorporation_date,
        website=payload.website,
        logo_key=payload.logo_key,
        industry=payload.industry,
        sub_industry=payload.sub_industry,
        short_description=payload.short_description,
        long_description=payload.long_description,
        current_monthly_revenue=payload.current_monthly_revenue,
        revenue_model=payload.revenue_model,
        revenue_consistency=payload.revenue_consistency,
        revenue_stage=payload.revenue_stage,
        existing_debt=1 if payload.existing_debt else 0,
        existing_investors=1 if payload.existing_investors else 0,
        intended_use_of_funds=json.dumps(payload.intended_use_of_funds),
        target_funding_size=payload.target_funding_size,
        preferred_timeline=payload.preferred_timeline,
        status="draft",
    )
    db.add(startup)
    db.commit()
    db.refresh(startup)
    return {"startup_code": f"STP-{startup.id:04d}", "id": startup.id}


@router.get("/startups/{startup_id}")
def get_startup(startup_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return {
        "startup_code": f"STP-{startup.id:04d}",
        "id": startup.id,
        "legal_name": startup.legal_name,
        "operating_name": startup.operating_name,
        "country": startup.country,
        "incorporation_type": startup.incorporation_type,
        "incorporation_date": startup.incorporation_date,
        "website": startup.website,
        "industry": startup.industry,
        "sub_industry": startup.sub_industry,
        "short_description": startup.short_description,
        "long_description": startup.long_description,
        "revenue_model": startup.revenue_model,
        "revenue_stage": startup.revenue_stage,
        "intended_use_of_funds": json.loads(startup.intended_use_of_funds),
    }


class ApplicationCreate(BaseModel):
    name: str
    application_type: str
    requested_limit_cents: int
    risk_preference: str


@router.post("/startups/{startup_id}/applications")
def create_application(
    startup_id: int,
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    application = Application(
        startup_id=startup.id,
        name=payload.name,
        application_type=payload.application_type,
        requested_limit_cents=payload.requested_limit_cents,
        risk_preference=payload.risk_preference,
        status="draft",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return {"application_code": f"APP-{application.id:04d}", "status": application.status}


@router.get("/startups/{startup_id}/applications")
def list_applications(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    apps = db.query(Application).filter(Application.startup_id == startup_id).all()
    return [
        {
            "application_code": f"APP-{app.id:04d}",
            "id": app.id,
            "name": app.name,
            "application_type": app.application_type,
            "created_at": app.created_at,
            "submitted_at": app.submitted_at,
            "reviewed_at": app.reviewed_at,
            "status": app.status,
        }
        for app in apps
    ]


@router.get("/applications/{application_id}")
def get_application(application_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    startup = db.query(Startup).filter(Startup.id == app.startup_id).first()
    if not startup or startup.founder_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    documents = db.query(Document).filter(Document.startup_id == app.startup_id).all()
    return {
        "application_code": f"APP-{app.id:04d}",
        "status": app.status,
        "name": app.name,
        "application_type": app.application_type,
        "requested_limit_cents": app.requested_limit_cents,
        "risk_preference": app.risk_preference,
        "admin_notes": app.admin_notes,
        "startup_snapshot": {
            "name": startup.operating_name or startup.legal_name,
            "industry": startup.industry,
            "country": startup.country,
            "short_description": startup.short_description,
        },
        "documents": [{"doc_type": doc.doc_type, "filename": doc.filename} for doc in documents],
    }


class ApplicationSubmit(BaseModel):
    fee_cents: int = 2500


@router.post("/applications/{application_id}/submit")
def submit_application(
    application_id: int,
    payload: ApplicationSubmit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application or application.status != "draft":
        raise HTTPException(status_code=400, detail="Application not in draft")
    startup = db.query(Startup).filter(Startup.id == application.startup_id).first()
    if not startup or startup.founder_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    payment_id = charge_application_fee(db, current_user.id, payload.fee_cents)
    application.fee_payment_id = payment_id
    application.status = "submitted"
    application.submitted_at = datetime.utcnow()
    db.add(AuditLog(actor_user_id=current_user.id, action="application_submitted", entity_type="application", entity_id=application.id))
    db.commit()
    return {"application_code": f"APP-{application.id:04d}", "status": application.status}


class DocumentPresign(BaseModel):
    filename: str
    doc_type: str
    startup_id: int


@router.post("/documents/presign")
def presign_document(payload: DocumentPresign, current_user=Depends(get_current_user)):
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


@router.get("/startups/{startup_id}/applications/approved")
def approved_applications(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    apps = db.query(Application).filter(Application.startup_id == startup_id, Application.status == "approved").all()
    return [
        {
            "application_code": f"APP-{app.id:04d}",
            "id": app.id,
            "name": app.name,
            "application_type": app.application_type,
            "approved_limit_cents": app.requested_limit_cents,
            "risk_preference": app.risk_preference,
            "reviewed_at": app.reviewed_at,
        }
        for app in apps
    ]


class RoundCreate(BaseModel):
    title: str


@router.post("/applications/{application_id}/rounds")
def create_round(
    application_id: int,
    payload: RoundCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    application = db.query(Application).filter(Application.id == application_id, Application.status == "approved").first()
    if not application:
        raise HTTPException(status_code=400, detail="Application not approved")
    startup = db.query(Startup).filter(Startup.id == application.startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    round_obj = Round(
        startup_id=application.startup_id,
        application_id=application.id,
        title=payload.title,
        max_raise_cents=application.requested_limit_cents,
        status="draft",
    )
    db.add(round_obj)
    db.commit()
    db.refresh(round_obj)
    return {"round_code": f"RND-{round_obj.id:04d}", "id": round_obj.id}


@router.get("/startups/{startup_id}/rounds")
def list_rounds(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    rounds = db.query(Round).filter(Round.startup_id == startup_id).all()
    data = []
    for round_obj in rounds:
        raised = (
            db.query(func.coalesce(func.sum(Investment.amount_cents), 0))
            .filter(Investment.round_id == round_obj.id)
            .scalar()
        )
        investors = db.query(Investment).filter(Investment.round_id == round_obj.id).count()
        data.append(
            {
                "round_code": f"RND-{round_obj.id:04d}",
                "id": round_obj.id,
                "status": round_obj.status,
                "tier_selected": round_obj.tier_selected,
                "max_raise_cents": round_obj.max_raise_cents,
                "raised_cents": raised,
                "investor_count": investors,
            }
        )
    return data


class TierRequest(BaseModel):
    risk_level: str = "medium"
    baseline_monthly_revenue_cents: int | None = None
    stage: str = "seed"


@router.post("/rounds/{round_id}/tiers")
def run_tiers(round_id: int, payload: TierRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    startup = db.query(Startup).filter(Startup.id == round_obj.startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
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
def list_tiers(round_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    startup = db.query(Startup).filter(Startup.id == round_obj.startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Round not found")
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
def select_tier(round_id: int, tier: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj or round_obj.status != "draft":
        raise HTTPException(status_code=400, detail="Round not in draft")
    startup = db.query(Startup).filter(Startup.id == round_obj.startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Round not found")
    option = db.query(TierOption).filter(TierOption.round_id == round_id, TierOption.tier == tier).first()
    if not option:
        raise HTTPException(status_code=404, detail="Tier not found")
    round_obj.tier_selected = tier
    db.commit()
    return {"round_code": f"RND-{round_obj.id:04d}", "tier_selected": tier}


@router.post("/rounds/{round_id}/publish")
def publish_round(round_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj or round_obj.status != "draft" or not round_obj.tier_selected:
        raise HTTPException(status_code=400, detail="Select tier before publish")
    startup = db.query(Startup).filter(Startup.id == round_obj.startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Round not found")
    application = db.query(Application).filter(Application.id == round_obj.application_id).first()
    if not application or application.status != "approved":
        raise HTTPException(status_code=400, detail="Application not approved")
    round_obj.status = "published"
    round_obj.published_at = datetime.utcnow()
    startup.status = "live"
    db.commit()
    return {"round_code": f"RND-{round_obj.id:04d}", "status": round_obj.status}


class RevenueReportCreate(BaseModel):
    startup_id: int
    month: str
    gross_revenue_cents: int


@router.post("/revenue/report")
def report_revenue(payload: RevenueReportCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == payload.startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    report = RevenueReport(
        startup_id=payload.startup_id,
        month=payload.month,
        gross_revenue_cents=payload.gross_revenue_cents,
        reported_by=current_user.id,
        distribution_status="pending",
    )
    db.add(report)
    db.add(
        LedgerEntry(
            entry_type="revenue_report",
            actor_user_id=current_user.id,
            startup_id=payload.startup_id,
            amount_cents=payload.gross_revenue_cents,
            metadata_json=json.dumps({"month": payload.month}),
        )
    )
    db.commit()
    return {"report_code": f"REV-{report.id:04d}"}


@router.get("/revenue/{startup_id}")
def list_revenue(startup_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    startup = db.query(Startup).filter(Startup.id == startup_id, Startup.founder_user_id == current_user.id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    reports = db.query(RevenueReport).filter(RevenueReport.startup_id == startup_id).all()
    data = []
    for report in reports:
        distribution = (
            db.query(Distribution)
            .filter(Distribution.startup_id == startup_id, Distribution.month == report.month)
            .first()
        )
        data.append(
            {
                "report_code": f"REV-{report.id:04d}",
                "month": report.month,
                "gross_revenue_cents": report.gross_revenue_cents,
                "created_at": report.created_at,
                "distribution_status": report.distribution_status,
                "total_distributed_cents": distribution.total_distributed_cents if distribution else 0,
            }
        )
    return data


@router.get("/exits")
def list_exits(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Forbidden")
    exits = (
        db.query(ExitRequest)
        .join(Contract)
        .join(Investment)
        .join(Round)
        .join(Startup)
        .filter(Startup.founder_user_id == current_user.id)
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
def settle_exit(exit_id: int, payload: ExitSettlement, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
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
