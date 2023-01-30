import time
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import PATH_TO_BROWSER


class Browser:
    """ Предоставляет доступ к браузеру. """
    CHECK_DICT = {
        By.ID: 'return document.getElementById',
        By.CLASS_NAME: 'return document.getElementsByClassName',
        By.TAG_NAME: 'return document.getElementsByTagName',
    }

    def __init__(self, user=True, full_load=False, extensions=False):
        options = Options()
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--ignore-certificate-errors-spki-list')

        if not extensions:
            options.add_argument('--disable-extensions')

        if user:
            options.add_argument("--user-data-dir=" + PATH_TO_BROWSER)

        if not full_load:
            capa = DesiredCapabilities.CHROME
            capa["pageLoadStrategy"] = "none"
            self.driver = webdriver.Chrome(options=options, desired_capabilities=capa)
        else:
            self.driver = webdriver.Chrome(options=options)

        self.driver.switch_to.new_window('tab')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def get(self, url: str) -> None:
        """ Загружает страницу. """
        self.driver.get(url)

    def execute(self, script: str, tries: int=5, sleep: float=0.5, arg: Any=None) -> Any:
        """ Выполняет js-скрипт в браузере
        :param script: скрипт
        :param tries: количество попыток
        :param sleep: время ожидания перед новой попыткой
        :param arg: аргументы для скрипта
        :return: результат выполнения
        """
        while tries > 0:
            try:
                return self.driver.execute_script(script, arg) if arg else self.driver.execute_script(script)
            except:
                time.sleep(sleep)
                tries -= 1
        return False

    def check_element(self, by: str, value: str, by_driver: bool=False) -> Any:
        """ Проверяет, есть ли на странице элемент
        :param by: как искать элемент [By.CLASS_NAME, By.ID, By.TAG_NAME]
        :param value: значение для поиска
        :param by_driver: искать через метод selenium или через script js
        :return: Any
        """
        try:
            if by_driver:
                return self.driver.find_element(by, value)
            else:
                return self.driver.execute_script(self.CHECK_DICT[by] + f'("{value}");')
        except:
            return False

    def wait_element(self, by: str, value: str, max_wait: float=10, by_driver: bool=False) -> bool:
        """ Ждет, пока на странице не появится указанный элемент
        :param by: как искать элемент [By.CLASS_NAME, By.ID, By.TAG_NAME]
        :param value: значение элемента, который ожидается
        :param max_wait: сколько секунд ждать
        :param by_driver: искать через метод selenium или через script js
        :return: True / None
        """
        while True:
            if self.check_element(by, value, by_driver):
                return True
            else:
                max_wait -= 0.2
                if max_wait < 0:
                    return False
                time.sleep(0.2)

    def get_and_wait(self, url: str, key: str, by: str=By.CLASS_NAME, max_wait: int=10) -> bool:
        """ Прогружает страницу и ждет до тех пор, пока не появится указанный элемент или не истечен время
        :param url: ссылка на страницу
        :param key: элемент, который ожидается
        :param by: по какому тегу будет происходить поиск элемента
        :param max_wait: максимальное количество ожидания (с)
        :return: True если элемент прогружен, в противном случае False
        """
        self.driver.get(url)
        return self.driver.wait_element(by, key, max_wait)

    def get_source(self) -> str:
        return self.driver.page_source

    def send_keys_to(self, by: str, key: str, value: str) -> None:
        """ Посылает элементу на странице указанное значение.
        :param by: как искать элемент [By.CLASS_NAME, By.ID, By.TAG_NAME]
        :param key: значение элемента, которому шлется value
        :param value: посылаемое значение
        """
        self.driver.find_element(by, key).send_keys(value)

    def refresh(self) -> None:
        self.driver.refresh()

    def shutdown(self) -> None:
        """ Закрывает вкладку и выключает браузер (chromedriver). """
        self.driver.close()
        self.driver.quit()
