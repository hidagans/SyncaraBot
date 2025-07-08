# syncara/shortcode/group_management.py
from syncara.console import console
from pyrogram.types import ChatPermissions
import asyncio

async def is_admin_or_owner(client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")

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
            'GROUP:DELETE_MESSAGE': 'Delete a message by its ID. Usage: [GROUP:DELETE_MESSAGE:message_id] or [GROUP:DELETE_MESSAGE:current_message_id] or [GROUP:DELETE_MESSAGE:reply_message]',
            'GROUP:PIN_MESSAGE': 'Pin a message in the chat. Usage: [GROUP:PIN_MESSAGE:message_id] or [GROUP:PIN_MESSAGE:current_message_id] or [GROUP:PIN_MESSAGE:reply_message]',
            'GROUP:UNPIN_MESSAGE': 'Unpin a specific message. Usage: [GROUP:UNPIN_MESSAGE:message_id] or [GROUP:UNPIN_MESSAGE:current_message_id] or [GROUP:UNPIN_MESSAGE:reply_message]',
            'GROUP:UNPIN_ALL': 'Unpin all messages in the chat. Usage: [GROUP:UNPIN_ALL:]',
            'GROUP:SET_TITLE': 'Set chat title. Usage: [GROUP:SET_TITLE:new_title]',
            'GROUP:SET_DESCRIPTION': 'Set chat description. Usage: [GROUP:SET_DESCRIPTION:new_description]',
            'GROUP:SET_PHOTO': 'Set chat photo. Usage: [GROUP:SET_PHOTO:photo_file_id]',
            'GROUP:DELETE_PHOTO': 'Delete chat photo. Usage: [GROUP:DELETE_PHOTO:]'
        }
        
        self.pending_responses = {}
    
    async def delete_message(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        """Delete a message by its ID"""
        try:
            params = params.strip()
            
            # Handle special keywords
            if params.lower() in ['current_message_id', 'this_message', 'current']:
                # Use the message that triggered this shortcode
                message_id = message.id
                console.info(f"Using current message ID: {message_id}")
            elif params.lower() in ['reply_message', 'replied_message']:
                # Delete the message being replied to
                if message.reply_to_message:
                    message_id = message.reply_to_message.id
                    console.info(f"Using replied message ID: {message_id}")
                else:
                    console.error("No replied message found")
                    return False
            else:
                # Try to parse as integer
                try:
                    message_id = int(params)
                except ValueError:
                    console.error(f"Invalid message ID parameter: {params}")
                    # Store error for delayed sending
                    response_id = f"group_delete_error_{message.id}"
                    self.pending_responses[response_id] = {
                        'text': f"❌ ID pesan tidak valid: {params}. Gunakan angka atau 'current_message_id'",
                        'chat_id': message.chat.id,
                        'reply_to_message_id': message.id
                    }
                    return response_id
            
            await client.delete_messages(message.chat.id, message_id)
            
            # Store for delayed sending
            response_id = f"group_delete_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil menghapus pesan dengan ID: {message_id}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:DELETE_MESSAGE] Deleted message {message_id}: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:DELETE_MESSAGE] Error: {e}")
            # Store error for delayed sending
            response_id = f"group_delete_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal menghapus pesan: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def pin_message(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Pin a message in the chat"""
        try:
            params = params.strip()
            
            # Handle special keywords
            if params.lower() in ['current_message_id', 'this_message', 'current']:
                # Use the message that triggered this shortcode
                message_id = message.id
                console.info(f"Using current message ID: {message_id}")
            elif params.lower() in ['reply_message', 'replied_message']:
                # Pin the message being replied to
                if message.reply_to_message:
                    message_id = message.reply_to_message.id
                    console.info(f"Using replied message ID: {message_id}")
                else:
                    console.error("No replied message found")
                    # Store error for delayed sending
                    response_id = f"group_pin_error_{message.id}"
                    self.pending_responses[response_id] = {
                        'text': "❌ Tidak ada pesan yang di-reply untuk di-pin",
                        'chat_id': message.chat.id,
                        'reply_to_message_id': message.id
                    }
                    return response_id
            else:
                # Try to parse as integer
                try:
                    message_id = int(params)
                except ValueError:
                    console.error(f"Invalid message ID parameter: {params}")
                    # Store error for delayed sending
                    response_id = f"group_pin_error_{message.id}"
                    self.pending_responses[response_id] = {
                        'text': f"❌ ID pesan tidak valid: {params}. Gunakan angka atau 'current_message_id'",
                        'chat_id': message.chat.id,
                        'reply_to_message_id': message.id
                    }
                    return response_id
            
            await client.pin_chat_message(
                chat_id=message.chat.id, 
                message_id=message_id,
                disable_notification=False
            )
            
            # Store for delayed sending
            response_id = f"group_pin_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"📌 Berhasil pin pesan dengan ID: {message_id}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:PIN_MESSAGE] Pinned message {message_id}: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:PIN_MESSAGE] Error: {e}")
            # Store error for delayed sending
            response_id = f"group_pin_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal pin pesan: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def unpin_message(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Unpin a specific message"""
        try:
            params = params.strip()
            
            # Handle special keywords
            if params.lower() in ['current_message_id', 'this_message', 'current']:
                # Use the message that triggered this shortcode
                message_id = message.id
                console.info(f"Using current message ID: {message_id}")
            elif params.lower() in ['reply_message', 'replied_message']:
                # Unpin the message being replied to
                if message.reply_to_message:
                    message_id = message.reply_to_message.id
                    console.info(f"Using replied message ID: {message_id}")
                else:
                    console.error("No replied message found")
                    # Store error for delayed sending
                    response_id = f"group_unpin_error_{message.id}"
                    self.pending_responses[response_id] = {
                        'text': "❌ Tidak ada pesan yang di-reply untuk di-unpin",
                        'chat_id': message.chat.id,
                        'reply_to_message_id': message.id
                    }
                    return response_id
            else:
                # Try to parse as integer
                try:
                    message_id = int(params)
                except ValueError:
                    console.error(f"Invalid message ID parameter: {params}")
                    # Store error for delayed sending
                    response_id = f"group_unpin_error_{message.id}"
                    self.pending_responses[response_id] = {
                        'text': f"❌ ID pesan tidak valid: {params}. Gunakan angka atau 'current_message_id'",
                        'chat_id': message.chat.id,
                        'reply_to_message_id': message.id
                    }
                    return response_id
            
            await client.unpin_chat_message(
                chat_id=message.chat.id,
                message_id=message_id
            )
            
            # Store for delayed sending
            response_id = f"group_unpin_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"📌 Berhasil unpin pesan dengan ID: {message_id}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:UNPIN_MESSAGE] Unpinned message {message_id}: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:UNPIN_MESSAGE] Error: {e}")
            # Store error for delayed sending
            response_id = f"group_unpin_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal unpin pesan: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def unpin_all_messages(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Unpin all messages in the chat"""
        try:
            await client.unpin_all_chat_messages(chat_id=message.chat.id)
            
            # Store for delayed sending
            response_id = f"group_unpin_all_{message.id}"
            self.pending_responses[response_id] = {
                'text': "📌 Berhasil unpin semua pesan dalam grup",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:UNPIN_ALL] Unpinned all messages: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:UNPIN_ALL] Error: {e}")
            return False
    
    async def set_chat_title(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Set chat title"""
        try:
            new_title = params.strip()
            if not new_title:
                return False
                
            await client.set_chat_title(chat_id=message.chat.id, title=new_title)
            
            # Store for delayed sending
            response_id = f"group_set_title_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil mengubah judul grup menjadi: {new_title}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:SET_TITLE] Changed title to {new_title}: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:SET_TITLE] Error: {e}")
            return False
    
    async def set_chat_description(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Set chat description"""
        try:
            new_description = params.strip()
            if not new_description:
                return False
                
            await client.set_chat_description(chat_id=message.chat.id, description=new_description)
            
            # Store for delayed sending
            response_id = f"group_set_desc_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil mengubah deskripsi grup menjadi: {new_description}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:SET_DESCRIPTION] Changed description: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:SET_DESCRIPTION] Error: {e}")
            return False
    
    async def set_chat_photo(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Set chat photo"""
        try:
            photo_file_id = params.strip()
            if not photo_file_id:
                return False
                
            await client.set_chat_photo(chat_id=message.chat.id, photo=photo_file_id)
            
            # Store for delayed sending
            response_id = f"group_set_photo_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Berhasil mengubah foto grup",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:SET_PHOTO] Changed photo: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:SET_PHOTO] Error: {e}")
            return False
    
    async def delete_chat_photo(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Delete chat photo"""
        try:
            await client.delete_chat_photo(chat_id=message.chat.id)
            
            # Store for delayed sending
            response_id = f"group_delete_photo_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Berhasil menghapus foto grup",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[GROUP:DELETE_PHOTO] Deleted photo: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[GROUP:DELETE_PHOTO] Error: {e}")
            return False
    
    async def send_pending_responses(self, client, response_ids):
        """Send pending responses"""
        sent_responses = []
        
        for response_id in response_ids:
            if response_id in self.pending_responses:
                response_data = self.pending_responses[response_id]
                
                try:
                    await client.send_message(
                        chat_id=response_data['chat_id'],
                        text=response_data['text'],
                        reply_to_message_id=response_data['reply_to_message_id']
                    )
                    sent_responses.append(response_id)
                    console.info(f"[GROUP] Sent response: {response_id}")
                    
                except Exception as e:
                    console.error(f"[GROUP] Error sending response {response_id}: {e}")
                    
                # Clean up
                del self.pending_responses[response_id]
                
        return sent_responses