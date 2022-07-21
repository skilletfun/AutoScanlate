import json
import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TG_BOT_TOKEN


class TGBot:
    def __init__(self):
        with open('bot/users.json', 'r') as users:
            self.ids = json.loads(users.read())['ids']
        self.bot = Bot(token=TG_BOT_TOKEN)
        self.dp = Dispatcher(self.bot)

    async def send_message(self, message):
        for id_user in self.ids:
            await self.bot.send_message(id_user, message)
            await asyncio.sleep(0.5)


async def send(message):
    bot = TGBot()
    await bot.send_message(message)
    await main(message)
