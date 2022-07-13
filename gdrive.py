import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from config import DRIVE_ID
import asyncio


class Drive:
    CREDENTIALS_FILE = 'creds.json'
    SCOPES = {
        'Сёдзе': '1pYp-eYB1HDhKgMB8EjQ_xCH_EaNFe5-62zlPRoGvH_AXmnMVXqyrz4u5sLLsNnjhL0wnut5j',
        'Сёнэн': '1GQNgefS6_YXrvPRzBCcKlpHHR9Jrmr019rFZHzO6NAm_LyA9IC-g1ZCmpyfXqCnQG0NO3-Hv'
    }
    TYPES = ['Перевод', 'Редакт', 'Клин', 'Тайп', 'Эдит', 'Звуки', 'Бета', 'Сканы']

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE, ['https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = googleapiclient.discovery.build('drive', 'v3', http=httpAuth)

    def logging(func):
        """ Decorator for logging. """

        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print('Error in function: ' + func.__name__ + '\n', 'Values:\n', args, kwargs, '\nError:\n', e)

        return wrapper

    @logging
    async def get_files(self, part, genre):
        q_filter_parent = f"mimeType = 'application/vnd.google-apps.folder' and name contains '{part}' and '{self.SCOPES[genre]}' in parents"
        parent = self.service.files().list(fields="files(id)", q=q_filter_parent).execute()['files']
        if len(parent) > 0:
            parent = parent[0]['id']
        else:
            return '-','-','-','-','-','-','-',
        q_filter = f"mimeType = 'application/vnd.google-apps.folder' and '{parent}' in parents"
        folders = self.service.files().list(fields="files(id, name)", q=q_filter).execute()['files']
        result = {}
        for el in self.TYPES:
            for folder in folders:
                if folder['name'].startswith(el):
                    result[el] = await self.get_last_file(folder['id'])
                    break
            else: result[el] = '-'
        if result['Эдит'] != '-':
            result['Тайп'] = result['Эдит']
        return [result[el] for el in self.TYPES[:4] + self.TYPES[5:]]

    @logging
    async def get_last_file(self, folder_id):
        q_filter = f"mimeType != 'application/vnd.google-apps.folder' and '{folder_id}' in parents"
        files = self.service.files().list(fields="files(name)", q=q_filter).execute()['files']
        nums = []
        for file in files:
            try:
                num = file['name'].split('.')[0]
                if num.find('-') > 0:
                    num = num[num.find('-'):].split()
                else:
                    num = num.split()
                for el in num:
                    if el.isdigit():
                        nums.append(int(el))
                else:
                    nums.append(0)
            except Exception as e:
                print(file['name'])
                print(e)
        return str(sorted(nums)[-1]) if len(nums) > 0 else '-'
