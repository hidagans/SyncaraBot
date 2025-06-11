import asyncio
import sys
import signal
from os import execl
from pyrogram import idle
from importlib import import_module
from syncara import *
from syncara.module import loadModule

shutdown_event = asyncio.Event()  # Event untuk menangani shutdown

# Fungsi untuk menangani sinyal SIGINT dan SIGTERM
def handle_signal(signal, frame):
    console.info("Stop signal received (SIGINT or SIGTERM). Exiting...")
    shutdown_event.set()

# Menangkap sinyal SIGINT dan SIGTERM
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# Fungsi untuk memuat plugin secara dinamis
async def loadPlugins():
    modules = loadModule()
    for mod in modules:
        import_module(f"manager.module.{mod}")
    console.info("Plugins installed")

async def main():
    await bot.start()
    console.info(f"@{bot.me.username} Bot")
    await asyncio.gather(loadPlugins(), idle(), shutdown_event.wait())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_signal, sig, None)
    
    try:
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        pass
    finally:
        tasks = asyncio.all_tasks(loop)
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()