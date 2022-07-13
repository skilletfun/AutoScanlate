import time
from fetching import Fetcher
from sheet import Sheet
import asyncio
from config import RANGES
from gdrive import Drive
from datetime import datetime


SORT_DATA = lambda data_list: [str(el[1]) if not type(el[1]) is tuple else list(map(str, el[1])) for el in sorted(data_list, key=lambda x: x[0])]

async def fill(fetcher, url, browser=False):
    return url[0], await fetcher.fetch(url[1], browser=browser)

async def fill_original():
    """ Заполнение столбца Оригинал """
    sheeter = Sheet()
    urls = sheeter.get_values()
    fetcher = Fetcher()
    original_dict = dict(await asyncio.gather(*[fill(fetcher, url) for url in enumerate(urls[0])]))
    fetcher.start_browser()
    br_original = await asyncio.gather(*[fill(fetcher, url, browser=True) for url in enumerate(urls[0])])
    original_dict.update(dict(filter(lambda x: x[1] != 'URL error', br_original)))
    fetcher.shutdown_browser()
    sheeter.write_values([[original_dict[k] for k in sorted(original_dict.keys())]], RANGES['original'])

async def fill_remanga():
    """ Заполнение столбцов Реманги
    Столбцы идут: Платка, бесплатка, количество платок, дата, реклама
    """
    sheeter = Sheet()
    urls = sheeter.get_values()
    fetcher = Fetcher()
    fetcher.start_browser()
    remanga_list = SORT_DATA(await asyncio.gather(*[fill(fetcher, url, browser=True) for url in enumerate(urls[1])]))
    fetcher.shutdown_browser()
    sheeter.write_values(remanga_list, RANGES['remanga'], dimension='ROWS')

async def fill_vk():
    """ Заполнение столбцов Группы ВК
    Столбцы идут: Платки, бесплатки
    """
    sheeter = Sheet()
    urls = sheeter.get_values()
    fetcher = Fetcher()
    vk_list = await asyncio.gather(*[fill(fetcher, url) for url in enumerate(urls[3])])
    vk_list = SORT_DATA(vk_list)
    sheeter.write_values([[el[0] for el in vk_list], [el[1] for el in vk_list]], RANGES['vk'])

async def fill_mangalib():
    """ Заполнение столбца Мангалиб """
    sheeter = Sheet()
    urls = sheeter.get_values()
    fetcher = Fetcher()
    fetcher.start_browser()
    mangalib_list = await asyncio.gather(*[fill(fetcher, url, browser=True) for url in enumerate(urls[2])])
    fetcher.shutdown_browser()
    sheeter.write_values([SORT_DATA(mangalib_list)], RANGES['mangalib'])

async def fill_drive():
    """ Заполнение столбцов Гугл диска """
    sheeter = Sheet()
    drive = Drive()
    names = sheeter.get_names_with_genres()
    drive_list = await asyncio.gather(*[drive.get_files(el[0], el[1]) for el in names])
    sheeter.write_values(drive_list, RANGES['drive'], dimension='ROWS')

if __name__ == '__main__':
    while True:
        try:
            if datetime.now().hour == 18:
                asyncio.run(fill_original())
            elif datetime.now().hour in [0, 5, 15, 21]:
                asyncio.run(fill_remanga())
                asyncio.run(fill_mangalib())
                asyncio.run(fill_vk())
            asyncio.run(fill_drive())
            time.sleep(3600)
        except Exception as e:
            print(e)
