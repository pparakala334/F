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
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "startups",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("founder_user_id", sa.Integer, nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("operating_name", sa.String(length=255)),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("incorporation_type", sa.String(length=50), nullable=False),
        sa.Column("incorporation_date", sa.String(length=20), nullable=False),
        sa.Column("website", sa.String(length=255)),
        sa.Column("logo_key", sa.String(length=255)),
        sa.Column("industry", sa.String(length=100), nullable=False),
        sa.Column("sub_industry", sa.String(length=100)),
        sa.Column("short_description", sa.String(length=255), nullable=False),
        sa.Column("long_description", sa.Text, nullable=False),
        sa.Column("current_monthly_revenue", sa.String(length=50), nullable=False),
        sa.Column("revenue_model", sa.String(length=50), nullable=False),
        sa.Column("revenue_consistency", sa.String(length=50), nullable=False),
        sa.Column("revenue_stage", sa.String(length=50), nullable=False),
        sa.Column("existing_debt", sa.Integer, nullable=False),
        sa.Column("existing_investors", sa.Integer, nullable=False),
        sa.Column("intended_use_of_funds", sa.Text, nullable=False),
        sa.Column("target_funding_size", sa.String(length=50), nullable=False),
        sa.Column("preferred_timeline", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("application_type", sa.String(length=50), nullable=False),
        sa.Column("requested_limit_cents", sa.Integer, nullable=False),
        sa.Column("risk_preference", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("fee_payment_id", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("submitted_at", sa.DateTime),
        sa.Column("reviewed_at", sa.DateTime),
        sa.Column("reviewer_id", sa.Integer),
        sa.Column("admin_notes", sa.Text),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "rounds",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("application_id", sa.Integer, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("max_raise_cents", sa.Integer, nullable=False),
        sa.Column("tier_selected", sa.String(length=20)),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("published_at", sa.DateTime),
    )

    op.create_table(
        "tier_options",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("round_id", sa.Integer, nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=False),
        sa.Column("revenue_share_bps", sa.Integer, nullable=False),
        sa.Column("time_cap_months", sa.Integer, nullable=False),
        sa.Column("payout_cap_mult", sa.Numeric(10, 2), nullable=False),
        sa.Column("min_hold_days", sa.Integer, nullable=False),
        sa.Column("exit_fee_bps_quarterly", sa.Integer, nullable=False),
        sa.Column("exit_fee_bps_offcycle", sa.Integer, nullable=False),
        sa.Column("explanation_json", sa.Text, nullable=False),
    )

    op.create_table(
        "investments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("round_id", sa.Integer, nullable=False),
        sa.Column("investor_user_id", sa.Integer, nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("payment_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("investment_id", sa.Integer, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("principal_cents", sa.Integer, nullable=False),
        sa.Column("payout_cap_cents", sa.Integer, nullable=False),
        sa.Column("revenue_share_bps", sa.Integer, nullable=False),
        sa.Column("start_date", sa.DateTime, nullable=False),
        sa.Column("end_date_cap", sa.DateTime),
        sa.Column("paid_to_date_cents", sa.Integer, nullable=False),
    )

    op.create_table(
        "revenue_reports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("month", sa.String(length=20), nullable=False),
        sa.Column("gross_revenue_cents", sa.Integer, nullable=False),
        sa.Column("reported_by", sa.Integer, nullable=False),
        sa.Column("distribution_status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "distributions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("startup_id", sa.Integer, nullable=False),
        sa.Column("month", sa.String(length=20), nullable=False),
        sa.Column("total_distributed_cents", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("created_by", sa.Integer, nullable=False),
    )

    op.create_table(
        "payouts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("contract_id", sa.Integer, nullable=False),
        sa.Column("distribution_id", sa.Integer, nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("payout_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "exits",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("contract_id", sa.Integer, nullable=False),
        sa.Column("requested_at", sa.DateTime, nullable=False),
        sa.Column("exit_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("quoted_amount_cents", sa.Integer),
        sa.Column("fee_cents", sa.Integer),
        sa.Column("settlement_method", sa.String(length=20)),
        sa.Column("settled_at", sa.DateTime),
    )

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("entry_type", sa.String(length=50), nullable=False),
        sa.Column("actor_user_id", sa.Integer),
        sa.Column("startup_id", sa.Integer),
        sa.Column("round_id", sa.Integer),
        sa.Column("contract_id", sa.Integer),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("metadata_json", sa.Text),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("actor_user_id", sa.Integer),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=False),
        sa.Column("metadata_json", sa.Text),
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
    op.drop_table("ledger_entries")
    op.drop_table("exits")
    op.drop_table("payouts")
    op.drop_table("distributions")
    op.drop_table("revenue_reports")
    op.drop_table("contracts")
    op.drop_table("investments")
    op.drop_table("tier_options")
    op.drop_table("rounds")
    op.drop_table("documents")
    op.drop_table("applications")
    op.drop_table("startups")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
