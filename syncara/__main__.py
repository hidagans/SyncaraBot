import asyncio
import sys
import signal
from os import execl
from pyrogram import idle
from importlib import import_module
from syncara import *
from syncara.modules import loadModule
from syncara.userbot import initialize_userbots, stop_userbots
from config.config import USERBOTS

shutdown_event = asyncio.Event()  # Event untuk menangani shutdown

# Fungsi untuk menangani sinyal SIGINT dan SIGTERM
def handle_signal(sig, frame):
    """Handle termination signals"""
    console.warning(f"Received signal {sig}, shutting down...")
    shutdown_event.set()

# Menangkap sinyal SIGINT dan SIGTERM
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# Fungsi untuk memuat plugin secara dinamis
async def loadPlugins():
    modules = loadModule()
    for mod in modules:
        import_module(f"syncara.modules.{mod}")
    console.info("Plugins installed")

async def main():
    try:
        # Start the bot
        await bot.start()
        console.success(f"Bot started as @{(await bot.get_me()).username}")
        
        # Initialize userbots
        if USERBOTS:
            await initialize_userbots()
        else:
            console.info("No userbots configured, running without userbots")
        
        # Load plugins
        await loadPlugins()
        
        # Set up signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, handle_signal)
        
        # Wait until shutdown
        await shutdown_event.wait()
        
    except Exception as e:
        console.error(f"Error in main: {str(e)}")
    finally:
        # Cleanup
        if USERBOTS:
            await stop_userbots()
        await bot.stop()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        console.warning("Received keyboard interrupt, shutting down...")
    finally:
        console.info("Bot stopped")
        sys.exit(0)
