# Architecture Overview

This monorepo contains:

- `apps/api`: FastAPI backend (Python 3.12) with SQLAlchemy 2.0 + Alembic.
- `apps/web`: React + Vite + TypeScript frontend with Tailwind and shadcn/ui.
- `packages/shared`: Shared types + schema stubs for validation.
- `infra`: Docker Compose for local development.
- `scripts`: Seed/demo data scripts.

The API implements provider stubs with graceful fallbacks when credentials are missing.
