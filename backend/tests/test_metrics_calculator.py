"""Tests for metrics calculator service."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import pytest

from backend.application.services.metrics_calculator import MetricsCalculator
from backend.application.services.scam_detector import ScamDetector
from backend.application.services.apply_advisor import ApplyAdvisor
from backend.domain.entities import Skill, Vacancy
from backend.domain.enums import Currency
from backend.domain.values import Money, SalaryRange

@pytest.fixture
def calculator() -> MetricsCalculator:
    return MetricsCalculator(
        scam_detector=ScamDetector(),
        apply_advisor=ApplyAdvisor(),
    )

@pytest.fixture
def vacancy() -> Vacancy:
    v = Vacancy.create(
        source_id=UUID("00000000-0000-0000-0000-000000000001"),
        external_id="ext-1",
        title="Python Developer",
        url="https://example.com/vacancy/1",
        description="A" * 500,
    )
    v.add_skill(Skill.create("Python"))
    return v

class TestMetricsCalculator:
    def test_calculate_returns_metric(self, calculator, vacancy):
        """Calculator returns a VacancyMetric with all fields."""
        salary = SalaryRange(
            min_amount=Money(Decimal("100000"), Currency.RUB),
            max_amount=Money(Decimal("200000"), Currency.RUB),
        )
        metric = calculator.calculate(vacancy, salary)
        assert metric is not None
        assert metric.vacancy_id == vacancy.id
        assert 0 <= metric.scam_score.value <= 100
        assert 0 <= metric.apply_score.value <= 100
        assert 0.0 <= metric.confidence.value <= 1.0
        assert metric.salary.is_defined is True

    def test_confidence_with_all_signals(self, calculator, vacancy):
        """Full vacancy data gives high confidence."""
        salary = SalaryRange(
            min_amount=Money(Decimal("100000"), Currency.RUB),
        )
        metric = calculator.calculate(vacancy, salary)
        assert metric.confidence.value >= 0.6

    def test_confidence_with_minimal_data(self, calculator, vacancy):
        """Minimal vacancy data gives lower confidence."""
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-2",
            title="Minimal",
            url="https://example.com",
        )
        salary = SalaryRange()
        metric = calculator.calculate(v, salary)
        assert metric.confidence.value <= 0.4

    def test_vacancy_gets_metric_attached(self, calculator, vacancy):
        """After calculation, vacancy.metric is set."""
        salary = SalaryRange(
            min_amount=Money(Decimal("100000"), Currency.RUB),
        )
        calculator.calculate(vacancy, salary)
        assert vacancy.metric is not None
        assert vacancy.metric.vacancy_id == vacancy.id
