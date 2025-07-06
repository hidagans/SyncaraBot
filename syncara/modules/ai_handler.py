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
DEBUG_MODE = False

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
        # Skip messages from bots
        if message.from_user and message.from_user.is_bot:
            return False
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
            if not userbot_info:
                return False
        
        # Check if in private chat
        if message.chat.type == enums.ChatType.PRIVATE:
            return True
        
        # Check if message is a reply to userbot's message
        if message.reply_to_message:
            if message.reply_to_message.from_user and message.reply_to_message.from_user.id == userbot_info['id']:
                return True
        
        # Check if userbot is mentioned in the message
        if message.entities:
            for entity in message.entities:
                if entity.type == enums.MessageEntityType.MENTION:
                    # Extract mentioned username
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                    if mentioned_username == f"@{userbot_info['username']}":
                        return True
                elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                    # Check if mentioned user is this userbot
                    if entity.user and entity.user.id == userbot_info['id']:
                        return True
        
        return False
    except Exception as e:
        console.error(f"Error in userbot filter: {str(e)}")
        return False

# Create the filter
custom_userbot_filter = filters.create(userbot_filter)

# Test handler untuk memastikan userbot menerima pesan - REMOVED to avoid conflicts
# @userbot.on_message(filters.all)
# async def test_all_messages(client, message):
#     """Test handler to see all messages received by userbot"""
#     try:
#         debug_log(f"🔔 USERBOT RECEIVED MESSAGE:")
#         debug_log(f"   From: {message.from_user.first_name if message.from_user else 'Unknown'}")
#         debug_log(f"   Chat: {message.chat.title if message.chat.title else 'Private'}")
#         debug_log(f"   Text: {message.text[:50] if message.text else 'No text'}...")
#         debug_log(f"   Message ID: {message.id}")
#         
#         # Also log to console for visibility
#         console.info(f"USERBOT MSG: {message.from_user.first_name if message.from_user else 'Unknown'} -> {message.text[:50] if message.text else 'No text'}")
#     except Exception as e:
#         debug_log(f"Error in test handler: {str(e)}")
#         console.error(f"Error in test handler: {str(e)}")

# Debug handler for all bot messages - REMOVED to avoid conflicts
# @bot.on_message(filters.all)
# async def debug_all_bot_messages(client, message):
#     """Debug handler to see all messages received by bot manager"""
#     try:
#         console.info(f"BOT MSG: {message.from_user.first_name if message.from_user else 'Unknown'} -> {message.text[:50] if message.text else 'No text'}")
#         debug_log(f"🔔 BOT RECEIVED MESSAGE:")
#         debug_log(f"   From: {message.from_user.first_name if message.from_user else 'Unknown'}")
#         debug_log(f"   Chat: {message.chat.title if message.chat.title else 'Private'}")
#         debug_log(f"   Text: {message.text[:50] if message.text else 'No text'}...")
#         debug_log(f"   Message ID: {message.id}")
#         
#         # Check if it's a command
#         if message.text and message.text.startswith('/'):
#             debug_log(f"🎯 COMMAND DETECTED: {message.text}")
#             console.info(f"COMMAND: {message.text}")
#     except Exception as e:
#         debug_log(f"Error in bot debug handler: {str(e)}")
#         console.error(f"Error in bot debug handler: {str(e)}")

# Bot manager commands
@bot.on_message(filters.command("start") | filters.command("help"))
async def start_command(client, message):
    """Handle start command for the manager bot"""
    try:
        from syncara.modules.system_prompt import system_prompt
        
        current_prompt = system_prompt.current_prompt_name
        
        await message.reply_text(
            "🤖 **Halo! Saya adalah SyncaraBot Manager**\n\n"
            "🎯 Bot ini mengelola userbot assistant yang melayani permintaan AI.\n\n"
            f"🧠 **Current AI Personality:** {current_prompt}\n\n"
            "📋 **Perintah yang tersedia:**\n"
            "• `/start` atau `/help` - Tampilkan pesan ini\n"
            "• `/test` - Test command\n"
            "• `/prompt` - Ganti AI personality (owner only)\n"
            "• `/debug` - Debug info (owner only)\n"
            "• `/shortcodes` - Lihat shortcode yang tersedia (owner only)\n"
            "• `/test_userbot` - Test userbot assistant (owner only)\n\n"
            "💡 **Cara menggunakan:**\n"
            "• Kirim pesan private ke @Aeris_sync\n"
            "• Mention @Aeris_sync di group\n"
            "• Reply ke pesan @Aeris_sync\n\n"
            "🎵 **Voice Chat Commands (via Assistant):**\n"
            "• `/startvc` - Start voice chat (owner only)\n"
            "• `/testvc` - Test voice chat (owner only)\n\n"
            "🚀 **AI Features:**\n"
            "• Chat AI dengan konteks\n"
            "• Analisis gambar\n"
            "• Multiple personality\n"
            "• Music player integration"
        )
    except Exception as e:
        console.error(f"Error in start_command: {str(e)}")
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
        await message.reply_text("✅ Test command berhasil! Bot berfungsi dengan baik.")
    except Exception as e:
        console.error(f"Error in test_command: {str(e)}")

