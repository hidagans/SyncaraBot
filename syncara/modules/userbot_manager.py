# syncara/modules/userbot_manager.py
from pyrogram import filters, Client
from pyrogram.types import CallbackQuery
from syncara import bot, assistant_manager, console
from config.config import OWNER_ID
from datetime import datetime
import pytz

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
    formatted_history = f"📝 **Chat History:**\n"
    formatted_history += f"📍 **Grup:** {chat_info['title']}\n"
    formatted_history += f"🆔 **Chat ID:** `{chat_info['id']}`\n"
    formatted_history += f"📱 **Type:** {chat_info['type']}\n"
    if chat_info['username']:
        formatted_history += f"👤 **Username:** @{chat_info['username']}\n"
    formatted_history += f"📊 **Total Messages:** {len(messages)}\n"
    formatted_history += "─" * 50 + "\n"
    
    for msg in messages:
        # Format timestamp
        timestamp = msg['timestamp'].strftime("%H:%M") if CHAT_HISTORY_CONFIG["include_timestamps"] else ""
        
        # Build sender info with detailed information
        sender = msg['sender']['display_name']
        sender_details = f"[ID:{msg['sender']['id']}"
        if msg['sender']['username']:
            sender_details += f" | @{msg['sender']['username']}"
        sender_details += "]"
        
        # Build message line with comprehensive info
        message_line = f"[{timestamp}] "
        
        # Add reply info if exists
        if msg['reply_to']:
            reply = msg['reply_to']
            reply_sender = reply['sender']['display_name']
            reply_details = f"[ID:{reply['sender']['id']}"
            if reply['sender']['username']:
                reply_details += f" | @{reply['sender']['username']}"
            reply_details += "]"
            
            # Truncate reply content if too long
            reply_content = reply['content']
            if len(reply_content) > 60:
                reply_content = reply_content[:60] + "..."
            
            message_line += f"↪️ **Reply to #{reply['message_id']}** from {reply_sender} {reply_details}: \"{reply_content}\" → "
        
        # Add main message with full details
        message_line += f"**#{msg['message_id']}** 〈 {sender} {sender_details} 〉: {msg['content']}\n"
        
        formatted_history += message_line
    
    formatted_history += "─" * 50 + "\n"
    
    return formatted_history

# Assistant management commands
@bot.on_message(filters.command("userbot_info") & filters.user(OWNER_ID))
async def userbot_info_command(client, message):
    """Get assistant information"""
    try:
        active_assistants = assistant_manager.get_active_assistants()
        
        if not active_assistants:
            await message.reply_text("⚠️ Tidak ada assistant yang aktif.")
            return
        
        text = f"🎭 **Informasi Assistant:**\n\n"
        
        for assistant_id in active_assistants:
            assistant = assistant_manager.get_assistant(assistant_id)
            config = assistant_manager.get_assistant_config(assistant_id)
            
            if assistant and config:
                try:
                    me = await assistant.get_me()
                    status = "🟢 Online" if assistant.is_connected else "🔴 Offline"
                    
                    text += f"{config['emoji']} **{config['name']}**\n"
                    text += f"• **Username:** @{config['username']}\n"
                    text += f"• **ID:** `{me.id}`\n"
                    text += f"• **Personality:** {config['personality']}\n"
                    text += f"• **Status:** {status}\n\n"
                    
                except Exception as e:
                    text += f"{config['emoji']} **{config['name']}**\n"
                    text += f"• **Username:** @{config['username']}\n"
                    text += f"• **Status:** ❌ Error\n\n"
        
        await message.reply_text(text)
        
    except Exception as e:
        console.error(f"Error in userbot_info_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil informasi assistant.")

