#!/usr/bin/env python
"""CLI для административных задач.

12 Factor — Admin processes: запускать как одноразовые процессы:
    python -m backend.manage seed
    python -m backend.manage db-check

Активируется также через poetry:
    poetry run manage seed
"""

from __future__ import annotations

import asyncio
import sys

class CLI:
    """Простой CLI без внешних зависимостей."""

    commands: dict[str, tuple[str, callable]] = {}

    @classmethod
    def command(cls, name: str, help_text: str = ""):
        def wrapper(func):
            cls.commands[name] = (help_text, func)
            return func
        return wrapper

    @classmethod
    def run(cls):
        args = sys.argv[1:]
        if not args or args[0] in ("-h", "--help", "help"):
            print("Usage: python -m backend.manage <command> [args]")
            print()
            print("Commands:")
            for name, (help_text, _) in sorted(cls.commands.items()):
                print(f"  {name:20s} {help_text}")
            return

        command = args[0]
        if command not in cls.commands:
            print(f"Unknown command: {command}")
            print(f"Available: {', '.join(cls.commands)}")
            sys.exit(1)

        _, func = cls.commands[command]
        result = func(*args[1:])
        if asyncio.iscoroutine(result):
            asyncio.run(result)

@CLI.command("seed", "Наполнить БД тестовыми данными")
async def seed():
    """Создаёт тестовый источник и компанию."""
    from backend.config import settings
    from backend.infrastructure.db.session import async_session_factory
    from backend.infrastructure.db.repositories import SQLSourceRepository
    from backend.infrastructure.db.unit_of_work import SQLUnitOfWork
    from backend.domain.entities import Source
    from backend.domain.enums import SourceType

    async with async_session_factory() as session:
        repo = SQLSourceRepository(session)
        uow = SQLUnitOfWork(
            session=session,
            source_repo=repo,
            company_repo=None,
            skill_repo=None,
            vacancy_repo=None,
            metric_repo=None,
        )

        source = Source.create(
            name="Test Telegram Channel",
            type=SourceType.TELEGRAM_CHANNEL,
            url="https://t.me/test_channel",
        )
        async with uow:
            await repo.add(source)
            await uow.commit()
        print(f"Created source: {source.id}")

@CLI.command("db-check", "Проверить подключение к БД")
async def db_check():
    """Проверяет доступность базы данных."""
    from backend.infrastructure.db.session import check_db_connection

    ok = await check_db_connection()
    if ok:
        print("Database: connected")
    else:
        print("Database: disconnected")
        sys.exit(1)

if __name__ == "__main__":
    CLI.run()
