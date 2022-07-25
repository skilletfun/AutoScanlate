ACCOUNTS = {
    'remanga': ('login', 'pass'),
    'kakao': ('login', 'pass'),
    'ridibooks': ('login', 'pass')
}

RANGES = {
    'original': 'F4:F1000',
    'remanga': 'G4:K1000',
    'mangalib': 'L4:L1000',
    'vk': 'O4:P1000',
    'drive': 'S4:Y1000',
    'names': ['A4:A1000', 'R4:R1000']
}

COLUMN_NAMES = {
    'vk': ('ВК (Платка)', 'ВК (Бесплатка)'),
    'drive': ('Drive (Перевод)', 'Drive (Редакт)', 'Drive (Клин)',
              'Drive (Тайп)', 'Drive (Звуки)', 'Drive (Бета)', 'Drive (Сканы)'
    ),
    'mangalib': ('Мангалиб',)
}

VK_API_TOKEN = ''

PATH_TO_BROWSER = ''

SHEET_ID = ''

DRIVE_FETCH_LIMIT = 30

HEADERS = {
    "Connection": "keep-alive",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}
