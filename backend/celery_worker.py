# backend/celery_worker.py

import os
from celery import Celery

redis_url = os.getenv("REDIS_URL")

celery_app = Celery(
    "spotify_tasks",
    broker=redis_url,
    backend=redis_url
)

import tasks  # ensures tasks get registered