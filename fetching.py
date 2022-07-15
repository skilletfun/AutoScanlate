import time
from bs4 import BeautifulSoup as bs
import requests as r
import json
from config import HEADERS, ACCOUNTS
import asyncio
import aiohttp
from browser import Browser
from selenium.webdriver.common.by import By
from fp.fp import FreeProxy


class Fetcher:
    def __init__(self):
        self.driver: Browser = None
        self.tries = 5
        self.sem = asyncio.Semaphore(5)
        self.sites = {
            'requests': {
                'https://page.kakao.com': self.kakao,
                'https://series.naver.com': self.series_naver,
                'https://seiga.nicovideo.jp': self.seiga_nicovideo,
                'https://web-ace.jp': self.web_ace,
                'https://gaugau.futabanet.jp': self.futabanet,
                'https://mechacomic.jp': self.mechacomic,
                'https://www.tappytoon.com': self.tappytoon
            },
            'browser': {
                'https://ridibooks.com': self.ridibooks,
                'https://manga.bilibili.com': self.bilibili,
                'https://www.bomtoon.com': self.bomtoon,
                'https://www.comico.kr': self.comico,
                'https://webtoon.kakao.com': self.webtoon_kakao,
                'https://pocket.shonenmagazine.com': self.shonenmagazine,
            }
        }

    def get_by_keys(self, dictionary, keys):
        dictionary = json.loads(dictionary)
        for key in keys:
            dictionary = dictionary[key]
        return dictionary

    async def fetch(self, url, browser=False):
        arr = self.sites['browser'] if browser else self.sites['requests']
        for key in arr.keys():
            if key in url:
                return await arr[key](url) if not browser else arr[key](url)
        else:
            return 'URL error'

    def start_browser(self, user=True, full_load=False, proxy=None):
        if self.driver:
            self.shutdown_browser()
        self.driver = Browser(user=user, full_load=full_load, proxy=proxy)

    def shutdown_browser(self):
        self.driver.shutdown()

    async def async_get_response(self, url):
        async with self.sem:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(url) as response:
                    self.tries = (self.tries - 1) if response.status != 200 else 5
                    return await response.text()

    def hyperlink(self, url, num):
        return f'=ГИПЕРССЫЛКА("{url}";"{num}")'

    async def kakao(self, url):
        res = bs(await self.async_get_response(url), 'lxml').find('script', {'id': '__NEXT_DATA__'})
        return self.hyperlink(url, self.get_by_keys(res.text, ['props', 'initialState', 'series', 'series', 'onSaleCount']))

    async def series_naver(self, url):
        num = bs(await self.async_get_response(url), 'lxml').find('h5', {'class': 'end_total_episode'}).text.split()[1][:-1]
        return self.hyperlink(url, num)

    async def seiga_nicovideo(self, url):
        num = len(bs(await self.async_get_response(url), 'lxml').find('div', {'id': 'episode_list'}).find('ul').find_all('li'))
        return self.hyperlink(url, str(num))

    async def web_ace(self, url):
        t_url = url + '/episode/' if url.endswith('/') else url + 'episode/'
        num = len(bs(await self.async_get_response(t_url), 'lxml').find('ul', {'class': 'table-view'}).find_all('li'))
        return self.hyperlink(url, str(num))

    async def mechacomic(self, url):
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'p-search_chapterNo'})
        return self.hyperlink(url, res.findAll('div', {'class', 'u-inlineBlock'})[-1].getText().strip()[1:-2])

    async def futabanet(self, url):
        from string import punctuation
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'detail-ex__btn-item--latest'})
        res = ''.join([(el if el.isdigit() or el in punctuation else '') for el in res.getText().strip().split('\n')[1][1:]])
        check_breaket = lambda x: '.' if x == '(' else ''
        return self.hyperlink(url, ''.join([el if el.isdigit() else check_breaket(el) for el in res]))

    async def tappytoon(self, url):
        res = bs(await self.async_get_response(url), 'lxml').find('script', {'id': '__NEXT_DATA__'})
        arr = self.get_by_keys(res.text, ['props', 'initialState', 'entities', 'chapters'])
        arr = [arr[key] for key in arr.keys()]
        for el in sorted(arr, key=lambda x: x['order'])[::-1]:
            if el['isPublished']:
                return self.hyperlink(url, el['order'])

    def bilibili(self, url):
        self.driver.get(url)
        self.driver.wait_element(By.CLASS_NAME, 'last-update', 5)
        num = self.driver.execute("return document.getElementsByClassName('last-update')[0].textContent;").split()[1]
        return self.hyperlink(url, num)

    def bomtoon(self, url):
        self.driver.get(url)
        self.driver.wait_element(By.ID, 'bt-sort-episode', 5)
        res = bs(self.driver.get_source(), 'lxml').find('div', {'id': 'bt-sort-episode'}).find('a')
        res = res.get_attribute_list('data-sort')[0].split(',')
        res.remove('h0')
        return self.hyperlink(url, len(res))

    def webtoon_kakao(self, url):
        self.driver.shutdown()

        self.start_browser(proxy=FreeProxy().get())

        self.driver.get(url)
        self.driver.wait_element(By.CLASS_NAME, 'mx-11', 5)
        self.driver.scroll_page('mx-11')
        num = len(bs(self.driver.get_source(), 'lxml').find('div', {'class': 'mx-11'}).find('ul').find_all('li'))
        return self.hyperlink(url, num)

    def shonenmagazine(self, url):
        self.driver.get(url)
        time.sleep(5)
        self.driver.driver.execute_script('window.scrollBy(0, 1500);')
        self.driver.wait_element(By.CLASS_NAME, 'js-read-more-button', 5)
        self.driver.execute("document.getElementsByClassName('js-read-more-button')[0].click();")
        time.sleep(3)
        counter = 0
        for l in self.driver.execute("return document.getElementsByClassName('series-episode-list');"):
            counter += len(l.find_elements(By.TAG_NAME, 'li'))
        return self.hyperlink(url, counter)

    def ridibooks(self, url):
        self.driver.get(url)
        time.sleep(3)
        if self.driver.driver.current_url.startswith('https://ridibooks.com/account/login?'):
            self.driver.send_keys_to(By.ID, 'login_id', ACCOUNTS['ridibooks'][0])
            self.driver.send_keys_to(By.ID, 'login_pw', ACCOUNTS['ridibooks'][1])
            self.driver.execute("document.getElementsByClassName('account-checkbox')[0].click();")
            self.driver.execute("document.getElementsByClassName('login-button')[0].click();")
            time.sleep(5)
            self.driver.get(url)
        if self.driver.wait_element(By.CLASS_NAME, 'book_count', 5):
            num = self.driver.driver.find_element(By.CLASS_NAME, 'book_count').text.split()[1][:-1]
        else:
            num = '-'
        return self.hyperlink(url, num)

    def comico(self, url):
        self.driver.get(url)
        while not self.driver.wait_element(By.CLASS_NAME, 'btn_kakao', 1, by_driver=True) \
            and not self.driver.wait_element(By.CLASS_NAME, 'list_product', 1, by_driver=True):
            continue
        if not self.driver.check_element(By.CLASS_NAME, 'list_product', by_driver=True):
            if not self.login_comico():
                num = 'NEED LOGIN'
            else:
                self.driver.wait_element(By.CLASS_NAME, 'list_product', 10, by_driver=True)
                num = len(bs(self.driver.get_source(), 'lxml').find('ul', {'class': 'list_product'}).findAll('li'))
        else:
            self.driver.wait_element(By.CLASS_NAME, 'list_product', 10, by_driver=True)
            num = len(bs(self.driver.get_source(), 'lxml').find('ul', {'class': 'list_product'}).findAll('li'))
        return self.hyperlink(url, num)

    def login_comico(self):
        s1 = "document.getElementsByClassName('layer_foot')[0].getElementsByTagName('button')[1].click();"
        s2 = "document.getElementsByClassName('btn_kakao')[0].click();"
        self.driver.wait_element(By.CLASS_NAME, 'layer_foot', 15, by_driver=True)
        self.driver.execute(s1 + s2)
        time.sleep(15)
        while True:
            if self.driver.check_element(By.CLASS_NAME, 'list_product', by_driver=True): return True
            elif 'accounts.kakao.com' in self.driver.driver.current_url:
                self.driver.send_keys_to(By.ID, 'id_email_2_label', ACCOUNTS['kakao'][0])
                self.driver.send_keys_to(By.ID, 'id_password_3_label', ACCOUNTS['kakao'][1])
                self.driver.execute("document.getElementById('staySignedIn').click();")
                self.driver.execute("document.getElementsByClassName('btn_confirm submit btn_g')[0].click();")
                time.sleep(5)
                if 'accounts.kakao.com' in self.driver.driver.current_url: return False
                else: return True
            time.sleep(0.2)
