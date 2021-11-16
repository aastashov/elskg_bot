import logging
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, executor, types

from conf import settings
from db import storage
from db.models import Package

logging.basicConfig(level=logging.INFO)


@dataclass
class TelegramBot:
    _bot = None

    @property
    def bot(self):
        if self._bot is None:
            self._bot = Bot(token=settings.TG_API_TOKEN)
        return self._bot

    _dp = None

    @property
    def dp(self):
        if self._dp is None:
            self._dp = Dispatcher(self.bot)
        return self._dp

    async def notification_change_status(self, package: Package):
        await self.bot.send_message(package.chat_id, f"{package.tracking}\n{package.status_text}")

    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)


bot = TelegramBot()

start_text = """Привет!

Я не официальный бот сайта https://els.kg и я смогу помочь тебе получить уведомление о смене статуса
твоей посылки.

/track <трек номер> - добавит посылку для отслеживания
/status - вернет список и статус всех твоих посылок
"""


@bot.dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply(start_text)


@bot.dp.message_handler(commands=["track"])
async def track(message: types.Message):
    package = Package(chat_id=message.chat.id, tracking=message.text.replace("/track", "").strip())
    storage.add_package(package)
    await message.reply("Ok!")


@bot.dp.message_handler(commands=["status"])
async def status(message: types.Message):
    packages = list(storage.fetch_my_packages(message.chat.id))
    if not packages:
        await message.reply("Ok!")
    else:
        reply_text = "\n".join([f"{p.tracking}: {p.status_text}" for p in packages])
        await message.reply(reply_text)
