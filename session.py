import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import ARGS_FOR_BROWSER


def main():
    options = Options()
    for arg in ARGS_FOR_BROWSER:
        options.add_argument(arg)

    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"

    driver = webdriver.Chrome(options=options, desired_capabilities=capa)

    with open('session.json', 'w') as out:
        out.write(json.dumps({'url': driver.command_executor._url, 'session_id': driver.session_id}))

    input('Нажмите Enter, чтобы завершить сессию...')

    with open('session.json', 'w') as out:
        out.write(json.dumps({'url': None, 'session_id': None}))

    exit(0)

if __name__ == '__main__':
    main()