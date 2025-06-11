import asyncio
from pyrogram import Client, idle
from pyrogram.types import Message
import datetime

# Import konfigurasi dan modul
from config import API_ID, API_HASH, BOT_TOKEN, USERBOT_SESSION
from database.mongodb import Database

# Inisialisasi database
db = Database()

# Inisialisasi bot
bot = Client(
    "syncara_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Inisialisasi userbot sebagai assistant (opsional)
userbot = None
if USERBOT_SESSION:
    userbot = Client(
        "syncara_assistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=USERBOT_SESSION
    )
    
async def main():
    # Start bot
    await bot.start()
    print(f"Bot started at {datetime.datetime.now()}")
    
    # Start userbot jika tersedia
    if userbot:
        await userbot.start()
        print(f"Assistant userbot started at {datetime.datetime.now()}")
    
    # Keep the program running
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
