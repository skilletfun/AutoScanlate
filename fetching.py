import time
from bs4 import BeautifulSoup as bs
import requests as r
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from config import PATH_TO_BROWSER, HEADERS, ACCOUNTS, VK_API_TOKEN
import asyncio
import aiohttp
import aiovk


class Browser:
    def __init__(self):
        options = Options()
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument('--disable-extensions')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument("--user-data-dir=" + PATH_TO_BROWSER)
        self.driver = webdriver.Chrome(options=options)
        self.driver.switch_to.new_window('tab')
        self.max_wait = 15

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

    def execute(self, script):
        res = self.driver.execute_script(script)
        time.sleep(0.5)
        return res

    def check_element(self, by, value, by_driver=False):
        try:
            return self.driver.execute_script(self.CHECK_DICT[by] + f'("{value}");') if not by_driver else self.driver.find_element(by, value)
        except:
            return None

    def wait_element(self, by, value, value2=None, by_driver=False):
        self.max_wait = 30
        if self.check_element(by, value, by_driver=by_driver):
            return 1
        while self.max_wait > 0:
            if self.check_element(by, value, by_driver=by_driver):
                return 1
            if self.check_element(by, value2, by_driver=by_driver) if value2 else False:
                return 2
            time.sleep(0.1)
            self.max_wait -= 1
            if self.max_wait % 10 == 0: self.driver.refresh()
        return 3

    def get_source(self):
        return self.driver.page_source

    def send_keys_to(self, by, key, value):
        self.driver.find_element(by, key).send_keys(value)

    def shutdown(self):
        self.driver.close()
        self.driver.quit()


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
                'https://ridibooks.com': self.ridibooks,
                'https://vk.com': self.vk,
                'https://gaugau.futabanet.jp': self.futabanet,
                'https://mechacomic.jp': self.mechacomic,
                'https://www.tappytoon.com': self.tappytoon
            },
            'browser': {
                'https://manga.bilibili.com': self.bilibili,
                'https://www.bomtoon.com': self.bomtoon,
                'https://mangalib.org/': self.mangalib,
                'https://www.comico.kr': self.comico,
                'https://webtoon.kakao.com': self.webtoon_kakao,
                'https://remanga.org': self.remanga,
                'https://pocket.shonenmagazine.com': self.shonenmagazine,
                'https://mangalib.me/': self.mangalib,
            }
        }

    def logging(func):
        """ Decorator for logging. """
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print('Error in function: ' + func.__name__ + '\n', 'Values:\n', args, kwargs, '\nError:\n', e)
        return wrapper

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

    def start_browser(self):
        if self.driver:
            self.shutdown_browser()
        self.driver = Browser()

    def shutdown_browser(self):
        self.driver.shutdown()

    async def async_get_response(self, url):
        async with self.sem:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(url) as response:
                    self.tries = (self.tries - 1) if response.status != 200 else 5
                    return await response.text()

    @logging
    async def kakao(self, url):
        res = bs(await self.async_get_response(url), 'lxml').find('script', {'id': '__NEXT_DATA__'})
        return self.get_by_keys(res.text, ['props', 'initialState', 'series', 'series', 'onSaleCount'])

    @logging
    async def series_naver(self, url):
        return bs(await self.async_get_response(url), 'lxml').find('h5', {'class': 'end_total_episode'}).text.split()[1][:-1]

    @logging
    async def seiga_nicovideo(self, url):
        return len(bs(await self.async_get_response(url), 'lxml').find('div', {'id': 'episode_list'}).find('ul').find_all('li'))

    @logging
    async def web_ace(self, url):
        url = url + '/episode/' if url.endswith('/') else url + 'episode/'
        return len(bs(await self.async_get_response(url), 'lxml').find('ul', {'class': 'table-view'}).find_all('li'))

    @logging
    async def mechacomic(self, url):
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'p-search_chapterNo'})
        return res.findAll('div', {'class', 'u-inlineBlock'})[-1].getText().strip()[1:-2]

    @logging
    async def futabanet(self, url):
        from string import punctuation
        res = bs(await self.async_get_response(url), 'lxml').find('div', {'class': 'detail-ex__btn-item--latest'})
        res = ''.join([(el if el.isdigit() or el in punctuation else '') for el in res.getText().strip().split('\n')[1][1:]])
        check_breaket = lambda x: '.' if x == '(' else ''
        return ''.join([el if el.isdigit() else check_breaket(el) for el in res])

    @logging
    async def tappytoon(self, url):
        res = bs(await self.async_get_response(url), 'lxml').find('script', {'id': '__NEXT_DATA__'})
        arr = self.get_by_keys(res.text, ['props', 'initialState', 'entities', 'chapter'])
        for el in sorted(arr, lambda x: x['order'])[::-1]:
            if el['isPublished']:
                return el['order']

    @logging
    async def ridibooks(self, url):
        res = await self.async_get_response(url)
        tries = 5
        while tries > 0:
            tries -= 1
            try:
                return bs(res, 'lxml').find('p', {'class': 'metadata_info_series_complete_wrap'}).text.split()[1][:-4]
            except: pass

    @logging
    def bilibili(self, url):
        self.driver.get(url)
        self.driver.wait_element(By.CLASS_NAME, 'last-update')
        return self.driver.execute("return document.getElementsByClassName('last-update')[0].textContent;").split()[1]

    @logging
    def comico(self, url):
        self.driver.get(url)
        self.driver.wait_element(By.CLASS_NAME, 'btn_kakao', value2='list_product', by_driver=True)
        if not self.driver.check_element(By.CLASS_NAME, 'list_product', by_driver=True):
            if not self.login_comico():
                return 'NEED LOGIN'
        return len(bs(self.driver.get_source(), 'lxml').find('ul', {'class': 'list_product'}).findAll('li'))

    @logging
    def bomtoon(self, url):
        res = bs(self.driver.get(url), 'lxml').find('div', {'id': 'bt-sort-episode'}).find('a')
        res = res.get_attribute_list('data-sort')[0].split(',')
        res.remove('h0')
        return len(res)

    @logging
    def webtoon_kakao(self, url):
        self.driver.get(url)
        self.driver.scroll_page('mx-11')
        return len(bs(self.driver.get_source(), 'lxml').find('div', {'class': 'mx-11'}).find('ul').find_all('li'))

    @logging
    def remanga(self, url):
        payed, free, marketing, date = -1, -1, -1, -1
        total_payed = 0
        timer = 15
        self.driver.get(url.replace('?subpath=about', ''))
        if not self.driver.check_element(By.CLASS_NAME, 'MuiAvatar-root'):
            self.login_remanga()
            self.driver.get(url)
        while True:
            try:
                status = self.driver.execute(
                    "return document.getElementsByClassName('MuiButton-label')[2].textContent;")
                marketing = status.split()[-1] if 'Продвигается' in status or 'В очереди' in status else 'Продвижение'
                children = self.driver.execute("return document.getElementsByClassName('MuiGrid-grid-md-6')[0].lastChild.children;")[1:]
                children[0].find_element(By.CSS_SELECTOR, 'div:nth-child(3)')
                break
            except:
                time.sleep(0.1)
                timer -= 1
                if timer < 0:
                    timer = 15
                    self.driver.driver.refresh()

        for child in children:
            el = child.find_element(By.CSS_SELECTOR, 'div:nth-child(3)').get_attribute('innerHTML')[2:5]
            date = child.find_element(By.CSS_SELECTOR, 'a > div > span:nth-child(2)').get_attribute('innerHTML')
            header = child.find_element(By.CSS_SELECTOR, 'a > h6').text.split()[1]

            if el.startswith('v'):
                total_payed += 1
                if payed == -1: payed = header
            elif el.startswith('p'):
                free = header
                break

        return payed, free, total_payed, date, marketing

    @logging
    def mangalib(self, url):
        self.driver.get(url)
        flag = self.driver.wait_element(By.CLASS_NAME, 'media-chapter__name', value2='paper empty section')
        if flag == 2: return '-1'
        elif flag == 3: return '-'
        chapter = self.driver.execute("return document.getElementsByClassName('media-chapter__name')[0].innerText;")
        if '-' in chapter:
            chapter = chapter[:chapter.index('-')]
        return chapter.strip().split()[-1]

    @logging
    def shonenmagazine(self, url):
        self.driver.get(url)
        self.driver.driver.execute_script('window.scrollBy(0, 1500);')
        self.driver.wait_element(By.CLASS_NAME, 'js-read-more-button')
        self.driver.execute("document.getElementsByClassName('js-read-more-button')[0].click();")
        time.sleep(3)
        counter = 0
        for l in self.driver.execute("return document.getElementsByClassName('series-episode-list');"):
            counter += len(l.find_elements(By.TAG_NAME, 'li'))
        return counter

    @logging
    async def vk(self, url):
        payed, free = -1, -1
        group_id, topic_id = url.split('-')[-1].split('_')
        async with self.sem:
            async with aiovk.TokenSession(access_token=VK_API_TOKEN) as ses:
                res = await aiovk.API(ses).board.getComments(group_id=group_id, topic_id=topic_id)
                res = '\n'.join([el['text'] for el in res['items']])
                for p in res.split('\n')[::-1]:
                    p = p.lower()
                    if len(p) > 10 and 'пончик' in p and payed == -1:
                        payed = p.split()[0] if 'сезон' not in p else p.split()[3]
                    elif len(p) > 10 and 'пончик' not in p:
                        free = p.split()[0] if 'сезон' not in p else p.split()[3]
                        break
        return payed, free

    @logging
    def login_remanga(self):
        self.driver.get('https://remanga.org')
        self.driver.execute("document.getElementsByClassName('MuiButtonBase-root')[7].click();")
        self.driver.send_keys_to(By.ID, 'login', ACCOUNTS['ramanga'][0])
        self.driver.send_keys_to(By.ID, 'password', ACCOUNTS['ramanga'][1])
        self.driver.execute(
            "document.getElementsByClassName('MuiButton-containedPrimary MuiButton-containedSizeLarge')[0].click();")
        time.sleep(3)

    @logging
    def login_comico(self):
        s1 = "document.getElementsByClassName('layer_foot')[0].getElementsByTagName('button')[1].click();"
        s2 = "document.getElementsByClassName('btn_kakao')[0].click();"
        self.driver.wait_element(By.CLASS_NAME, 'layer_foot', by_driver=True)
        self.driver.execute(s1 + s2)
        while True:
            if self.driver.check_element(By.CLASS_NAME, 'list_product', by_driver=True): return True
            elif 'accounts.kakao.com' in self.driver.driver.current_url: return False
            time.sleep(0.2)
