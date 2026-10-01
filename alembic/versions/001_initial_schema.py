"""initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""

    # ── sources ────────────────────────────────────────────────
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "type IN ('telegram_channel', 'career_site', 'job_board', 'other')",
            name="ck_sources_type",
        ),
    )

    # ── companies ──────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("website", sa.String(1024), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── skills ─────────────────────────────────────────────────
    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
    )

    # ── vacancies ──────────────────────────────────────────────
    op.create_table(
        "vacancies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("sources.id", ondelete="RESTRICT"),
                  nullable=False, index=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("companies.id", ondelete="SET NULL"),
                  nullable=True, index=True),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, default=""),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("employment_type", sa.String(32), nullable=True),
        sa.Column("work_mode", sa.String(32), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, default="new"),
        sa.Column("raw_data", postgresql.JSONB(), nullable=False, default=dict),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_id", "external_id",
                            name="uq_vacancies_source_external"),
        sa.CheckConstraint(
            "status IN ('new', 'processed', 'archived')",
            name="ck_vacancies_status",
        ),
        sa.CheckConstraint(
            "employment_type IS NULL OR employment_type IN "
            "('full_time', 'part_time', 'contract', 'internship', 'freelance')",
            name="ck_vacancies_employment_type",
        ),
        sa.CheckConstraint(
            "work_mode IS NULL OR work_mode IN ('remote', 'hybrid', 'office')",
            name="ck_vacancies_work_mode",
        ),
    )
    op.create_index(
        "ix_vacancies_status_published",
        "vacancies",
        ["status", "published_at"],
    )

    # ── vacancy_skills (M2M) ───────────────────────────────────
    op.create_table(
        "vacancy_skills",
        sa.Column("vacancy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vacancies.id", ondelete="CASCADE"),
                  primary_key=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("skills.id", ondelete="CASCADE"),
                  primary_key=True),
    )

    # ── vacancy_metrics ────────────────────────────────────────
    op.create_table(
        "vacancy_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vacancy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vacancies.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("salary_min", sa.Numeric(14, 2), nullable=True),
        sa.Column("salary_max", sa.Numeric(14, 2), nullable=True),
        sa.Column("salary_currency", sa.String(8), nullable=True),
        sa.Column("salary_gross", sa.Boolean(), nullable=True),
        sa.Column("scam_score", sa.SmallInteger(), nullable=False),
        sa.Column("apply_score", sa.SmallInteger(), nullable=False),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False, default=dict),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "scam_score BETWEEN 0 AND 100", name="ck_metric_scam_score",
        ),
        sa.CheckConstraint(
            "apply_score BETWEEN 0 AND 100", name="ck_metric_apply_score",
        ),
        sa.CheckConstraint(
            "confidence BETWEEN 0 AND 1", name="ck_metric_confidence",
        ),
        sa.CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_metric_salary_range",
        ),
        sa.CheckConstraint(
            "salary_currency IS NULL OR salary_currency IN "
            "('RUB', 'USD', 'EUR', 'KZT', 'BYN', 'OTHER')",
            name="ck_metric_salary_currency",
        ),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("vacancy_metrics")
    op.drop_table("vacancy_skills")
    op.drop_table("vacancies")
    op.drop_table("skills")
    op.drop_table("companies")
    op.drop_table("sources")