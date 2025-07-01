# syncara/modules/userbot_manager.py
from pyrogram import filters
from syncara import bot, console
from syncara.userbot import get_userbot, get_all_userbots, get_userbot_names
from syncara.modules.ai_handler import USERBOT_PROMPT_MAPPING
from syncara.modules.system_prompt import SystemPrompt
from config.config import OWNER_ID

# Inisialisasi komponen
system_prompt = SystemPrompt()

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