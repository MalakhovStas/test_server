from celery.result import AsyncResult
from django.contrib import admin
from django.contrib import messages
from django.db import models
from django.forms import Textarea
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html

from config.celery.tasks import run_process_selected_tests
from config.utils.misc import get_bool_from_str, get_list_from_str
from .forms import TestCaseAdminForm
from .models import Project, TestClass, TestCase, ProjectEnvs


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 0
    # max_num = 0
    can_delete = True
    show_change_link = True
    readonly_fields = (
        'created_at',
        'updated_at',
        'render_result',
        'title_with_link',
        'select',
        'last_testing'
    )
    list_filter = ('result',)
    list_display = ('title_with_link', 'result')
    fieldsets = [(None, {
        'fields': (
            'title_with_link',
            'type',
            'result',
            'test_class',
            'path',
            'description',
            'created_at',
            'updated_at',
            'last_testing',
            'select',
        )}), ]

    ordering = ['test_class']
    raw_id_fields = ['test_class']

    def title_with_link(self, obj):
        """Метод для отображения ссылки на title"""
        url = reverse(
            viewname=f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=[obj.id]
        )
        return format_html(f'<a href="{url}">{obj.title}</a>')

    title_with_link.short_description = 'Title'

    @staticmethod
    def render_result(obj):
        """Метод для отображения знаков результата выполнения"""
        if obj.result:
            return '✅'
        else:
            return '❌'

    @staticmethod
    def select(obj):
        """Метод для отображения чекбокса select"""
        return format_html(f'<input type="checkbox" class="select-checkbox" object-id="{obj.id}">')

    def has_change_permission(self, request, obj=None):
        """Метод для запрета изменения прав"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Метод для запрета удаления прав"""
        if request.user.is_superuser:
            return True
        return False

    def has_add_permission(self, request, *args, **kwargs):
        """Метод для запрета добавления прав"""
        if request.user.is_superuser:
            return True
        return False


class ProjectEnvsInline(admin.TabularInline):
    model = ProjectEnvs
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    fieldsets = [(None, {'fields': ()})]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Регистрация модели Project в админке"""
    change_form_template = 'admin/project_change_form.html'

    inlines = [ProjectEnvsInline, TestCaseInline]
    list_display = [
        'title',
        'description',
        'total_coverage',
        'total_tests',
        'passed_tests',
        'failed_tests'
    ]
    fieldsets = [(None, {
        'fields': (
            'title',
            'version',
            'authors',
            'description',
            'repository',
            'total_tests',
            'passed_tests',
            'failed_tests',
            'coverage_display',
            'select_all_tests'
        )}), ]
    readonly_fields = [
        'title',
        'version',
        'authors',
        'description',
        'repository',
        'total_tests',
        'passed_tests',
        'failed_tests',
        'coverage_display',
        'select_all_tests'

    ]
    search_fields = ['title', 'id']
    ordering = ['title']

    class Media:
        js = ('/static/admin/js/testcase_admin.js',)

    def get_urls(self):
        urls = super().get_urls()
        include_urls = [path('process-selected-tests/', self.process_selected_tests_view)]
        return include_urls + urls

    def process_selected_tests_view(self, request):
        if request.method == 'POST':
            from_path = request.POST.get('from-path')
            select_all_tests = get_bool_from_str(request.POST.get('select-all-tests'))
            selected_tests = get_list_from_str(request.POST.get('selected-tests-id'))

            if select_all_tests or selected_tests:
                task: AsyncResult = run_process_selected_tests.delay(
                    project_title=request.POST.get('project-title').replace('5F', ''),
                    select_all_tests=select_all_tests,
                    selected_tests=selected_tests,
                )
                request.session['task_id'] = task.task_id
                messages.add_message(
                    request,
                    messages.INFO,
                    "Процесс тестирования выбранных тест кейсов запущен"
                )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Выберите тест кейсы для запуска тестирования"
                )
            return redirect(from_path, permanent=True)
        else:
            return redirect('admin/', permanent=True)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        self.request = request
        return queryset

    @staticmethod
    def total_coverage(obj):
        """Отображение общего уровня покрытия проекта тестами в процентах"""
        return format_html(f"{obj.coverage.get('totals').get('percent_covered_display')}%</b>")

    @staticmethod
    def coverage_display(obj):
        """Отображение уровня покрытия проекта тестами, с подробным описанием каждого модуля"""
        display = (
            f"<p><b>Total - {obj.coverage.get('totals').get('percent_covered_display')}%</b> "
            f"| covered_lines - <b>{obj.coverage.get('totals').get('covered_lines')}</b> "
            f"| missing_lines - <b>{obj.coverage.get('totals').get('missing_lines')}</b></p>"
        )
        # print(obj.coverage)
        for name, value in obj.coverage.get('files').items():
            # print('cover file:', name)
            if not name.endswith('__init__.py'):
                display += (
                    f"<p><b>{name}</b> - <b>{value.get('summary').get('percent_covered_display')}%"
                    f"</b> "
                    f"| covered_lines - <b>{value.get('summary').get('covered_lines')}</b> "
                    f"| missing_lines - <b>{value.get('summary').get('missing_lines')}</b> "
                    f"{value.get('missing_lines')}</p>"
                )
        return format_html(display)

    def select_all_tests(self, obj):
        form_html = ('<input type="checkbox" class="select-checkbox" object-id='
                     '"select_all_tests-checkbox" id="select_all_tests-checkbox-id"/>')
        if self.request.session.get('task_id'):
            del self.request.session['task_id']
        return format_html(form_html)


@admin.register(ProjectEnvs)
class ProjectEnvsAdmin(admin.ModelAdmin):
    """Регистрация модели ProjectEnvs в админке"""
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 50, 'cols': 150})},
    }


@admin.register(TestClass)
class TestClassAdmin(admin.ModelAdmin):
    """Регистрация модели TestClass в админке"""
    inlines = [TestCaseInline]
    list_display = ['title', 'project', 'path']
    search_fields = ['title', 'id']
    ordering = ['title']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    """Регистрация модели TestCase в админке"""
    form = TestCaseAdminForm
    list_display = ['title', 'type', 'project', 'test_class', 'result']
    search_fields = ['title', 'id']
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_testing',
    ]
    fieldsets = [(None, {
        'fields': (
            'created_at',
            'updated_at',
            'last_testing',
            'type',
            'project',
            'test_class',
            'title',
            'description',
            'path',
            'result',
            'error_description',
        )}), ]

# class TestClassInline(admin.StackedInline):
#     inlines = [TestCaseInline]
#     model = TestClass
#     extra = 0
#     # max_num = 0
#     can_delete = False
#     show_change_link = True
#     # verbose_name = _('telegram account')
#     # verbose_name_plural = ''
#     # fieldsets = [(None, {'fields': ()})]
