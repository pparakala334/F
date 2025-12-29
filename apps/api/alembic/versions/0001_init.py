"""init

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255)),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "startup_applications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("founder_id", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "startups",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("founder_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )

    op.create_table(
        "rounds",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("selected_tier", sa.String(length=20)),
        sa.Column("max_raise_cents", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "tier_options",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("round_id", sa.Integer, nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=False),
        sa.Column("multiple", sa.Numeric(10, 2), nullable=False),
        sa.Column("revenue_share_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("months", sa.Integer, nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
    )

    op.create_table(
        "investments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("investor_id", sa.Integer, nullable=False),
        sa.Column("round_id", sa.Integer, nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("investment_id", sa.Integer, nullable=False),
        sa.Column("payout_cap_multiple", sa.Numeric(10, 2), nullable=False),
        sa.Column("months_cap", sa.Integer, nullable=False),
        sa.Column("min_hold_months", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_paid_cents", sa.Integer, nullable=False),
    )

    op.create_table(
        "revenue_reports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("month", sa.String(length=20), nullable=False),
        sa.Column("gross_revenue_cents", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "distributions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("contract_id", sa.Integer, nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "exit_requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("contract_id", sa.Integer, nullable=False),
        sa.Column("window", sa.String(length=20), nullable=False),
        sa.Column("fee_bps", sa.Integer, nullable=False),
        sa.Column("settlement", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )

    op.create_table(
        "loan_offers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("fee_cents", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("entry_type", sa.String(length=50), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("meta", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("storage_url", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "service_providers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text),
    )

    op.create_table(
        "intro_requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("provider_id", sa.Integer, nullable=False),
        sa.Column("requester_id", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor_id", sa.Integer, nullable=False),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("details", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "email_outbox",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("to_address", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("html", sa.Text, nullable=False),
        sa.Column("provider_message_id", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "analytics_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("event", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer),
        sa.Column("properties", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("email_outbox")
    op.drop_table("audit_logs")
    op.drop_table("intro_requests")
    op.drop_table("service_providers")
    op.drop_table("documents")
    op.drop_table("ledger_entries")
    op.drop_table("loan_offers")
    op.drop_table("exit_requests")
    op.drop_table("distributions")
    op.drop_table("revenue_reports")
    op.drop_table("contracts")
    op.drop_table("investments")
    op.drop_table("tier_options")
    op.drop_table("rounds")
    op.drop_table("startups")
    op.drop_table("startup_applications")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
