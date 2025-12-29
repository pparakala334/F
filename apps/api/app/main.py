from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings
from app.auth.router import router as auth_router
from app.applications.router import router as applications_router
from app.rounds.router import router as rounds_router
from app.investments.router import router as investments_router
from app.admin.router import router as admin_router
from app.distributions.router import router as distributions_router
from app.documents.router import router as documents_router
from app.services_marketplace.router import router as services_router
from app.users.router import router as users_router
from app.startups.router import router as startups_router
from app.revenue.router import router as revenue_router
from app.exits.router import router as exits_router
from app.loans.router import router as loans_router
from app.ledger.router import router as ledger_router
from app.audit.router import router as audit_router

app = FastAPI(title=f"{settings.company_name} API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(applications_router, prefix="/applications", tags=["applications"])
app.include_router(rounds_router, prefix="/rounds", tags=["rounds"])
app.include_router(investments_router, prefix="/investments", tags=["investments"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(distributions_router, prefix="/distributions", tags=["distributions"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(services_router, prefix="/services", tags=["services"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(startups_router, prefix="/startups", tags=["startups"])
app.include_router(revenue_router, prefix="/revenue", tags=["revenue"])
app.include_router(exits_router, prefix="/exits", tags=["exits"])
app.include_router(loans_router, prefix="/loans", tags=["loans"])
app.include_router(ledger_router, prefix="/ledger", tags=["ledger"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])


@app.get("/health")
def health():
    return {"status": "ok", "company": settings.company_name}
