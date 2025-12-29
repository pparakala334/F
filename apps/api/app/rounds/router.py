from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Round, TierOption, Startup
from app.algorithm.service import calculate_tiers

router = APIRouter()


class RoundCreate(BaseModel):
    startup_id: int
    max_raise_cents: int


@router.post("/")
def create_round(payload: RoundCreate, db: Session = Depends(get_db)):
    startup = db.query(Startup).filter(Startup.id == payload.startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    round_obj = Round(startup_id=payload.startup_id, status="draft", max_raise_cents=payload.max_raise_cents)
    db.add(round_obj)
    db.commit()
    db.refresh(round_obj)

    tiers = calculate_tiers(payload.max_raise_cents)
    for tier in tiers:
        db.add(
            TierOption(
                round_id=round_obj.id,
                tier=tier.name,
                multiple=tier.multiple,
                revenue_share_percent=tier.revenue_share_percent,
                months=tier.months,
                explanation=tier.explanation,
            )
        )
    db.commit()
    return {"round_code": f"RND-{round_obj.id:04d}", "status": round_obj.status}


@router.get("/{round_id}/tiers")
def get_tiers(round_id: int, db: Session = Depends(get_db)):
    options = db.query(TierOption).filter(TierOption.round_id == round_id).all()
    return [
        {
            "tier": opt.tier,
            "multiple": float(opt.multiple),
            "revenue_share_percent": float(opt.revenue_share_percent),
            "months": opt.months,
            "explanation": opt.explanation,
        }
        for opt in options
    ]


@router.post("/{round_id}/select-tier")
def select_tier(round_id: int, tier: str, db: Session = Depends(get_db)):
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    if round_obj.status != "draft":
        raise HTTPException(status_code=400, detail="Round not in draft")
    option = db.query(TierOption).filter(TierOption.round_id == round_id, TierOption.tier == tier).first()
    if not option:
        raise HTTPException(status_code=404, detail="Tier not found")
    round_obj.selected_tier = tier
    db.commit()
    return {"round_code": f"RND-{round_obj.id:04d}", "selected_tier": tier}


@router.post("/{round_id}/publish")
def publish_round(round_id: int, db: Session = Depends(get_db)):
    round_obj = db.query(Round).filter(Round.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    if round_obj.status != "draft" or not round_obj.selected_tier:
        raise HTTPException(status_code=400, detail="Select tier before publishing")
    round_obj.status = "published"
    db.commit()
    return {"round_code": f"RND-{round_obj.id:04d}", "status": round_obj.status}


@router.get("/published")
def list_published(db: Session = Depends(get_db)):
    rounds = db.query(Round).filter(Round.status == "published").all()
    data = []
    for r in rounds:
        startup = db.query(Startup).filter(Startup.id == r.startup_id).first()
        data.append(
            {
                "round_code": f"RND-{r.id:04d}",
                "startup_name": startup.name if startup else "Unknown",
                "status": r.status,
                "max_raise_cents": r.max_raise_cents,
                "selected_tier": r.selected_tier,
            }
        )
    return data
