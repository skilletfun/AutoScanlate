import httplib2
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from config import DRIVE_ID
import asyncio
from sheet import Sheet
from logger import log
import json
from config import RANGES,DRIVE_FETCH_LIMIT


class Drive:
    CREDENTIALS_FILE = 'creds.json'
    SCOPES = {
        'Сёдзе': '1pYp-eYB1HDhKgMB8EjQ_xCH_EaNFe5-62zlPRoGvH_AXmnMVXqyrz4u5sLLsNnjhL0wnut5j',
        'Сёнэн': '1GQNgefS6_YXrvPRzBCcKlpHHR9Jrmr019rFZHzO6NAm_LyA9IC-g1ZCmpyfXqCnQG0NO3-Hv'
    }
    TYPES = ['Перевод', 'Редакт', 'Клин', 'Тайп', 'Эдит', 'Звуки', 'Бета', 'Сканы']

    def __init__(self):
        self.sem = asyncio.Semaphore(20)

    async def get_creds(self):
        service_account_key = json.load(open('creds.json'))
        return ServiceAccountCreds(
            scopes=['https://www.googleapis.com/auth/drive'],
            **service_account_key
        )

    @log
    async def parse(self, names):
        async with Aiogoogle(service_account_creds=await self.get_creds()) as aiog:
            async with asyncio.Semaphore(DRIVE_FETCH_LIMIT):
                return await asyncio.gather(*[self.get_files(aiog, el[0], el[1]) for el in names])

    async def get_files(self, aiog, title, genre) -> list[list[str], ...]:
        """ Пробегается по папкам с тайтлами
        :param aiog: объект, выполняющий запросы
        :param title: название тайтла
        :param genre: жанр тайтла
        :return: список со строками (ROWS) для гугл-таблицы
        """
        service = await aiog.discover("drive", "v3")
        q_parent = f"mimeType = 'application/vnd.google-apps.folder' and name contains '{title}' and '{self.SCOPES[genre]}' in parents"
        # Запрос 1, возвращает id папки с тайтлом
        parent = (await aiog.as_service_account(service.files.list(fields="files(id)", q=q_parent)))['files']
        if len(parent) > 0: parent = parent[0]['id']    # Если тайтла не нашлось, то возвращаем прочерки
        else: return '-','-','-','-','-','-','-'

        await asyncio.sleep(0.5)

        q_filter = f"mimeType = 'application/vnd.google-apps.folder' and '{parent}' in parents"
        # Запрос 2, возвращает id + name папок внутри папок с тайтлами
        folders = (await aiog.as_service_account(service.files.list(fields="files(id, name)", q=q_filter)))['files']

        await asyncio.sleep(0.5)

        result = {}
        for el in self.TYPES:
            for folder in folders:
                if folder['name'].startswith(el):
                    # Выполнение запроса 3 для каждой папки. Максимум - 8 раз.
                    result[el] = await self.get_last_file(folder['id'], service, aiog)
                    break
            else: result[el] = '-'
        if result['Эдит'] != '-':
            result['Тайп'] = result['Эдит']
        return [result[el] for el in self.TYPES[:4] + self.TYPES[5:]]

    async def get_last_file(self, folder_id: str, service, aiog) -> str:
        """ Находит номер последней главы в папке
        :param folder_id: id гугл-папки, в которой происходит поиск
        :param service: объект, через генерирует запросы
        :param aiog: объект, который выполняет запросы
        :return: номер последней главы
        """
        q_filter = f"mimeType != 'application/vnd.google-apps.folder' and '{folder_id}' in parents"
        # Запрос 3, возвращает список файлов в папке
        files = (await aiog.as_service_account(service.files.list(fields="files(name)", q=q_filter)))['files']
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
            except:
                pass
        return str(sorted(nums)[-1]) if len(nums) > 0 else '-'

async def main():
    sheeter = Sheet()
    drive = Drive()
    names = sheeter.get_names_with_genres()
    await drive.get_creds()
    drive_list = await drive.parse(names)
    sheeter.write_values(drive_list, RANGES['drive'], dimension='ROWS')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError:
        pass

