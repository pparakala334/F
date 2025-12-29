from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.auth.security import create_access_token, verify_password, hash_password
from app.settings import settings

router = APIRouter()


class AuthRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    company_name: str
    okta_enabled: bool


@router.post("/register", response_model=AuthResponse)
def register(payload: AuthRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role="investor", country=settings.country_mode)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return AuthResponse(access_token=token, role=user.role, company_name=settings.company_name, okta_enabled=settings.enable_okta)


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return AuthResponse(access_token=token, role=user.role, company_name=settings.company_name, okta_enabled=settings.enable_okta)


@router.get("/okta/config")
def okta_config():
    return {
        "enabled": settings.enable_okta,
        "issuer": settings.okta_issuer,
        "client_id": settings.okta_client_id,
        "redirect_uri": settings.okta_redirect_uri,
        "company_name": settings.company_name,
    }
