# T-Academy-task-SRE

Сервис анализа вакансий: сбор, метрики, CRUD API (FastAPI + PostgreSQL + Alembic).

## Быстрый старт (docker compose)

```bash
cp .env.example .env          # укажите DB_PASSWORD
docker compose up --build     # поднимает db + backend (+ frontend)
```

Что происходит при старте backend-контейнера:

1. `docker/entrypoint.sh` ждёт готовности PostgreSQL (`depends_on: service_healthy`);
2. применяет миграции: `alembic upgrade head`;
3. запускает `uvicorn backend.main:app`.

Если БД недоступна, entrypoint повторяет попытки (`MIGRATION_RETRIES`, по умолчанию 30)
и завершает контейнер с ошибкой — приложение не начнёт обслуживать трафик
с неактуальной схемой БД.

API: `http://localhost:8000/api/v1/health`, документация — `http://localhost:8000/docs`.

## Локальная разработка (без Docker)

```bash
poetry install --with dev
cp .env.example .env          # хост БД: localhost, VA_RUN_MIGRATIONS=true
poetry run alembic upgrade head
poetry run uvicorn backend.main:app --reload
```

## Миграции (Alembic)

Конфигурация: `alembic.ini` (каталог скриптов — `alembic/`),
подключение к БД — `alembic/env.py`. **DSN всегда берётся из переменной
окружения `VA_DB_DSN`** (12 Factor: config), в `alembic.ini` секретов нет.

| Команда | Назначение |
| --- | --- |
| `make migrate` | `alembic upgrade head` — применить все миграции |
| `make migrate-down` | `alembic downgrade -1` — откатить последнюю |
| `make migrate-current` | текущая ревизия БД |
| `make migrate-history` | история миграций |
| `make makemigration M="add index"` | новая миграция (autogenerate из моделей) |

Напрямую:

```bash
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "add index"
poetry run alembic check          # проверить, что модели и миграции не разошлись
```

Модели — `backend/infrastructure/db/models.py`, они попадают в `Base.metadata`,
поэтому autogenerate видит схему целиком.

### Где применяются миграции

| Окружение | Кто применяет | Настройка |
| --- | --- | --- |
| Docker-образ | `docker/entrypoint.sh` до старта uvicorn | `VA_RUN_MIGRATIONS=false` |
| docker compose | entrypoint контейнера backend | `VA_RUN_MIGRATIONS=false` |
| Kubernetes | init-контейнер `migrate` (тот же образ, `command: ["migrate"]`) | `VA_RUN_MIGRATIONS=false` |
| Локально / тесты | lifespan приложения | `VA_RUN_MIGRATIONS=true` |

Одновременный запуск миграций из нескольких реплик безопасен: в `alembic/env.py`
используется transaction-level advisory-лок PostgreSQL
(`pg_advisory_xact_lock`).

## Kubernetes

Манифесты — в `k8s/`. Проверено на minikube (v1.37): миграции применяет
init-контейнер `migrate`, backend и frontend поднимаются, `/api/v1/*` работают.

```bash
kubectl apply -f k8s/
kubectl get pods -w
```

Порядок старта backend-пода: init-контейнер `migrate`
(`/app/docker/entrypoint.sh migrate`) ждёт PostgreSQL и делает `alembic upgrade head`,
и только после его успешного завершения стартует приложение
(`VA_RUN_MIGRATIONS=false` в `k8s/backend-config.yaml`).

### Локальный кластер (minikube)

Образы не тянутся из реестра (`imagePullPolicy: Never`), поэтому их нужно
загрузить в кластер:

```bash
docker build -t backend:latest .
docker build -t frontend:latest ./frontend
minikube image load backend:latest
minikube image load frontend:latest
kubectl apply -f k8s/
```

Проверка (NodePort с Windows-хоста может быть недоступен):

```bash
kubectl port-forward svc/frontend-service 18090:80
curl http://127.0.0.1:18090/api/v1/health
```

Для реального кластера замените `image: backend:latest` / `frontend:latest`
на образы из реестра и уберите `imagePullPolicy: Never`.

### Два момента, специфичных для k8s

1. **Upstream frontend'а.** `frontend/nginx.conf` получает хост backend'а из
   `BACKEND_HOST`. В compose это `backend:8000`, в k8s — FQDN
   `backend-service.default.svc.cluster.local:8000` (короткое имя `backend-service`
   nginx не резолвит: search-домены из `/etc/resolv.conf` он не читает).
2. **DNS-резолвер.** Так как `proxy_pass` использует переменную, nginx резолвит
   имя в рантайме и требует `resolver` в виде IP (`DNS_RESOLVER`). Значение —
   `nameserver` из `/etc/resolv.conf` пода либо:

   ```bash
   kubectl get svc -n kube-system kube-dns -o jsonpath='{.spec.clusterIP}'
   ```

### Переменные окружения

| Переменная | Назначение | По умолчанию |
| --- | --- | --- |
| `VA_DB_DSN` | DSN подключения (обязательна) | — |
| `VA_RUN_MIGRATIONS` | применять миграции при старте приложения | `true` |
| `VA_ALEMBIC_CONFIG` | путь до `alembic.ini` в контейнере | `/app/alembic.ini` |
| `MIGRATION_RETRIES` | число попыток применения миграций в entrypoint | `30` |
| `MIGRATION_RETRY_DELAY` | пауза между попытками, сек | `2` |
| `BACKEND_HOST` | upstream для nginx во frontend (compose: `backend:8000`) | `backend:8000` |
| `DNS_RESOLVER` | DNS-резолвер для nginx (compose: `127.0.0.11`) | `127.0.0.11` |

## Тесты и линт

```bash
make test
make lint
```

## Административные команды

```bash
python -m backend.manage db-check   # проверить подключение к БД
python -m backend.manage seed       # тестовые данные
```
