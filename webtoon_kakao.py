import time

from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By

from logger import log
from browser import Browser


@log
def scroll_page(driver: Browser) -> None:
    """ Прокручивает страницу до самого нижнего элемента. """
    old_count, count = 0, -1
    script1 = f"document.getElementsByClassName('mx-11')[0].getElementsByTagName('ul')[0].lastChild.scrollIntoView();"
    script2 = f"return document.getElementsByClassName('mx-11')[0].getElementsByTagName('ul')[0].childElementCount;"
    # Прокручиваем до тех пор, пока точно не убедимся, что больше элементов нет
    while old_count != count or old_count <= 0:
        try:
            old_count = count
            driver.execute(script1)
            time.sleep(5)
            count = driver.execute(script2)
        except:
            pass

@log
def main(url: str) -> str:
    driver = Browser(user=True, full_load=True, extensions=True)
    try:
        driver.get(url)
        driver.wait_element(By.CLASS_NAME, 'mx-11', 20)
        scroll_page(driver)
        num = len(bs(driver.get_source(), 'lxml').find('div', {'class': 'mx-11'}).find('ul').find_all('li'))
        return f'=ГИПЕРССЫЛКА("{url}";"{num}")'
    except Exception as e:
        raise e
    finally:
        driver.shutdown()


if __name__ == '__main__':
    main()
