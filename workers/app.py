from celery import Celery

from core.settings import settings

celery_app = Celery(
    "tasks", broker=settings.celery.broker_url, backend=settings.celery.result_backend, include=["workers.tasks"]
)
