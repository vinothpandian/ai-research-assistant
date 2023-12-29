from celery import Celery

from core.settings import settings

celery_app = Celery("tasks")

celery_app.conf.update(
    broker_url=settings.celery.broker_url,
    result_backend=settings.celery.result_backend,
    include=["workers.tasks"],
)
