import json
import time
from typing import Union, Any

from logger import log
from browser import Browser
from config import KAKAO_LOGIN_FIELDS_ID, SESSION_PATH

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def connect_to_browser():
    with open(SESSION_PATH) as inf:
        js = json.loads(inf.read())
        if js['url'] and js['session_id']:
            return Browser(js['url'], js['session_id'])

def get_by_keys(dictionary: str, keys: list[str]) -> Any:
    """ Принимает на вход словарь и проходит вглубь по ключам
    :param dictionary: словарь, по которому происходит итерация
    :param keys: список ключей
    :return: результат итерации, вернуться может все что угодно
    """
    js_dictionary = json.loads(dictionary)
    for key in keys:
        js_dictionary = js_dictionary[key]
    return js_dictionary

def hyperlink(url: str, num: Union[str, int]) -> str:
    """ Создает гиперссылку из ссылки и номера
    :param url: ссылка
    :param num: число
    :return: гиперссылка
    """
    return f'=ГИПЕРССЫЛКА("{url}";"{num}")'

def format_number(num: str) -> str:
    """ Принимает на вход строку, откуда вычленяет цифры и возвращает строку только из числа
    :param num: строка, которая может содержать в себе цифры
    :return: число или прочерк
    """
    result = ''.join([el if el.isdigit() else ' ' for el in num])
    return '.'.join(result.split()) if result else '-'

def titles_for_download(orig_arr, new_arr) -> list:
    result_arr = []
    for i in range(min(len(orig_arr), len(new_arr))):
        if orig_arr[i].strip() and new_arr[i].strip() and orig_arr[i] != '-' and new_arr[i] != '-':
            old = orig_arr[i] if orig_arr[i].isdigit() else orig_arr[i].split(';')[1][1:-2]
            new = new_arr[i].split(';')[1][1:-2]
            if old != '-' and new != '-' and int(new) > int(old):
                result_arr.append(new_arr[i].split(';')[0][14:-1])
    return result_arr
