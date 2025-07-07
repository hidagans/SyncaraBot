# syncara/shortcode/group_management.py
from syncara.console import console
from pyrogram.types import ChatPermissions

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
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Delete a message by its ID"""
        try:
            message_id = int(params)
            await client.delete_messages(message.chat.id, message_id)
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"✅ Berhasil menghapus pesan dengan ID: {message_id}",
                reply_to_message_id=message.id
            )
            
            console.info(f"Deleted message {message_id} in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error deleting message: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal menghapus pesan: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False
    
    async def pin_message(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Pin a message in the chat"""
        try:
            message_id = int(params)
            await client.pin_chat_message(
                chat_id=message.chat.id, 
                message_id=message_id,
                disable_notification=False
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"📌 Berhasil pin pesan dengan ID: {message_id}",
                reply_to_message_id=message.id
            )
            
            console.info(f"Pinned message {message_id} in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error pinning message: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal pin pesan: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False
    
    async def unpin_message(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Unpin a specific message"""
        try:
            message_id = int(params)
            await client.unpin_chat_message(
                chat_id=message.chat.id,
                message_id=message_id
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"📌 Berhasil unpin pesan dengan ID: {message_id}",
                reply_to_message_id=message.id
            )
            
            console.info(f"Unpinned message {message_id} in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error unpinning message: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal unpin pesan: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False
    
    async def unpin_all_messages(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Unpin all messages in the chat"""
        try:
            await client.unpin_all_chat_messages(chat_id=message.chat.id)
            
            await client.send_message(
                chat_id=message.chat.id,
                text="📌 Berhasil unpin semua pesan dalam grup",
                reply_to_message_id=message.id
            )
            
            console.info(f"Unpinned all messages in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error unpinning all messages: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal unpin semua pesan: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False
    
    async def set_chat_title(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Set chat title"""
        try:
            new_title = params.strip()
            if not new_title:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Judul grup tidak boleh kosong",
                    reply_to_message_id=message.id
                )
                return False
                
            await client.set_chat_title(chat_id=message.chat.id, title=new_title)
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"✅ Berhasil mengubah judul grup menjadi: **{new_title}**",
                reply_to_message_id=message.id
            )
            
            console.info(f"Set chat title to '{new_title}' in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error setting chat title: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal mengubah judul grup: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False
    
    async def set_chat_description(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Set chat description"""
        try:
            new_description = params.strip()
            if not new_description:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Deskripsi tidak boleh kosong",
                    reply_to_message_id=message.id
                )
                return False
                
            await client.set_chat_description(chat_id=message.chat.id, description=new_description)
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"✅ Berhasil mengubah deskripsi grup menjadi:\n\n{new_description}",
                reply_to_message_id=message.id
            )
            
            console.info(f"Set chat description in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error setting chat description: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal mengubah deskripsi grup: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False
    
    async def set_chat_photo(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Set chat photo"""
        try:
            photo_file_id = params.strip()
            if not photo_file_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ File ID foto tidak boleh kosong",
                    reply_to_message_id=message.id
                )
                return False
                
            await client.set_chat_photo(chat_id=message.chat.id, photo=photo_file_id)
            
            await client.send_message(
                chat_id=message.chat.id,
                text="🖼️ Berhasil mengubah foto profil grup",
                reply_to_message_id=message.id
            )
            
            console.info(f"Set chat photo in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error setting chat photo: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal mengubah foto profil grup: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False
    
    async def delete_chat_photo(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Hanya admin atau pemilik grup yang bisa menjalankan perintah ini.",
                reply_to_message_id=message.id
            )
            return False
        """Delete chat photo"""
        try:
            await client.delete_chat_photo(chat_id=message.chat.id)
            
            await client.send_message(
                chat_id=message.chat.id,
                text="🖼️ Berhasil menghapus foto profil grup",
                reply_to_message_id=message.id
            )
            
            console.info(f"Deleted chat photo in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error deleting chat photo: {e}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal menghapus foto profil grup: {str(e)}",
                    reply_to_message_id=message.id
                )
            except:
                pass
            return False