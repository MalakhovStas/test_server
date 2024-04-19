from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.db.models import Q

from config.tools.process_selected_tests_manager import ProcessSelectedTests
from test_cases.models import Project, TestCase
from .handlers import CeleryTaskHandler


@shared_task(bind=True, name='run_process_selected_tests', base=CeleryTaskHandler)
def run_process_selected_tests(self, project_title, select_all_tests, selected_tests) -> str:
    """Задача запускает процесс тестирования приложения"""
    project = Project.objects.filter(Q(title__icontains=project_title)).get()

    if not select_all_tests and selected_tests:
        selected_tests = list(TestCase.objects.in_bulk(selected_tests).values())

    progress = ProgressRecorder(self)
    ProcessSelectedTests(project=project, progress=progress).run_process(
        select_all_tests=select_all_tests,
        selected_tests=selected_tests
    )
    return '⚠ Для отображения актуальной информации о тестировании проекта, обновите страницу.'
