from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RevenueReport

router = APIRouter()


class RevenueCreate(BaseModel):
    startup_id: int
    month: str
    gross_revenue_cents: int


@router.post("/")
def create_report(payload: RevenueCreate, db: Session = Depends(get_db)):
    report = RevenueReport(
        startup_id=payload.startup_id,
        month=payload.month,
        gross_revenue_cents=payload.gross_revenue_cents,
    )
    db.add(report)
    db.commit()
    return {"report_code": f"REV-{report.id:04d}", "month": report.month}


@router.get("/startup/{startup_id}")
def list_reports(startup_id: int, db: Session = Depends(get_db)):
    reports = db.query(RevenueReport).filter(RevenueReport.startup_id == startup_id).all()
    return [
        {"report_code": f"REV-{r.id:04d}", "month": r.month, "gross_revenue_cents": r.gross_revenue_cents}
        for r in reports
    ]
