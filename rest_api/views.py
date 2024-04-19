from typing import Union

from django.contrib.auth.models import Group
from django.db.models import Model
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from test_cases.models import Project, TestClass, TestCase
from .serializers import GroupSerializer
from .serializers import ProjectSerializer, TestClassSerializer, TestCaseSerializer


class GroupsViewSet(ModelViewSet):
    """Представление для обработки запросов к модели Group"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class MultipleModelsCreateView(APIView):
    """Представление для обработки запросов содержащих данные для создания
    экземпляров моделей: Project, TestClass, TestCase"""

    @staticmethod
    def change_instance_model(
            instance: Model, validated_data: dict, exclusion_fields: list) -> list:
        """Логика обновления экземпляров моделей в случае изменения полей не входящих
         в список exclusion_fields, возвращает список изменённых полей модели"""
        updated_fields = []
        for field, value in validated_data.items():
            if field not in exclusion_fields:
                if getattr(instance, field) != value:
                    setattr(instance, field, value)
                    updated_fields.append(field)
        return updated_fields

    def project_data_handler(self, project_data: dict) -> dict[str, Union[int, list]]:
        """Обработчик входящих данных для создания экземпляров модели Project"""
        result_data = {"create_project": 0, "update_project": 0, "project_errors": []}
        project_serializer = ProjectSerializer(data=project_data)
        if project_serializer.is_valid():
            project_serializer.save()
            result_data['create_project'] += 1
        else:
            if (project_title := project_serializer.errors.get('title')) and (
                    'project with this title already exists' in project_title[0]):
                project = Project.objects.get(title=project_data.get('title'))
                if self.change_instance_model(
                        instance=project,
                        validated_data=project_data,
                        exclusion_fields=['title']
                ):
                    project.save()
                    result_data['update_project'] += 1
            else:
                result_data['project_errors'].append(project_serializer.errors)
        return result_data

    def test_classes_list_handler(self, test_classes_list: list) -> dict[str, Union[int, list]]:
        """Обработчик входящих данных для создания экземпляров модели TestClass"""
        result_data = {
            "create_test_classes": 0, "update_test_classes": 0, "test_classes_errors": []
        }

        for test_class_data in test_classes_list:
            test_class_serializer = TestClassSerializer(data=test_class_data)

            if test_class_serializer.is_valid():
                test_class = TestClass.objects.filter(
                    project=test_class_serializer.validated_data.get('project'),
                    title=test_class_serializer.validated_data.get('title'),
                ).first()
                if not test_class:
                    test_class_serializer.save()
                    result_data['create_test_classes'] += 1
                else:
                    if self.change_instance_model(
                            instance=test_class,
                            validated_data=test_class_serializer.validated_data,
                            exclusion_fields=['project', 'title']
                    ):
                        test_class.save()
                        result_data['update_test_classes'] += 1
            else:
                result_data['test_classes_errors'].append(test_class_serializer.errors)
        # print(test_classes_list)
        return result_data

    def test_cases_list_handler(self, test_cases_list: list) -> dict[str, Union[int, list]]:
        """Обработчик входящих данных для создания экземпляров модели TestCase"""
        result_data = {
            "create_test_cases": 0, "update_test_cases": 0, "test_cases_errors": []
        }

        for test_case_data in test_cases_list:
            test_case_serializer = TestCaseSerializer(data=test_case_data)

            if test_case_serializer.is_valid():
                # print('\n\n', test_case_data)
                test_case = TestCase.objects.filter(
                    project=test_case_serializer.validated_data.get('project'),
                    test_class=test_case_serializer.validated_data.get('test_class'),
                    title=test_case_serializer.validated_data.get('title'),
                ).first()
                if not test_case:
                    test_case_serializer.save()
                    result_data['create_test_cases'] += 1
                else:
                    if updated_fields := self.change_instance_model(
                            instance=test_case,
                            validated_data=test_case_serializer.validated_data,
                            exclusion_fields=['project', 'test_class']
                    ):
                        if len(updated_fields) == 1 and 'last_testing' in updated_fields:
                            test_case.save(update_fields=updated_fields)
                        else:
                            test_case.save()
                            result_data['update_test_cases'] += 1

            else:
                result_data['test_cases_errors'].append(test_case_serializer.errors)
        return result_data

    def post(self, request: Request):
        """Обработчик данных входящих методом POST по соответствующему url"""
        response_data = {}
        if project_data := request.data.get('project'):
            response_data.update(self.project_data_handler(project_data))

        if test_classes_list := request.data.get('test_classes'):
            response_data.update(self.test_classes_list_handler(test_classes_list))

        if test_cases_list := request.data.get('test_cases'):
            response_data.update(self.test_cases_list_handler(test_cases_list))

        return Response(response_data, status=201 if response_data else 401)
