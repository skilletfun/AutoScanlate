import time
from typing import Tuple

from selenium.webdriver.common.by import By

from sheet import Sheet
from browser import Browser
from logger import log
from config import RANGES


@log
def wait(driver: Browser) -> Tuple[str, list]:
    """ Загружает страницу, пока не появятся необходимые элементы.
    :param driver: объект браузера
    :return: возвращает данные для столбца Реклама и список глав
    """
    timer, tries = 30, 5
    marketing = '-'
    children = []

    while True:
        try:
            # Если тайтл не принадлежит аккаунту, то вернется текст Читать / Прочитано / Продолжить
            status = driver.execute("return document.getElementsByClassName('Button_label__py8bK')[1].textContent;")
            # Если элемент существует, то True, если не существует False
            if status:
                if 'Продвигается' in status or 'В очереди' in status:
                    marketing = status.split()[-1]
                elif 'Продвижение' in status:
                    marketing = 'Продвижение'

            flag_chapters_count = driver.execute("return document.getElementsByClassName('Tabs_flexContainer__Zbnn6')[0].children[1].textContent;")
            if flag_chapters_count and not flag_chapters_count.endswith('(0)'):
                # Возвращает список элементов-глав, откуда будут вытащены параметры глав для таблицы
                while not children:
                    children = driver.execute("return document.getElementsByClassName('Chapters_container__G5BYo')[1].children;")
            break
        except:
            time.sleep(0.1)
            timer -= 1
            if timer < 0:
                timer, tries = 30, tries-1
                if tries < 0: return '-', []
                driver.refresh()
    return marketing, children

@log
def main():
    sheeter = Sheet()
    urls = sheeter.get_values('C4:C1000')[0]
    driver = Browser(full_load=True)

    try:
        result_arr = []
        for url in urls:
            if url.startswith('http'):
                url = url.replace('?subpath=about', '')
                url = url.replace('?subpath=content', '')
                if not url.endswith('?p=content'):
                    url += '?p=content'

                payed = free = date = '-'   # Платка, бесплатка и дата для таблицы
                total_payed = 0             # Всего платок для таблицы

                driver.get(url)
                time.sleep(1)
                marketing, children = wait(driver)

                for child in children:
                    # True если платная, False если бесплатная
                    chapter_type_flag = driver.execute("return arguments[0].getElementsByTagName('svg')[0].hasAttribute('aria-label');", arg=child)
                    # Дата главы
                    if date == '-':
                        date = driver.execute("return arguments[0].getElementsByTagName('p')[1].textContent;", arg=child).replace('/', '.')
                    # Номер главы
                    num = driver.execute("return arguments[0].getElementsByTagName('p')[0].textContent;", arg=child).split()[1]

                    if chapter_type_flag:
                        total_payed += 1
                        if payed == '-':
                            payed = f'=ГИПЕРССЫЛКА("{url}";"{num}")'
                    else:
                        free = f'=ГИПЕРССЫЛКА("{url}";"{num}")'
                        break
                result_arr.append([payed, free, total_payed, date, marketing])
            else:
                result_arr.append(['-', '-', '-', '-', '-'])
        sheeter.write_values(result_arr, RANGES['remanga'], dimension='ROWS')
    except Exception as e:
        raise e
    finally:
        driver.shutdown()

if __name__ == '__main__':
    main()
