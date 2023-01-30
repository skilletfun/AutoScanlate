from typing import List

import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from config import SHEET_ID, SOURCE_RANGES, DEBUG


class Sheet:
    CREDENTIALS_FILE = 'creds.json'

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE,
            'https://www.googleapis.com/auth/spreadsheets')
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)

    def get_values(self, out_range: str, dimension:str='COLUMNS') -> List[List[str]]:
        """ Возвращает данные из таблицы
        :param out_range: диапазон данных
        :param dimension: брать по столбцам или строкам
        :return: данные из таблицы
        """
        urls = self.service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=out_range,
            majorDimension=dimension
        ).execute()
        return urls['values']

    def get_names_with_genres(self) -> List[List[str]]:
        """ Возвращает из таблицы названия тайтлов и их жанр. """
        values = self.service.spreadsheets().values().batchGet(
            spreadsheetId=SHEET_ID,
            ranges=[SOURCE_RANGES['names'], SOURCE_RANGES['genres']],
            majorDimension='COLUMNS'
        ).execute()
        return list(zip(values['valueRanges'][0]['values'][0],values['valueRanges'][1]['values'][0]))

    def write_values(self, data: list, input_range: str, dimension: str='COLUMNS') -> None:
        """ Пишет в таблицу данные
        :param data: данные
        :param input_range: диапазон, в который будет произведена вставка
        :param dimension: каким образом вставлять данные (столбцы / строки) ['COLUMNS', 'ROWS']
        """
        if DEBUG:
            print(*data, sep='\n')
        else:
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        {"range": input_range,
                         "majorDimension": dimension,
                         "values": data},
                    ]
                }
            ).execute()
