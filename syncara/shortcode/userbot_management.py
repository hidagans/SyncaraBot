# syncara/shortcode/userbot_management.py
from syncara import console
from syncara.userbot import get_userbot, get_all_userbots

class UserbotManagementShortcode:
    def __init__(self):
        self.handlers = {
            'USERBOT:SEND_MESSAGE': self.send_message,
            'USERBOT:JOIN_CHAT': self.join_chat,
            'USERBOT:LEAVE_CHAT': self.leave_chat,
            'USERBOT:FORWARD_MESSAGE': self.forward_message,
            'USERBOT:REACT': self.react_to_message,
            'USERBOT:EDIT_MESSAGE': self.edit_message,
            'USERBOT:SEND_PHOTO': self.send_photo,
            'USERBOT:SEND_DOCUMENT': self.send_document,
        }
        
        self.descriptions = {
            'USERBOT:SEND_MESSAGE': 'Send message using userbot. Usage: [USERBOT:SEND_MESSAGE:userbot_name:chat_id:message_text]',
            'USERBOT:JOIN_CHAT': 'Join chat using userbot. Usage: [USERBOT:JOIN_CHAT:userbot_name:invite_link_or_username]',
            'USERBOT:LEAVE_CHAT': 'Leave chat using userbot. Usage: [USERBOT:LEAVE_CHAT:userbot_name:chat_id]',
            'USERBOT:FORWARD_MESSAGE': 'Forward message using userbot. Usage: [USERBOT:FORWARD_MESSAGE:userbot_name:from_chat:message_id:to_chat]',
            'USERBOT:REACT': 'React to message using userbot. Usage: [USERBOT:REACT:userbot_name:chat_id:message_id:emoji]',
            'USERBOT:EDIT_MESSAGE': 'Edit message using userbot. Usage: [USERBOT:EDIT_MESSAGE:userbot_name:chat_id:message_id:new_text]',
            'USERBOT:SEND_PHOTO': 'Send photo using userbot. Usage: [USERBOT:SEND_PHOTO:userbot_name:chat_id:photo_file_id:caption]',
            'USERBOT:SEND_DOCUMENT': 'Send document using userbot. Usage: [USERBOT:SEND_DOCUMENT:userbot_name:chat_id:document_file_id:caption]'
        }
    
    async def send_message(self, client, message, params):
        """Send message using userbot"""
        try:
            parts = params.split(':', 2)
            if len(parts) < 3:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            chat_id = parts[1]
            text = parts[2]
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            # Convert chat_id to int if possible
            try:
                chat_id = int(chat_id)
            except ValueError:
                pass  # Use as username/chat link
            
            await userbot.send_message(chat_id=chat_id, text=text)
            console.info(f"Sent message to {chat_id} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error sending message via userbot: {e}")
            return False
    
    async def join_chat(self, client, message, params):
        """Join chat using userbot"""
        try:
            parts = params.split(':', 1)
            if len(parts) < 2:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            chat_link = parts[1]
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            await userbot.join_chat(chat_link)
            console.info(f"Joined chat {chat_link} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error joining chat via userbot: {e}")
            return False
    
    async def leave_chat(self, client, message, params):
        """Leave chat using userbot"""
        try:
            parts = params.split(':', 1)
            if len(parts) < 2:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            chat_id = parts[1]
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            # Convert chat_id to int if possible
            try:
                chat_id = int(chat_id)
            except ValueError:
                pass  # Use as username
            
            await userbot.leave_chat(chat_id)
            console.info(f"Left chat {chat_id} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error leaving chat via userbot: {e}")
            return False
    
    async def forward_message(self, client, message, params):
        """Forward message using userbot"""
        try:
            parts = params.split(':', 3)
            if len(parts) < 4:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            from_chat = parts[1]
            message_id = int(parts[2])
            to_chat = parts[3]
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            # Convert chat IDs to int if possible
            try:
                from_chat = int(from_chat)
            except ValueError:
                pass
            try:
                to_chat = int(to_chat)
            except ValueError:
                pass
            
            await userbot.forward_messages(
                chat_id=to_chat,
                from_chat_id=from_chat,
                message_ids=message_id
            )
            console.info(f"Forwarded message {message_id} from {from_chat} to {to_chat} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error forwarding message via userbot: {e}")
            return False
    
    async def react_to_message(self, client, message, params):
        """React to message using userbot"""
        try:
            parts = params.split(':', 3)
            if len(parts) < 4:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            chat_id = parts[1]
            message_id = int(parts[2])
            emoji = parts[3]
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            # Convert chat_id to int if possible
            try:
                chat_id = int(chat_id)
            except ValueError:
                pass
            
            await userbot.send_reaction(
                chat_id=chat_id,
                message_id=message_id,
                emoji=emoji
            )
            console.info(f"Reacted to message {message_id} in {chat_id} with {emoji} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error reacting to message via userbot: {e}")
            return False
    
    async def edit_message(self, client, message, params):
        """Edit message using userbot"""
        try:
            parts = params.split(':', 3)
            if len(parts) < 4:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            chat_id = parts[1]
            message_id = int(parts[2])
            new_text = parts[3]
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            # Convert chat_id to int if possible
            try:
                chat_id = int(chat_id)
            except ValueError:
                pass
            
            await userbot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text
            )
            console.info(f"Edited message {message_id} in {chat_id} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error editing message via userbot: {e}")
            return False
    
    async def send_photo(self, client, message, params):
        """Send photo using userbot"""
        try:
            parts = params.split(':', 3)
            if len(parts) < 3:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            chat_id = parts[1]
            photo_file_id = parts[2]
            caption = parts[3] if len(parts) > 3 else ""
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            # Convert chat_id to int if possible
            try:
                chat_id = int(chat_id)
            except ValueError:
                pass
            
            await userbot.send_photo(
                chat_id=chat_id,
                photo=photo_file_id,
                caption=caption if caption else None
            )
            console.info(f"Sent photo to {chat_id} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error sending photo via userbot: {e}")
            return False
    
    async def send_document(self, client, message, params):
        """Send document using userbot"""
        try:
            parts = params.split(':', 3)
            if len(parts) < 3:
                return False
                
            userbot_name = parts[0] if parts[0] else None
            chat_id = parts[1]
            document_file_id = parts[2]
            caption = parts[3] if len(parts) > 3 else ""
            
            # Get userbot
            userbot = get_userbot(userbot_name)
            if not userbot:
                console.warning(f"Userbot '{userbot_name}' not found")
                return False
            
            # Convert chat_id to int if possible
            try:
                chat_id = int(chat_id)
            except ValueError:
                pass
            
            await userbot.send_document(
                chat_id=chat_id,
                document=document_file_id,
                caption=caption if caption else None
            )
            console.info(f"Sent document to {chat_id} using userbot {userbot_name}")
            return True
        except Exception as e:
            console.error(f"Error sending document via userbot: {e}")
            return False