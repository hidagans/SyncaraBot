# syncara/modules/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, console
from .system_prompt import SystemPrompt
from .process_shortcode import process_shortcode
from syncara.userbot import get_userbot, get_all_userbots, get_userbot_names
from config.config import OWNER_ID
from datetime import datetime
import pytz
import asyncio

# Inisialisasi komponen
system_prompt = SystemPrompt()
replicate_api = ReplicateAPI()

# Cache untuk informasi userbot agar tidak flood API
USERBOT_INFO_CACHE = {}

# Mapping userbot name to system prompt name
USERBOT_PROMPT_MAPPING = {
    "userbot1": "AERIS",
    "userbot2": "KAIROS",
    "userbot3": "LYRA",
    "userbot4": "NOVA",
    "userbot5": "ZEKE"
}

# Konfigurasi untuk mengatur jumlah pesan riwayat
CHAT_HISTORY_CONFIG = {
    "enabled": True,
    "limit": 20,
    "include_media_info": True,
    "include_timestamps": True
}

async def cache_userbot_info(userbot_client, userbot_name):
    """Cache userbot information to avoid API flood"""
    try:
        if userbot_name not in USERBOT_INFO_CACHE:
            me = await userbot_client.get_me()
            USERBOT_INFO_CACHE[userbot_name] = {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name
            }
            console.info(f"Cached info for userbot: {userbot_name} (@{me.username})")
        return USERBOT_INFO_CACHE[userbot_name]
    except Exception as e:
        console.error(f"Error caching userbot info for {userbot_name}: {str(e)}")
        return None

