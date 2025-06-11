import logging
import os
import re
import subprocess
import sys
from typing import Callable

import pyrogram
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyromod import listen

from config import *

logging.basicConfig(
    level=logging.INFO,
    format="[ %(levelname)s ] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
    ],
)

logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)

console = logging.getLogger(__name__)

class Bot(Client):
    __module__ = "pyrogram.client"
    _bot = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.me = None

    def on_message(self, filters=None):
        def decorator(func):
            for ub in self._bot:
                ub.add_handler(MessageHandler(func, filters))
            return func
        return decorator

    def on_callback_query(self, filters=None):
        def decorator(func):
            for ub in self._bot:
                ub.add_handler(CallbackQueryHandler(func, filters))
            return func
        return decorator

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        if self not in self._bot:
            self._bot.append(self)
        console.info(f"Starting Bot ({self.me.first_name})")

# Inisialisasi bot
bot = Bot(
    name="SyncaraBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)