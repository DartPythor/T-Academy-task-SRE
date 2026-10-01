from __future__ import annotations

from dataclasses import dataclass, field

from backend.domain.entities import Vacancy
from backend.domain.values import ApplyScore

Signal = tuple[str, int, "callable[[Vacancy], bool]"]

@dataclass
class ApplyAdvisor:
    """Линейная модель: apply_score = сумма бонусов за хорошие сигналы
    минус штрафы за скам/недостаток данных, обрезанная в [0, 100].
    """

    max_score: int = 100

    positive_signals: list[Signal] = field(
        default_factory=lambda: [
            ("has_company", 15, lambda v: v.company_id is not None),
            ("has_salary", 20, lambda v: _has_salary(v)),
            ("long_description", 10, lambda v: len(v.description or "") > 500),
            ("has_location", 5, lambda v: bool(v.location)),
            ("has_skills", 10, lambda v: bool(v.skills)),
            ("has_published_at", 5, lambda v: v.published_at is not None),
        ]
    )

    def score(self, vacancy: Vacancy) -> ApplyScore:
        raw = 0
        for _, weight, predicate in self.positive_signals:
            if predicate(vacancy):
                raw += weight

        if vacancy.metric is not None:
            raw -= int(vacancy.metric.scam_score.value * 0.5)
            raw -= int((1.0 - vacancy.metric.confidence.value) * 10)

        return ApplyScore(max(0, min(raw, self.max_score)))

def _has_salary(vacancy: Vacancy) -> bool:
    return vacancy.metric is not None and vacancy.metric.salary.is_defined

