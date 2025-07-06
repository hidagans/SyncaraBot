# syncara/modules/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, userbot, console
from config.config import OWNER_ID, SESSION_STRING
from datetime import datetime
import pytz

# Inisialisasi komponen
replicate_api = ReplicateAPI()

# Cache untuk informasi userbot agar tidak flood API
USERBOT_INFO_CACHE = {}

# Mapping userbot name to system prompt name
USERBOT_PROMPT_MAPPING = {
    "SyncaraUbot": "AERIS",  # Default untuk userbot utama
}

# Konfigurasi untuk mengatur jumlah pesan riwayat
CHAT_HISTORY_CONFIG = {
    "enabled": True,
    "limit": 20,
    "include_media_info": True,
    "include_timestamps": True
}

# Debug logging untuk troubleshooting
DEBUG_MODE = True

def debug_log(message):
    """Debug logging helper"""
    if DEBUG_MODE:
        console.info(f"[DEBUG] {message}")

async def cache_userbot_info():
    """Cache userbot information to avoid API flood"""
    try:
        if not SESSION_STRING:
            console.warning("No session string configured for userbot")
            return None
            
        if userbot.name not in USERBOT_INFO_CACHE:
            me = await userbot.get_me()
            USERBOT_INFO_CACHE[userbot.name] = {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name
            }
            console.info(f"Cached info for userbot: {userbot.name} (@{me.username})")
        return USERBOT_INFO_CACHE[userbot.name]
    except Exception as e:
        console.error(f"Error caching userbot info: {str(e)}")
        return None

# Create custom filter for userbot interactions
async def userbot_filter(_, __, message):
    """Custom filter to detect userbot interactions"""
    try:
        debug_log(f"=== FILTER CHECK START ===")
        debug_log(f"Message from: {message.from_user.first_name if message.from_user else 'Unknown'} (ID: {message.from_user.id if message.from_user else 'None'})")
        debug_log(f"Chat type: {message.chat.type}")
        debug_log(f"Message text: {message.text[:100] if message.text else 'No text'}")
        
        # Skip messages from bots
        if message.from_user and message.from_user.is_bot:
            debug_log("❌ Skipping bot message")
            return False
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
        if not userbot_info:
            debug_log("⚠️ Userbot info not in cache, trying to cache...")
            userbot_info = await cache_userbot_info()
            if not userbot_info:
                debug_log("❌ Failed to get userbot info")
                return False
        
        debug_log(f"✅ Userbot info: @{userbot_info['username']} (ID: {userbot_info['id']})")
        
        # Check if in private chat
        if message.chat.type == enums.ChatType.PRIVATE:
            debug_log("✅ Private chat detected - WILL RESPOND")
            return True
        
        # Check if message is a reply to userbot's message
        if message.reply_to_message:
            debug_log(f"📝 Reply detected to message from ID: {message.reply_to_message.from_user.id if message.reply_to_message.from_user else 'None'}")
            if message.reply_to_message.from_user and message.reply_to_message.from_user.id == userbot_info['id']:
                debug_log("✅ Reply to userbot detected - WILL RESPOND")
                return True
        
        # Check if userbot is mentioned in the message
        if message.entities:
            debug_log(f"🔍 Checking {len(message.entities)} entities...")
            for i, entity in enumerate(message.entities):
                debug_log(f"Entity {i}: type={entity.type}, offset={entity.offset}, length={entity.length}")
                if entity.type == enums.MessageEntityType.MENTION:
                    # Extract mentioned username
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                    debug_log(f"🏷️ Found mention: {mentioned_username}")
                    if mentioned_username == f"@{userbot_info['username']}":
                        debug_log("✅ Userbot mentioned - WILL RESPOND")
                        return True
                elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                    # Check if mentioned user is this userbot
                    if entity.user and entity.user.id == userbot_info['id']:
                        debug_log("✅ Userbot text mention detected - WILL RESPOND")
                        return True
        else:
            debug_log("ℹ️ No entities found in message")
        
        debug_log("❌ No trigger conditions met - WILL NOT RESPOND")
        debug_log("=== FILTER CHECK END ===")
        return False
    except Exception as e:
        console.error(f"Error in userbot filter: {str(e)}")
        debug_log(f"❌ Filter error: {str(e)}")
        return False

