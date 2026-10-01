"""Tests for apply advisor service."""
from __future__ import annotations

from uuid import UUID

import pytest

from backend.application.services.apply_advisor import ApplyAdvisor
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

@pytest.fixture
def advisor() -> ApplyAdvisor:
    return ApplyAdvisor()

class TestApplyAdvisor:
    def test_rich_vacancy_scores_high(self, advisor):
        """A vacancy with all positive signals scores ~65."""
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-1",
            title="Python Developer",
            url="https://example.com",
            description="A" * 600,
            location="Moscow",
        )
        company = Company.create(name="Acme")
        v.company_id = company.id
        v.published_at = __import__("datetime").datetime.now()
        v.add_skill(__import__("backend.domain.entities", fromlist=["Skill"]).Skill.create("Python"))

        metric = VacancyMetric.create(
            vacancy_id=v.id,
            salary=SalaryRange(
                min_amount=Money(__import__("decimal").Decimal("100000"), Currency.RUB),
            ),
            scam_score=ScamScore(0),
            apply_score=ApplyScore(50),
            confidence=Confidence(0.9),
        )
        v.attach_metric(metric)

        score = advisor.score(v)
        assert score.value >= 50

    def test_poor_vacancy_scores_low(self, advisor):
        """A bare vacancy with no data scores low."""
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-1",
            title="Python Developer",
            url="https://example.com",
        )

        metric = VacancyMetric.create(
            vacancy_id=v.id,
            salary=SalaryRange(),
            scam_score=ScamScore(80),
            apply_score=ApplyScore(0),
            confidence=Confidence(0.2),
        )
        v.attach_metric(metric)

        score = advisor.score(v)
        assert score.value <= 30

    def test_score_range(self, advisor):
        """Score is always in [0, 100]."""
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-1",
            title="Test",
            url="https://example.com",
        )
        metric = VacancyMetric.create(
            vacancy_id=v.id,
            salary=SalaryRange(),
            scam_score=ScamScore(0),
            apply_score=ApplyScore(50),
            confidence=Confidence(0.0),
        )
        v.attach_metric(metric)

        score = advisor.score(v)
        assert 0 <= score.value <= 100
