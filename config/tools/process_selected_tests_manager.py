"""Модуль инструментов для запуска и контроля выполнения тестов"""
import inspect
import os
import subprocess

from celery_progress.backend import ProgressRecorder

from config.settings import BASE_DIR
from test_cases.models import Project


class ProcessSelectedTests:
    """Класс для запуска и контроля выполнения тестов"""
    general_ssh_host = 'ssh://git@git.kfinance.ru:2422'
    general_branch = 'development'
    general_env_path = '/env/.env.local'
    general_docker_up_path = '/docker/up.sh'
    general_docker_down_path = '/docker/down.sh'
    projects_process_directory = 'projects'

    # sudo_password = ''

    def __init__(self, project: Project, progress: ProgressRecorder):
        self.project = project
        self.progress = progress

        self.project_lower_name = self.project.title.lower()
        self.project_process_dir = f'{self.projects_process_directory}/{self.project_lower_name}'

    def run_process(self, select_all_tests: bool, selected_tests: list):
        """Запуск процесса тестирования проекта"""
        processes = (
            self.clone_project,
            self.run_docker,
            self.poetry_install,
            self.run_tests,
            self.delete_project
        )
        for num, process in enumerate(processes, 1):
            self.progress.set_progress(
                current=num,
                total=len(processes),
                description=inspect.getdoc(process)
            )
            if process.__name__ == 'run_tests':
                process(select_all_tests=select_all_tests, selected_tests=selected_tests)
            else:
                process()

    def clone_project(self):
        """Клонирование репозитория проекта"""
        repository = f"{self.general_ssh_host}{self.project.repository}"
        subprocess.Popen([
            'git',
            'clone',
            '--branch',
            f'{self.general_branch}',
            f'{repository}',
            f'{self.project_process_dir}'
        ]).wait()

        with open(f'{self.project_process_dir}{self.general_env_path}', 'w') as file:
            file.write(self.project.env.environments)

    def run_docker(self):
        """Запуск Docker контейнеров проекта"""
        if 'docker' in os.listdir(self.project_process_dir):
            subprocess.Popen([f'{self.project_process_dir}{self.general_docker_up_path}']).wait()

    def poetry_install(self):
        """Установка зависимостей проекта"""
        os.chdir(f'{self.project_process_dir}')
        # subprocess.Popen(['poetry', 'config', 'virtualenvs.in-project', 'true']).wait()
        subprocess.Popen(['poetry', 'update']).wait()
        os.chdir(BASE_DIR)

    def run_tests(self, select_all_tests: bool, selected_tests: list):
        """Запуск тест кейсов проекта"""
        os.chdir(f'{self.project_process_dir}')
        if select_all_tests:
            subprocess.Popen(['pytest']).wait()
        else:
            if selected_tests:
                for test_case in selected_tests:
                    subprocess.Popen([
                        'pytest',
                        f'{test_case.path}::{test_case.test_class.title}::{test_case.title}'
                    ]).wait()
        os.chdir(BASE_DIR)

    def delete_project(self):
        """Остановка Docker контейнеров и Удаление проекта"""
        if 'docker' in os.listdir(self.project_process_dir):
            subprocess.Popen([f'{self.project_process_dir}{self.general_docker_down_path}']).wait()

        subprocess.Popen(['sudo', 'rm', '-Rf', f'{self.project_process_dir}']).wait()
        # delete_process = subprocess.Popen(
        #     ['sudo', '-S', 'rm', '-Rf', f'{self.project_process_dir}'],
        #     universal_newlines=True
        # )
        # delete_process.communicate(self.sudo_password + '\n')
        subprocess.Popen(['poetry', 'update']).wait()
