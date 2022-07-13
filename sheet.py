import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, RANGES

class Sheet:
    CREDENTIALS_FILE = 'creds.json'

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)

    def get_values(self):
        urls = self.service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='B1:E1000',
            majorDimension='COLUMNS'
        ).execute()
        return [el[3:] for el in urls['values']]

    def get_names_with_genres(self):
        values = self.service.spreadsheets().values().batchGet(
            spreadsheetId=SHEET_ID,
            ranges=RANGES['names'],
            majorDimension='COLUMNS'
        ).execute()
        return list(zip(values['valueRanges'][0]['values'][0],values['valueRanges'][1]['values'][0]))

    def write_values(self, data, drange, dimension='COLUMNS'):
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": drange,
                     "majorDimension": dimension,
                     "values": data},
                ]
            }
        ).execute()

