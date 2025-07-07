# syncara/shortcode/userbot_management.py
from syncara.console import console
from pyrogram.types import ChatPermissions

async def is_admin_or_owner(client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")

class UserbotManagementShortcode:
    def __init__(self):
        self.handlers = {
            'USERBOT:STATUS': self.get_status,
            'USERBOT:INFO': self.get_info,
            'USERBOT:JOIN': self.join_chat,
            'USERBOT:LEAVE': self.leave_chat,
            'USERBOT:SEND': self.send_message,
        }
        
        self.descriptions = {
            'USERBOT:STATUS': 'Get userbot status and connection info',
            'USERBOT:INFO': 'Get detailed userbot information',
            'USERBOT:JOIN': 'Join a chat/group. Usage: [USERBOT:JOIN:chat_id]',
            'USERBOT:LEAVE': 'Leave a chat/group. Usage: [USERBOT:LEAVE:chat_id]',
            'USERBOT:SEND': 'Send message as userbot. Usage: [USERBOT:SEND:chat_id,message]',
        }
    
    async def get_status(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Get userbot status"""
        try:
            from syncara import userbot
            if userbot.is_connected:
                me = await userbot.get_me()
                status_text = f"✅ **Userbot Status:**\n\n"
                status_text += f"**Name:** {me.first_name}\n"
                status_text += f"**Username:** @{me.username}\n"
                status_text += f"**ID:** {me.id}\n"
                status_text += f"**Status:** Connected"
            else:
                status_text = "❌ Userbot not connected"
            
            await client.send_message(
                chat_id=message.chat.id,
                text=status_text,
                reply_to_message_id=message.id
            )
            return True
        except Exception as e:
            console.error(f"Error getting userbot status: {e}")
            return False
    
    async def get_info(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Get detailed userbot information"""
        try:
            from syncara import userbot
            me = await userbot.get_me()
            info_text = f"🤖 **Userbot Information:**\n\n"
            info_text += f"**Name:** {me.first_name}\n"
            info_text += f"**Username:** @{me.username}\n"
            info_text += f"**ID:** {me.id}\n"
            info_text += f"**Phone:** {me.phone_number or 'Unknown'}\n"
            info_text += f"**Connected:** {userbot.is_connected}"
            
            await client.send_message(
                chat_id=message.chat.id,
                text=info_text,
                reply_to_message_id=message.id
            )
            return True
        except Exception as e:
            console.error(f"Error getting userbot info: {e}")
            return False
    
    async def join_chat(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Join a chat/group"""
        try:
            from syncara import userbot
            chat_id = params.strip()
            if not chat_id:
                return False
            
            await userbot.join_chat(chat_id)
            await client.send_message(
                chat_id=message.chat.id,
                text=f"✅ Joined chat: {chat_id}",
                reply_to_message_id=message.id
            )
            return True
        except Exception as e:
            console.error(f"Error joining chat: {e}")
            return False
    
    async def leave_chat(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Leave a chat/group"""
        try:
            from syncara import userbot
            chat_id = params.strip()
            if not chat_id:
                return False
            
            await userbot.leave_chat(chat_id)
            await client.send_message(
                chat_id=message.chat.id,
                text=f"✅ Left chat: {chat_id}",
                reply_to_message_id=message.id
            )
            return True
        except Exception as e:
            console.error(f"Error leaving chat: {e}")
            return False
    
    async def send_message(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Send message as userbot"""
        try:
            from syncara import userbot
            # Parse params: chat_id,message_text
            parts = params.split(',', 1)
            if len(parts) < 2:
                return False
            
            chat_id = parts[0].strip()
            message_text = parts[1].strip()
            
            await userbot.send_message(
                chat_id=chat_id,
                text=message_text
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"✅ Message sent to {chat_id}",
                reply_to_message_id=message.id
            )
            return True
        except Exception as e:
            console.error(f"Error sending message: {e}")
            return False 