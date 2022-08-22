import time

from selenium.webdriver.common.by import By

from sheet import Sheet
from browser import Browser
from logger import log
from config import RANGES, ACCOUNTS


@log
def login_remanga(driver: Browser) -> None:
    """ Вход в аккаунт Реманги.
    :param driver: объект браузера
    """
    driver.get('https://remanga.org')
    time.sleep(5)
    driver.execute("document.getElementsByClassName('MuiButtonBase-root')[7].click();")
    time.sleep(3)
    driver.send_keys_to(By.ID, 'login', ACCOUNTS['remanga'][0])
    driver.send_keys_to(By.ID, 'password', ACCOUNTS['remanga'][1])
    driver.execute(
        "document.getElementsByClassName('MuiButton-containedPrimary MuiButton-containedSizeLarge')[0].click();")
    time.sleep(5)

@log
def wait(driver: Browser) -> (str, list):
    """ Загружает страницу, пока не появятся необходимые элементы.
    :param driver: объект браузера
    :return: возвращает данные для столбца Реклама и список глав
    """
    timer, tries = 30, 5
    while True:
        try:
            # Если тайтл не принадлежит аккаунту, то вернется текст Читать / Прочитано / Продолжить
            status = driver.execute("return document.getElementsByClassName('MuiButton-label')[2].textContent;")
            if 'Продвигается' in status or 'В очереди' in status:
                marketing = status.split()[-1]
            elif 'Продвижение' in status:
                marketing = 'Продвижение'
            elif 'Нет глав' in status:
                return '-', []
            else:
                marketing = '-'
            children = driver.execute("return document.getElementsByClassName('MuiGrid-grid-md-6')[0].lastChild.children;")[1:]
            children[0].find_element(By.CSS_SELECTOR, 'div:nth-child(3)')
            break
        except:
            time.sleep(0.1)
            timer -= 1
            if timer < 0:
                timer, tries = 30, tries-1
                if tries < 0: return '-', []
                driver.driver.refresh()
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
                payed, free, marketing, date = '-', '-', '-', '-'
                total_payed = 0

                driver.get(url)

                marketing, children = wait(driver)
                for child in children:
                    # Возвращает кусок текста, по которому точно можно сказать, платная или бесплатная глава
                    el = child.find_element(By.CSS_SELECTOR, 'div:nth-child(3)').get_attribute('innerHTML')[2:5]
                    # Дата главы
                    if date == '-':
                        date = child.find_element(By.CSS_SELECTOR, 'a > div > span:nth-child(2)').get_attribute('innerHTML')
                    # Номер главы
                    num = child.find_element(By.CSS_SELECTOR, 'a > h6').text.split()[1]

                    if el.startswith('v'):
                        total_payed += 1
                        if payed == '-': payed = f'=ГИПЕРССЫЛКА("{url}";"{num}")'
                    elif el.startswith('p'):
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
