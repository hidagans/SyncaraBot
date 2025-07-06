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
        debug_log(f"Filter checking message from {message.from_user.first_name if message.from_user else 'Unknown'}")
        
        # Skip messages from bots
        if message.from_user and message.from_user.is_bot:
            debug_log("Skipping bot message")
            return False
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
        if not userbot_info:
            debug_log("Userbot info not in cache, trying to cache...")
            userbot_info = await cache_userbot_info()
            if not userbot_info:
                debug_log("Failed to get userbot info")
                return False
        
        debug_log(f"Userbot info: @{userbot_info['username']} (ID: {userbot_info['id']})")
        
        # Check if in private chat
        if message.chat.type == enums.ChatType.PRIVATE:
            debug_log("Private chat detected - will respond")
            return True
        
        # Check if message is a reply to userbot's message
        if message.reply_to_message:
            if message.reply_to_message.from_user and message.reply_to_message.from_user.id == userbot_info['id']:
                debug_log("Reply to userbot detected - will respond")
                return True
        
        # Check if userbot is mentioned in the message
        if message.entities:
            for entity in message.entities:
                if entity.type == enums.MessageEntityType.MENTION:
                    # Extract mentioned username
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                    debug_log(f"Found mention: {mentioned_username}")
                    if mentioned_username == f"@{userbot_info['username']}":
                        debug_log("Userbot mentioned - will respond")
                        return True
                elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                    # Check if mentioned user is this userbot
                    if entity.user and entity.user.id == userbot_info['id']:
                        debug_log("Userbot text mention detected - will respond")
                        return True
        
        debug_log("No trigger conditions met - will not respond")
        return False
    except Exception as e:
        console.error(f"Error in userbot filter: {str(e)}")
        return False

# Create the filter
custom_userbot_filter = filters.create(userbot_filter)

# Bot manager commands
@bot.on_message(filters.command(["start", "help"]))
async def start_command(client, message):
    """Handle start command for the manager bot"""
    try:
        await message.reply_text(
            "🤖 **Halo! Saya adalah SyncaraBot Manager**\n\n"
            "🎯 Bot ini mengelola userbot assistant yang melayani permintaan AI.\n\n"
            "📋 **Perintah yang tersedia:**\n"
            "• `/start` atau `/help` - Tampilkan pesan ini\n"
            "• `/status` - Cek status bot dan userbot\n"
            "• `/prompts` - Lihat daftar system prompt\n"
            "• `/userbot` - Info userbot assistant\n\n"
            "💡 **Cara menggunakan:**\n"
            "Mention atau reply ke userbot assistant untuk berinteraksi dengan AI!"
        )
        console.info(f"Start command executed by user {message.from_user.id}")
    except Exception as e:
        console.error(f"Error in start_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat memproses perintah.")

@bot.on_message(filters.command("status"))
async def status_command(client, message):
    """Show bot and userbot status"""
    try:
        # Get bot info
        me = await client.get_me()
        
        status_text = f"📊 **Status SyncaraBot**\n\n"
        status_text += f"🤖 **Manager Bot:**\n"
        status_text += f"• Nama: {me.first_name}\n"
        status_text += f"• Username: @{me.username}\n"
        status_text += f"• ID: `{me.id}`\n"
        status_text += f"• Status: 🟢 Online\n\n"
        
        # Get userbot info
        if SESSION_STRING:
            try:
                userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
                if not userbot_info:
                    userbot_info = await cache_userbot_info()
                
                if userbot_info:
                    status_text += f"🎭 **Userbot Assistant:**\n"
                    status_text += f"• Nama: {userbot_info['first_name']}\n"
                    status_text += f"• Username: @{userbot_info['username']}\n"
                    status_text += f"• ID: `{userbot_info['id']}`\n"
                    status_text += f"• Status: 🟢 Online\n"
                    
                    # Get current prompt
                    current_prompt = USERBOT_PROMPT_MAPPING.get(userbot.name, "DEFAULT")
                    status_text += f"• System Prompt: {current_prompt}\n"
                else:
                    status_text += f"🎭 **Userbot Assistant:**\n"
                    status_text += f"• Status: ❌ Error loading info\n"
            except Exception as e:
                status_text += f"🎭 **Userbot Assistant:**\n"
                status_text += f"• Status: ❌ Offline ({str(e)})\n"
        else:
            status_text += f"🎭 **Userbot Assistant:**\n"
            status_text += f"• Status: ⚠️ Tidak dikonfigurasi\n"
        
        status_text += f"\n⚙️ **Fitur:**\n"
        status_text += f"• AI Chat: 🟢 Aktif\n"
        status_text += f"• Shortcode: 🟢 Aktif\n"
        status_text += f"• Riwayat Chat: {'🟢 Aktif' if CHAT_HISTORY_CONFIG['enabled'] else '🔴 Nonaktif'}\n"
        status_text += f"• System Prompt: 🟢 Aktif\n"
        
        await message.reply_text(status_text)
        console.info(f"Status command executed by user {message.from_user.id}")
        
    except Exception as e:
        console.error(f"Error in status_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil status.")

