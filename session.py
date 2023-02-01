import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import ARGS_FOR_BROWSER

def start_session():
    options = Options()
    for arg in ARGS_FOR_BROWSER:
        options.add_argument(arg)
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(options=options, desired_capabilities=capa)
    with open('session.json', 'w') as out:
        out.write(json.dumps({'url': driver.command_executor._url, 'session_id': driver.session_id}))
    return driver

def close_session():
    with open('session.json') as inf:
        js = json.loads(inf.read())
        if js['url'] and js['session_id']:
            driver = webdriver.Remote(command_executor=js['url'])
            driver.close()
            driver.session_id = js['session_id']
            driver.close()
            driver.quit()
    with open('session.json', 'w') as out:
        out.write(json.dumps({'url': None, 'session_id': None}))


def main():
    driver = start_session()
    input('Нажмите Enter, чтобы завершить сессию...')
    close_session()
    exit(0)

if __name__ == '__main__':
    main()