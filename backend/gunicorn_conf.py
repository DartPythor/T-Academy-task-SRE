"""Gunicorn configuration for production deployment.

12 Factor — Concurrency: scale-out via process model.
Используется для production-запуска через gunicorn:
    gunicorn -c backend/gunicorn_conf.py backend.main:app

В dev-режиме используйте `uvicorn --reload`.
"""

from __future__ import annotations

import os

workers = int(os.getenv("WORKER_COUNT", "1"))
worker_class = "uvicorn.workers.UvicornWorker"

bind = "0.0.0.0:8000"

timeout = 120
graceful_timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

daemon = False
pidfile = None

worker_connections = 1000
max_requests = 2000
max_requests_jitter = 200
