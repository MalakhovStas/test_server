from django.contrib.auth.models import Group
from rest_framework import serializers

from test_cases.models import Project, TestClass, TestCase


class ProjectSerializer(serializers.ModelSerializer):
    """Для обработки данных модели Project"""
    authors = serializers.ListField()
    coverage = serializers.DictField()

    class Meta:
        """Класс определения метаданных"""
        model = Project
        fields = 'title', 'version', 'description', 'authors', 'repository', 'coverage'


class TestClassSerializer(serializers.ModelSerializer):
    """Для обработки данных модели TestClass"""

    class Meta:
        """Класс определения метаданных"""
        model = TestClass
        fields = 'project', 'title', 'description', 'path'


class TestCaseSerializer(serializers.ModelSerializer):
    """Для обработки данных модели TestCase"""

    def is_valid(self, *args, **kwargs):
        """Переопределение метода"""
        result = super().is_valid(*args, **kwargs)
        if result:
            class_instance = TestClass.objects.filter(project=self.validated_data.get('project'),
                                                      title=self.initial_data.get('class')).first()
            self.validated_data['test_class'] = class_instance
        return result

    class Meta:
        """Класс определения метаданных"""
        model = TestCase
        fields = ('type', 'project', 'test_class', 'title', 'description',
                  'path', 'test_data', 'result', 'error_description', 'last_testing')


class GroupSerializer(serializers.ListSerializer):
    """Для обработки данных модели Group"""

    class Meta:
        """Класс определения метаданных"""
        model = Group
        fields = "pk", "name"
