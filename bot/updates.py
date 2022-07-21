import asyncio

from math import ceil

from sheet import Sheet
from bot.bot import send
from config import RANGES, COLUMN_NAMES


class Updater:
    """ Выбирает тайтлы, где произошли изменения, и отправляет все это через боту. """
    def __init__(self, dimension: str):
        """
        :param dimension: как будут предоставлены данные (ROWS / COLUMNS)
        """
        self.dimension = dimension
        self.sheet = Sheet()
        self.titles = self.sheet.get_values('A4:A1000')[0]

    async def set_initial_state(self, key: str) -> None:
        """ Запоминает начальные значения столбцов
        :param key: какие столбцы запоминать
        """
        self.columns = COLUMN_NAMES[key]
        self.initial_state = self.sheet.get_values(RANGES[key], dimension=self.dimension)

    async def set_final_state(self, values: list) -> None:
        """ Принимает конечные значения и находит изменения
        :param values: значения
        """
        self.final_state = [list(map(lambda x: x.split(';')[-1][1:-2] if ';' in x else x, el)) for el in values]
        await self.solve()

    async def solve(self) -> None:
        """ Находит данные, которые изменились и представляет их в определенном формате. """
        result = []
        for i in range(len(self.titles)):
            for el in enumerate(list(zip(self.initial_state[i], self.final_state[i]))):
                if el[1][0] != el[1][1]:
                    result.append(await self.format_update(i, el[0], el[1][0], el[1][1]))
        await self.send_updates(result)

    async def format_update(self, title_index: int, column_index: int, old_value: str, new_value: str) -> str:
        """ Представляет данные в определенном формате. """
        return 30*'=' + '\n' \
               + 'Тайтл:         ' + self.titles[title_index] + '\n' \
               + 'Столбец:   ' + self.columns[column_index] + '\n' \
               + 'Главы:        ' + old_value + '  =>  ' + new_value

    async def send_updates(self, updates: list) -> None:
        """ Отправляет сформированное сообщение боту. """
        counter = ceil(len(updates) / 20)
        values = [f'Обновления ({i+1} из {counter})\n\n' + '\n'.join(updates[i*20:(i+1)*20]) for i in range(counter)]
        await send(values)
