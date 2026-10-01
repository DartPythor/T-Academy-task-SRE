# Changelog

## [Unreleased]

### Added
- 12 Factor App compliance implementation
  - Config via environment with mandatory validation (Factor 3)
  - Secrets removed from default values (Factor 3)
  - JSON structured logging with Correlation ID middleware (Factor 11)
  - Health check with database connectivity (Factor 9)
  - Poetry-based Docker build with OCI labels (Factor 2, 5)
  - Gunicorn + Uvicorn workers for production concurrency (Factor 8)
  - Alembic database migrations (Factor 12)
  - CLI management commands via `manage` script (Factor 12)
  - Dev/Prod parity via docker-compose.override.yml (Factor 10)
  - Makefile for common development tasks
  - Dev dependencies (pytest, ruff, mypy)
  - Build script with Git SHA tagging and OCI labels
  - `.env.example` template with all documented variables
  - Backing services retry logic (Factor 4)

### Changed
- `backend/config.py`: removed hardcoded DB credentials, added validation
- `Dockerfile`: multi-stage build using Poetry, added OCI labels
- `docker-compose.yml`: secrets via `${VAR:?error}` only, added `env_file`
- `pyproject.toml`: added dev-dependencies group
- `backend/infrastructure/db/session.py`: added pool configuration
- `backend/presentation/api/health.py`: extended with DB check

### Removed
- Auto `create_all` on startup — replaced by Alembic migrations