from time import sleep

from selenium.webdriver.common.by import By

from sheet import Sheet
from browser import Browser
from logger import log
from config import RANGES, SOURCE_RANGES
from helper_funcs import connect_to_browser


@log
def get_chapter(driver: Browser) -> str:
    """ Возвращает номер последней загруженной на сайт главы. """
    total_time = 5
    while True:
        try:
            chapter = driver.execute("return document.getElementsByClassName('media-chapter__name')[0].innerText;")
            if '-' in chapter:
                chapter = chapter[:chapter.index('-')]
            return chapter.strip().split()[-1]
        except:
            total_time -= 0.1
            if total_time < 0:
                return 'TIME EXCEEDED'
            sleep(0.1)

@log
def load_url(driver: Browser, url: str) -> str:
    """ Возвращает номер последней загруженной на сайт главы, если она есть.
     В противном случае возвращает прочерк.
     Максимум секунд на прогрузку страницы - total_time
     """
    total_time = 5
    driver.get(url.replace('mangalib.me', 'mangalib.org'))  # Потому что к .me - access denied
    while True:
        if driver.check_element(By.CLASS_NAME, 'media-chapter__name', max_wait=5, by_driver=True):
            return f'=ГИПЕРССЫЛКА("{url}";"{get_chapter(driver)}")'
        elif driver.check_element(By.CLASS_NAME, 'paper empty section'):
            return f'=ГИПЕРССЫЛКА("{url}";"-")'
        else:
            total_time -= 0.2
            if total_time < 0:
                return f'=ГИПЕРССЫЛКА("{url}";"-")'
            sleep(0.2)

@log
def main():
    with connect_to_browser() as driver:
        sheeter = Sheet()
        result_arr = [load_url(driver, url) for url in sheeter.get_values(SOURCE_RANGES['mangalib'])[0]]
        sheeter.write_values([result_arr], RANGES['mangalib'])


if __name__ == '__main__':
    main()
