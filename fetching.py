import time
import json
import asyncio
from typing import Union, Any

import aiohttp
from bs4 import BeautifulSoup as bs
from browser import Browser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from logger import log
from config import HEADERS, ACCOUNTS, KAKAO_LOGIN_FIELDS_ID


class Fetcher:
    def __init__(self):
        self.driver: Browser = None
        self.tries = 5
        self.sem = asyncio.Semaphore(5)
        self.sites = {
            'requests': {
                'https://seiga.nicovideo.jp': self.seiga_nicovideo,
                'https://web-ace.jp': self.web_ace,
                'https://gaugau.futabanet.jp': self.futabanet,
                'https://mechacomic.jp': self.mechacomic,
                'https://www.tappytoon.com': self.tappytoon
            },
            'browser': {
                'https://series.naver.com': self.series_naver,
                'https://page.kakao.com': self.kakao,
                'https://ridibooks.com': self.ridibooks,
                'https://manga.bilibili.com': self.bilibili,
                'https://www.bomtoon.com': self.bomtoon,
                'https://www.comico.kr': self.comico,
                'https://pocket.shonenmagazine.com': self.shonenmagazine,
            }
        }

    @log
    def get_by_keys(self, dictionary: str, keys: list[str]) -> Any:
        """ Принимает на вход словарь и проходит вглубь по ключам
        :param dictionary: словарь, по которому происходит итерация
        :param keys: список ключей
        :return: результат итерации, вернуться может все что угодно
        """
        dictionary = json.loads(dictionary)
        for key in keys:
            dictionary = dictionary[key]
        return dictionary

    @log
    async def fetch(self, url: str, browser: bool=False) -> str:
        """ Принимает на вход ссылку и возвращает результат парсинга сайта
        :param url: ссылка
        :param browser: требуется ли для парсинга браузер
        :return: гиперссылка на url и номер главы, если глав нет - прочерк, если неизвестный сайт - URL error
        """
        arr = self.sites['browser'] if browser else self.sites['requests']
        for key in arr.keys():
            if key in url:
                return await arr[key](url) if not browser else arr[key](url)
        else:
            return 'url error'

    @log
    def start_browser(self, user: bool=True, full_load: bool=False) -> None:
        """ Запускает браузер. Если он уже запущен - сначала закроет
        :param user: использовать ли профиль браузера по умолчанию (сохраненные аккаунты)
        :param full_load: прогружать ли страницу полностью перед тем как выполнять код
        """
        if self.driver:
            self.shutdown_browser()
        self.driver = Browser(user=user, full_load=full_load)
        self.login_kakao()

    @log
    def shutdown_browser(self) -> None:
        """ Закрывает браузер. """
        self.driver.shutdown()

    @log
    async def async_get_response(self, url: str) -> str:
        """ Запрашивает станицу по ссылке, возвращает результат (HTML)
        :param url: ссылка на страницу
        :return: исходный код страницы
        """
        async with self.sem:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(url) as response:
                    self.tries = (self.tries - 1) if response.status != 200 else 5
                    return await response.text()

    @log
    def hyperlink(self, url: str, num: Union[str, int]) -> str:
        """ Создает гиперссылку из ссылки и номера
        :param url: ссылка
        :param num: число
        :return: гиперссыка
        """
        return f'=ГИПЕРССЫЛКА("{url}";"{num}")'

    def get_and_wait(self, url: str, key: str, by: By=By.CLASS_NAME, max_wait: int=10) -> bool:
        """ Прогружает страницу и ждет до тех пор, пока не появится указанный элемент или не истечен время
        :param url: ссылка на страницу
        :param key: элемент, который ожидается
        :param by: по какому тегу будет происходить поиск элемента
        :param max_wait: максимальное количество ожидания (с)
        :return: True если элемент прогружен, в противном случае False
        """
        self.driver.get(url)
        return self.driver.wait_element(by, key, max_wait)

    @staticmethod
    def format_number(num: str):
        result = ''.join([el if el.isdigit() else ' ' for el in num])
        return '.'.join(result.split()) if result else '-'

    @log
    def kakao(self, url: str) -> str:
        if self.get_and_wait(url, 'css-1imdls4-Text-BelowTabSelectBox'):
            time.sleep(1)
            self.driver.execute('document.getElementsByClassName("css-1imdls4-Text-BelowTabSelectBox")[0].click();')
            time.sleep(1)
            self.driver.execute('document.getElementsByClassName("css-169255i-DialogCheckButton")[1].click();')
            time.sleep(1)
        if self.driver.wait_element(By.CLASS_NAME, 'css-121idz6-SingleListViewItem'):
            script = "return document.getElementsByClassName('css-121idz6-SingleListViewItem')[0].getAttribute('data-t-obj');"
            num_str = self.driver.execute(script, tries=20)
            num = json.loads(num_str)['eventMeta']['name']
            return self.hyperlink(url, num[:num.index('화')][-3:].strip())
        return self.hyperlink(url, '-')

    @log
    def series_naver(self, url: str) -> str:
        if 'sortOrder=DESC' not in url:
            url += '&sortOrder=DESC'
        if self.get_and_wait(url, 'volumeList', by=By.ID):
            script = "return document.getElementById('volumeList').firstChild.getElementsByTagName('strong')[0].textContent;"
            if res := self.driver.execute(script):
                res = res[:res.rfind('(')]
                res = ''.join([el for el in res.split('.')[0].split('-')[0].split()[-1] if el.isdigit()])
                return self.hyperlink(url, res)
        return self.hyperlink(url, '-')

    @log
    async def seiga_nicovideo(self, url: str) -> str:
        soup = bs(await self.async_get_response(url), 'lxml')
        num = soup.find_all('div', {'class': 'title'})[-1].text
        return self.hyperlink(url, self.format_number(num))

    @log
    async def web_ace(self, url: str) -> str:
        t_url = url + '/episode/' if url.endswith('/') else url + 'episode/'
        chapter = bs(await self.async_get_response(t_url), 'lxml').find('ul', {'class': 'table-view'}).find_all('li')[0]
        num = chapter.find('p', {'class': 'text-bold'}).text
        num = ''.join([el for el in num if el.isdigit() or el == '-']).replace('-', '.')
        return self.hyperlink(url, num)

    @log
    async def mechacomic(self, url: str) -> str:
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'p-search_chapterNo'})
        return self.hyperlink(url, res.findAll('div', {'class', 'u-inlineBlock'})[-1].getText().strip()[1:-2]) if res else '-'

    @log
    async def futabanet(self, url: str) -> str:
        from string import punctuation
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'detail-ex__btn-item--latest'})
        res = res.getText().strip().split('\n')[1][1:]
        res = ''.join([(el if el.isdigit() or el in punctuation else '') for el in res])
        if '.' in res:
            res = res[:res.rfind('(')]
        check_bracket = lambda x: '.' if x == '(' else ''
        return self.hyperlink(url, ''.join([el if el.isdigit() else check_bracket(el) for el in res]))

    @log
    async def tappytoon(self, url: str) -> str:
        res = bs(await self.async_get_response(url), 'lxml').find('script', {'id': '__NEXT_DATA__'})
        arr = self.get_by_keys(res.text, ['props', 'initialState', 'entities', 'chapters'])
        arr = [arr[key] for key in arr.keys()]
        for el in sorted(arr, key=lambda x: x['order'])[::-1]:
            if el['isPublished']:
                return self.hyperlink(url, el['order'])

    @log
    def bilibili(self, url: str) -> str:
        self.driver.get(url)
        self.driver.wait_element(By.CLASS_NAME, 'last-update', 10)
        num = self.driver.execute("return document.getElementsByClassName('last-update')[0].textContent;").split()[1]
        return self.hyperlink(url, num)

    @log
    def bomtoon(self, url: str) -> str:
        self.driver.get(url)
        self.driver.wait_element(By.ID, 'bt-sort-episode', 10)
        res = bs(self.driver.get_source(), 'lxml').find('div', {'id': 'bt-sort-episode'}).find('a')
        res = res.get_attribute_list('data-sort')[0].split(',')
        res.remove('h0')
        return self.hyperlink(url, len(res))

    @log
    def shonenmagazine(self, url: str) -> str:
        self.driver.get(url)
        time.sleep(5)
        self.driver.driver.execute_script('window.scrollBy(0, 1500);')
        self.driver.wait_element(By.CLASS_NAME, 'series-episode-list-title', 10)
        num = self.driver.execute("return document.getElementsByClassName('series-episode-list-title')[0].textContent;")
        num = ''.join([el if el.isdigit() else ' ' for el in num]).split()[0]
        return self.hyperlink(url, num)

    @log
    def webtoon_kakao(self, url):
        import webtoon_kakao
        return webtoon_kakao.main(url)

    @log
    def ridibooks(self, url: str) -> str:
        self.driver.get(url)
        time.sleep(3)
        if self.driver.driver.current_url.startswith('https://ridibooks.com/account/login?'):
            self.login_ridibooks()
            time.sleep(5)
            self.driver.get(url)
        if self.driver.wait_element(By.CLASS_NAME, 'book_count', 10):
            # Сколько всего глав на странице
            num = int(self.driver.driver.find_element(By.CLASS_NAME, 'book_count').text.split()[1][:-1])
            num = self.driver.execute(f"return document.getElementsByClassName('js_book_title')[{num-1}].textContent;")
            num = num.split()[-1][:-1]
        else: num = '-'
        return self.hyperlink(url, num)

    @log
    def comico(self, url: str) -> str:
        self.driver.get(url)
        while not self.driver.wait_element(By.CLASS_NAME, 'btn_kakao', 1, by_driver=True) \
            and not self.driver.wait_element(By.CLASS_NAME, 'list_product', 1, by_driver=True):
            continue
        if not self.driver.check_element(By.CLASS_NAME, 'list_product', by_driver=True):
            if not self.login_comico():
                num = 'NEED LOGIN'
            else:
                self.driver.wait_element(By.CLASS_NAME, 'list_product', 10, by_driver=True)
                num = self.format_number(self.driver.driver.find_elements(By.CLASS_NAME, 'tit_episode')[-1].text)
        else:
            self.driver.wait_element(By.CLASS_NAME, 'list_product', 10, by_driver=True)
            num = self.format_number(self.driver.driver.find_elements(By.CLASS_NAME, 'tit_episode')[-1].text)
        return self.hyperlink(url, num)

    @log
    def login_comico(self) -> None:
        s1 = "document.getElementsByClassName('layer_foot')[0].getElementsByTagName('button')[1].click();"
        s2 = "document.getElementsByClassName('btn_kakao')[0].click();"
        self.driver.wait_element(By.CLASS_NAME, 'layer_foot', 15, by_driver=True)
        self.driver.execute(s1 + s2)
        return self.driver.wait_element(By.CLASS_NAME, 'list_product', 30)

    @log
    def login_kakao(self) -> None:
        self.driver.get('https://page.kakao.com/main')
        if self.driver.wait_element(By.CLASS_NAME, 'css-dqete9-Icon-PcHeader', 15):
            time.sleep(10)
            self.driver.execute('window.stop();')
            parent = self.driver.driver.current_window_handle
            self.driver.execute("document.getElementsByClassName('css-dqete9-Icon-PcHeader')[0].click();")
            time.sleep(5)
            if len(self.driver.driver.window_handles) == 2:
                return None
            # Переключимся на окно авторизации
            handle = self.driver.driver.window_handles[-1]
            self.driver.driver.switch_to.window(handle)
            self.driver.wait_element(By.ID, KAKAO_LOGIN_FIELDS_ID['login'], max_wait=15, by_driver=True)
            time.sleep(5)
            if not self.driver.execute(f"return document.getElementById('{KAKAO_LOGIN_FIELDS_ID['login']}').innerHTML;") \
                and not self.driver.execute(f"return document.getElementById('{KAKAO_LOGIN_FIELDS_ID['password']}').innerHTML;"):
                self.driver.driver.find_element(By.ID, KAKAO_LOGIN_FIELDS_ID['login']).send_keys(Keys.CONTROL, 'a')
                self.driver.driver.find_element(By.ID, KAKAO_LOGIN_FIELDS_ID['login']).send_keys(Keys.DELETE)
                self.driver.driver.find_element(By.ID, KAKAO_LOGIN_FIELDS_ID['password']).send_keys(Keys.CONTROL, 'a')
                self.driver.driver.find_element(By.ID, KAKAO_LOGIN_FIELDS_ID['password']).send_keys(Keys.DELETE)
                self.driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['login'], ACCOUNTS['kakao'][0])
                self.driver.send_keys_to(By.ID, KAKAO_LOGIN_FIELDS_ID['password'], ACCOUNTS['kakao'][1])
            try:
                self.driver.execute(f"document.getElementsByClassName('{KAKAO_LOGIN_FIELDS_ID['staySigned']}')[0].click();")
            except:
                pass
            time.sleep(0.5)
            self.driver.execute(f"document.getElementsByClassName('{KAKAO_LOGIN_FIELDS_ID['buttonLogin']}')[0].click();")
            time.sleep(5)
            self.driver.driver.switch_to.window(parent)

    @log
    def login_ridibooks(self):
        self.driver.send_keys_to(By.ID, 'login_id', ACCOUNTS['ridibooks'][0])
        self.driver.send_keys_to(By.ID, 'login_pw', ACCOUNTS['ridibooks'][1])
        self.driver.execute("document.getElementsByClassName('account-checkbox')[0].click();")
        self.driver.execute("document.getElementsByClassName('login-button')[0].click();")
