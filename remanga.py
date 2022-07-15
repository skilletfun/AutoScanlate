from sheet import Sheet
from browser import Browser
from logger import Logger
from selenium.webdriver.common.by import By
from time import sleep
from config import RANGES, ACCOUNTS
import time


def login_remanga(driver):
    driver.get('https://remanga.org')
    driver.execute("document.getElementsByClassName('MuiButtonBase-root')[7].click();")
    driver.send_keys_to(By.ID, 'login', ACCOUNTS['ramanga'][0])
    driver.send_keys_to(By.ID, 'password', ACCOUNTS['ramanga'][1])
    driver.execute(
        "document.getElementsByClassName('MuiButton-containedPrimary MuiButton-containedSizeLarge')[0].click();")
    time.sleep(3)

def wait(driver):
    timer = 30
    tries = 5
    while True:
        try:
            status = driver.execute("return document.getElementsByClassName('MuiButton-label')[2].textContent;")
            marketing = status.split()[-1] if 'Продвигается' in status or 'В очереди' in status else 'Продвижение'
            children = driver.execute("return document.getElementsByClassName('MuiGrid-grid-md-6')[0].lastChild.children;")[1:]
            children[0].find_element(By.CSS_SELECTOR, 'div:nth-child(3)')
            break
        except:
            time.sleep(0.1)
            timer -= 1
            if timer < 0:
                timer = 30
                tries -= 1
                if tries < 0:
                    return '-', '-', []
                driver.driver.refresh()
    return status, marketing, children

if __name__ == '__main__':
    log = Logger()
    log.log('Start parse Remanga')
    sheeter = Sheet()
    urls = sheeter.get_values('C4:C1000')[0]
    driver = Browser(full_load=True)
    try:
        result_arr = []
        for url in urls:
            payed, free, marketing, date = -1, -1, -1, -1
            total_payed = 0

            driver.get(url.replace('?subpath=about', ''))

            if not driver.check_element(By.CLASS_NAME, 'MuiAvatar-root'):
                login_remanga(driver)
                driver.get(url)

            status, marketing, children = wait(driver)

            for child in children:
                el = child.find_element(By.CSS_SELECTOR, 'div:nth-child(3)').get_attribute('innerHTML')[2:5]
                date = child.find_element(By.CSS_SELECTOR, 'a > div > span:nth-child(2)').get_attribute('innerHTML')
                header = child.find_element(By.CSS_SELECTOR, 'a > h6').text.split()[1]

                if el.startswith('v'):
                    total_payed += 1
                    if payed == -1: payed = f'=ГИПЕРССЫЛКА("{url}";"{header}")'
                elif el.startswith('p'):
                    free = f'=ГИПЕРССЫЛКА("{url}";"{header}")'
                    break
            result_arr.append([payed, free, total_payed, date, marketing])
        sheeter.write_values(result_arr, RANGES['remanga'], dimension='ROWS')
    except Exception as e:
        log.error(e)
    finally:
        driver.shutdown()
