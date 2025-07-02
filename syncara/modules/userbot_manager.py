# syncara/modules/userbot_manager.py
from pyrogram import filters
from syncara import bot, console
from syncara.userbot import get_userbot, get_all_userbots, get_userbot_names
from syncara.modules.ai_handler import USERBOT_PROMPT_MAPPING
from syncara.modules.system_prompt import SystemPrompt
from config.config import OWNER_ID

# Inisialisasi komponen
system_prompt = SystemPrompt()

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from syncara.modules.music_player import music_player
from syncara import console

@bot.on_callback_query(filters.regex(r"^music_"))
async def handle_music_callback(client: Client, callback_query: CallbackQuery):
    """Handle music player callbacks from bot manager"""
    try:
        await music_player.handle_callback(client, callback_query)
    except Exception as e:
        console.error(f"Error handling music callback: {e}")
        await callback_query.answer("❌ Terjadi kesalahan.")

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
        
        # Get chat info
        try:
            chat = await client.get_chat(chat_id)
            chat_info = {
                'id': chat.id,
                'title': chat.title if chat.title else "Private Chat",
                'type': chat.type.name,
                'username': chat.username if hasattr(chat, 'username') else None
            }
        except Exception as e:
            console.error(f"Error getting chat info: {str(e)}")
            chat_info = {
                'id': chat_id,
                'title': "Unknown Chat",
                'type': "unknown",
                'username': None
            }
        
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
                
                # Get sender info with detailed information
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
                
                # Get reply info if exists
                reply_info = None
                if message.reply_to_message:
                    reply_msg = message.reply_to_message
                    reply_sender_info = {
                        'id': None,
                        'name': "Unknown",
                        'username': None
                    }
                    
                    if reply_msg.from_user:
                        reply_sender_info = {
                            'id': reply_msg.from_user.id,
                            'name': reply_msg.from_user.first_name or "Unknown",
                            'username': reply_msg.from_user.username
                        }
                        
                        # Check if reply is to assistant
                        if reply_msg.from_user.id == userbot_info['id']:
                            reply_sender_info['display_name'] = f"{userbot_info['first_name']} (Assistant)"
                        else:
                            reply_sender_info['display_name'] = reply_sender_info['name']
                            
                    elif reply_msg.sender_chat:
                        reply_sender_info = {
                            'id': reply_msg.sender_chat.id,
                            'name': reply_msg.sender_chat.title or "Channel",
                            'username': reply_msg.sender_chat.username,
                            'display_name': reply_msg.sender_chat.title or "Channel"
                        }
                    
                    reply_content = reply_msg.text or reply_msg.caption or "[Media]"
                    if len(reply_content) > 100:
                        reply_content = reply_content[:100] + "..."
                    
                    reply_info = {
                        'message_id': reply_msg.id,
                        'sender': reply_sender_info,
                        'content': reply_content
                    }
                
                # Add to messages list with all detailed info
                messages.append({
                    'message_id': message.id,
                    'sender': sender_info,
                    'chat': chat_info,
                    'content': content,
                    'timestamp': message.date.astimezone(tz),
                    'reply_to': reply_info
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
    """Format chat history with detailed information including group info, message IDs, user IDs, and reply info"""
    if not messages or not CHAT_HISTORY_CONFIG["enabled"]:
        return ""
    
    # Get chat info from first message
    chat_info = messages[0]['chat']
    
    # Build header with group/chat information
    formatted_history = f"\n=== RIWAYAT PERCAKAPAN {len(messages)} PESAN TERAKHIR ===\n"
    formatted_history += f"📍 Grup: {chat_info['title']} ({chat_info['type']})\n"
    formatted_history += f"🆔 Chat ID: {chat_info['id']}\n"
    if chat_info['username']:
        formatted_history += f"🔗 Username: @{chat_info['username']}\n"
    formatted_history += "──────────────────────────────────────\n"
    
    for msg in messages:
        # Format timestamp
        timestamp = msg['timestamp'].strftime("%H:%M") if CHAT_HISTORY_CONFIG["include_timestamps"] else ""
        
        # Build sender info with ID
        sender = msg['sender']['display_name']
        if msg['sender']['username']:
            sender += f" (@{msg['sender']['username']})"
        sender += f" [ID:{msg['sender']['id']}]"
        
        # Build message line with message ID
        message_line = f"[{timestamp}] #{msg['message_id']} "
        
        # Add reply info if exists
        if msg['reply_to']:
            reply = msg['reply_to']
            reply_sender = reply['sender']['display_name']
            if reply['sender']['username']:
                reply_sender += f" (@{reply['sender']['username']})"
            message_line += f"↩️ Reply to #{reply['message_id']} from {reply_sender} [ID:{reply['sender']['id']}]: "
        
        message_line += f"{sender}: {msg['content']}\n"
        
        formatted_history += message_line
    
    formatted_history += "──────────────────────────────────────\n"
    formatted_history += "=== AKHIR RIWAYAT PERCAKAPAN ===\n\n"
    
    return formatted_history

@bot.on_message(filters.command("userbots") & filters.user(OWNER_ID))
async def list_userbots(client, message):
    """List all available userbots"""
    try:
        userbot_names = get_userbot_names()
        
        if not userbot_names:
            await message.reply_text("Tidak ada userbot yang tersedia.")
            return
            
        text = "🤖 **Daftar Userbot yang Tersedia:**\n\n"
        
        for i, name in enumerate(userbot_names, 1):
            userbot = get_userbot(name)
            me = await userbot.get_me()
            prompt_name = USERBOT_PROMPT_MAPPING.get(name, "DEFAULT")
            text += f"{i}. **{name}** - @{me.username} ({me.id})\n   System Prompt: {prompt_name}\n\n"
            
        await message.reply_text(text)
        
    except Exception as e:
        console.error(f"Error in list_userbots: {str(e)}")
        await message.reply_text("Terjadi kesalahan saat mengambil daftar userbot.")

@bot.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_command(client, message):
    """Broadcast a message using all userbots"""
    try:
        # Check if there's a message to broadcast
        if len(message.command) < 2:
            await message.reply_text("Gunakan: /broadcast [pesan]")
            return
            
        # Get the message to broadcast
        broadcast_text = message.text.split(None, 1)[1]
        
        # Get all userbots
        userbots = get_all_userbots()
        if not userbots:
            await message.reply_text("Tidak ada userbot yang tersedia untuk broadcast.")
            return
            
        # Send status message
        status_msg = await message.reply_text("Memulai broadcast...")
        
        # Track success and failure
        success_count = 0
        failed_count = 0
        
        # Broadcast to all userbots' dialogs
        for userbot in userbots:
            try:
                me = await userbot.get_me()
                
                # Get all dialogs
                async for dialog in userbot.get_dialogs():
                    try:
                        # Skip bot chats and channels where we can't write
                        if dialog.chat.type == "bot" or (dialog.chat.type == "channel" and not dialog.chat.is_creator):
                            continue
                            
                        # Send message
                        await userbot.send_message(dialog.chat.id, broadcast_text)
                        success_count += 1
                        
                        # Update status every 10 successful messages
                        if success_count % 10 == 0:
                            await status_msg.edit_text(f"Broadcast sedang berjalan...\n✅ Berhasil: {success_count}\n❌ Gagal: {failed_count}")
                            
                    except Exception as e:
                        failed_count += 1
                        console.error(f"Failed to send broadcast to {dialog.chat.id}: {str(e)}")
                        
            except Exception as e:
                console.error(f"Error with userbot {userbot.name}: {str(e)}")
                
        # Send final status
        await status_msg.edit_text(f"Broadcast selesai!\n✅ Berhasil: {success_count}\n❌ Gagal: {failed_count}")
        
    except Exception as e:
        console.error(f"Error in broadcast_command: {str(e)}")
        await message.reply_text("Terjadi kesalahan saat melakukan broadcast.")

@bot.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def userbot_stats(client, message):
    """Get stats about userbots"""
    try:
        userbots = get_all_userbots()
        if not userbots:
            await message.reply_text("Tidak ada userbot yang tersedia.")
            return
            
        text = "📊 **Statistik Userbot:**\n\n"
        
        for userbot in userbots:
            try:
                me = await userbot.get_me()
                
                # Count dialogs by type
                groups = 0
                supergroups = 0
                private = 0
                channels = 0
                bots = 0
                
                async for dialog in userbot.get_dialogs():
                    if dialog.chat.type == "group":
                        groups += 1
                    elif dialog.chat.type == "supergroup":
                        supergroups += 1
                    elif dialog.chat.type == "private":
                        private += 1
                    elif dialog.chat.type == "channel":
                        channels += 1
                    elif dialog.chat.type == "bot":
                        bots += 1
                
                total = groups + supergroups + private + channels + bots
                
                # Get prompt name for this userbot
                prompt_name = USERBOT_PROMPT_MAPPING.get(userbot.name, "DEFAULT")
                
                text += f"**@{me.username}** ({userbot.name}):\n"
                text += f"- System Prompt: {prompt_name}\n"
                text += f"- Total Chats: {total}\n"
                text += f"- Grup: {groups}\n"
                text += f"- Supergrup: {supergroups}\n"
                text += f"- Private: {private}\n"
                text += f"- Channel: {channels}\n"
                text += f"- Bot: {bots}\n\n"
                
            except Exception as e:
                console.error(f"Error getting stats for userbot: {str(e)}")
                text += f"**{userbot.name}**: Error getting stats\n\n"
                
        await message.reply_text(text)
        
    except Exception as e:
        console.error(f"Error in userbot_stats: {str(e)}")
        await message.reply_text("Terjadi kesalahan saat mengambil statistik userbot.")

@bot.on_message(filters.command("send") & filters.user(OWNER_ID))
async def send_as_userbot(client, message):
    """Send a message as userbot to a specific chat"""
    try:
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("Gunakan: /send [userbot_name] [chat_id] [pesan]")
            return
            
        # Get userbot name, chat_id and message text
        userbot_name = message.command[1]
        chat_id = message.command[2]
        text = message.text.split(None, 3)[3]
        
        # Get userbot
        userbot = get_userbot(userbot_name)
        if not userbot:
            await message.reply_text(f"Userbot '{userbot_name}' tidak ditemukan.")
            return
            
        # Send message
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username/chat link
            pass
            
        await userbot.send_message(chat_id, text)
        await message.reply_text(f"Pesan berhasil dikirim ke {chat_id} menggunakan userbot '{userbot_name}'")
        
    except Exception as e:
        console.error(f"Error in send_as_userbot: {str(e)}")
        await message.reply_text(f"Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("join") & filters.user(OWNER_ID))
async def join_chat(client, message):
    """Join a chat using userbot"""
    try:
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("Gunakan: /join [userbot_name] [username/invite_link]")
            return
            
        # Get userbot name and chat link/username
        userbot_name = message.command[1]
        chat = message.command[2]
        
        # Get userbot
        userbot = get_userbot(userbot_name)
        if not userbot:
            await message.reply_text(f"Userbot '{userbot_name}' tidak ditemukan.")
            return
            
        # Join chat
        chat = await userbot.join_chat(chat)
        await message.reply_text(f"Userbot '{userbot_name}' berhasil bergabung ke {chat.title}")
        
    except Exception as e:
        console.error(f"Error in join_chat: {str(e)}")
        await message.reply_text(f"Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("leave") & filters.user(OWNER_ID))
async def leave_chat(client, message):
    """Leave a chat using userbot"""
    try:
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("Gunakan: /leave [userbot_name] [chat_id]")
            return
            
        # Get userbot name and chat_id
        userbot_name = message.command[1]
        chat_id = message.command[2]
        
        # Get userbot
        userbot = get_userbot(userbot_name)
        if not userbot:
            await message.reply_text(f"Userbot '{userbot_name}' tidak ditemukan.")
            return
            
        # Leave chat
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username
            pass
            
        await userbot.leave_chat(chat_id)
        await message.reply_text(f"Userbot '{userbot_name}' berhasil keluar dari chat {chat_id}")
        
    except Exception as e:
        console.error(f"Error in leave_chat: {str(e)}")
        await message.reply_text(f"Terjadi kesalahan: {str(e)}")

# Tambahan perintah untuk mengatur fitur riwayat chat
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

# Konfigurasi untuk mengatur jumlah pesan riwayat
CHAT_HISTORY_CONFIG = {
    "enabled": True,
    "limit": 20,
    "include_media_info": True,
    "include_timestamps": True
}

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