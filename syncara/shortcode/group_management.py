# syncara/shortcode/group_management.py
from syncara import console
from pyrogram.types import ChatPermissions

class GroupManagementShortcode:
    def __init__(self):
        self.handlers = {
            'GROUP:DELETE_MESSAGE': self.delete_message,
            'GROUP:PIN_MESSAGE': self.pin_message,
            'GROUP:UNPIN_MESSAGE': self.unpin_message,
            'GROUP:UNPIN_ALL': self.unpin_all_messages,
            'GROUP:SET_TITLE': self.set_chat_title,
            'GROUP:SET_DESCRIPTION': self.set_chat_description,
            'GROUP:SET_PHOTO': self.set_chat_photo,
            'GROUP:DELETE_PHOTO': self.delete_chat_photo,
        }
        
        self.descriptions = {
            'GROUP:DELETE_MESSAGE': 'Delete a message by its ID. Usage: [GROUP:DELETE_MESSAGE:message_id]',
            'GROUP:PIN_MESSAGE': 'Pin a message in the chat. Usage: [GROUP:PIN_MESSAGE:message_id]',
            'GROUP:UNPIN_MESSAGE': 'Unpin a specific message. Usage: [GROUP:UNPIN_MESSAGE:message_id]',
            'GROUP:UNPIN_ALL': 'Unpin all messages in the chat. Usage: [GROUP:UNPIN_ALL:]',
            'GROUP:SET_TITLE': 'Set chat title. Usage: [GROUP:SET_TITLE:new_title]',
            'GROUP:SET_DESCRIPTION': 'Set chat description. Usage: [GROUP:SET_DESCRIPTION:new_description]',
            'GROUP:SET_PHOTO': 'Set chat photo. Usage: [GROUP:SET_PHOTO:photo_file_id]',
            'GROUP:DELETE_PHOTO': 'Delete chat photo. Usage: [GROUP:DELETE_PHOTO:]'
        }
    
    async def delete_message(self, client, message, params):
        """Delete a message by its ID"""
        try:
            message_id = int(params)
            await client.delete_messages(message.chat.id, message_id)
            console.info(f"Deleted message {message_id} in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error deleting message: {e}")
            return False
    
    async def pin_message(self, client, message, params):
        """Pin a message in the chat"""
        try:
            message_id = int(params)
            await client.pin_chat_message(
                chat_id=message.chat.id, 
                message_id=message_id,
                disable_notification=False
            )
            console.info(f"Pinned message {message_id} in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error pinning message: {e}")
            return False
    
    async def unpin_message(self, client, message, params):
        """Unpin a specific message"""
        try:
            message_id = int(params)
            await client.unpin_chat_message(
                chat_id=message.chat.id,
                message_id=message_id
            )
            console.info(f"Unpinned message {message_id} in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error unpinning message: {e}")
            return False
    
    async def unpin_all_messages(self, client, message, params):
        """Unpin all messages in the chat"""
        try:
            await client.unpin_all_chat_messages(chat_id=message.chat.id)
            console.info(f"Unpinned all messages in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error unpinning all messages: {e}")
            return False
    
    async def set_chat_title(self, client, message, params):
        """Set chat title"""
        try:
            new_title = params.strip()
            if not new_title:
                return False
            await client.set_chat_title(chat_id=message.chat.id, title=new_title)
            console.info(f"Set chat title to '{new_title}' in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error setting chat title: {e}")
            return False
    
    async def set_chat_description(self, client, message, params):
        """Set chat description"""
        try:
            new_description = params.strip()
            await client.set_chat_description(chat_id=message.chat.id, description=new_description)
            console.info(f"Set chat description in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error setting chat description: {e}")
            return False
    
    async def set_chat_photo(self, client, message, params):
        """Set chat photo"""
        try:
            photo_file_id = params.strip()
            if not photo_file_id:
                return False
            await client.set_chat_photo(chat_id=message.chat.id, photo=photo_file_id)
            console.info(f"Set chat photo in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error setting chat photo: {e}")
            return False
    
    async def delete_chat_photo(self, client, message, params):
        """Delete chat photo"""
        try:
            await client.delete_chat_photo(chat_id=message.chat.id)
            console.info(f"Deleted chat photo in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error deleting chat photo: {e}")
            return False