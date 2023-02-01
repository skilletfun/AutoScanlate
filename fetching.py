import time
import json
import asyncio
from typing import Union, Any, List

import aiohttp
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from logger import log
from browser import Browser
from config import HEADERS, ACCOUNTS, KAKAO_LOGIN_FIELDS_ID
from helper_funcs import hyperlink, format_number


class Fetcher:
    def __init__(self):
        self.tries = 5
        self.sem = asyncio.Semaphore(5)
        self.sites = {
            'requests': {
                'https://seiga.nicovideo.jp': self.seiga_nicovideo,
                'https://web-ace.jp': self.web_ace,
                'https://gaugau.futabanet.jp': self.futabanet,
                'https://mechacomic.jp': self.mechacomic
            },
            'browser': {
                'https://www.lezhin.com': self.lezhin,
                'https://www.tappytoon.com': self.tappytoon,
                'https://series.naver.com': self.series_naver,
                'https://page.kakao.com': self.kakao,
                'https://ridibooks.com': self.ridibooks,
                'https://manga.bilibili.com': self.bilibili,
                'https://www.bomtoon.com': self.bomtoon,
                'https://bomtoon.com': self.bomtoon,
                'https://www.comico.': self.comico,
                'https://www.pocketcomics.com': self.comico,
                'https://pocket.shonenmagazine.com': self.shonenmagazine,
            }
        }

    @log
    async def fetch(self, url: str, browser: Browser=None) -> str:
        """ Принимает на вход ссылку и возвращает результат парсинга сайта
        :param url: ссылка
        :param browser: требуется ли для парсинга браузер
        :return: гиперссылка на url и номер главы, если глав нет - прочерк, если неизвестный сайт - URL error
        """
        arr = self.sites['browser'] if browser else self.sites['requests']
        for key in arr.keys():
            if key in url:
                self.driver = browser
                return await arr[key](url) if not browser else arr[key](url)
        return 'url error'

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
    def kakao(self, url: str) -> str:
        if self.driver.get_and_wait(url, 'mr-4pxr', max_wait=5):
            time.sleep(0.5)
            i = 1 if self.driver.execute('return document.getElementsByClassName("mr-4pxr")[0].textContent;') == '구매한 회차' else 0
            self.driver.execute(f'document.getElementsByClassName("mr-4pxr")[{i}].click();')
            self.driver.wait_element(By.CLASS_NAME, 'mx-22pxr')
            time.sleep(0.5)
            self.driver.execute('document.getElementsByClassName("mx-22pxr")[1].click();')
            time.sleep(0.5)
            if self.driver.wait_element(By.CLASS_NAME, 'mb-4pxr'):
                script = "return document.getElementsByClassName('mb-4pxr')[0].textContent;"
                num_str = self.driver.execute(script)
                return hyperlink(url, num_str[:num_str.index('화')][-3:].strip())
        return hyperlink(url, '-')

    @log
    def series_naver(self, url: str) -> str:
        script = "return document.getElementById('volumeList').firstChild.getElementsByTagName('strong')[0].textContent;"
        if 'sortOrder=DESC' not in url:
            url += '&sortOrder=DESC'
        self.driver.get(url)
        while not ((res := self.driver.execute(script)) is False):
            res = res[:res.rfind('(')]
            res = ''.join([el for el in res.split('.')[0].split('-')[0].split()[-1] if el.isdigit()])
            return hyperlink(url, res)
        return hyperlink(url, '-')

    @log
    async def seiga_nicovideo(self, url: str) -> str:
        soup = bs(await self.async_get_response(url), 'lxml')
        num = soup.find_all('div', {'class': 'title'})[-1].text
        return hyperlink(url, format_number(num))

    @log
    async def web_ace(self, url: str) -> str:
        t_url = url + '/episode/' if url.endswith('/') else url + 'episode/'
        chapter = bs(await self.async_get_response(t_url), 'lxml').find('ul', {'class': 'table-view'}).find_all('li')[0]
        num = chapter.find('p', {'class': 'text-bold'}).text
        num = ''.join([el for el in num if el.isdigit() or el == '-']).replace('-', '.')
        return hyperlink(url, num)

    @log
    async def mechacomic(self, url: str) -> str:
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'p-search_chapterNo'})
        return hyperlink(url, res.findAll('div', {'class', 'u-inlineBlock'})[-1].getText().strip()[1:-2]) if res else '-'

    @log
    async def futabanet(self, url: str) -> str:
        from string import punctuation
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'detail-ex__btn-item--latest'})
        res = res.getText().strip().split('\n')[1][1:]
        res = ''.join([(el if el.isdigit() or el in punctuation else '') for el in res])
        if '.' in res:
            res = res[:res.rfind('(')]
        check_bracket = lambda x: '.' if x == '(' else ''
        return hyperlink(url, ''.join([el if el.isdigit() else check_bracket(el) for el in res]))

    @log
    def tappytoon(self, url: str) -> str:
        self.driver.get(url)
        self.driver.execute("document.getElementsByClassName('css-901oao r-zdkpiq r-fppytw r-1o4mh9l r-adoza8 r-1kyvuxt r-13hce6t r-q4m81j')[0].click();")
        time.sleep(3)
        num = '-'
        script_1 = "return document.getElementsByClassName('css-901oao css-vcwn7f r-i1xj32 r-1wbh5a2 r-1qhq223 r-1o4mh9l r-adoza8 r-1kyvuxt r-dnmrzs r-1ez4vuq r-1iln25a');"
        script_2 = "return document.getElementsByClassName('css-901oao r-zdkpiq r-1wbh5a2 r-1qhq223 r-1o4mh9l r-adoza8 r-1kyvuxt r-dnmrzs r-1ez4vuq');"
        for num, check in zip(self.driver.execute(script_1), self.driver.execute(script_2)):
            num = self.driver.driver.execute_script("return arguments[0].textContent;", num)
            check = self.driver.driver.execute_script("return arguments[0].textContent;", check)
            if not check.startswith('View'):
                num = num.split()[-1]
                break
        return hyperlink(url, num)

    @log
    def bilibili(self, url: str) -> str:
        self.driver.get_and_wait(url, 'last-update')
        num = self.driver.execute("return document.getElementsByClassName('last-update')[0].textContent;").split()[1]
        return hyperlink(url, num)

    @log
    def bomtoon(self, url: str) -> str:
        self.driver.get_and_wait(url, 'bt-sort-episode', By.ID)
        res = bs(self.driver.get_source(), 'lxml').find('div', {'id': 'bt-sort-episode'}).find('a')
        res = res.get_attribute_list('data-sort')[0].split(',')
        res.remove('h0')
        return hyperlink(url, len(res))

    @log
    def shonenmagazine(self, url: str) -> str:
        self.driver.get(url)
        time.sleep(5)
        self.driver.driver.execute_script('window.scrollBy(0, 1500);')
        self.driver.wait_element(By.CLASS_NAME, 'series-episode-list-title', 10)
        num = self.driver.execute("return document.getElementsByClassName('series-episode-list-title')[0].textContent;")
        num = ''.join([el if el.isdigit() else ' ' for el in num]).split()[0]
        return hyperlink(url, num)

    @log
    def webtoon_kakao(self, url: str) -> str:
        import webtoon_kakao
        return webtoon_kakao.main(url)

    @log
    def ridibooks(self, url: str) -> str:
        if self.driver.get_and_wait(url, 'book_count'):
            # Сколько всего глав на странице
            num = int(self.driver.driver.find_element(By.CLASS_NAME, 'book_count').text.split()[1][:-1])
            num = self.driver.execute(f"return document.getElementsByClassName('js_book_title')[{num-1}].textContent;")
            num = num.split()[-1][:-1]
        else: num = '-'
        return hyperlink(url, num)
    
    @log
    def lezhin(self, url: str) -> str:
        if self.driver.get_and_wait(url, 'episode__name'):
            num = self.driver.execute(f"return document.getElementsByClassName('episode__name');")[-1]
            num = int(self.driver.driver.execute_script("return arguments[0].textContent;", num))
        else: num = '-'
        return hyperlink(url, num)

    @log
    def comico(self, url: str) -> str:
        self.driver.get(url)
        while not self.driver.wait_element(By.CLASS_NAME, 'list_product'):
            time.sleep(0.2)
            continue
        return hyperlink(url, format_number(self.driver.driver.find_elements(By.CLASS_NAME, 'tit_episode')[-1].text))
