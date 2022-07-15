from sheet import Sheet
from browser import Browser
from logger import Logger
from selenium.webdriver.common.by import By
from time import sleep
from config import RANGES


if __name__ == '__main__':
    log = Logger()
    log.log('Start parse Mangalib')
    sheeter = Sheet()
    urls = sheeter.get_values('D4:D1000')[0]
    driver = Browser(user=False)
    try:
        result_arr = []
        for url in urls:
            total_time = 5
            driver.get(url)
            while True:
                if driver.check_element(By.CLASS_NAME, 'media-chapter__name', by_driver=True):
                    chapter = driver.execute("return document.getElementsByClassName('media-chapter__name')[0].innerText;")
                    chapter_url = driver.execute("return document.getElementsByClassName('media-chapter__name')[0].children[0].href;")
                    if '-' in chapter:
                        chapter = chapter[:chapter.index('-')]
                    num = chapter.strip().split()[-1]
                    result_arr.append(f'=ГИПЕРССЫЛКА("{url}";"{num}")')
                    break
                elif driver.check_element(By.CLASS_NAME, 'paper empty section'):
                    result_arr.append(f'=ГИПЕРССЫЛКА("{url}";"-")')
                    break
                else:
                    total_time -= 0.2
                    if total_time < 0:
                        result_arr.append(f'=ГИПЕРССЫЛКА("{url}";"-")')
                        break
                    sleep(0.2)
                    continue
        sheeter.write_values([result_arr], RANGES['mangalib'])
    except Exception as e:
        log.error(e)
    finally:
        driver.shutdown()

