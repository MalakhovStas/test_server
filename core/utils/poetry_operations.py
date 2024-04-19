"""Модуль инструментов для работы с Poetry из кода приложения"""
import subprocess

from loguru import logger

from config import settings


class PoetryOperations:
    """Класс описывающий операции с виртуальным окружением poetry"""

    def __init__(self):
        self.sign = f'{self.__class__.__name__}:'
        self.logger = logger

    def run_subprocess(self, command: list) -> bool:
        """Вызывает subprocess с переданной командой, логирует результат.
        Если процесс завершился ошибкой возвращает False в противном случае True"""
        # pylint: disable=consider-using-with
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if error := process.stderr.read().decode("utf-8"):
            result = False
            self.logger.warning(f'{self.sign} {error=}')
        else:
            result = True
            if settings.DEBUG:
                self.logger.debug(f'{self.sign} {process.stdout.read().decode("utf-8")}')
        return result

    def poetry_check(self) -> bool:
        """Проверяет содержимое файла pyproject.toml и его соответствие файлу poetry.lock,
        возвращает подробный отчет, если есть какие-либо ошибки"""
        return self.run_subprocess(command=["poetry", "check"])

    def add_driver(self, driver_name: str) -> bool:
        """Добавление кода драйвера в виртуальное окружение poetry,
        с git если имя драйвера и адрес в git указаны в файле .env"""
        if driver_remote_path := settings.GIT_REMOTE_DRIVERS.get(driver_name):
            result = self.run_subprocess(command=[
                "poetry", "add", f"git+{driver_remote_path}#{settings.GIT_BRANCH}",
                "--group", "drivers"])
            if settings.DEBUG:
                self.logger.debug(f'{self.sign} Poetry add driver: {driver_name}')
        else:
            result = False
            self.logger.warning(f'{self.sign} Poetry not add driver: {driver_name} > '
                                'not found driver remote path in .env')
        return result

    def remove_driver(self, driver_name: str) -> bool:
        """Удаляет пакет драйвера из виртуального окружения poetry и из pyproject.toml"""
        if driver_package_name := settings.DRIVERS_ALLOCATOR.get(driver_name):
            result = self.run_subprocess(command=[
                "poetry", "remove", driver_package_name, "--group", "drivers"])
            if settings.DEBUG:
                self.logger.debug(f'{self.sign} Poetry remove driver: {driver_name}')
        else:
            result = False
            self.logger.warning(f'{self.sign} Poetry not remove driver: {driver_name} > '
                                'not found driver package name in PoetryOperations.allocator')
        return result

    def update_driver(self, driver_name: str) -> bool:
        """Обновление кода драйвера с git на последний коммит, ветки указанной в pyproject.toml"""
        if driver_package_name := settings.DRIVERS_ALLOCATOR.get(driver_name):
            result = self.run_subprocess(command=["poetry", "update", driver_package_name])
            if settings.DEBUG:
                self.logger.debug(f'{self.sign} Poetry update driver: {driver_name}')
        else:
            result = False
            self.logger.warning(f'{self.sign} Poetry not update driver: {driver_name} > '
                                'not found driver package name in PoetryOperations.allocator')
        return result
