from sheet import Sheet
from bot.bot import send
from config import RANGES, COLUMN_NAMES


class Updater:
    def __init__(self, dimension: str):
        self.dimension = dimension
        self.sheet = Sheet()
        self.titles = self.sheet.get_values('A4:A1000')[0]

    async def set_initial_state(self, key: str):
        self.columns = COLUMN_NAMES[key]
        self.initial_state = self.sheet.get_values(RANGES[key], dimension=self.dimension)

    async def set_final_state(self, values: list):
        self.final_state = [list(map(lambda x: x.split(';')[-1][1:-2] if ';' in x else x, el)) for el in values]
        await self.solve()

    async def solve(self):
        result = ['Обновления']
        for i in range(len(self.titles)):
            for el in enumerate(list(zip(self.initial_state[i], self.final_state[i]))):
                if el[1][0] != el[1][1]:
                    result.append(await self.format_update(i, el[0], el[1][0], el[1][1]))
        await self.send_updates('\n'.join(result))

    async def format_update(self, title_index: int, column_index: int, old_value: str, new_value: str) -> str:
        return 30*'=' + '\n' \
               + 'Тайтл:         ' + self.titles[title_index] + '\n' \
               + 'Столбец:   ' + self.columns[column_index] + '\n' \
               + 'Главы:        ' + old_value + '  =>  ' + new_value

    async def send_updates(self, updates: list):
        await send(updates)