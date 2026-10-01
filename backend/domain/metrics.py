from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from backend.domain.values import (
    ApplyScore,
    Confidence,
    SalaryRange,
    ScamScore,
)

@dataclass
class VacancyMetric:
    id: UUID
    vacancy_id: UUID
    salary: SalaryRange
    scam_score: ScamScore
    apply_score: ApplyScore
    confidence: Confidence
    details: dict = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        vacancy_id: UUID,
        salary: SalaryRange,
        scam_score: ScamScore,
        apply_score: ApplyScore,
        confidence: Confidence,
        details: Optional[dict] = None,
    ) -> "VacancyMetric":
        return cls(
            id=uuid4(),
            vacancy_id=vacancy_id,
            salary=salary,
            scam_score=scam_score,
            apply_score=apply_score,
            confidence=confidence,
            details=details or {},
        )

    def recalculate(
        self,
        salary: SalaryRange,
        scam_score: ScamScore,
        apply_score: ApplyScore,
        confidence: Confidence,
        details: Optional[dict] = None,
    ) -> None:
        self.salary = salary
        self.scam_score = scam_score
        self.apply_score = apply_score
        self.confidence = confidence
        self.details = details or {}
        self.calculated_at = datetime.now(timezone.utc)

