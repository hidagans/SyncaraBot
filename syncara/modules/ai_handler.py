# syncara/modules/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, userbot, console
from .system_prompt import SystemPrompt
from .process_shortcode import process_shortcode
from config.config import OWNER_ID, SESSION_STRING
from datetime import datetime
import pytz

# Inisialisasi komponen
system_prompt = SystemPrompt()
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
        # Get userbot information from cache
        userbot_info = USERBOT_INFO_CACHE.get(client.name)
        
        if not userbot_info:
            console.error(f"No cached info for userbot: {client.name}")
            return
        
        # Set the appropriate system prompt for this userbot
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
            'message': current_msg_info
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

# Additional utility commands for owner
@bot.on_message(filters.command("historyconfig") & filters.user(OWNER_ID))
async def configure_history(client, message):
    """Configure chat history settings"""
    try:
        # Check command format
        if len(message.command) < 2:
            # Show current config
            config_text = f"⚙️ **Konfigurasi Riwayat Chat:**\n\n"
            config_text += f"• Status: {'🟢 Aktif' if CHAT_HISTORY_CONFIG['enabled'] else '🔴 Nonaktif'}\n"
            config_text += f"• Jumlah Pesan: {CHAT_HISTORY_CONFIG['limit']}\n"
            config_text += f"• Info Media: {'✅ Ya' if CHAT_HISTORY_CONFIG['include_media_info'] else '❌ Tidak'}\n"
            config_text += f"• Timestamp: {'✅ Ya' if CHAT_HISTORY_CONFIG['include_timestamps'] else '❌ Tidak'}\n\n"
            config_text += f"📋 **Perintah yang tersedia:**\n"
            config_text += f"• `/historyconfig enable/disable` - Aktifkan/nonaktifkan riwayat\n"
            config_text += f"• `/historyconfig limit [angka]` - Atur jumlah pesan (1-50)\n"
            config_text += f"• `/historyconfig media on/off` - Atur info media\n"
            config_text += f"• `/historyconfig timestamp on/off` - Atur timestamp"
            
            await message.reply_text(config_text)
            return
            
        # Get setting and value
        setting = message.command[1].lower()
        
        if setting == "enable":
            CHAT_HISTORY_CONFIG["enabled"] = True
            await message.reply_text("✅ Riwayat chat diaktifkan")
            
        elif setting == "disable":
            CHAT_HISTORY_CONFIG["enabled"] = False
            await message.reply_text("✅ Riwayat chat dinonaktifkan")
            
        elif setting == "limit":
            if len(message.command) < 3:
                await message.reply_text("❌ Gunakan: /historyconfig limit [angka]")
                return
                
            try:
                limit = int(message.command[2])
                if 1 <= limit <= 50:
                    CHAT_HISTORY_CONFIG["limit"] = limit
                    await message.reply_text(f"✅ Jumlah pesan riwayat diatur ke {limit}")
                else:
                    await message.reply_text("❌ Jumlah pesan harus antara 1-50")
            except ValueError:
                await message.reply_text("❌ Masukkan angka yang valid")
                
        elif setting == "media":
            if len(message.command) < 3:
                await message.reply_text("❌ Gunakan: /historyconfig media on/off")
                return
                
            value = message.command[2].lower()
            if value == "on":
                CHAT_HISTORY_CONFIG["include_media_info"] = True
                await message.reply_text("✅ Info media diaktifkan")
            elif value == "off":
                CHAT_HISTORY_CONFIG["include_media_info"] = False
                await message.reply_text("✅ Info media dinonaktifkan")
            else:
                await message.reply_text("❌ Gunakan 'on' atau 'off'")
                
        elif setting == "timestamp":
            if len(message.command) < 3:
                await message.reply_text("❌ Gunakan: /historyconfig timestamp on/off")
                return
                
            value = message.command[2].lower()
            if value == "on":
                CHAT_HISTORY_CONFIG["include_timestamps"] = True
                await message.reply_text("✅ Timestamp diaktifkan")
            elif value == "off":
                CHAT_HISTORY_CONFIG["include_timestamps"] = False
                await message.reply_text("✅ Timestamp dinonaktifkan")
            else:
                await message.reply_text("❌ Gunakan 'on' atau 'off'")
                
        else:
            await message.reply_text("❌ Setting tidak dikenal. Gunakan: enable, disable, limit, media, atau timestamp")
        
    except Exception as e:
        console.error(f"Error in configure_history: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengatur konfigurasi.")

