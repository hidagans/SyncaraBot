# syncara/__init__.py
import logging
import os
import pyrogram
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from config.config import *
from config.assistants_config import ASSISTANT_CONFIG
from syncara.modules.autonomous_ai import AutonomousAI
import asyncio

# Hapus seluruh konfigurasi logging dan instance console dari sini.
# Semua file harus import console dari syncara.console

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

# Assistant Configuration sudah diimport dari config.assistants_config

# Global instances
bot = None
assistants = {}  # Dictionary untuk menyimpan semua assistant
autonomous_ai = AutonomousAI()

class AssistantManager:
    """Manager untuk mengelola multiple assistants"""
    
    def __init__(self):
        self.assistants = {}
        self.active_assistants = []
    
    async def initialize_assistant(self, assistant_id, config):
        """Initialize assistant berdasarkan config"""
        try:
            if not config.get("session_string"):
                console.warning(f"Assistant {assistant_id} tidak memiliki session string")
                return None
            
            assistant = Ubot(
                name=f"Syncara{assistant_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=config["session_string"],
            )
            
            await assistant.start()
            
            self.assistants[assistant_id] = {
                "client": assistant,
                "config": config,
                "status": "active"
            }
            
            self.active_assistants.append(assistant_id)
            
            console.info(f"✅ Assistant {assistant_id} (@{config['username']}) initialized successfully")
            return assistant
            
        except Exception as e:
            console.error(f"❌ Error initializing assistant {assistant_id}: {str(e)}")
            return None
    
    async def initialize_all_assistants(self):
        """Initialize semua assistant yang enabled"""
        console.info("🚀 Initializing all assistants...")
        
        for assistant_id, config in ASSISTANT_CONFIG.items():
            if config.get("enabled") and config.get("session_string"):
                await self.initialize_assistant(assistant_id, config)
            elif config.get("enabled") and not config.get("session_string"):
                console.warning(f"⚠️ Assistant {assistant_id} enabled tapi tidak ada session string")
        
        console.info(f"✅ Total {len(self.active_assistants)} assistants active: {', '.join(self.active_assistants)}")
    
    def get_assistant(self, assistant_id):
        """Get assistant client berdasarkan ID"""
        if assistant_id in self.assistants:
            return self.assistants[assistant_id]["client"]
        return None
    
    def get_assistant_config(self, assistant_id):
        """Get assistant config berdasarkan ID"""
        if assistant_id in self.assistants:
            return self.assistants[assistant_id]["config"]
        return None
    
    def get_all_assistants(self):
        """Get semua assistant yang active"""
        return self.assistants
    
    def get_active_assistants(self):
        """Get list assistant yang active"""
        return self.active_assistants
    
    async def stop_assistant(self, assistant_id):
        """Stop assistant tertentu"""
        if assistant_id in self.assistants:
            try:
                await self.assistants[assistant_id]["client"].stop()
                self.assistants[assistant_id]["status"] = "stopped"
                if assistant_id in self.active_assistants:
                    self.active_assistants.remove(assistant_id)
                console.info(f"✅ Assistant {assistant_id} stopped")
            except Exception as e:
                console.error(f"❌ Error stopping assistant {assistant_id}: {str(e)}")
    
    async def stop_all_assistants(self):
        """Stop semua assistant"""
        console.info("🛑 Stopping all assistants...")
        
        for assistant_id in list(self.assistants.keys()):
            await self.stop_assistant(assistant_id)
        
        console.info("✅ All assistants stopped")

# Create assistant manager instance
assistant_manager = AssistantManager()

# Initialize both instances
async def initialize_syncara():
    """Initialize bot manager dan semua assistants"""
    global bot
    
    console.info("🚀 Initializing SyncaraBot with Multiple Assistants...")
    
    # Create bot manager instance
    bot = Bot(
        name="SyncaraBot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )
    
    # Start bot manager
    await bot.start()
    
    # Initialize all assistants
    await assistant_manager.initialize_all_assistants()
    
    console.info("🎉 SyncaraBot initialized successfully!")
    return bot, assistant_manager

async def stop_syncara():
    """Stop bot manager dan semua assistants"""
    console.info("🛑 Stopping SyncaraBot...")
    
    # Stop all assistants
    await assistant_manager.stop_all_assistants()
    
    # Stop bot manager
    await bot.stop()
    
    console.info("✅ SyncaraBot stopped completely")

async def start_autonomous_mode():
    """Start autonomous AI mode"""
    console.info("🚀 Starting Autonomous AI Mode...")
    # Start autonomous AI in background
    asyncio.create_task(autonomous_ai.start_autonomous_mode())
    console.info("✅ Autonomous AI Mode started!")

# Helper functions untuk backward compatibility
def get_userbot():
    """Get default userbot (AERIS) untuk backward compatibility"""
    return assistant_manager.get_assistant("AERIS")

def get_assistant_by_username(username):
    """Get assistant berdasarkan username"""
    for assistant_id, assistant_data in assistant_manager.assistants.items():
        if assistant_data["config"]["username"] == username:
            return assistant_data["client"]
    return None

# Export untuk backward compatibility
userbot = get_userbot()  # Default ke AERIS