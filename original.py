import asyncio
from typing import Union, Tuple

from buyer import buy
from logger import log
from sheet import Sheet
from fetching import Fetcher
from browser import Browser
from config import RANGES, SOURCE_RANGES
from helper_funcs import login_all, titles_for_download


async def fetch(fetcher: Fetcher, url: Tuple[int, str], browser: Browser=None) -> Tuple[int, Union[int, str]]:
    """ Запрашивает страницу и возвращает номер последней главы
    :param fetcher: объект, выполняющий запросы и обработку данных
    :param url: ссылка на главу
    :param browser: браузер
    :return: кортеж из порядкового номера (для сортировки) и номера главы
    """
    return url[0], await fetcher.fetch(url[1], browser=browser)

@log
async def fill_original(urls: list[str]) -> None:
    """ Заполнение столбца Оригинал """
    fetcher = Fetcher()
    original_dict = dict(await asyncio.gather(*[fetch(fetcher, url) for url in enumerate(urls)]))

    with Browser(full_load=True) as driver:
        login_all(driver)
        br_original = await asyncio.gather(*[fetch(fetcher, url, browser=driver) for url in enumerate(urls)])

    original_dict.update(dict(filter(lambda x: x[1] != 'url error', br_original)))

    webtoon_urls = [el for el in enumerate(urls) if el[1].startswith('https://webtoon.kakao.com')]
    webtoon_dict = {el[0]: fetcher.webtoon_kakao(el[1]) for el in webtoon_urls}

    original_dict.update(webtoon_dict)
    return [original_dict[k] if type(original_dict[k]) is str else '-' for k in sorted(original_dict.keys())]

@log
async def main():
    sheeter = Sheet()
    urls = sheeter.get_values(SOURCE_RANGES['original'])[0]
    await fill_original(urls)
    sheeter.write_values(
        [result_arr],
        RANGES['original']
    )
    buy(titles_for_download(sheeter.get_values(RANGES['original'])[0], result_arr))


if __name__ == '__main__':
    asyncio.run(main())