@bot.on_message(filters.command("test") & filters.user(OWNER_ID))
async def test_ai_command(client, message):
    """Test AI response functionality"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Check command format
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **Format salah!**\n\n"
                "**Gunakan:** `/test [pesan_test]`\n\n"
                "**Contoh:** `/test Halo, apa kabar?`"
            )
            return
            
        # Get test message
        test_message = " ".join(message.command[1:])
        
        await message.reply_text("🧪 Menguji respons AI...")
        
        # Create a mock message object for testing
        class MockMessage:
            def __init__(self, text, chat_id, message_id, from_user_id):
                self.text = text
                self.caption = None
                self.photo = None
                self.chat = type('Chat', (), {'id': chat_id, 'type': enums.ChatType.PRIVATE})()
                self.id = message_id
                self.from_user = type('User', (), {
                    'id': from_user_id,
                    'first_name': 'Test User',
                    'username': 'testuser'
                })()
                self.reply_to_message = None
        
        # Create mock message
        mock_msg = MockMessage(
            text=test_message,
            chat_id=message.chat.id,
            message_id=999999,
            from_user_id=message.from_user.id
        )
        
        # Process AI response
        await process_ai_response(userbot, mock_msg, test_message)
        
        await message.edit_text("✅ Test AI selesai! Periksa respons di atas.")
        
    except Exception as e:
        console.error(f"Error in test_ai_command: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan saat menguji AI: {str(e)}")

@bot.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_command(client, message):
    """Show detailed statistics"""
    try:
        # Get bot info
        me = await client.get_me()
        
        # Get userbot info
        userbot_info = None
        if SESSION_STRING:
            userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
            if not userbot_info:
                userbot_info = await cache_userbot_info()
        
        # Format stats message
        stats_text = f"📊 **Statistik Lengkap SyncaraBot**\n\n"
        
        # Bot Manager Stats
        stats_text += f"🤖 **Manager Bot:**\n"
        stats_text += f"• Nama: {me.first_name}\n"
        stats_text += f"• Username: @{me.username}\n"
        stats_text += f"• ID: `{me.id}`\n"
        stats_text += f"• Status: 🟢 Online\n\n"
        
        # Userbot Stats
        if userbot_info:
            stats_text += f"🎭 **Userbot Assistant:**\n"
            stats_text += f"• Nama: {userbot_info['first_name']}\n"
            stats_text += f"• Username: @{userbot_info['username']}\n"
            stats_text += f"• ID: `{userbot_info['id']}`\n"
            stats_text += f"• Status: 🟢 Online\n"
            
            current_prompt = USERBOT_PROMPT_MAPPING.get(userbot.name, "DEFAULT")
            stats_text += f"• System Prompt: {current_prompt}\n\n"
        else:
            stats_text += f"🎭 **Userbot Assistant:**\n"
            stats_text += f"• Status: ⚠️ Tidak dikonfigurasi\n\n"
        
        # Configuration Stats
        stats_text += f"⚙️ **Konfigurasi:**\n"
        stats_text += f"• Riwayat Chat: {'🟢 Aktif' if CHAT_HISTORY_CONFIG['enabled'] else '🔴 Nonaktif'}\n"
        stats_text += f"• Limit Riwayat: {CHAT_HISTORY_CONFIG['limit']} pesan\n"
        stats_text += f"• Info Media: {'✅ Ya' if CHAT_HISTORY_CONFIG['include_media_info'] else '❌ Tidak'}\n"
        stats_text += f"• Timestamp: {'✅ Ya' if CHAT_HISTORY_CONFIG['include_timestamps'] else '❌ Tidak'}\n\n"
        
        # System Prompt Stats
        available_prompts = system_prompt.get_available_prompts()
        stats_text += f"📝 **System Prompts:**\n"
        stats_text += f"• Tersedia: {len(available_prompts)} prompt\n"
        if userbot_info:
            current_prompt = USERBOT_PROMPT_MAPPING.get(userbot.name, "DEFAULT")
            stats_text += f"• Aktif: {current_prompt}\n"
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        console.error(f"Error in stats_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil statistik.")

@bot.on_message(filters.command("health") & filters.user(OWNER_ID))
async def health_check_command(client, message):
    """Perform and display health check"""
    try:
        await message.reply_text("🏥 Melakukan pemeriksaan kesehatan sistem...")
        
        health_status = {
            "bot_manager": False,
            "userbot": False,
            "system_prompt": False,
            "replicate_api": False,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check bot manager
        try:
            me = await client.get_me()
            health_status["bot_manager"] = True
        except Exception as e:
            console.error(f"Bot manager health check failed: {str(e)}")
        
        # Check userbot
        if SESSION_STRING:
            try:
                userbot_info = await cache_userbot_info()
                health_status["userbot"] = bool(userbot_info)
            except Exception as e:
                console.error(f"Userbot health check failed: {str(e)}")
        
        # Check system prompt
        try:
            prompts = system_prompt.get_available_prompts()
            health_status["system_prompt"] = len(prompts) > 0
        except Exception as e:
            console.error(f"System prompt health check failed: {str(e)}")
        
        # Check Replicate API
        try:
            # Simple test to see if API is accessible
            health_status["replicate_api"] = hasattr(replicate_api, 'generate_response')
        except Exception as e:
            console.error(f"Replicate API health check failed: {str(e)}")
        
        # Format health check results
        health_text = f"🏥 **Pemeriksaan Kesehatan Sistem**\n\n"
        health_text += f"⏰ **Waktu:** {health_status['timestamp']}\n\n"
        
        # Check each component
        components = [
            ("🤖 Bot Manager", health_status["bot_manager"]),
            ("🎭 Userbot", health_status["userbot"]),
            ("📝 System Prompt", health_status["system_prompt"]),
            ("🤖 Replicate API", health_status["replicate_api"])
        ]
        
        all_healthy = True
        for name, status in components:
            icon = "✅" if status else "❌"
            health_text += f"{icon} {name}: {'Sehat' if status else 'Bermasalah'}\n"
            if not status:
                all_healthy = False
        
        # Overall status
        health_text += f"\n🎯 **Status Keseluruhan:** "
        health_text += f"{'✅ Semua Sistem Sehat' if all_healthy else '⚠️ Ada Masalah pada Sistem'}"
        
        await message.edit_text(health_text)
        
    except Exception as e:
        console.error(f"Error in health_check_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat pemeriksaan kesehatan.")

# Initialize cache when module is loaded
async def initialize_ai_handler():
    """Initialize AI handler components"""
    try:
        console.info("Initializing AI handler...")
        
        # Cache userbot info if available
        if SESSION_STRING:
            await cache_userbot_info()
            console.info("AI handler initialized with userbot support")
        else:
            console.warning("AI handler initialized without userbot")
        
    except Exception as e:
        console.error(f"Error initializing AI handler: {str(e)}")