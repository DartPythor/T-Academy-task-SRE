"""Tests for domain entities and value objects."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import pytest

from backend.domain.entities import Company, Skill, Source, Vacancy
from backend.domain.enums import (
    Currency,
    EmploymentType,
    SourceType,
    VacancyStatus,
    WorkMode,
)
from backend.domain.metrics import VacancyMetric
from backend.domain.values import (
    ApplyScore,
    Confidence,
    Money,
    SalaryRange,
    ScamScore,
)

class TestMoney:
    def test_create(self):
        m = Money(amount=Decimal("100.50"), currency=Currency.USD)
        assert m.amount == Decimal("100.50")
        assert m.currency == Currency.USD

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            Money(amount=Decimal("-1"), currency=Currency.USD)

class TestSalaryRange:
    def test_empty(self):
        s = SalaryRange()
        assert s.is_defined is False

    def test_partial(self):
        s = SalaryRange(
            min_amount=Money(Decimal("100"), Currency.USD)
        )
        assert s.is_defined is True

    def test_currency_mismatch_raises(self):
        with pytest.raises(ValueError, match="currency mismatch"):
            SalaryRange(
                min_amount=Money(Decimal("100"), Currency.USD),
                max_amount=Money(Decimal("200"), Currency.EUR),
            )

    def test_min_greater_than_max_raises(self):
        with pytest.raises(ValueError, match="min > max"):
            SalaryRange(
                min_amount=Money(Decimal("300"), Currency.USD),
                max_amount=Money(Decimal("100"), Currency.USD),
            )

class TestScamScore:
    def test_valid_range(self):
        assert ScamScore(0).value == 0
        assert ScamScore(50).value == 50
        assert ScamScore(100).value == 100

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            ScamScore(-1)
        with pytest.raises(ValueError):
            ScamScore(101)

    def test_suspicious(self):
        assert ScamScore(70).is_suspicious is True
        assert ScamScore(50).is_suspicious is False

class TestApplyScore:
    def test_verdict_apply(self):
        assert ApplyScore(70).verdict == "apply"
        assert ApplyScore(100).verdict == "apply"

    def test_verdict_maybe(self):
        assert ApplyScore(40).verdict == "maybe"
        assert ApplyScore(69).verdict == "maybe"

    def test_verdict_skip(self):
        assert ApplyScore(0).verdict == "skip"
        assert ApplyScore(39).verdict == "skip"

class TestConfidence:
    def test_valid(self):
        assert Confidence(0.5).value == 0.5
        assert Confidence(0.0).value == 0.0
        assert Confidence(1.0).value == 1.0

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            Confidence(-0.1)
        with pytest.raises(ValueError):
            Confidence(1.1)

class TestSource:
    def test_create(self):
        s = Source.create(
            name="Test Channel",
            type=SourceType.TELEGRAM_CHANNEL,
            url="https://t.me/test",
        )
        assert isinstance(s.id, UUID)
        assert s.name == "Test Channel"
        assert s.enabled is True

    def test_disable(self):
        s = Source.create("Test", SourceType.OTHER, "https://example.com")
        s.disable()
        assert s.enabled is False

    def test_enable(self):
        s = Source.create("Test", SourceType.OTHER, "https://example.com")
        s.disable()
        s.enable()
        assert s.enabled is True

class TestCompany:
    def test_create(self):
        c = Company.create(name="Acme Inc.")
        assert isinstance(c.id, UUID)
        assert c.name == "Acme Inc."

    def test_create_with_website(self):
        c = Company.create(name="Acme", website="https://acme.com")
        assert c.website == "https://acme.com"

class TestSkill:
    def test_create(self):
        s = Skill.create("Python")
        assert s.name == "python"

    def test_immutable(self):
        s = Skill.create("Python")
        with pytest.raises(AttributeError):
            s.name = "Java"

class TestVacancy:
    def test_create(self):
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-1",
            title="Python Developer",
            url="https://example.com/vacancy/1",
        )
        assert v.status == VacancyStatus.NEW
        assert v.skills == []
        assert v.metric is None

    def test_add_skill(self):
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-1",
            title="Python Developer",
            url="https://example.com/vacancy/1",
        )
        skill = Skill.create("Python")
        v.add_skill(skill)
        assert skill in v.skills

    def test_attach_metric(self):
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-1",
            title="Python Developer",
            url="https://example.com/vacancy/1",
        )
        metric = VacancyMetric.create(
            vacancy_id=v.id,
            salary=SalaryRange(),
            scam_score=ScamScore(10),
            apply_score=ApplyScore(80),
            confidence=Confidence(0.9),
        )
        v.attach_metric(metric)
        assert v.metric is not None
        assert v.status == VacancyStatus.PROCESSED

    def test_archive(self):
        v = Vacancy.create(
            source_id=UUID("00000000-0000-0000-0000-000000000001"),
            external_id="ext-1",
            title="Python Developer",
            url="https://example.com/vacancy/1",
        )
        v.archive()
        assert v.status == VacancyStatus.ARCHIVED
