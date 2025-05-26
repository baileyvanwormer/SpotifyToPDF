# backend/celery_worker.py

from celery import Celery

celery_app = Celery(
    "spotify_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

import tasks  # ensures tasks get registered