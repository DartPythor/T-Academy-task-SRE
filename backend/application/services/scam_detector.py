from __future__ import annotations

from dataclasses import dataclass, field

from backend.domain.entities import Vacancy
from backend.domain.values import ScamScore

Signal = tuple[str, int, "callable[[Vacancy], bool]"]

@dataclass
class ScamDetector:
    """Линейная модель: scam_score = сумма весов сработавших сигналов,
    обрезанная в [0, 100]. Зарплата уже приходит готовой в vacancy.metric.
    """

    max_score: int = 100

    signals: list[Signal] = field(
        default_factory=lambda: [
            ("no_company", 20, lambda v: v.company_id is None),
            ("short_description", 10, lambda v: len(v.description or "") < 200),
            ("no_salary", 15, lambda v: not _has_salary(v)),
            ("urgent_language", 15, lambda v: _has_any(v.description, (
                "срочно", "быстрый доход", "без опыта", "легкие деньги",
            ))),
            ("contact_only_messenger", 15, lambda v: _has_any(v.description, (
                "только телеграм", "только whatsapp", "пишите в лс",
            ))),
            ("too_good_salary", 20, lambda v: _too_good_salary(v)),
            ("suspicious_domain", 10, lambda v: _suspicious_url(v.url)),
        ]
    )

    def score(self, vacancy: Vacancy) -> ScamScore:
        raw = 0
        for _, weight, predicate in self.signals:
            if predicate(vacancy):
                raw += weight
        return ScamScore(min(raw, self.max_score))

def _has_salary(vacancy: Vacancy) -> bool:
    return vacancy.metric is not None and vacancy.metric.salary.is_defined

def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = (text or "").lower()
    return any(n in lowered for n in needles)

def _too_good_salary(vacancy: Vacancy) -> bool:
    if vacancy.metric is None:
        return False
    salary = vacancy.metric.salary
    if salary.max_amount is None:
        return False
    if len(vacancy.description or "") > 500:
        return False
    return float(salary.max_amount.amount) > 500_000

def _suspicious_url(url: str) -> bool:
    lowered = (url or "").lower()
    return any(host in lowered for host in ("bit.ly", "tinyurl", "t.me/joinchat"))

