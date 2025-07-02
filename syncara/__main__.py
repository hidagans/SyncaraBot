import asyncio
import sys
import signal
from os import execl
from pyrogram import idle
from importlib import import_module
from syncara import *
from syncara.modules import loadModule

shutdown_event = asyncio.Event()

def handle_signal(sig, frame):
    """Handle termination signals"""
    console.warning(f"Received signal {sig}, shutting down...")
    shutdown_event.set()


# Menangkap sinyal SIGINT dan SIGTERM
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)



try:
    from syncara.userbot import initialize_userbots, stop_userbots
    from syncara.modules.ai_handler import setup_userbot_handlers
    has_userbot = True
except ImportError:
    has_userbot = False


# Fungsi untuk memuat plugin secara dinamis
async def loadPlugins():
    modules = loadModule()
    for mod in modules:
        import_module(f"syncara.modules.{mod}")
    console.info("Plugins installed")

async def main():
    try:
        # Initialize both bot and userbot
        bot, userbot = await initialize_syncara()
        await loadPlugins()
        await setup_userbot_handlers(userbot)
        
        # Keep the application running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        console.warning("Received keyboard interrupt")
    finally:
        await stop_syncara()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        console.warning("Received keyboard interrupt, shutting down...")
    finally:
        console.info("Bot stopped")
        sys.exit(0)