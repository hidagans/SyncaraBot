# syncara/__main__.py
import asyncio
import sys
import signal
from pyrogram import idle
from importlib import import_module
from syncara import initialize_syncara, stop_syncara
from syncara.modules import loadModule
from syncara.console import console

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

async def setup_ai_handler():
    """Setup AI handler after initialization"""
    try:
        from syncara.modules.ai_handler import setup_assistant_handlers
        await setup_assistant_handlers()
        console.info("✅ AI handler setup completed")
    except ImportError:
        console.warning("⚠️ AI handler not available")
    except Exception as e:
        console.error(f"❌ Error setting up AI handler: {str(e)}")

async def setup_channel_manager():
    """Setup channel manager for auto-posting"""
    try:
        from syncara.modules.channel_manager import channel_manager
        console.info("📢 Channel Manager initialized")
        console.info("📊 Use [CHANNEL:STATUS] to check status")
        console.info("🚀 Use [CHANNEL:START] to activate auto-posting")
        
        # Optional: Auto-start channel posting (uncomment if needed)
        # from syncara import bot
        # asyncio.create_task(channel_manager.start_auto_posting(bot))
        # console.info("🚀 Channel auto-posting started automatically")
        
        return channel_manager
    except Exception as e:
        console.error(f"❌ Error setting up channel manager: {str(e)}")
        return None

async def main():
    """Main application entry point"""
    try:
        # Initialize SyncaraBot (both bot and userbot)
        console.info("🚀 Starting SyncaraBot...")
        
        # Initialize database
        from syncara.database import initialize_database
        await initialize_database()
        
        # Initialize SyncaraBot
        bot_manager, userbot_client = await initialize_syncara()
        
        # Load plugins AFTER bot initialization
        console.info("🔌 Loading plugins...")
        await loadPlugins()
        
        # Setup AI handler
        console.info("🤖 Setting up AI handler...")
        await setup_ai_handler()
        
        # Setup channel manager
        console.info("📢 Setting up Channel Manager...")
        channel_manager = await setup_channel_manager()
        
        # Start autonomous AI mode
        console.info("🧠 Starting autonomous AI mode...")
        from syncara import start_autonomous_mode
        await start_autonomous_mode()
        
        console.info("✅ SyncaraBot is ready and running!")
        console.info("💡 Available features:")
        console.info("   - 🤖 AI Assistant with learning capabilities")
        console.info("   - 📢 Auto-posting channel management")
        console.info("   - 🎨 Canvas file management")
        console.info("   - 🖼️ Image generation")
        console.info("   - 👥 User/Group management")
        console.info("   - 📝 Todo management")
        console.info("   - 🔄 Multi-step workflow processing")
        console.info("")
        # Get bot info from assistant manager
        bot_info = "Unknown"
        userbot_info = "Not available"
        
        try:
            if hasattr(bot_manager, 'bot') and bot_manager.bot and hasattr(bot_manager.bot, 'me'):
                bot_info = f"@{bot_manager.bot.me.username}" if bot_manager.bot.me.username else "Unknown"
            elif hasattr(bot_manager, 'get_bot_info'):
                bot_info = bot_manager.get_bot_info()
        except:
            pass
            
        try:
            if hasattr(bot_manager, 'assistants') and bot_manager.assistants:
                first_assistant = list(bot_manager.assistants.values())[0]
                if hasattr(first_assistant, 'me') and first_assistant.me:
                    userbot_info = first_assistant.me.first_name or "Assistant"
        except:
            pass
            
        console.info(f"📱 Bot username: {bot_info}")
        console.info(f"🤖 Userbot: {userbot_info}")
        console.info("")
        console.info("📊 Channel Management:")
        console.info("   - Use [CHANNEL:STATUS] to check auto-posting status")
        console.info("   - Use [CHANNEL:START] to activate auto-posting") 
        console.info("   - Use [CHANNEL:STOP] to deactivate auto-posting")
        console.info("   - Use [CHANNEL:STATS] to view analytics")
        console.info("")
        console.info("⏹️ Press Ctrl+C to stop the bot")
        
        # Keep the bot running using pyrogram's idle
        await idle()
        
    except KeyboardInterrupt:
        console.warning("⏹️ Received keyboard interrupt")
        
        # Stop channel auto-posting if running
        try:
            from syncara.modules.channel_manager import channel_manager
            if channel_manager.is_running:
                console.info("📢 Stopping channel auto-posting...")
                await channel_manager.stop_auto_posting()
        except:
            pass
        
    except Exception as e:
        console.error(f"❌ Error in main: {str(e)}")
        raise
    finally:
        # Cleanup
        console.info("🧹 Shutting down...")
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