@bot.on_message(filters.command("prompt") & filters.user(OWNER_ID))
async def change_prompt_command(client, message):
    """Change system prompt"""
    try:
        from syncara.modules.system_prompt import system_prompt
        
        # Parse command: /prompt <prompt_name>
        args = message.text.split()
        if len(args) < 2:
            available_prompts = system_prompt.get_available_prompts()
            current_prompt = system_prompt.current_prompt_name
            
            response = f"🤖 **System Prompt Manager**\n\n"
            response += f"**Current:** {current_prompt}\n\n"
            response += f"**Available Prompts:**\n"
            for prompt in available_prompts:
                response += f"• {prompt}\n"
            response += f"\n**Usage:** `/prompt <prompt_name>`"
            
            await message.reply_text(response)
            return
        
        prompt_name = args[1].upper()
        if system_prompt.set_prompt(prompt_name):
            await message.reply_text(f"✅ System prompt changed to: **{prompt_name}**")
        else:
            await message.reply_text(f"❌ Prompt '{prompt_name}' not found!")
            
    except Exception as e:
        console.error(f"Error in change_prompt_command: {str(e)}")
        await message.reply_text("❌ Error changing prompt")

@bot.on_message(filters.command("shortcodes") & filters.user(OWNER_ID))
async def shortcodes_command(client, message):
    """Show available shortcodes"""
    try:
        from syncara.shortcode import registry
        
        response = f"🔧 **Shortcode Registry Status**\n\n"
        response += f"**Handlers:** {len(registry.shortcodes)}\n"
        response += f"**Descriptions:** {len(registry.descriptions)}\n\n"
        
        if registry.descriptions:
            response += "**Available Shortcodes:**\n"
            for shortcode, desc in registry.descriptions.items():
                response += f"• `{shortcode}` - {desc}\n"
        else:
            response += "❌ No shortcodes available"
        
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in shortcodes_command: {str(e)}")
        await message.reply_text(f"❌ Error: {str(e)}")

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