# Create the filter
custom_userbot_filter = filters.create(userbot_filter)

# Test handler untuk memastikan userbot menerima pesan
@userbot.on_message(filters.all)
async def test_all_messages(client, message):
    """Test handler to see all messages received by userbot"""
    try:
        debug_log(f"🔔 USERBOT RECEIVED MESSAGE:")
        debug_log(f"   From: {message.from_user.first_name if message.from_user else 'Unknown'}")
        debug_log(f"   Chat: {message.chat.title if message.chat.title else 'Private'}")
        debug_log(f"   Text: {message.text[:50] if message.text else 'No text'}...")
        debug_log(f"   Message ID: {message.id}")
        
        # Also log to console for visibility
        console.info(f"USERBOT MSG: {message.from_user.first_name if message.from_user else 'Unknown'} -> {message.text[:50] if message.text else 'No text'}")
    except Exception as e:
        debug_log(f"Error in test handler: {str(e)}")
        console.error(f"Error in test handler: {str(e)}")

# Debug handler for all bot messages
@bot.on_message(filters.all)
async def debug_all_bot_messages(client, message):
    """Debug handler to see all messages received by bot manager"""
    try:
        console.info(f"BOT MSG: {message.from_user.first_name if message.from_user else 'Unknown'} -> {message.text[:50] if message.text else 'No text'}")
        debug_log(f"🔔 BOT RECEIVED MESSAGE:")
        debug_log(f"   From: {message.from_user.first_name if message.from_user else 'Unknown'}")
        debug_log(f"   Chat: {message.chat.title if message.chat.title else 'Private'}")
        debug_log(f"   Text: {message.text[:50] if message.text else 'No text'}...")
        debug_log(f"   Message ID: {message.id}")
        
        # Check if it's a command
        if message.text and message.text.startswith('/'):
            debug_log(f"🎯 COMMAND DETECTED: {message.text}")
            console.info(f"COMMAND: {message.text}")
    except Exception as e:
        debug_log(f"Error in bot debug handler: {str(e)}")
        console.error(f"Error in bot debug handler: {str(e)}")

# Bot manager commands
@bot.on_message(filters.command("start") | filters.command("help"))
async def start_command(client, message):
    """Handle start command for the manager bot"""
    try:
        debug_log(f"🚀 START COMMAND HANDLER TRIGGERED!")
        debug_log(f"Start command from user {message.from_user.id}")
        console.info(f"🚀 START COMMAND: from user {message.from_user.id}")
        await message.reply_text(
            "🤖 **Halo! Saya adalah SyncaraBot Manager**\n\n"
            "🎯 Bot ini mengelola userbot assistant yang melayani permintaan AI.\n\n"
            "📋 **Perintah yang tersedia:**\n"
            "• `/start` atau `/help` - Tampilkan pesan ini\n"
            "• `/status` - Cek status bot dan userbot\n"
            "• `/prompts` - Lihat daftar system prompt\n"
            "• `/userbot` - Info userbot assistant\n"
            "• `/debug` - Debug info (owner only)\n\n"
            "💡 **Cara menggunakan:**\n"
            "Mention atau reply ke userbot assistant untuk berinteraksi dengan AI!"
        )
        console.info(f"✅ Start command executed by user {message.from_user.id}")
    except Exception as e:
        console.error(f"❌ Error in start_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat memproses perintah.")