@bot.on_message(filters.command("userbot"))
async def userbot_info_command(client, message):
    """Show userbot information"""
    try:
        if not SESSION_STRING:
            await message.reply_text(
                "⚠️ **Userbot tidak dikonfigurasi**\n\n"
                "Untuk menggunakan fitur AI assistant, silakan konfigurasi SESSION_STRING di config."
            )
            return
            
        userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
            
        if not userbot_info:
            await message.reply_text("❌ Gagal mendapatkan informasi userbot.")
            return
            
        text = f"🎭 **Userbot Assistant Info:**\n\n"
        text += f"• **Nama:** {userbot_info['first_name']}\n"
        text += f"• **Username:** @{userbot_info['username']}\n"
        text += f"• **ID:** `{userbot_info['id']}`\n"
        text += f"• **Status:** 🟢 Online\n"
        
        # Get current prompt
        current_prompt = USERBOT_PROMPT_MAPPING.get(userbot.name, "DEFAULT")
        text += f"• **System Prompt:** {current_prompt}\n\n"
        
        text += f"💡 **Cara menggunakan:**\n"
        text += f"• Mention @{userbot_info['username']} untuk berinteraksi\n"
        text += f"• Reply ke pesan userbot untuk melanjutkan percakapan\n"
        text += f"• Kirim pesan langsung di chat pribadi"
            
        await message.reply_text(text)
        console.info(f"Userbot info command executed by user {message.from_user.id}")
        
    except Exception as e:
        console.error(f"Error in userbot_info_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil info userbot.")

@bot.on_message(filters.command("prompts") & filters.user(OWNER_ID))
async def list_prompts(client, message):
    """List all available system prompts"""
    try:
        # Import di dalam fungsi untuk menghindari circular import
        from syncara.modules.system_prompt import SystemPrompt
        system_prompt = SystemPrompt()
        
        available_prompts = system_prompt.get_available_prompts()
        
        if not available_prompts:
            await message.reply_text("❌ Tidak ada system prompt yang tersedia.")
            return
            
        text = f"📝 **Daftar System Prompt yang Tersedia:**\n\n"
        
        for i, prompt_name in enumerate(available_prompts, 1):
            text += f"{i}. **{prompt_name}**\n"
            
        # Add current mapping info
        text += f"\n🔗 **Current Mapping:**\n"
        if SESSION_STRING:
            current_prompt = USERBOT_PROMPT_MAPPING.get(userbot.name, "DEFAULT")
            text += f"• **{userbot.name}** → {current_prompt}\n"
        else:
            text += f"• Userbot tidak dikonfigurasi\n"
            
        await message.reply_text(text)
        console.info(f"Prompts command executed by owner {message.from_user.id}")
        
    except Exception as e:
        console.error(f"Error in list_prompts: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil daftar system prompt.")

