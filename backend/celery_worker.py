# backend/celery_worker.py

import os
from celery import Celery

redis_url = os.getenv("REDIS_URL")

celery_app = Celery(
    "spotify_tasks",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_time_limit=300,        # hard kill after 5 min
    task_soft_time_limit=270,   # raises SoftTimeLimitExceeded at 4.5 min
    timezone='UTC'
)

import tasks  # ensures tasks get registered