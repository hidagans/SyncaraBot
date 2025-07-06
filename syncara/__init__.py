# syncara/__init__.py
import logging
import os
import pyrogram
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
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

    def on_message(self, filters=None):
        def decorator(func):
            self.add_handler(MessageHandler(func, filters))
            return func
        return decorator

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        console.info(f"Bot Manager started as @{self.me.username} ({self.me.id})")

class Ubot(Client):
    """Enhanced Userbot class"""
    __module__ = "pyrogram.client"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.me = None

    def on_message(self, filters=None):
        def decorator(func):
            self.add_handler(MessageHandler(func, filters))
            return func
        return decorator

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        console.info(f"Userbot started as @{self.me.username} ({self.me.id})")

# Global instances - akan diinisialisasi nanti
bot = None
userbot = None

# Initialize both instances
async def initialize_syncara():
    """Initialize both bot and userbot"""
    global bot, userbot
    
    console.info("Initializing SyncaraBot...")
    
    # Create bot instance
    bot = Bot(
        name="SyncaraBot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )
    
    # Create userbot instance
    userbot = Ubot(
        name="SyncaraUbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
    )
    
    # Start bot
    await bot.start()
    
    # Start userbot if session string is available
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