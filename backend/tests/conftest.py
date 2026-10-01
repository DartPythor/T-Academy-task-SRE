"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

os.environ["VA_DB_DSN"] = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
