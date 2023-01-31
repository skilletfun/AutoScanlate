import json
import time
from typing import Union, Any

from browser import Browser
from logger import log
from config import ACCOUNTS, KAKAO_LOGIN_FIELDS_ID, LOGIN_TO

from selenium.webdriver.common.by import By


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

def titles_for_download(orig_arr, new_arr):
    result_arr = []
    for i in range(min(len(orig_arr), len(new_arr))):
        if orig_arr[i].strip() and new_arr[i].strip() and orig_arr[i] != '-' and new_arr[i] != '-':
            old = orig_arr[i] if orig_arr[i].isdigit() else orig_arr[i].split(';')[1][1:-2]
            new = new_arr[i].split(';')[1][1:-2]
            if old != '-' and new != '-' and int(new) > int(old):
                result_arr.append(new_arr[i].split(';')[0][14:-1])
    return result_arr


@log
def login_comico(driver: Browser) -> bool:
    driver.get('https://comico.kr/login')
    driver.execute("document.getElementsByClassName('btn_kakao')[0].click();")
    time.sleep(10)

@log
def login_kakao(driver: Browser) -> None:
    driver.get('https://page.kakao.com/main')
    if driver.wait_element(By.CLASS_NAME, 'css-dqete9-Icon-PcHeader', 5):
        parent = driver.driver.current_window_handle
        driver.execute("document.getElementsByClassName('css-dqete9-Icon-PcHeader')[0].click();")
        time.sleep(5)
        if len(driver.driver.window_handles) == 2:
            return None
        # Переключимся на окно авторизации
        handle = driver.driver.window_handles[-1]
        try:
            driver.driver.switch_to.window(handle)
            driver.wait_element(By.ID, KAKAO_LOGIN_FIELDS_ID['login'], max_wait=15, by_driver=True)
            time.sleep(5)
            if not driver.execute(f"return document.getElementById('{KAKAO_LOGIN_FIELDS_ID['login']}').innerHTML;") \
                and not driver.execute(f"return document.getElementById('{KAKAO_LOGIN_FIELDS_ID['password']}').innerHTML;"):
                driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['login'], (Keys.CONTROL, 'a'))
                driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['login'], Keys.DELETE)
                driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['password'], (Keys.CONTROL, 'a'))
                driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['password'], Keys.DELETE)
                driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['login'], ACCOUNTS['kakao'][0])
                driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['password'], ACCOUNTS['kakao'][1])
            time.sleep(0.5)
            try:
                driver.execute(f"document.getElementsByClassName('{KAKAO_LOGIN_FIELDS_ID['staySigned']}')[0].click();")
            except:
                pass
            time.sleep(0.5)
            driver.execute(f"document.getElementsByClassName('{KAKAO_LOGIN_FIELDS_ID['buttonLogin']}')[0].click();")
            time.sleep(5)
        finally:
            driver.driver.switch_to.window(parent)

@log
def login_ridibooks(driver: Browser):
    driver.get('https://ridibooks.com/account/login')
    if driver.current_url.startswith("https://ridibooks.com/account/login"):
        input_form = driver.execute(f"return document.getElementsByTagName('input');")
        input_form[0].send_keys(ACCOUNTS['ridibooks'][0])
        input_form[1].send_keys(ACCOUNTS['ridibooks'][1])
        time.sleep(0.5)
        driver.execute("document.getElementsByTagName('button')[0].click();")
        time.sleep(0.5)
        driver.execute("document.getElementsByTagName('button')[1].click();")
        time.sleep(5)

@log
def login_lezhin(driver: Browser):
    pass

@log
def login_all(driver: Browser):
    if LOGIN_TO['KAKAO']:
        login_kakao(driver)
    if LOGIN_TO['COMICO']:
        login_comico(driver)
    if LOGIN_TO['RIDIBOOKS']:
        login_ridibooks(driver)
    if LOGIN_TO['LEZHIN']:
        login_lezhin(driver)
