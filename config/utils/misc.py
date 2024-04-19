"""Модуль реализации дополнительных инструментов приложения"""
import json
from json import JSONDecodeError


def get_bool_from_str(string: str) -> bool:
    """Возвращает логическое значение True если строка имеет json формат и равна true
    и False во всех остальных случаях"""
    try:
        result = json.loads(string)
    except JSONDecodeError:
        result = None
    return result if result is True else False


def get_list_from_str(string: str) -> list:
    """Возвращает список элементов, если строка имеет json формат списка иначе пустой список"""
    try:
        result = json.loads(string)
    except JSONDecodeError:
        result = []
    return result
