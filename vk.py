import math
import asyncio
from time import time, sleep

import aiovk

from logger import log
from sheet import Sheet
from config import RANGES, SOURCE_RANGES, VK_API_TOKEN


@log
async def fill_vk():
    """ Заполнение столбцов Группы ВК
    Столбцы идут: Платки, бесплатки
    Заполняется строками
    """
    payed, free = '-', '-'
    sheeter = Sheet()
    urls = sheeter.get_values(SOURCE_RANGES['vk'])[0]
    group_id = urls[0].split('-')[1].split('_')[0]
    topics = [el.split('-')[1].split('_')[1] for el in urls]
    result_arr = []
    async with aiovk.TokenSession(access_token=VK_API_TOKEN) as ses:
        for i in range(math.ceil(len(topics) / 25)):
            time_flag = time()
            # 25 потому что максимум можно получить 25 записей за раз (ограничение ВК АПИ)
            script = ','.join(['API.board.getComments({"group_id":' + group_id +', "topic_id":' + topic_id+'})' for topic_id in topics[i*25:(i+1)*25]])
            script = 'return [' + script + '];'
            res = await aiovk.API(ses).execute(code=script)

            for el in enumerate(res):
                res = '\n'.join([note['text'] for note in el[1]['items']])
                for p in res.split('\n')[::-1]:
                    p = p.lower()
                    if len(p) > 10 and 'пончик' in p and payed == '-':
                        payed = p.split()[0] if 'сезон' not in p else p.split()[3]
                    elif len(p) > 10 and 'пончик' not in p:
                        free = p.split()[0] if 'сезон' not in p else p.split()[3]
                        link = f'https://vk.com/topic-{group_id}_{topics[el[0] + i*25]}'
                        free = f'=ГИПЕРССЫЛКА("{link}";"{free}")'
                        break
                result_arr.append([payed, free])
                payed, free = '-', '-'
            time_flag = 0.35 - time() - time_flag       # Оганичение на 3 запроса к ВК АПИ в секунду
            sleep(time_flag if time_flag > 0 else 0)    # Если не прошло 0.35 секунд (0.35 * 3 > 1 секунды), то пауза
    sheeter.write_values(result_arr, RANGES['vk'], dimension='ROWS')


if __name__ == '__main__':
    asyncio.run(fill_vk())
