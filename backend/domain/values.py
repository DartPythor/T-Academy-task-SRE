from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from backend.domain.enums import Currency

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("amount must be non-negative")

@dataclass(frozen=True)
class SalaryRange:
    """Зарплатная вилка. Любая граница может быть None, если источник её не указал."""
    min_amount: Optional[Money] = None
    max_amount: Optional[Money] = None
    gross: Optional[bool] = None

    def __post_init__(self) -> None:
        if self.min_amount and self.max_amount:
            if self.min_amount.currency != self.max_amount.currency:
                raise ValueError("currency mismatch in salary range")
            if self.min_amount.amount > self.max_amount.amount:
                raise ValueError("min > max")

    @property
    def is_defined(self) -> bool:
        return self.min_amount is not None or self.max_amount is not None

@dataclass(frozen=True)
class SourceRef:
    """Ссылка на внешний источник вакансии."""
    source_id: UUID
    external_id: str
    url: str

@dataclass(frozen=True)
class ScamScore:
    """Оценка вероятности обмана, 0..100. Чем выше — тем подозрительнее."""
    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 100:
            raise ValueError("scam score must be in [0, 100]")

    @property
    def is_suspicious(self) -> bool:
        return self.value >= 70

@dataclass(frozen=True)
class ApplyScore:
    """Насколько стоит откликаться: 0..100, чем выше — тем лучше."""
    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 100:
            raise ValueError("apply score must be in [0, 100]")

    @property
    def verdict(self) -> str:
        if self.value >= 70:
            return "apply"
        if self.value >= 40:
            return "maybe"
        return "skip"

@dataclass(frozen=True)
class Confidence:
    """Уверенность в расчётах метрик, 0.0..1.0."""
    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("confidence must be in [0, 1]")

