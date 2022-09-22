# Аккаунты, которые будут использоваться в работе
ACCOUNTS = {
    'remanga': ('login', 'pass'),
    'kakao': ('login', 'pass'),
    'ridibooks': ('login', 'pass')
}

# Диапазоны данных в таблице (для записи)
RANGES = {
    'original': 'F4:F1000',
    'remanga': 'G4:K1000',
    'mangalib': 'L4:L1000',
    'vk': 'O4:P1000',
    'drive': 'S4:Y1000',
    'names': ['A4:A1000', 'R4:R1000']
}

# Токен вк для парсинга обсуждений группы
VK_API_TOKEN = ''

# Путь до браузерной папки User data
PATH_TO_BROWSER = ''

# ID таблицы
SHEET_ID = ''

# Максимальное количество запросов к диску в секунду
DRIVE_FETCH_LIMIT = 30

# Название и ID гугл-папок, по которым будет происходить поиск
DRIVE_SCOPES = {
    'folder1': 'id1',
    'folder2': 'id2',
    'folder3': 'id3'
}

# ID полей окна авторизации Kakao
KAKAO_LOGIN_FILEDS_ID = {
    'login': 'id_email_2', # новый - input-loginKey
    'password': 'id_password_3' # новый - input-password
}

# Кастомные заголовки
HEADERS = {
    "Connection": "keep-alive",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}
