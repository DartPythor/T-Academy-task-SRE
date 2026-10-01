from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.infrastructure.db.base import Base, utcnow

class SourceORM(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    vacancies: Mapped[list["VacancyORM"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('telegram_channel', 'career_site', 'job_board', 'other')",
            name="ck_sources_type",
        ),
    )

class CompanyORM(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(1024))
    description: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    vacancies: Mapped[list["VacancyORM"]] = relationship(back_populates="company")

class SkillORM(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)

class VacancySkillORM(Base):
    __tablename__ = "vacancy_skills"

    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )

class VacancyORM(Base):
    __tablename__ = "vacancies"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        index=True,
    )

    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    employment_type: Mapped[Optional[str]] = mapped_column(String(32))
    work_mode: Mapped[Optional[str]] = mapped_column(String(32))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="new")
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    source: Mapped["SourceORM"] = relationship(back_populates="vacancies")
    company: Mapped[Optional["CompanyORM"]] = relationship(back_populates="vacancies")
    metric: Mapped[Optional["VacancyMetricORM"]] = relationship(
        back_populates="vacancy",
        uselist=False,
        cascade="all, delete-orphan",
    )
    skills: Mapped[list["SkillORM"]] = relationship(
        secondary="vacancy_skills",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "source_id", "external_id", name="uq_vacancies_source_external"
        ),
        CheckConstraint(
            "status IN ('new', 'processed', 'archived')",
            name="ck_vacancies_status",
        ),
        CheckConstraint(
            "employment_type IS NULL OR employment_type IN "
            "('full_time', 'part_time', 'contract', 'internship', 'freelance')",
            name="ck_vacancies_employment_type",
        ),
        CheckConstraint(
            "work_mode IS NULL OR work_mode IN ('remote', 'hybrid', 'office')",
            name="ck_vacancies_work_mode",
        ),
        Index("ix_vacancies_status_published", "status", "published_at"),
    )

class VacancyMetricORM(Base):
    __tablename__ = "vacancy_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    salary_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    salary_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    salary_currency: Mapped[Optional[str]] = mapped_column(String(8))
    salary_gross: Mapped[Optional[bool]] = mapped_column(Boolean)

    scam_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    apply_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)

    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    vacancy: Mapped["VacancyORM"] = relationship(back_populates="metric")

    __table_args__ = (
        CheckConstraint(
            "scam_score BETWEEN 0 AND 100", name="ck_metric_scam_score"
        ),
        CheckConstraint(
            "apply_score BETWEEN 0 AND 100", name="ck_metric_apply_score"
        ),
        CheckConstraint(
            "confidence BETWEEN 0 AND 1", name="ck_metric_confidence"
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_metric_salary_range",
        ),
        CheckConstraint(
            "salary_currency IS NULL OR salary_currency IN "
            "('RUB', 'USD', 'EUR', 'KZT', 'BYN', 'OTHER')",
            name="ck_metric_salary_currency",
        ),
    )

