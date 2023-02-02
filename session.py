import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import ARGS_FOR_BROWSER, SESSION_PATH, PATH_TO_BROWSER


def main():
    options = Options()
    for arg in ARGS_FOR_BROWSER:
        options.add_argument(arg)

    options.add_argument('--user-data-dir=' + PATH_TO_BROWSER)
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"

    driver = webdriver.Chrome(options=options, desired_capabilities=capa)

    with open(SESSION_PATH, 'w') as out:
        out.write(json.dumps({'url': driver.command_executor._url, 'session_id': driver.session_id}))

    input('Нажмите Enter, чтобы завершить сессию...')

    with open(SESSION_PATH, 'w') as out:
        out.write(json.dumps({'url': None, 'session_id': None}))


if __name__ == '__main__':
    main()