# Userbot message handler for group interactions
@userbot.on_message(custom_userbot_filter & (filters.text | filters.photo))
async def userbot_message_handler(client, message):
    """Handle messages for userbot assistant when mentioned or replied"""
    try:
        # Get text from either message text or caption
        text = message.text or message.caption
        
        if not text:
            return
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(client.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
        
        if userbot_info and f"@{userbot_info['username']}" in text:
            text = text.replace(f"@{userbot_info['username']}", "").strip()
        
        # Get photo if exists
        photo_file_id = None
        if message.photo:
            photo_file_id = message.photo.file_id
        
        # Send typing action
        await client.send_chat_action(
            chat_id=message.chat.id,
            action=enums.ChatAction.TYPING
        )
        
        # Process AI response
        await process_ai_response(client, message, text, photo_file_id)
        
    except Exception as e:
        console.error(f"Error in userbot message handler: {str(e)}")

# Private message handler for userbot
@userbot.on_message(filters.text & filters.private)
async def simple_private_handler(client, message):
    """Handler for private messages to userbot"""
    try:
        # Process with AI response
        await process_ai_response(client, message, message.text)
        
    except Exception as e:
        console.error(f"Error in private handler: {str(e)}")
        # Fallback response
        await client.send_message(
            chat_id=message.chat.id,
            text="❌ Maaf, terjadi kesalahan saat memproses pesan Anda.",
            reply_to_message_id=message.id
        )

# Rest of the functions remain the same...
async def get_chat_history(client, chat_id, limit=None):
    """Get chat history with detailed information including message ID, user ID, and reply info"""
    try:
        # Check if history is enabled
        if not CHAT_HISTORY_CONFIG["enabled"]:
            return []
            
        # Use configured limit if not specified
        if limit is None:
            limit = CHAT_HISTORY_CONFIG["limit"]
        
        messages = []
        
        # Get userbot info from cache
        userbot_name = getattr(client, 'name', 'unknown')
        userbot_info = USERBOT_INFO_CACHE.get(userbot_name)
        
        if not userbot_info:
            # Fallback: get info but with rate limiting
            try:
                me = await client.get_me()
                userbot_info = {
                    'id': me.id,
                    'username': me.username,
                    'first_name': me.first_name,
                    'last_name': me.last_name
                }
                USERBOT_INFO_CACHE[userbot_name] = userbot_info
            except Exception as e:
                console.error(f"Error getting userbot info: {str(e)}")
                return []
        
        # Get timezone for timestamp formatting
        tz = pytz.timezone('Asia/Jakarta')
        
        async for message in client.get_chat_history(chat_id, limit=limit):
            try:
                # Skip service messages
                if message.service:
                    continue
                
                # Get message content
                content = message.text or message.caption or ""
                
                # Handle media messages
                if not content.strip() and CHAT_HISTORY_CONFIG["include_media_info"]:
                    if message.photo:
                        content = "[Foto]"
                    elif message.video:
                        content = "[Video]"
                    elif message.document:
                        content = f"[Dokumen: {message.document.file_name or 'Unknown'}]"
                    elif message.audio:
                        content = "[Audio]"
                    elif message.voice:
                        content = "[Voice Note]"
                    elif message.sticker:
                        content = f"[Sticker: {message.sticker.emoji or ''}]"
                    elif message.animation:
                        content = "[GIF]"
                    else:
                        content = "[Media]"
                
                # Skip if still empty
                if not content.strip():
                    continue
                
                # Get sender info
                sender_info = {
                    'id': None,
                    'name': "Unknown",
                    'username': None,
                    'is_bot': False,
                    'is_assistant': False
                }
                
                if message.from_user:
                    sender_info = {
                        'id': message.from_user.id,
                        'name': message.from_user.first_name or "Unknown",
                        'username': message.from_user.username,
                        'is_bot': message.from_user.is_bot,
                        'is_assistant': message.from_user.id == userbot_info['id']
                    }
                    
                    # Add assistant label
                    if sender_info['is_assistant']:
                        sender_info['display_name'] = f"{userbot_info['first_name']} (Assistant)"
                    else:
                        sender_info['display_name'] = sender_info['name']
                        
                elif message.sender_chat:
                    sender_info = {
                        'id': message.sender_chat.id,
                        'name': message.sender_chat.title or "Channel",
                        'username': message.sender_chat.username,
                        'is_bot': False,
                        'is_assistant': False,
                        'display_name': message.sender_chat.title or "Channel"
                    }
                
                # Add to messages list
                messages.append({
                    'message_id': message.id,
                    'sender': sender_info,
                    'content': content,
                    'timestamp': message.date.astimezone(tz),
                })
                
            except Exception as e:
                console.error(f"Error processing message in history: {str(e)}")
                continue
        
        # Reverse to get chronological order (oldest first)
        messages.reverse()
        
        return messages
        
    except Exception as e:
        console.error(f"Error getting chat history: {str(e)}")
        return []

def format_chat_history(messages):
    """Format chat history for AI context"""
    try:
        if not messages:
            return ""
        
        formatted_history = []
        
        for msg in messages:
            sender_name = msg['sender']['display_name']
            content = msg['content']
            timestamp = msg['timestamp'].strftime("%H:%M")
            
            # Format: [HH:MM] Sender: Message
            formatted_history.append(f"[{timestamp}] {sender_name}: {content}")
        
        return "\n".join(formatted_history)
        
    except Exception as e:
        console.error(f"Error formatting chat history: {str(e)}")
        return ""

async def process_ai_response(client, message, prompt, photo_file_id=None):
    """Process AI response using Replicate API with system prompt and chat history"""
    try:
        # Send typing action
        await client.send_chat_action(
            chat_id=message.chat.id,
            action=enums.ChatAction.TYPING
        )
        
        # Get system prompt
        from syncara.modules.system_prompt import system_prompt
        
        # Prepare context for system prompt
        context = {
            'bot_name': 'AERIS',
            'bot_username': 'Aeris_sync',
            'user_id': message.from_user.id if message.from_user else 0
        }
        
        system_prompt_text = system_prompt.get_chat_prompt(context)
        
        # Get chat history for context
        chat_history = await get_chat_history(client, message.chat.id)
        formatted_history = format_chat_history(chat_history)
        
        # Prepare full prompt with context
        full_prompt = prompt
        
        # Add chat history if available
        if formatted_history:
            full_prompt = f"📝 **Chat History:**\n{formatted_history}\n\n💬 **Current Message:**\n{prompt}"
        
        # Generate AI response using Replicate
        console.info(f"Generating AI response for: {prompt[:50]}...")
        
        ai_response = await replicate_api.generate_response(
            prompt=full_prompt,
            system_prompt=system_prompt_text,
            temperature=0.7,
            max_tokens=2048,
            image_file_id=photo_file_id,
            client=client
        )
        
        # Process shortcodes in AI response
        try:
            from syncara.shortcode import registry
            console.info(f"Shortcode registry loaded with {len(registry.shortcodes)} handlers")
            processed_response = await process_shortcodes_in_response(ai_response, client, message)
        except ImportError as e:
            console.error(f"Import error for shortcode registry: {e}")
            processed_response = ai_response
        except Exception as e:
            console.error(f"Error processing shortcodes: {e}")
            processed_response = ai_response
        
        # Send the AI response
        await client.send_message(
            chat_id=message.chat.id,
            text=f"{processed_response}",
            reply_to_message_id=message.id
        )
        
        console.info("✅ AI response sent successfully")
        
    except Exception as e:
        console.error(f"Error in process_ai_response: {str(e)}")
        # Fallback response
        await client.send_message(
            chat_id=message.chat.id,
            text=f"❌ Maaf, terjadi kesalahan saat memproses permintaan Anda.\n\nError: {str(e)[:100]}...",
            reply_to_message_id=message.id
        )

async def process_shortcodes_in_response(response_text, client, message):
    """Process shortcodes in AI response and execute them"""
    try:
        import re
        from syncara.shortcode import registry
        
        # Pattern to match shortcodes like [CATEGORY:ACTION:params]
        shortcode_pattern = r'\[([A-Z]+:[A-Z_]+):([^\]]*)\]'
        
        async def replace_shortcode(match):
            full_shortcode = match.group(0)  # Full match like [USER:PROMOTE:7691971162]
            shortcode_name = match.group(1).strip()  # USER:PROMOTE
            params_str = match.group(2).strip()  # 7691971162
            
            console.info(f"Processing shortcode: {shortcode_name} with params: '{params_str}'")
            
            # Execute shortcode with params as string
            try:
                result = await registry.execute_shortcode(shortcode_name, client, message, params_str)
                if result:
                    console.info(f"Shortcode {shortcode_name} executed successfully")
                    return f"[Executed: {shortcode_name}]"
                else:
                    console.error(f"Shortcode {shortcode_name} failed")
                    return f"[Failed: {shortcode_name}]"
            except Exception as e:
                console.error(f"Error executing shortcode {shortcode_name}: {str(e)}")
                return f"[Error: {shortcode_name}]"
        
        # Process shortcodes one by one since re.sub doesn't support async
        processed_response = response_text
        matches = list(re.finditer(shortcode_pattern, response_text))
        
        # Process in reverse order to avoid index issues
        for match in reversed(matches):
            replacement = await replace_shortcode(match)
            start, end = match.span()
            processed_response = processed_response[:start] + replacement + processed_response[end:]
        
        return processed_response
        
    except Exception as e:
        console.error(f"Error processing shortcodes: {str(e)}")
        return response_text

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
        
        # Check handlers
        if hasattr(bot, 'dispatcher'):
            console.info(f"Bot handlers registered: {len(bot.dispatcher.groups)}")
        if hasattr(userbot, 'dispatcher'):
            console.info(f"Userbot handlers registered: {len(userbot.dispatcher.groups)}")
        
        # Add manual handler for userbot private messages
        from pyrogram.handlers import MessageHandler
        
        async def manual_userbot_handler(client, message):
            if message.chat.type == enums.ChatType.PRIVATE and message.text:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"🤖 **Halo! Saya adalah AERIS Assistant**\n\nSaya menerima pesan Anda: {message.text[:100]}...\n\nSilakan ajukan pertanyaan atau request yang Anda butuhkan!",
                    reply_to_message_id=message.id
                )
        
        userbot.add_handler(MessageHandler(manual_userbot_handler, filters.text))
        console.info("✅ Userbot private handler added")
        
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

# Hapus semua command terkait music player dan voice chat
def remove_music_commands():
    pass  # Placeholder agar tidak error import