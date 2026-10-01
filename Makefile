.PHONY: install install-dev lint test run-dev run build build-prod clean

VERSION ?= 0.1.0

install:
	poetry install --only main

install-dev:
	poetry install --with dev

lint:
	ruff check backend/
	ruff format --check backend/

format:
	ruff format backend/
	ruff check --fix backend/

test:
	pytest -v --cov=backend --cov-report=term-missing

run-dev:
	poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

build:
	docker compose build

build-prod:
	@echo "Building version: $(VERSION)"
	GIT_SHA=$$(git rev-parse --short HEAD); \
	BUILD_DATE=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	docker build \
		--build-arg VERSION=$(VERSION) \
		--build-arg GIT_SHA=$$GIT_SHA \
		--build-arg BUILD_DATE=$$BUILD_DATE \
		-t vacancy-analyzer:$(VERSION)-$$GIT_SHA \
		-t vacancy-analyzer:latest \
		.

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage coverage.xml htmlcov/
