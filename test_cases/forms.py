from django import forms

from .models import TestCase


class TestCaseAdminForm(forms.ModelForm):
    """Форма для отображения модели TestCase"""

    class Meta:
        """Класс определения метаданных"""
        model = TestCase
        fields = '__all__'

    class Media:
        """Класс определения медиа данных"""
        js = ('admin/js/testcase_admin.js',)
