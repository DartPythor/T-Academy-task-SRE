from __future__ import annotations

from dataclasses import dataclass

from backend.application.services.apply_advisor import ApplyAdvisor
from backend.application.services.scam_detector import ScamDetector
from backend.domain.entities import Vacancy, VacancyMetric
from backend.domain.values import Confidence, SalaryRange, ApplyScore, ScamScore

@dataclass
class MetricsCalculator:
    """Считает метрики вакансии, когда зарплатная вилка уже известна.

    Шаги:
      1. Создать VacancyMetric с готовой SalaryRange.
      2. Посчитать scam_score (использует salary).
      3. Посчитать apply_score (использует scam_score и confidence).
      4. Посчитать confidence по заполненности полей.
    """

    scam_detector: ScamDetector
    apply_advisor: ApplyAdvisor

    def calculate(self, vacancy: Vacancy, salary: SalaryRange) -> VacancyMetric:
        confidence = Confidence(self._confidence(vacancy, salary.is_defined))

        metric = VacancyMetric.create(
            vacancy_id=vacancy.id,
            salary=salary,
            scam_score=ScamScoreZero,
            apply_score=ApplyScoreZero,
            confidence=confidence,
        )
        vacancy.metric = metric

        metric.scam_score = self.scam_detector.score(vacancy)

        metric.apply_score = self.apply_advisor.score(vacancy)

        return metric

    @staticmethod
    def _confidence(vacancy: Vacancy, salary_defined: bool) -> float:
        signals = [
            salary_defined,
            vacancy.company_id is not None,
            bool(vacancy.description),
            vacancy.published_at is not None,
            bool(vacancy.skills),
        ]
        return round(sum(signals) / len(signals), 2)

from backend.domain.values import ApplyScore, ScamScore

ScamScoreZero = ScamScore(0)
ApplyScoreZero = ApplyScore(0)