@bot.on_message(filters.command("debug") & filters.user(OWNER_ID))
async def debug_command(client, message):
    """Debug command to check AI handler status"""
    try:
        debug_info = f"🔍 **Debug Info:**\n\n"
        
        # Check userbot info cache
        if USERBOT_INFO_CACHE:
            for name, info in USERBOT_INFO_CACHE.items():
                debug_info += f"**Userbot {name}:**\n"
                debug_info += f"• ID: `{info['id']}`\n"
                debug_info += f"• Username: @{info['username']}\n"
                debug_info += f"• Name: {info['first_name']}\n\n"
        else:
            debug_info += "❌ No userbot info cached\n\n"
        
        # Check prompt mapping
        debug_info += f"**Prompt Mapping:**\n"
        for name, prompt in USERBOT_PROMPT_MAPPING.items():
            debug_info += f"• {name} → {prompt}\n"
        
        debug_info += f"\n**Config:**\n"
        debug_info += f"• SESSION_STRING: {'✅ Set' if SESSION_STRING else '❌ Not set'}\n"
        debug_info += f"• Chat History: {'✅ Enabled' if CHAT_HISTORY_CONFIG['enabled'] else '❌ Disabled'}\n"
        debug_info += f"• Debug Mode: {'✅ On' if DEBUG_MODE else '❌ Off'}\n"
        
        # Check handlers
        debug_info += f"\n**Handlers:**\n"
        debug_info += f"• Userbot handlers: {len(userbot.dispatcher.groups) if hasattr(userbot, 'dispatcher') else 'Unknown'}\n"
        debug_info += f"• Bot handlers: {len(client.dispatcher.groups) if hasattr(client, 'dispatcher') else 'Unknown'}\n"
        
        await message.reply_text(debug_info)
        
    except Exception as e:
        console.error(f"Error in debug command: {str(e)}")
        await message.reply_text(f"❌ Debug error: {str(e)}")

@bot.on_message(filters.command("test"))
async def test_command(client, message):
    """Simple test command"""
    try:
        debug_log(f"🧪 TEST COMMAND HANDLER TRIGGERED!")
        console.info(f"🧪 TEST COMMAND: from user {message.from_user.id}")
        await message.reply_text("✅ Test command berhasil! Bot berfungsi dengan baik.")
    except Exception as e:
        console.error(f"❌ Error in test_command: {str(e)}")

