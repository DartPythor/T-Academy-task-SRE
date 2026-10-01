"""Tests for scam detection service."""
from __future__ import annotations

from uuid import UUID

import pytest

from backend.application.services.scam_detector import ScamDetector
from backend.domain.entities import Company, Vacancy
from backend.domain.enums import Currency
from backend.domain.metrics import VacancyMetric
from backend.domain.values import (
    ApplyScore,
    Confidence,
    Money,
    SalaryRange,
    ScamScore,
)

from decimal import Decimal

@pytest.fixture
def detector() -> ScamDetector:
    return ScamDetector()

@pytest.fixture
def vacancy() -> Vacancy:
    v = Vacancy.create(
        source_id=UUID("00000000-0000-0000-0000-000000000001"),
        external_id="ext-1",
        title="Python Developer",
        url="https://example.com/vacancy/1",
        description="A" * 500,
    )
    company = Company.create(name="Safe Corp")
    v.company_id = company.id

    metric = VacancyMetric.create(
        vacancy_id=v.id,
        salary=SalaryRange(
            min_amount=Money(Decimal("100000"), Currency.RUB),
            max_amount=Money(Decimal("150000"), Currency.RUB),
        ),
        scam_score=ScamScore(0),
        apply_score=ApplyScore(50),
        confidence=Confidence(0.9),
    )
    v.attach_metric(metric)
    return v

class TestScamDetector:
    def test_clean_vacancy(self, detector, vacancy):
        """Clean vacancy with all signals absent — score should be 0."""
        score = detector.score(vacancy)
        assert score.value == 0

    def test_no_company(self, detector, vacancy):
        """Missing company adds 20 points."""
        score = detector.score(vacancy)
        assert score.value == 0

    def test_short_description(self, detector, vacancy):
        """Short description adds 10 points."""
        vacancy.description = "Short"
        score = detector.score(vacancy)
        assert score.value >= 10

    def test_no_salary(self, detector, vacancy):
        """Missing salary adds 15 points."""
        vacancy.metric = VacancyMetric.create(
            vacancy_id=vacancy.id,
            salary=SalaryRange(),
            scam_score=ScamScore(0),
            apply_score=ApplyScore(50),
            confidence=Confidence(0.9),
        )
        score = detector.score(vacancy)
        assert score.value >= 15

    def test_suspicious_url(self, detector, vacancy):
        """bit.ly URL adds 10 points."""
        vacancy.url = "https://bit.ly/3xyz"
        score = detector.score(vacancy)
        assert score.value >= 10

    def test_max_score_capped(self, detector, vacancy):
        """Score is capped at 100."""
        vacancy.company_id = None
        vacancy.description = ""
        vacancy.url = "https://bit.ly/3xyz"
        vacancy.metric = VacancyMetric.create(
            vacancy_id=vacancy.id,
            salary=SalaryRange(),
            scam_score=ScamScore(0),
            apply_score=ApplyScore(50),
            confidence=Confidence(0.9),
        )
        score = detector.score(vacancy)
        assert score.value <= 100
