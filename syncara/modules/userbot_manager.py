# syncara/modules/userbot_manager.py
from pyrogram import filters, Client
from pyrogram.types import CallbackQuery
from syncara import bot, userbot, console
from config.config import OWNER_ID, SESSION_STRING
from datetime import datetime
import pytz

@bot.on_callback_query(filters.regex(r"^music_"))
async def handle_music_callback(client: Client, callback_query: CallbackQuery):
    """Handle music player callbacks from bot manager"""
    try:
        from syncara.modules.music_player import music_player
        await music_player.handle_callback(client, callback_query)
    except Exception as e:
        console.error(f"Error handling music callback: {e}")
        await callback_query.answer("❌ Terjadi kesalahan.")

async def get_chat_history(client, chat_id, limit=None):
    """Get chat history with detailed information including message ID, user ID, and reply info"""
    try:
        # Import di dalam fungsi untuk menghindari circular import
        from syncara.modules.ai_handler import CHAT_HISTORY_CONFIG, USERBOT_INFO_CACHE
        
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
    if not messages:
        return ""
    
    # Import di dalam fungsi untuk menghindari circular import
    from syncara.modules.ai_handler import CHAT_HISTORY_CONFIG
    
    if not CHAT_HISTORY_CONFIG["enabled"]:
        return ""
    
    # Get chat info from first message
    chat_info = messages[0]['chat']
    
    # Build header with group/chat information
    formatted_history = f"\n=== RIWAYAT PERCAKAPAN {len(messages)} PESAN TERAKHIR ===\n"
    formatted_history += f"📍 Grup: {chat_info['title']} ({chat_info['type']})\n"
    formatted_history += f"🆔 Chat ID: {chat_info['id']}\n"
    if chat_info['username']:
        formatted_history += f"👤 Username: @{chat_info['username']}\n"
    formatted_history += "\n"
    
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
            message_line += f"↪️ Reply to #{reply['message_id']} from {reply_sender} [ID:{reply['sender']['id']}]: "
        
        message_line += f"{sender}: {msg['content']}\n"
        
        formatted_history += message_line
    
    formatted_history += "\n"
    formatted_history += "=== AKHIR RIWAYAT PERCAKAPAN ===\n\n"
    
    return formatted_history

# Simplified userbot commands since we only have one userbot now
@bot.on_message(filters.command("userbot_info") & filters.user(OWNER_ID))
async def userbot_info_command(client, message):
    """Get userbot information"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Import di dalam fungsi untuk menghindari circular import
        from syncara.modules.ai_handler import USERBOT_INFO_CACHE, USERBOT_PROMPT_MAPPING, cache_userbot_info
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
            
        if not userbot_info:
            await message.reply_text("❌ Gagal mendapatkan informasi userbot.")
            return
            
        # Get prompt name for this userbot
        prompt_name = USERBOT_PROMPT_MAPPING.get(userbot.name, "DEFAULT")
        
        text = f"🎭 **Informasi Userbot:**\n\n"
        text += f"• **Nama:** {userbot_info['first_name']}\n"
        text += f"• **Username:** @{userbot_info['username']}\n"
        text += f"• **ID:** `{userbot_info['id']}`\n"
        text += f"• **System Prompt:** {prompt_name}\n"
        text += f"• **Status:** 🟢 Online\n"
        
        await message.reply_text(text)
        
    except Exception as e:
        console.error(f"Error in userbot_info_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil informasi userbot.")

@bot.on_message(filters.command("send") & filters.user(OWNER_ID))
async def send_as_userbot(client, message):
    """Send a message as userbot to a specific chat"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/send [chat_id] [pesan]`")
            return
            
        # Get chat_id and message text
        chat_id = message.command[1]
        text = message.text.split(None, 2)[2]
        
        # Send message
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username/chat link
            pass
            
        await userbot.send_message(chat_id, text)
        await message.reply_text(f"✅ Pesan berhasil dikirim ke {chat_id}")
        
    except Exception as e:
        console.error(f"Error in send_as_userbot: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("join") & filters.user(OWNER_ID))
async def join_chat(client, message):
    """Join a chat using userbot"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Check command format
        if len(message.command) < 2:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/join [username/invite_link]`")
            return
            
        # Get chat link/username
        chat = message.command[1]
        
        # Join chat
        chat_info = await userbot.join_chat(chat)
        await message.reply_text(f"✅ Userbot berhasil bergabung ke **{chat_info.title}**")
        
    except Exception as e:
        console.error(f"Error in join_chat: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("leave") & filters.user(OWNER_ID))
async def leave_chat(client, message):
    """Leave a chat using userbot"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Check command format
        if len(message.command) < 2:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/leave [chat_id]`")
            return
            
        # Get chat_id
        chat_id = message.command[1]
        
        # Leave chat
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username
            pass
            
        await userbot.leave_chat(chat_id)
        await message.reply_text(f"✅ Userbot berhasil keluar dari chat {chat_id}")
        
    except Exception as e:
        console.error(f"Error in leave_chat: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("history") & filters.user(OWNER_ID))
async def test_history(client, message):
    """Test chat history feature"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Check command format
        if len(message.command) < 2:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/history [chat_id]`")
            return
            
        # Get chat_id
        chat_id = message.command[1]
        
        # Convert chat_id to int if possible
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username
            pass
            
        # Get chat history
        history = await get_chat_history(userbot, chat_id, limit=20)
        
        if not history:
            await message.reply_text("❌ Tidak ada riwayat chat yang ditemukan.")
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
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")