@bot.on_message(filters.command("send") & filters.user(OWNER_ID))
async def send_as_userbot(client, message):
    """Send a message as assistant to a specific chat"""
    try:
        active_assistants = assistant_manager.get_active_assistants()
        
        if not active_assistants:
            await message.reply_text("⚠️ Tidak ada assistant yang aktif.")
            return
            
        # Check command format
        if len(message.command) < 4:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/send [ASSISTANT] [chat_id] [pesan]`\n\n**Assistant yang tersedia:** " + ", ".join(active_assistants))
            return
            
        # Get assistant, chat_id and message text
        assistant_id = message.command[1].upper()
        chat_id = message.command[2]
        text = message.text.split(None, 3)[3]
        
        # Get assistant
        assistant = assistant_manager.get_assistant(assistant_id)
        if not assistant:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak ditemukan atau tidak aktif.")
            return
        
        # Send message
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username/chat link
            pass
            
        await assistant.send_message(chat_id, text)
        await message.reply_text(f"✅ Pesan berhasil dikirim ke {chat_id} menggunakan {assistant_id}")
        
    except Exception as e:
        console.error(f"Error in send_as_userbot: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("join") & filters.user(OWNER_ID))
async def join_chat(client, message):
    """Join a chat using assistant"""
    try:
        active_assistants = assistant_manager.get_active_assistants()
        
        if not active_assistants:
            await message.reply_text("⚠️ Tidak ada assistant yang aktif.")
            return
            
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/join [ASSISTANT] [username/invite_link]`\n\n**Assistant yang tersedia:** " + ", ".join(active_assistants))
            return
            
        # Get assistant and chat link/username
        assistant_id = message.command[1].upper()
        chat = message.command[2]
        
        # Get assistant
        assistant = assistant_manager.get_assistant(assistant_id)
        if not assistant:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak ditemukan atau tidak aktif.")
            return
        
        # Join chat
        chat_info = await assistant.join_chat(chat)
        await message.reply_text(f"✅ {assistant_id} berhasil bergabung ke **{chat_info.title}**")
        
    except Exception as e:
        console.error(f"Error in join_chat: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("leave") & filters.user(OWNER_ID))
async def leave_chat(client, message):
    """Leave a chat using assistant"""
    try:
        active_assistants = assistant_manager.get_active_assistants()
        
        if not active_assistants:
            await message.reply_text("⚠️ Tidak ada assistant yang aktif.")
            return
            
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/leave [ASSISTANT] [chat_id]`\n\n**Assistant yang tersedia:** " + ", ".join(active_assistants))
            return
            
        # Get assistant and chat_id
        assistant_id = message.command[1].upper()
        chat_id = message.command[2]
        
        # Get assistant
        assistant = assistant_manager.get_assistant(assistant_id)
        if not assistant:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak ditemukan atau tidak aktif.")
            return
        
        # Leave chat
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username
            pass
            
        await assistant.leave_chat(chat_id)
        await message.reply_text(f"✅ {assistant_id} berhasil keluar dari chat {chat_id}")
        
    except Exception as e:
        console.error(f"Error in leave_chat: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

@bot.on_message(filters.command("history") & filters.user(OWNER_ID))
async def test_history(client, message):
    """Test chat history feature"""
    try:
        active_assistants = assistant_manager.get_active_assistants()
        
        if not active_assistants:
            await message.reply_text("⚠️ Tidak ada assistant yang aktif.")
            return
            
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("❌ **Format salah!**\n\n**Gunakan:** `/history [ASSISTANT] [chat_id]`\n\n**Assistant yang tersedia:** " + ", ".join(active_assistants))
            return
            
        # Get assistant and chat_id
        assistant_id = message.command[1].upper()
        chat_id = message.command[2]
        
        # Get assistant
        assistant = assistant_manager.get_assistant(assistant_id)
        if not assistant:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak ditemukan atau tidak aktif.")
            return
        
        # Convert chat_id to int if possible
        try:
            chat_id = int(chat_id)
        except ValueError:
            # If not numeric, use as username
            pass
            
        # Get chat history
        history = await get_chat_history(assistant, chat_id, limit=20)
        
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
                await message.reply_text(f"**Riwayat Chat {assistant_id} (Bagian {i+1}/{len(chunks)}):**\n\n{chunk}")
        else:
            await message.reply_text(f"**Riwayat Chat {assistant_id}:**\n\n{formatted}")
        
    except Exception as e:
        console.error(f"Error in test_history: {str(e)}")
        await message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")