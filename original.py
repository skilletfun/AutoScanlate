import time
from fetching import Fetcher
from sheet import Sheet
import asyncio
from config import RANGES
from logger import Logger


async def fill(fetcher, url, browser=False):
    return url[0], await fetcher.fetch(url[1], browser=browser)

async def fill_original():
    """ Заполнение столбца Оригинал """
    fetcher = Fetcher()
    fetcher.start_browser()
    try:
        sheeter = Sheet()
        urls = sheeter.get_values()
        original_dict = dict(await asyncio.gather(*[fill(fetcher, url) for url in enumerate(urls[0])]))
        br_original = await asyncio.gather(*[fill(fetcher, url, browser=True) for url in enumerate(urls[0])])
        original_dict.update(dict(filter(lambda x: x[1] != 'URL error', br_original)))
        sheeter.write_values([[original_dict[k] for k in sorted(original_dict.keys())]], RANGES['original'])
    finally:
        fetcher.shutdown_browser()


if __name__ == '__main__':
    log = Logger()
    log.log('Start parse Original')
    try:
        asyncio.run(fill_original())
    except Exception as e:
        log.error(e)