# Bot manager hanya menerima perintah dari owner
@bot.on_message(filters.command(["start", "help"]))
async def start_command(client, message):
    """Handle start command for the manager bot"""
    try:
        await message.reply_text(
            "👋 **Halo! Saya adalah SyncaraBot Manager**\n\n"
            "🤖 Bot ini mengelola userbot assistant yang melayani permintaan AI.\n\n"
            "📝 **Perintah yang tersedia:**\n"
            "• `/start` atau `/help` - Tampilkan pesan ini\n"
            "• `/status` - Cek status bot dan userbot\n"
            "• `/prompts` - Lihat daftar system prompt\n"
            "• `/userbots` - Lihat daftar userbot\n\n"
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
        
        status_text = f"🤖 **Status SyncaraBot**\n\n"
        status_text += f"📱 **Manager Bot:**\n"
        status_text += f"• Nama: {me.first_name}\n"
        status_text += f"• Username: @{me.username}\n"
        status_text += f"• ID: `{me.id}`\n"
        status_text += f"• Status: ✅ Online\n\n"
        
        # Get userbot info
        userbots = get_all_userbots()
        if userbots:
            status_text += f"👥 **Userbot Assistant ({len(userbots)} aktif):**\n"
            for i, userbot in enumerate(userbots, 1):
                try:
                    userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
                    if userbot_info:
                        status_text += f"• {i}. {userbot_info['first_name']} (@{userbot_info['username']})\n"
                    else:
                        status_text += f"• {i}. {userbot.name} (Loading...)\n"
                except:
                    status_text += f"• {i}. {userbot.name} (Error)\n"
        else:
            status_text += f"👥 **Userbot Assistant:**\n• ❌ Tidak ada userbot aktif\n"
        
        status_text += f"\n📊 **Fitur:**\n"
        status_text += f"• AI Chat: ✅ Aktif\n"
        status_text += f"• Shortcode: ✅ Aktif\n"
        status_text += f"• Riwayat Chat: {'✅ Aktif' if CHAT_HISTORY_CONFIG['enabled'] else '❌ Nonaktif'}\n"
        status_text += f"• System Prompt: ✅ Aktif\n"
        
        await message.reply_text(status_text)
        console.info(f"Status command executed by user {message.from_user.id}")
        
    except Exception as e:
        console.error(f"Error in status_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil status.")

@bot.on_message(filters.command("userbots"))
async def list_userbots_command(client, message):
    """List all available userbots"""
    try:
        userbots = get_all_userbots()
        
        if not userbots:
            await message.reply_text("❌ Tidak ada userbot yang tersedia.")
            return
            
        text = "👥 **Daftar Userbot Assistant:**\n\n"
        
        for i, userbot in enumerate(userbots, 1):
            try:
                userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
                if userbot_info:
                    text += f"{i}. **{userbot_info['first_name']}**\n"
                    text += f"   • Username: @{userbot_info['username']}\n"
                    text += f"   • ID: `{userbot_info['id']}`\n"
                    text += f"   • Status: ✅ Online\n\n"
                else:
                    text += f"{i}. **{userbot.name}**\n"
                    text += f"   • Status: 🔄 Loading...\n\n"
            except Exception as e:
                text += f"{i}. **{userbot.name}**\n"
                text += f"   • Status: ❌ Error\n\n"
        
        text += "💡 **Cara menggunakan:**\n"
        text += "Mention (@username) atau reply ke pesan userbot untuk berinteraksi dengan AI!"
            
        await message.reply_text(text)
        console.info(f"Userbots command executed by user {message.from_user.id}")
        
    except Exception as e:
        console.error(f"Error in list_userbots_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil daftar userbot.")


@bot.on_message(filters.command("prompts") & filters.user(OWNER_ID))
async def list_prompts(client, message):
    """List all available system prompts"""
    try:
        available_prompts = system_prompt.get_available_prompts()
        
        if not available_prompts:
            await message.reply_text("❌ Tidak ada system prompt yang tersedia.")
            return
            
        text = "📝 **Daftar System Prompt yang Tersedia:**\n\n"
        
        for i, prompt_name in enumerate(available_prompts, 1):
            text += f"{i}. **{prompt_name}**\n"
            
        # Add mapping info
        text += "\n🔄 **Mapping Userbot ke System Prompt:**\n\n"
        for userbot_name, prompt_name in USERBOT_PROMPT_MAPPING.items():
            text += f"• **{userbot_name}** → {prompt_name}\n"
            
        await message.reply_text(text)
        console.info(f"Prompts command executed by owner {message.from_user.id}")
        
    except Exception as e:
        console.error(f"Error in list_prompts: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil daftar system prompt.")

@bot.on_message(filters.command("setprompt") & filters.user(OWNER_ID))
async def set_prompt_command(client, message):
    """Set system prompt for a userbot"""
    try:
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("Gunakan: /setprompt [userbot_name] [prompt_name]")
            return
            
        # Get userbot name and prompt name
        userbot_name = message.command[1].lower()
        prompt_name = message.command[2].upper()
        
        # Check if userbot exists
        userbot_names = get_userbot_names()
        if userbot_name not in userbot_names:
            await message.reply_text(f"Userbot '{userbot_name}' tidak ditemukan.\n\nUserbot yang tersedia: {', '.join(userbot_names)}")
            return
            
        # Check if prompt exists
        available_prompts = system_prompt.get_available_prompts()
        if prompt_name not in available_prompts:
            await message.reply_text(f"System prompt '{prompt_name}' tidak ditemukan.\n\nPrompt yang tersedia: {', '.join(available_prompts)}")
            return
            
        # Update mapping
        USERBOT_PROMPT_MAPPING[userbot_name] = prompt_name
        await message.reply_text(f"Berhasil mengatur system prompt '{prompt_name}' untuk userbot '{userbot_name}'")
        
    except Exception as e:
        console.error(f"Error in set_prompt_command: {str(e)}")
        await message.reply_text("Terjadi kesalahan saat mengatur system prompt.")

@bot.on_message(filters.command("setprompt") & filters.user(OWNER_ID))
async def set_prompt_command(client, message):
    """Set system prompt for a userbot"""
    try:
        # Check command format
        if len(message.command) < 3:
            await message.reply_text(
                "❌ **Format salah!**\n\n"
                "**Gunakan:** `/setprompt [userbot_name] [prompt_name]`\n\n"
                "**Contoh:** `/setprompt userbot1 AERIS`"
            )
            return
            
        # Get userbot name and prompt name
        userbot_name = message.command[1].lower()
        prompt_name = message.command[2].upper()
        
        # Check if userbot exists
        userbot_names = get_userbot_names()
        if userbot_name not in userbot_names:
            await message.reply_text(
                f"❌ **Userbot '{userbot_name}' tidak ditemukan.**\n\n"
                f"**Userbot yang tersedia:** {', '.join(userbot_names)}"
            )
            return
            
        # Check if prompt exists
        available_prompts = system_prompt.get_available_prompts()
        if prompt_name not in available_prompts:
            await message.reply_text(
                f"❌ **System prompt '{prompt_name}' tidak ditemukan.**\n\n"
                f"**Prompt yang tersedia:** {', '.join(available_prompts)}"
            )
            return
            
        # Update mapping
        USERBOT_PROMPT_MAPPING[userbot_name] = prompt_name
        await message.reply_text(
            f"✅ **Berhasil!**\n\n"
            f"System prompt **'{prompt_name}'** telah diatur untuk userbot **'{userbot_name}'**"
        )
        console.info(f"Prompt mapping updated: {userbot_name} -> {prompt_name}")
        
    except Exception as e:
        console.error(f"Error in set_prompt_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengatur system prompt.")

@bot.on_message(filters.command("historyconfig") & filters.user(OWNER_ID))
async def configure_history(client, message):
    """Configure chat history settings"""
    try:
        # Check command format
        if len(message.command) < 2:
            # Show current config
            config_text = "⚙️ **Konfigurasi Riwayat Chat:**\n\n"
            config_text += f"- Status: {'Aktif' if CHAT_HISTORY_CONFIG['enabled'] else 'Nonaktif'}\n"
            config_text += f"- Jumlah Pesan: {CHAT_HISTORY_CONFIG['limit']}\n"
            config_text += f"- Info Media: {'Ya' if CHAT_HISTORY_CONFIG['include_media_info'] else 'Tidak'}\n"
            config_text += f"- Timestamp: {'Ya' if CHAT_HISTORY_CONFIG['include_timestamps'] else 'Tidak'}\n\n"
            config_text += "**Perintah yang tersedia:**\n"
            config_text += "- `/historyconfig enable/disable` - Aktifkan/nonaktifkan riwayat\n"
            config_text += "- `/historyconfig limit [angka]` - Atur jumlah pesan (1-50)\n"
            config_text += "- `/historyconfig media on/off` - Atur info media\n"
            config_text += "- `/historyconfig timestamp on/off` - Atur timestamp"
            
            await message.reply_text(config_text)
            return
            
        # Get setting and value
        setting = message.command[1].lower()
        
        if setting == "enable":
            CHAT_HISTORY_CONFIG["enabled"] = True
            await message.reply_text("✅ Riwayat chat diaktifkan")
            
        elif setting == "disable":
            CHAT_HISTORY_CONFIG["enabled"] = False
            await message.reply_text("❌ Riwayat chat dinonaktifkan")
            
        elif setting == "limit":
            if len(message.command) < 3:
                await message.reply_text("Gunakan: /historyconfig limit [angka]")
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
                await message.reply_text("Gunakan: /historyconfig media on/off")
                return
                
            value = message.command[2].lower()
            if value == "on":
                CHAT_HISTORY_CONFIG["include_media_info"] = True
                await message.reply_text("✅ Info media diaktifkan")
            elif value == "off":
                CHAT_HISTORY_CONFIG["include_media_info"] = False
                await message.reply_text("❌ Info media dinonaktifkan")
            else:
                await message.reply_text("❌ Gunakan 'on' atau 'off'")
                
        elif setting == "timestamp":
            if len(message.command) < 3:
                await message.reply_text("Gunakan: /historyconfig timestamp on/off")
                return
                
            value = message.command[2].lower()
            if value == "on":
                CHAT_HISTORY_CONFIG["include_timestamps"] = True
                await message.reply_text("✅ Timestamp diaktifkan")
            elif value == "off":
                CHAT_HISTORY_CONFIG["include_timestamps"] = False
                await message.reply_text("❌ Timestamp dinonaktifkan")
            else:
                await message.reply_text("❌ Gunakan 'on' atau 'off'")
                
        else:
            await message.reply_text("❌ Setting tidak dikenal. Gunakan: enable, disable, limit, media, atau timestamp")
        
    except Exception as e:
        console.error(f"Error in configure_history: {str(e)}")
        await message.reply_text("Terjadi kesalahan saat mengatur konfigurasi.")

@bot.on_message(filters.command("history") & filters.user(OWNER_ID))
async def test_history(client, message):
    """Test chat history feature"""
    try:
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("Gunakan: /history [userbot_name] [chat_id]")
            return
            
        # Get userbot name and chat_id
        userbot_name = message.command[1]
        chat_id = message.command[2]
        
        # Get userbot
        userbot = get_userbot(userbot_name)
        if not userbot:
            await message.reply_text(f"Userbot '{userbot_name}' tidak ditemukan.")
            return
            
        # Convert chat_id to int if possible
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username
            pass
            
        # Get chat history
        history = await get_chat_history(userbot, chat_id, limit=20)
        
        if not history:
            await message.reply_text("Tidak ada riwayat chat yang ditemukan.")
            return
            
        # Format and send history
        formatted = format_chat_history(history)
        
        # Split message if too long
        if len(formatted) > 4000:
            # Send in chunks
            chunks = [formatted[i:i+4000] for i in range(0, len(formatted), 4000)]
            for i, chunk in enumerate(chunks):
                await message.reply_text(f"**Riwayat Chat (Bagian {i+1}/{len(chunks)}):**\n\n{chunk}")
        else:
            await message.reply_text(f"**Riwayat Chat:**\n\n{formatted}")
        
    except Exception as e:
        console.error(f"Error in test_history: {str(e)}")
        await message.reply_text(f"Terjadi kesalahan: {str(e)}")

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

# Userbot assistant menangani interaksi AI hanya ketika di-mention atau di-reply
async def setup_userbot_handlers():
    """Setup handlers for userbot assistant"""
    try:
        # Get all userbots
        userbots = get_all_userbots()
        if not userbots:
            console.error("No userbot available to set up handlers")
            return
            
        # Cache userbot info first to avoid API flood
        for userbot in userbots:
            userbot_name = userbot.name
            await cache_userbot_info(userbot, userbot_name)
            # Add small delay to avoid flood
            await asyncio.sleep(1)
            
        # Set up message handler for each userbot
        for userbot in userbots:
            userbot_name = userbot.name
            
            # Create custom filter for this specific userbot
            def create_userbot_filter(userbot_name):
                async def userbot_filter(_, __, message):
                    try:
                        # Skip messages from bots
                        if message.from_user and message.from_user.is_bot:
                            return False
                        
                        # Get userbot info from cache
                        userbot_info = USERBOT_INFO_CACHE.get(userbot_name)
                        if not userbot_info:
                            console.error(f"No cached info for userbot: {userbot_name}")
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
                
                return filters.create(userbot_filter)
            
            # Apply the custom filter to this userbot
            userbot_filter = create_userbot_filter(userbot_name)
            
            @userbot.on_message(userbot_filter & (filters.text | filters.photo))
            async def userbot_message_handler(client, message):
                """Handle messages for userbot assistant when mentioned or replied"""
                try:
                    # Get text from either message text or caption
                    text = message.text or message.caption
                    
                    if not text:
                        return
                    
                    # Get userbot info from cache
                    userbot_name = getattr(client, 'name', 'unknown')
                    userbot_info = USERBOT_INFO_CACHE.get(userbot_name)
                    
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
            
            console.info(f"Userbot '{userbot_name}' handler set up successfully")
        
    except Exception as e:
        console.error(f"Error setting up userbot handlers: {str(e)}")

async def process_ai_response(client, message, prompt, photo_file_id=None):
    """Process AI response with detailed context including current message info"""
    try:
        # Get userbot information from cache
        userbot_name = getattr(client, 'name', 'unknown')
        userbot_info = USERBOT_INFO_CACHE.get(userbot_name)
        
        if not userbot_info:
            console.error(f"No cached info for userbot: {userbot_name}")
            return
        
        # Set the appropriate system prompt for this userbot
        prompt_name = USERBOT_PROMPT_MAPPING.get(userbot_name, "DEFAULT")
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
                text="Maaf, terjadi kesalahan dalam memproses permintaan Anda.",
                reply_to_message_id=message.id
            )
        except:
            pass