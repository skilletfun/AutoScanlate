# Установить значение False, если продакшн
# При True запись в таблицу происходить не будет, результат будет выводиться в консоль
DEBUG = True

# Аккаунты, которые будут использоваться в работе
ACCOUNTS = {
    'kakao': ('login', 'pass'),
    'ridibooks': ('login', 'pass')
}

# В какие аккаунты потребуется авторизация (True - требуется, False - не требуется)
LOGIN_TO = {
    'KAKAO': True,
    'RIDIBOOKS': True,
    'COMICO': True
}

# Диапазоны данных в таблице для записи
RANGES = {
    'original': 'F4:F1000',
    'remanga': 'H4:L1000',
    'mangalib': 'L4:L1000',
    'vk': 'O4:P1000',
    'drive': 'S4:Y1000',
}

# Диапазоны исходных даных в таблице
SOURCE_RANGES = {
    'names': 'A4:A1000',
    'original': 'B4:B1000',
    'remanga': 'C4:C1000',
    'mangalib': 'D4:D1000',
    'vk': 'E4:E1000',
    'genres': 'S4:S1000'
}

# Токен вк для парсинга обсуждений группы
VK_API_TOKEN = ''

# Путь до браузерной папки User data
PATH_TO_BROWSER = 'C:\\Users\\Sergey\\AppData\\Local\\Chromium\\User Data'

# ID таблицы
SHEET_ID = '1pHLEf1qmTpZxxqZFW4xBPgopdHWzzR_R6fSl7bkyHp0'

# Максимальное количество запросов к диску в секунду
DRIVE_FETCH_LIMIT = 30

# Название и ID гугл-папок, по которым будет происходить поиск
DRIVE_SCOPES = {
    'folder1': 'id1',
    'folder2': 'id2',
    'folder3': 'id3'
}

# ID полей окна авторизации Kakao
KAKAO_LOGIN_FIELDS_ID = {
    'login': 'id_email_2',          # новый - input-loginKey
    'password': 'id_password_3',    # новый - input-password
    'staySigned': 'staySignedIn',   # новый - ico_check
    'buttonLogin': 'btn_confirm submit btn_g'   # новый - btn_g highlight
}

# Кастомные заголовки
HEADERS = {
    "Connection": "keep-alive",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}
