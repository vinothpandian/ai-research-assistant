import os

from celery import Celery

from core.settings import settings

os.environ.get("CELERY_BROKER_URL")

celery_app = Celery('tasks')

celery_app.conf.update(
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['workers.tasks']
)
