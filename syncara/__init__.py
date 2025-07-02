# syncara/__init__.py
import logging
import os
from pyrogram import Client
from config.config import *

# Logging configuration
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
    """Enhanced Bot class with custom handlers"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.me = None

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        console.info(f"Bot Manager started as @{self.me.username} ({self.me.id})")

class Ubot(Client):
    """Enhanced Userbot class"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.me = None

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        console.info(f"Userbot started as @{self.me.username} ({self.me.id})")

# Global instances
bot = Bot(
    name="SyncaraBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

userbot = Ubot(
    name="SyncaraUbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,  # Menggunakan session string untuk userbot
)

# Initialize both instances
async def initialize_syncara():
    """Initialize both bot and userbot"""
    console.info("Initializing SyncaraBot...")
    await bot.start()
    
    if SESSION_STRING:
        await userbot.start()
        console.info("SyncaraBot initialized with userbot")
    else:
        console.warning("SyncaraBot initialized without userbot")
    
    return bot, userbot

async def stop_syncara():
    """Stop both bot and userbot"""
    console.info("Stopping SyncaraBot...")
    
    if userbot.is_connected:
        await userbot.stop()
    
    await bot.stop()
    console.info("SyncaraBot stopped")