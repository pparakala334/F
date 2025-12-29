from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings
from app.auth.router import router as auth_router
from app.founder.router import router as founder_router
from app.investor.router import router as investor_router
from app.admin.router import router as admin_router

app = FastAPI(title=f"{settings.company_name} API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(founder_router, prefix="/founder", tags=["founder"])
app.include_router(investor_router, prefix="/investor", tags=["investor"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/health")
def health():
    return {"status": "ok", "company": settings.company_name}
