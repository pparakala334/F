from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import StartupApplication
from app.providers.payments import charge_application_fee

router = APIRouter()


class ApplicationCreate(BaseModel):
    founder_id: int
    company_name: str
    description: str | None = None
    fee_cents: int = 2500


class ApplicationResponse(BaseModel):
    id: int
    status: str
    company_name: str
    fee_payment_id: str


@router.post("/", response_model=ApplicationResponse)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    payment_id = charge_application_fee(db, payload.founder_id, payload.fee_cents)
    application = StartupApplication(
        founder_id=payload.founder_id,
        company_name=payload.company_name,
        description=payload.description,
        status="pending",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return ApplicationResponse(
        id=application.id,
        status=application.status,
        company_name=application.company_name,
        fee_payment_id=payment_id,
    )


@router.get("/")
def list_applications(db: Session = Depends(get_db)):
    apps = db.query(StartupApplication).all()
    return [
        {
            "id": app.id,
            "status": app.status,
            "company_name": app.company_name,
            "description": app.description,
        }
        for app in apps
    ]


@router.post("/{application_id}/decision")
def decide(application_id: int, decision: str, db: Session = Depends(get_db)):
    application = db.query(StartupApplication).filter(StartupApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.status != "pending":
        raise HTTPException(status_code=400, detail="Application already decided")
    if decision not in {"approved", "denied"}:
        raise HTTPException(status_code=400, detail="Invalid decision")
    application.status = decision
    db.commit()
    return {"id": application.id, "status": application.status}
