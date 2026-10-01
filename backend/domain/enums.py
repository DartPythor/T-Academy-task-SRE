from __future__ import annotations

from enum import Enum

class SourceType(str, Enum):
    TELEGRAM_CHANNEL = "telegram_channel"
    CAREER_SITE = "career_site"
    JOB_BOARD = "job_board"
    OTHER = "other"

class VacancyStatus(str, Enum):
    NEW = "new"
    PROCESSED = "processed"
    ARCHIVED = "archived"

class Currency(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    KZT = "KZT"
    BYN = "BYN"
    OTHER = "OTHER"

class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"

class WorkMode(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    OFFICE = "office"

