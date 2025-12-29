# Radion Revenue-Share Marketplace (Demo)

A production-structured monorepo for a revenue-share startup funding marketplace demo (non-equity). This demo includes end-to-end flows with simulated money movements and provider stubs.

## Stack

- **Frontend**: React + Vite + TypeScript + Tailwind + shadcn/ui + Framer Motion
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic + Postgres
- **Auth**: Okta OIDC preferred; JWT email/password fallback
- **Infra**: Docker Compose for Postgres + API + Web

## Setup

1. Copy environment file:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker-compose -f infra/docker-compose.yml up --build
```

- API: http://localhost:8000
- Web: http://localhost:5173

## Seed Demo Data

```bash
docker-compose -f infra/docker-compose.yml exec api python /scripts/seed_demo_data.py
```

### Demo Accounts

- Admin: `admin@demo.com` / `password`
- Founder: `founder@demo.com` / `password`
- Investor: `investor@demo.com` / `password`

## Notes

- The demo includes simulated payment flows and provider stubs when keys are not present.
- Disclaimers are required on critical actions (invest, publish, exit).