@bot.on_message(filters.command("setprompt") & filters.user(OWNER_ID))
async def set_prompt_command(client, message):
    """Set system prompt for userbot"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Check command format
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **Format salah!**\n\n"
                "**Gunakan:** `/setprompt [prompt_name]`\n\n"
                "**Contoh:** `/setprompt AERIS`"
            )
            return
            
        # Get prompt name
        prompt_name = message.command[1].upper()
        
        # Import di dalam fungsi untuk menghindari circular import
        from syncara.modules.system_prompt import SystemPrompt
        system_prompt = SystemPrompt()
        
        # Check if prompt exists
        available_prompts = system_prompt.get_available_prompts()
        if prompt_name not in available_prompts:
            await message.reply_text(
                f"❌ **System prompt '{prompt_name}' tidak ditemukan.**\n\n"
                f"**Prompt yang tersedia:** {', '.join(available_prompts)}"
            )
            return
            
        # Update mapping
        USERBOT_PROMPT_MAPPING[userbot.name] = prompt_name
        await message.reply_text(
            f"✅ **Berhasil!**\n\n"
            f"System prompt **'{prompt_name}'** telah diatur untuk userbot **'{userbot.name}'**"
        )
        console.info(f"Prompt mapping updated: {userbot.name} -> {prompt_name}")
        
    except Exception as e:
        console.error(f"Error in set_prompt_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengatur system prompt.")

# Userbot message handler - seamless dengan decorator
@userbot.on_message(custom_userbot_filter & (filters.text | filters.photo))
async def userbot_message_handler(client, message):
    """Handle messages for userbot assistant when mentioned or replied"""
    try:
        debug_log(f"Handler triggered for message: {message.text[:50] if message.text else 'No text'}...")
        
        # Get text from either message text or caption
        text = message.text or message.caption
        
        if not text:
            debug_log("No text found in message")
            return
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(client.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
        
        if userbot_info and f"@{userbot_info['username']}" in text:
            text = text.replace(f"@{userbot_info['username']}", "").strip()
            debug_log("Removed username mention from text")
        
        # Get photo if exists
        photo_file_id = None
        if message.photo:
            photo_file_id = message.photo.file_id
            debug_log("Photo detected in message")
        
        # Send typing action
        debug_log("Sending typing action...")
        await client.send_chat_action(
            chat_id=message.chat.id,
            action=enums.ChatAction.TYPING
        )
        
        # Process AI response
        debug_log("Processing AI response...")
        await process_ai_response(client, message, text, photo_file_id)
        
    except Exception as e:
        console.error(f"Error in userbot message handler: {str(e)}")

async def get_chat_history(client, chat_id, limit=None):
    """Get chat history for context"""
    try:
        # Check if history is enabled
        if not CHAT_HISTORY_CONFIG["enabled"]:
            return []
            
        # Use configured limit if not specified
        if limit is None:
            limit = CHAT_HISTORY_CONFIG["limit"]
        
        messages = []
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(client.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
            
        if not userbot_info:
            console.error("No userbot info available for chat history")
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
                sender_name = "Unknown"
                if message.from_user:
                    if message.from_user.id == userbot_info['id']:
                        sender_name = f"{userbot_info['first_name']} (Assistant)"
                    else:
                        sender_name = message.from_user.first_name or message.from_user.username or "User"
                elif message.sender_chat:
                    sender_name = message.sender_chat.title or "Channel"
                
                # Format timestamp if enabled
                timestamp = ""
                if CHAT_HISTORY_CONFIG["include_timestamps"]:
                    timestamp = message.date.astimezone(tz).strftime("%H:%M")
                
                # Add to messages list
                messages.append({
                    'sender': sender_name,
                    'content': content,
                    'timestamp': timestamp,
                    'is_assistant': message.from_user and message.from_user.id == userbot_info['id']
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
    if not messages or not CHAT_HISTORY_CONFIG["enabled"]:
        return ""
    
    formatted_history = f"\n=== RIWAYAT PERCAKAPAN {len(messages)} PESAN TERAKHIR ===\n"
    
    for msg in messages:
        if CHAT_HISTORY_CONFIG["include_timestamps"] and msg['timestamp']:
            formatted_history += f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}\n"
        else:
            formatted_history += f"{msg['sender']}: {msg['content']}\n"
    
    formatted_history += "=== AKHIR RIWAYAT PERCAKAPAN ===\n\n"
    
    return formatted_history

async def process_ai_response(client, message, prompt, photo_file_id=None):
    """Process AI response with detailed context including current message info"""
    try:
        # Import di dalam fungsi untuk menghindari circular import
        from syncara.modules.system_prompt import SystemPrompt
        from syncara.modules.process_shortcode import process_shortcode
        
        # Get userbot information from cache
        userbot_info = USERBOT_INFO_CACHE.get(client.name)
        
        if not userbot_info:
            console.error(f"No cached info for userbot: {client.name}")
            return
        
        # Set the appropriate system prompt for this userbot
        system_prompt = SystemPrompt()
        prompt_name = USERBOT_PROMPT_MAPPING.get(client.name, "DEFAULT")
        system_prompt.set_prompt(prompt_name)
        
        # Get chat history for context
        chat_history = await get_chat_history(client, message.chat.id, limit=CHAT_HISTORY_CONFIG["limit"])
        formatted_history = format_chat_history(chat_history)
        
        # Get current message detailed info
        current_msg_info = {
            'message_id': message.id,
            'chat_id': message.chat.id,
            'from_user': {
                'id': message.from_user.id if message.from_user else None,
                'name': message.from_user.first_name if message.from_user else "Unknown",
                'username': message.from_user.username if message.from_user else None
            }
        }
        
        # Add reply info if exists
        if message.reply_to_message:
            reply = message.reply_to_message
            reply_sender = "Unknown"
            reply_sender_id = None
            reply_sender_username = None
            
            if reply.from_user:
                reply_sender = reply.from_user.first_name
                reply_sender_id = reply.from_user.id
                reply_sender_username = reply.from_user.username
                if reply.from_user.id == userbot_info['id']:
                    reply_sender = f"{userbot_info['first_name']} (Assistant)"
            elif reply.sender_chat:
                reply_sender = reply.sender_chat.title
                reply_sender_id = reply.sender_chat.id
                reply_sender_username = reply.sender_chat.username
            
            current_msg_info['reply_to'] = {
                'message_id': reply.id,
                'sender': {
                    'id': reply_sender_id,
                    'name': reply_sender,
                    'username': reply_sender_username
                },
                'content': (reply.text or reply.caption or "[Media]")[:100] + ("..." if len(reply.text or reply.caption or "") > 100 else "")
            }
        
        # Prepare context for system prompt
        context = {
            'bot_name': userbot_info['first_name'],
            'bot_username': userbot_info['username'],
            'message': current_msg_info,
            'user_id': current_msg_info['from_user']['id']
        }
        
        # Get formatted system prompt
        formatted_prompt = system_prompt.get_chat_prompt(context)
        
        # Add chat history context to system prompt
        if formatted_history:
            formatted_prompt += f"\n{formatted_history}"
            formatted_prompt += "Berdasarkan riwayat percakapan di atas, jawab pertanyaan atau tanggapi pesan berikut dengan konteks yang sesuai:\n\n"
        
        # Add current message context
        formatted_prompt += f"Pesan saat ini:\n"
        formatted_prompt += f"ID: #{current_msg_info['message_id']}\n"
        
        if current_msg_info.get('reply_to'):
            reply_info = current_msg_info['reply_to']
            formatted_prompt += f"Reply ke: #{reply_info['message_id']} dari {reply_info['sender']['name']}"
            if reply_info['sender']['username']:
                formatted_prompt += f" (@{reply_info['sender']['username']})"
            formatted_prompt += f" [ID:{reply_info['sender']['id']}]\n"
            formatted_prompt += f"Isi pesan yang di-reply: {reply_info['content']}\n"
        
        formatted_prompt += f"Dari: {current_msg_info['from_user']['name']}"
        if current_msg_info['from_user']['username']:
            formatted_prompt += f" (@{current_msg_info['from_user']['username']})"
        formatted_prompt += f" [ID:{current_msg_info['from_user']['id']}]\n"
        formatted_prompt += f"Pesan: {prompt}\n\n"
        
        # Generate AI response
        response = await replicate_api.generate_response(
            prompt=prompt,
            system_prompt=formatted_prompt,
            image_file_id=photo_file_id,
            client=client
        )
        
        # Process shortcodes in response
        processed_response = await process_shortcode(client, message, response)
        
        # Send response if not empty
        if processed_response.strip():
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=processed_response,
                    reply_to_message_id=message.id
                )
            except Exception as e:
                console.error(f"Error sending AI response: {str(e)}")
        
    except Exception as e:
        console.error(f"Error in process_ai_response: {str(e)}")
        try:
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Maaf, terjadi kesalahan dalam memproses permintaan Anda.",
                reply_to_message_id=message.id
            )
        except Exception as send_error:
            console.error(f"Error sending error message: {str(send_error)}")

# Initialize cache when module is loaded
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
        
    except Exception as e:
        console.error(f"Error initializing AI handler: {str(e)}")