@bot.on_message(filters.command("test_userbot") & filters.user(OWNER_ID))
async def test_userbot_command(client, message):
    """Test userbot functionality"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Test sending message from userbot
        test_msg = await userbot.send_message(
            chat_id=message.chat.id,
            text="🧪 **Test Message dari Userbot**\n\nJika Anda melihat pesan ini, userbot berfungsi dengan baik!"
        )
        
        await message.reply_text(
            f"✅ **Test berhasil!**\n\n"
            f"Userbot berhasil mengirim pesan dengan ID: `{test_msg.id}`\n\n"
            f"Sekarang coba reply atau mention userbot untuk test AI handler."
        )
        
    except Exception as e:
        console.error(f"Error in test_userbot_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

# Userbot message handler - dengan debug yang lebih detail
@userbot.on_message(custom_userbot_filter & (filters.text | filters.photo))
async def userbot_message_handler(client, message):
    """Handle messages for userbot assistant when mentioned or replied"""
    try:
        debug_log(f"🚀 HANDLER TRIGGERED!")
        debug_log(f"Handler triggered for message: {message.text[:50] if message.text else 'No text'}...")
        
        # Get text from either message text or caption
        text = message.text or message.caption
        
        if not text:
            debug_log("❌ No text found in message")
            return
        
        debug_log(f"📝 Processing text: {text[:100]}...")
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(client.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
        
        if userbot_info and f"@{userbot_info['username']}" in text:
            text = text.replace(f"@{userbot_info['username']}", "").strip()
            debug_log("✂️ Removed username mention from text")
        
        # Get photo if exists
        photo_file_id = None
        if message.photo:
            photo_file_id = message.photo.file_id
            debug_log("📸 Photo detected in message")
        
        # Send typing action
        debug_log("⌨️ Sending typing action...")
        await client.send_chat_action(
            chat_id=message.chat.id,
            action=enums.ChatAction.TYPING
        )
        
        # Process AI response
        debug_log("🤖 Processing AI response...")
        await process_ai_response(client, message, text, photo_file_id)
        debug_log("✅ AI response processing completed")
        
    except Exception as e:
        console.error(f"Error in userbot message handler: {str(e)}")
        debug_log(f"❌ Handler error: {str(e)}")

# Simplified version for testing - respond to ALL text messages to userbot
@userbot.on_message(filters.text & filters.private)
async def simple_private_handler(client, message):
    """Simple handler for private messages to userbot"""
    try:
        debug_log(f"🔥 SIMPLE PRIVATE HANDLER TRIGGERED!")
        debug_log(f"Private message: {message.text[:50]}...")
        
        await client.send_message(
            chat_id=message.chat.id,
            text=f"🤖 **Test Response**\n\nSaya menerima pesan: {message.text[:100]}...",
            reply_to_message_id=message.id
        )
        
    except Exception as e:
        console.error(f"Error in simple private handler: {str(e)}")

# Rest of the functions remain the same...
async def get_chat_history(client, chat_id, limit=None):
    """Get chat history for context"""
    # ... existing implementation ...
    return []

def format_chat_history(messages):
    """Format chat history for AI context"""
    # ... existing implementation ...
    return ""

async def process_ai_response(client, message, prompt, photo_file_id=None):
    """Process AI response with detailed context including current message info"""
    try:
        debug_log(f"🎯 Starting AI response processing...")
        debug_log(f"Prompt: {prompt[:100]}...")
        
        # For now, send a simple test response
        await client.send_message(
            chat_id=message.chat.id,
            text=f"🤖 **AI Response Test**\n\nPrompt received: {prompt[:200]}...\n\n_AI processing will be implemented here_",
            reply_to_message_id=message.id
        )
        
        debug_log("✅ Test response sent")
        
    except Exception as e:
        console.error(f"Error in process_ai_response: {str(e)}")
        debug_log(f"❌ AI response error: {str(e)}")

async def initialize_ai_handler():
    """Initialize AI handler components"""
    try:
        console.info("Initializing AI handler...")
        
        # Cache userbot info if available
        if SESSION_STRING:
            userbot_info = await cache_userbot_info()
            if userbot_info:
                console.info(f"✅ AI handler initialized with userbot: @{userbot_info['username']} (ID: {userbot_info['id']})")
                debug_log(f"Userbot cached: {userbot_info}")
            else:
                console.error("❌ Failed to cache userbot info")
        else:
            console.warning("⚠️ AI handler initialized without userbot (no SESSION_STRING)")
        
        # Test handler registration
        debug_log(f"Userbot handlers registered: {len(userbot.dispatcher.groups) if hasattr(userbot, 'dispatcher') else 'Unknown'}")
        
        # Check bot handlers
        if hasattr(bot, 'dispatcher'):
            console.info(f"Bot handlers registered: {len(bot.dispatcher.groups)}")
            for group_id, handlers in bot.dispatcher.groups.items():
                console.info(f"  Group {group_id}: {len(handlers)} handlers")
        else:
            console.warning("Bot dispatcher not available")
            
        # Check userbot handlers
        if hasattr(userbot, 'dispatcher'):
            console.info(f"Userbot handlers registered: {len(userbot.dispatcher.groups)}")
            for group_id, handlers in userbot.dispatcher.groups.items():
                console.info(f"  Group {group_id}: {len(handlers)} handlers")
        else:
            console.warning("Userbot dispatcher not available")
        
    except Exception as e:
        console.error(f"Error initializing AI handler: {str(e)}")

# Export important functions and variables for other modules
__all__ = [
    'process_ai_response',
    'initialize_ai_handler',
    'get_chat_history',
    'format_chat_history',
    'cache_userbot_info',
    'USERBOT_INFO_CACHE',
    'USERBOT_PROMPT_MAPPING',
    'CHAT_HISTORY_CONFIG'
]