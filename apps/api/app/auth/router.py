from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.auth.security import create_access_token, verify_password, hash_password, decode_token
from app.settings import settings

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str
    role: str
    country: str = "CA"


class AuthRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    company_name: str


def ensure_admin(db: Session) -> None:
    admin = db.query(User).filter(User.email == settings.admin_email).first()
    if not admin:
        db.add(
            User(
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                role="admin",
                country=settings.country_mode,
            )
        )
        db.commit()


def get_current_user(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    ensure_admin(db)
    if payload.role not in {"founder", "investor"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        country=payload.country,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return AuthResponse(access_token=token, role=user.role, company_name=settings.company_name)


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    ensure_admin(db)
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return AuthResponse(access_token=token, role=user.role, company_name=settings.company_name)


@router.post("/logout")
def logout():
    return {"status": "ok"}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "user_code": f"USR-{current_user.id:04d}",
        "email": current_user.email,
        "role": current_user.role,
        "country": current_user.country,
    }
