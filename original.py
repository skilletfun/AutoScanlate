import asyncio
from typing import Union, Tuple

from logger import log
from sheet import Sheet
from config import RANGES
from fetching import Fetcher


async def fetch(fetcher: Fetcher, url: str, browser: bool=False) -> Tuple[int, Union[int, str]]:
    """ Запрашивает страницу и возвращает номер последней главы
    :param fetcher: объект, выполняющий запросы и обработку данных
    :param url: ссылка на главу
    :param browser: требуется ли для загрузки страницы браузер
    :return: кортеж из порядкового номера (для сортировки) и номера главы
    """
    return url[0], await fetcher.fetch(url[1], browser=browser)

@log
async def fill_original() -> None:
    """ Заполнение столбца Оригинал """
    fetcher = Fetcher()
    fetcher.start_browser(full_load=True)
    try:
        sheeter = Sheet()
        urls = sheeter.get_values('B4:B1000')[0]
        # Словарь с номерами глав, полученных без браузера
        original_dict = dict(await asyncio.gather(*[fetch(fetcher, url) for url in enumerate(urls)]))
        # Словарь с номерами глав, полученных через браузер
        br_original = await asyncio.gather(*[fetch(fetcher, url, browser=True) for url in enumerate(urls)])
        # Полный словарь
        original_dict.update(dict(filter(lambda x: x[1] != 'url error', br_original)))
        fetcher.shutdown_browser()

        webtoon_urls = [el for el in enumerate(urls) if el[1].startswith('https://webtoon.kakao.com')]
        webtoon_dict = {el[0]: fetcher.webtoon_kakao(el[1]) for el in webtoon_urls}
        original_dict.update(webtoon_dict)

        sheeter.write_values([[original_dict[k] for k in sorted(original_dict.keys())]], RANGES['original'])
    finally:
        fetcher.shutdown_browser()


if __name__ == '__main__':
    asyncio.run(fill_original())
