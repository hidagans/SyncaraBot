# syncara/__main__.py
import asyncio
import sys
import signal
from pyrogram import idle
from importlib import import_module
from syncara import initialize_syncara, stop_syncara, console
from syncara.modules import loadModule

# Event untuk menangani shutdown
shutdown_event = asyncio.Event()

def handle_signal(sig, frame):
    """Handle termination signals"""
    console.warning(f"Received signal {sig}, shutting down...")
    shutdown_event.set()

# Set up signal handlers
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

async def loadPlugins():
    """Load all plugins dynamically"""
    modules = loadModule()
    for mod in modules:
        try:
            import_module(f"syncara.modules.{mod}")
            console.info(f"Loaded plugin: {mod}")
        except Exception as e:
            console.error(f"Failed to load plugin {mod}: {str(e)}")
    console.info("All plugins loaded")

async def main():
    """Main application entry point"""
    try:
        # Initialize SyncaraBot (both bot and userbot)
        console.info("Starting SyncaraBot...")
        bot_manager, userbot_client = await initialize_syncara()
        
        # Load plugins
        await loadPlugins()
        
        console.info("🚀 SyncaraBot is ready and running!")
        console.info("Press Ctrl+C to stop the bot")
        
        # Keep the bot running using pyrogram's idle
        await idle()
        
    except KeyboardInterrupt:
        console.warning("Received keyboard interrupt")
    except Exception as e:
        console.error(f"Error in main: {str(e)}")
        raise
    finally:
        # Cleanup
        console.info("Shutting down...")
        await stop_syncara()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.warning("Application interrupted by user")
    except Exception as e:
        console.error(f"Fatal error: {str(e)}")
    finally:
        console.info("Application terminated")
        sys.exit(0)