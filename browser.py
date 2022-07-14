from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from config import PATH_TO_BROWSER, ACCOUNTS
import time


class Browser:
    def __init__(self, user=True, full_load=False):
        options = Options()
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument('--disable-extensions')
        options.add_argument('--blink-settings=imagesEnabled=false')

        if user:
            options.add_argument("--user-data-dir=" + PATH_TO_BROWSER)

        if not full_load:
            capa = DesiredCapabilities.CHROME
            capa["pageLoadStrategy"] = "none"
            self.driver = webdriver.Chrome(options=options, desired_capabilities=capa)
        else:
            self.driver = webdriver.Chrome(options=options)

        self.driver.switch_to.new_window('tab')
        self.max_wait = 5

        self.CHECK_DICT = {
            By.ID: 'return document.getElementById',
            By.CLASS_NAME: 'return document.getElementsByClassName',
            By.TAG_NAME: 'return document.getElementsByTagName',
        }

    def scroll_page(self, key):
        old_count = 0
        count = -1
        while old_count != count or old_count <= 0:
            try:
                old_count = count
                self.driver.execute_script(
                    f"document.getElementsByClassName('{key}')[0].getElementsByTagName('ul')[0].lastChild.scrollIntoView();")
                time.sleep(2)
                count = self.driver.execute_script(
                    f"return document.getElementsByClassName('{key}')[0].getElementsByTagName('ul')[0].childElementCount;")
            except: pass

    def get(self, url):
        self.driver.get(url)
        return self.get_source()

    def execute(self, script, sleep=0):
        res = self.driver.execute_script(script)
        time.sleep(sleep)
        return res

    def check_element(self, by, value, by_driver=False):
        """ Проверяет, есть ли на странице элемент
        :param by: как искать элемент [By.CLASS_NAME, By.ID, By.TAG_NAME]
        :param value: значение для поиска
        :param by_driver: искать через метод selenium или через script js
        :return: True / None
        """
        try:
            return self.driver.execute_script(self.CHECK_DICT[by] + f'("{value}");') if not by_driver else self.driver.find_element(by, value)
        except:
            return None

    def wait_element(self, by, value, max_wait, by_driver=False):
        while True:
            if self.check_element(by, value, by_driver):
                return True
            else:
                max_wait -= 0.2
                if max_wait < 0:
                    return False
                time.sleep(0.2)


    def get_source(self):
        return self.driver.page_source

    def send_keys_to(self, by, key, value):
        self.driver.find_element(by, key).send_keys(value)

    def shutdown(self):
        self.driver.close()
        self.driver.quit()