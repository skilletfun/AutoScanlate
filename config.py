# Установить значение False, если продакшн
# При True запись в таблицу происходить не будет, результат будет выводиться в консоль
DEBUG = True

# Диапазоны данных в таблице для записи результата парсинга
# Если данные не на первом листе, то указать сначала название листа с воскл. знаком (Лист!А1:А1000)
RANGES = {
    'original': 'G4:G1000',
    'remanga': 'H4:L1000',
    'mangalib': 'L4:L1000',
    'vk': 'O4:P1000',
    'drive': 'S4:Y1000',
}

# Диапазоны исходных данных в таблице (названия, ссылки, жанры)
# Если данные не на первом листе, то указать сначала название листа с воскл. знаком (Лист!А1:А1000)
SOURCE_RANGES = {
    'names': 'A4:A1000',
    'original': 'B4:B1000',
    'remanga': 'C4:C1000',
    'mangalib': 'D4:D1000',
    'vk': 'E4:E1000',
    'genres': 'S4:S1000',
    'tests': 'TestData!A1:A999'
}

# Токен вк для парсинга обсуждений в группе
VK_API_TOKEN = ''

# Путь до браузерной папки User Data
PATH_TO_BROWSER = 'C:\\Users\\User\\AppData\\Local\\Chromium\\User Data'

# ID Google-таблицы
SHEET_ID = ''

# Путь до файла с сессией браузера
SESSION_PATH = '../session.json'

# Максимальное количество запросов к Google-диску в секунду
# При значении выше плюс минус 30 Google сбрасывает соединение
DRIVE_FETCH_LIMIT = 15

# Название и ID Google-папок с жанрами, по которым будет происходить поиск
DRIVE_SCOPES = {
    'folder_name_1': 'folder_id_1',
    'folder_name_2': 'folder_id_2',
    'folder_name_3': 'folder_id_3',
    'folder_name_4': 'folder_id_4'
}

# ID полей окна авторизации Kakao
KAKAO_LOGIN_FIELDS_ID = {
    'login': 'input-loginKey',
    'password': 'input-password',
    'staySigned': 'ico_check',
    'buttonLogin': 'btn_g highlight'
}

# Кастомные заголовки
HEADERS = {
    "Connection": "keep-alive",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}

# С какими параметрами будет запущена сессия
ARGS_FOR_BROWSER = [
    '--disable-features=VizDisplayCompositor',
    '--blink-settings=imagesEnabled=false',
    '--ignore-certificate-errors-spki-list'
]
