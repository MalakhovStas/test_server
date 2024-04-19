from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Project(BaseModel):
    """Модель тестируемого проекта"""
    title = models.CharField(max_length=1024, primary_key=True, verbose_name=_('title'))
    version = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('version'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    authors = models.JSONField(blank=True, null=True, verbose_name=_('authors'))
    repository = models.CharField(
        max_length=1024, blank=True, null=True, verbose_name=_('repository'))
    coverage = models.JSONField(blank=True, null=True, verbose_name=_("coverage"))

    @property
    def total_tests(self):
        """Динамический расчёт количества тестов в проекте"""
        return TestCase.objects.filter(project=self).count()

    @property
    def passed_tests(self):
        """Динамический расчёт количества тестов успешных в проекте"""
        return TestCase.objects.filter(project=self, result=True).count()

    @property
    def failed_tests(self):
        """Динамический расчёт количества упавших тестов в проекте"""
        return TestCase.objects.filter(project=self, result=False).count()

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.title


class ProjectEnvs(BaseModel):
    """Секретные зависимости проекта"""
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='env', verbose_name=_('project')
    )
    environments = models.TextField(blank=True, null=True, verbose_name=_('environments'))

    def __str__(self):
        return f'Environments for project: {self.project}'


class TestClass(BaseModel):
    """Модель тестового класса"""

    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name=_('project')
    )
    title = models.CharField(max_length=1024, verbose_name=_('title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    path = models.CharField(max_length=1024, verbose_name=_('path'))

    class Meta:
        verbose_name = _('test class')
        verbose_name_plural = _('test classes')

    def __str__(self):
        return self.title


class TestCase(BaseModel):
    """Модель тест кейса"""

    TEST_CASE_TYPES = [
        ("unit", _("Unit test")),
        ("integration", _("Integration test")),
        ("system", _("System test")),
        ("end_to_end", _("End-to-End test")),
    ]

    type = models.CharField(
        max_length=64,
        blank=True,
        null=False,
        default='unit',
        choices=TEST_CASE_TYPES,
        verbose_name=_("test type")
    )

    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name='test_cases',
        verbose_name=_('project')
    )
    test_class = models.ForeignKey(
        to=TestClass,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='test_cases',
        verbose_name=_('test class')
    )
    title = models.CharField(max_length=1024, verbose_name=_('title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    path = models.CharField(max_length=1024, verbose_name=_('path'))
    test_data = models.TextField(blank=True, null=True, verbose_name=_('test data'))
    result = models.BooleanField(verbose_name=_('result'))
    error_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('error description')
    )
    last_testing = models.DateTimeField(
        blank=True,
        verbose_name=_('last testing'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('test case')
        verbose_name_plural = _('test cases')

    def __str__(self):
        return self.title
