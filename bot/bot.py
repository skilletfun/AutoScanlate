import json
import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TG_BOT_TOKEN


class TGBot:
    """ Отправляет сообщения в чаты, которые указаны в файле. """
    def __init__(self):
        with open('bot/users.json', 'r') as users:
            self.ids = json.loads(users.read())['ids']
        self.bot = Bot(token=TG_BOT_TOKEN)
        self.dp = Dispatcher(self.bot)

    async def send_messages(self, messages: list) -> None:
        """ Принимает список строк и отправляет их через бота в чаты. """
        for id_user in self.ids:
            for message in messages:
                await self.bot.send_message(id_user, message)
                await asyncio.sleep(1)


async def send(messages: list) -> None:
    """ Принимает список строк и отправляет их через бота в чаты. """
    bot = TGBot()
    await bot.send_messages(messages)
