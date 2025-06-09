import asyncio
from pyrogram import Client, idle
from pyrogram.types import Message
import datetime

# Import konfigurasi dan modul
from config import API_ID, API_HASH, BOT_TOKEN, USERBOT_SESSION
from database.mongodb import Database
from handlers.command_handler import start_command, help_command
from handlers.shortcode_handler import handle_shortcode

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

# Register command handlers
bot.add_handler(start_command)
bot.add_handler(help_command)

# Message handler untuk shortcode
@bot.on_message()
async def message_handler(client: Client, message: Message):
    # Tambahkan user ke database jika belum ada
    if message.from_user:
        await db.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name
        )
    
    # Tambahkan group ke database jika belum ada
    if message.chat and message.chat.type in ["group", "supergroup"]:
        await db.add_group(message.chat.id, message.chat.title)
    
    # Proses shortcode jika ada
    await handle_shortcode(client, message, db)

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
