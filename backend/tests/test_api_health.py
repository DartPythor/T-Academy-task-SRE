"""Tests for API health endpoint."""
from __future__ import annotations

import os

import pytest

os.environ["VA_DB_DSN"] = "postgresql+asyncpg://test:test@localhost:5432/test_db"
# Тесты не требуют живой БД — миграции при старте приложения отключены.
os.environ["VA_RUN_MIGRATIONS"] = "false"

from backend.main import create_app
from backend.presentation.schemas.common import HealthResponse

@pytest.fixture
def app():
    return create_app()

class TestHealthEndpoint:
    def test_health_response_structure(self, app):
        """Health endpoint returns expected structure regardless of DB status."""
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert data["database"] in ("connected", "disconnected", "unknown")
        assert "timestamp" in data

    def test_health_response_type(self, app):
        """Health response conforms to HealthResponse schema."""
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/v1/health")
        HealthResponse(**response.json())
        assert True
