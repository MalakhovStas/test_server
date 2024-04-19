"""Инициализация основных инструментов"""
from __future__ import absolute_import, unicode_literals
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
from django.conf import settings

if not settings.configured:
    django.setup()

from .celery.config import app as celery_app

from . import logging  # noqa F401,E402

__all__ = ("celery_app",)
