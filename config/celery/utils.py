"""Модуль дополнительных инструментов для конфигурации Celery"""
from kombu import Queue, Exchange


def route_tasks(name: str, args: list, kwargs: dict, options, task=None, **kw) -> dict:
    """Маршрутизатор задач"""
    return {
        "exchange": "default",
        "exchange_type": "direct",
        "routing_key": "default",
    }


def create_queues() -> list:
    """Создаёт список очередей"""
    queues = [
        Queue(
            name="default",
            exchange=Exchange(name="default", type="direct"),
            routing_key="default",
        ),
    ]
    return queues
