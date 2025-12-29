from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ServiceProvider, IntroRequest

router = APIRouter()


class ProviderCreate(BaseModel):
    name: str
    category: str
    description: str | None = None


class IntroCreate(BaseModel):
    provider_id: int
    requester_id: int


@router.get("/")
def list_providers(db: Session = Depends(get_db)):
    providers = db.query(ServiceProvider).all()
    return [
        {"provider_code": f"SP-{p.id:04d}", "name": p.name, "category": p.category, "description": p.description}
        for p in providers
    ]


@router.post("/")
def create_provider(payload: ProviderCreate, db: Session = Depends(get_db)):
    provider = ServiceProvider(name=payload.name, category=payload.category, description=payload.description)
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return {"provider_code": f"SP-{provider.id:04d}", "name": provider.name}


@router.post("/intro")
def request_intro(payload: IntroCreate, db: Session = Depends(get_db)):
    intro = IntroRequest(provider_id=payload.provider_id, requester_id=payload.requester_id, status="pending")
    db.add(intro)
    db.commit()
    return {"status": "pending"}
