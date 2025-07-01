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
        # Start the manager bot
        await bot.start()
        console.info(f"Manager bot started as @{bot.me.username}")
        
        # Initialize userbots if available
        if has_userbot and USERBOTS:
            await initialize_userbots()
            console.info("Userbots initialized")
            
            # Set up userbot handlers
            await setup_userbot_handlers()
            console.info("Userbot handlers set up")
        else:
            console.warning("No userbots configured, running with manager bot only")
        
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
        if has_userbot and USERBOTS:
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