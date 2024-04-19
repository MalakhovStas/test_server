"""Основной модуль конфигурации Celery"""
from __future__ import absolute_import

from celery import Celery
from django.conf import settings

from . import utils

# Список путей к задачам celery
imports = ['config.celery.tasks']

app = Celery("test_server", include=imports)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(packages=imports, force=True)

app.conf.update(
    broker_url=settings.REDIS_URL,
    result_backend="django-db",
    broker_transport_options={
        "priority_steps": list(range(1, settings.X_MAX_PRIORITY + 1)),
        "queue_order_strategy": "priority",
    },
    cache_backend='default',
    task_queues=utils.create_queues(),
    task_routes=utils.route_tasks,
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    accept_content=['application/json'],
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1,
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    broker_connection_retry_on_startup=True,
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    default_delivery_mode="persistent",
    beat_schedule='django_celery_beat.schedulers:DatabaseScheduler'
)
