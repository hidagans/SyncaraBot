# syncara/modules/pyrogram_bound_methods.py
"""
Bound methods support untuk Pyrogram types.
Menambahkan method-method Indonesia ke types seperti Chat, Message, dll.
"""

from pyrogram import types, enums
from pyrogram.errors import RPCError
from typing import Union, List, Optional, AsyncGenerator, Dict, Any, BinaryIO
from syncara.console import console
import asyncio
from datetime import datetime, timedelta

class PyrogramBoundMethods:
    """
    Mixin class untuk menambahkan bound methods support.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_bound_methods()
    
    def _setup_bound_methods(self):
        """Setup bound methods untuk semua types"""
        # Chat bound methods
        self._setup_chat_bound_methods()
        # Message bound methods
        self._setup_message_bound_methods()
        # User bound methods
        self._setup_user_bound_methods()
        # InlineQuery bound methods
        self._setup_inline_query_bound_methods()
        # ChatJoinRequest bound methods
        self._setup_chat_join_request_bound_methods()
    
    def _setup_chat_bound_methods(self):
        """Setup bound methods untuk Chat type"""
        
        async def arsip_chat(chat_self):
            """Arsipkan chat ini"""
            return await self.arsip_chat(chat_self.id)
        
        async def unarsip_chat(chat_self):
            """Batal arsipkan chat ini"""
            return await self.unarsip_chat(chat_self.id)
        
        async def set_judul(chat_self, title: str):
            """Set judul chat ini"""
            return await self.set_judul_chat(chat_self.id, title)
        
        async def set_deskripsi(chat_self, description: str):
            """Set deskripsi chat ini"""
            return await self.set_deskripsi_chat(chat_self.id, description)
        
        async def set_foto(chat_self, photo: Union[str, BinaryIO]):
            """Set foto chat ini"""
            return await self.set_foto_chat(chat_self.id, photo)
        
        async def hapus_foto(chat_self):
            """Hapus foto chat ini"""
            return await self.hapus_foto_chat(chat_self.id)
        
        async def ban_member(chat_self, user_id: Union[int, str], until_date: Optional[datetime] = None):
            """Ban member dari chat ini"""
            return await self.ban_member_chat(chat_self.id, user_id, until_date)
        
        async def unban_member(chat_self, user_id: Union[int, str]):
            """Unban member dari chat ini"""
            return await self.unban_member_chat(chat_self.id, user_id)
        
        async def restrict_member(chat_self, user_id: Union[int, str], permissions: types.ChatPermissions, until_date: Optional[datetime] = None):
            """Batasi member di chat ini"""
            return await self.batasi_member_chat(chat_self.id, user_id, permissions, until_date)
        
        async def promote_member(chat_self, user_id: Union[int, str], privileges: types.ChatPrivileges):
            """Promosikan member di chat ini"""
            return await self.promosi_member_chat(chat_self.id, user_id, privileges)
        
        async def get_member(chat_self, user_id: Union[int, str]):
            """Dapatkan info member dari chat ini"""
            return await self.get_member_chat(chat_self.id, user_id)
        
        async def get_members(chat_self, limit: int = 200, offset: int = 0):
            """Dapatkan daftar member dari chat ini"""
            return await self.get_daftar_member(chat_self.id, limit=limit, offset=offset)
        
        async def add_members(chat_self, user_ids: List[Union[int, str]]):
            """Tambahkan member ke chat ini"""
            return await self.tambah_member_chat(chat_self.id, user_ids)
        
        async def join(chat_self):
            """Bergabung ke chat ini"""
            return await self.gabung_chat(chat_self.id)
        
        async def leave(chat_self):
            """Keluar dari chat ini"""
            return await self.keluar_chat(chat_self.id)
        
        async def mark_unread(chat_self):
            """Tandai chat ini sebagai belum dibaca"""
            return await self.tandai_chat_belum_dibaca(chat_self.id)
        
        async def set_protected_content(chat_self, enabled: bool):
            """Set konten terlindungi untuk chat ini"""
            return await self.set_konten_terlindungi(chat_self.id, enabled)
        
        async def unpin_all_messages(chat_self):
            """Unpin semua pesan di chat ini"""
            return await self.unpin_semua_pesan(chat_self.id)
        
        async def delete_chat(chat_self):
            """Hapus chat ini (channel/supergroup)"""
            if chat_self.type == enums.ChatType.CHANNEL:
                return await self.hapus_channel(chat_self.id)
            elif chat_self.type == enums.ChatType.SUPERGROUP:
                return await self.hapus_supergroup(chat_self.id)
            else:
                raise ValueError("Chat type tidak mendukung penghapusan")
        
        async def set_slow_mode(chat_self, seconds: int):
            """Set slow mode untuk chat ini"""
            return await self.set_mode_lambat(chat_self.id, seconds)
        
        async def get_online_count(chat_self):
            """Hitung member online di chat ini"""
            return await self.hitung_member_online(chat_self.id)
        
        async def get_event_log(chat_self, limit: int = 100, offset_id: int = 0):
            """Dapatkan log event dari chat ini"""
            return await self.get_log_event_chat(chat_self.id, limit, offset_id)
        
        async def backup_chat(chat_self, limit: int = 1000):
            """Backup chat ini"""
            return await self.backup_lengkap_chat(chat_self.id, limit)
        
        # Bind methods ke Chat type
        types.Chat.arsip = arsip_chat
        types.Chat.unarsip = unarsip_chat
        types.Chat.set_judul = set_judul
        types.Chat.set_deskripsi = set_deskripsi
        types.Chat.set_foto = set_foto
        types.Chat.hapus_foto = hapus_foto
        types.Chat.ban_member = ban_member
        types.Chat.unban_member = unban_member
        types.Chat.restrict_member = restrict_member
        types.Chat.promote_member = promote_member
        types.Chat.get_member = get_member
        types.Chat.get_members = get_members
        types.Chat.add_members = add_members
        types.Chat.join = join
        types.Chat.leave = leave
        types.Chat.mark_unread = mark_unread
        types.Chat.set_protected_content = set_protected_content
        types.Chat.unpin_all_messages = unpin_all_messages
        types.Chat.delete_chat = delete_chat
        types.Chat.set_slow_mode = set_slow_mode
        types.Chat.get_online_count = get_online_count
        types.Chat.get_event_log = get_event_log
        types.Chat.backup_chat = backup_chat
    
    def _setup_message_bound_methods(self):
        """Setup bound methods untuk Message type"""
        
        async def reply_text(message_self, text: str, **kwargs):
            """Reply pesan ini dengan teks"""
            return await self.kirim_pesan(
                chat_id=message_self.chat.id,
                text=text,
                reply_to_message_id=message_self.id,
                **kwargs
            )
        
        async def reply_photo(message_self, photo: Union[str, BinaryIO], caption: str = None, **kwargs):
            """Reply pesan ini dengan foto"""
            return await self.kirim_foto(
                chat_id=message_self.chat.id,
                photo=photo,
                caption=caption,
                reply_to_message_id=message_self.id,
                **kwargs
            )
        
        async def reply_video(message_self, video: Union[str, BinaryIO], caption: str = None, **kwargs):
            """Reply pesan ini dengan video"""
            return await self.kirim_video(
                chat_id=message_self.chat.id,
                video=video,
                caption=caption,
                reply_to_message_id=message_self.id,
                **kwargs
            )
        
        async def reply_audio(message_self, audio: Union[str, BinaryIO], caption: str = None, **kwargs):
            """Reply pesan ini dengan audio"""
            return await self.kirim_audio(
                chat_id=message_self.chat.id,
                audio=audio,
                caption=caption,
                reply_to_message_id=message_self.id,
                **kwargs
            )
        
        async def reply_document(message_self, document: Union[str, BinaryIO], caption: str = None, **kwargs):
            """Reply pesan ini dengan dokumen"""
            return await self.kirim_dokumen(
                chat_id=message_self.chat.id,
                document=document,
                caption=caption,
                reply_to_message_id=message_self.id,
                **kwargs
            )
        
        async def edit_text(message_self, text: str, **kwargs):
            """Edit teks pesan ini"""
            return await self.edit_pesan(
                chat_id=message_self.chat.id,
                message_id=message_self.id,
                text=text,
                **kwargs
            )
        
        async def edit_caption(message_self, caption: str, **kwargs):
            """Edit caption pesan ini"""
            return await self.edit_pesan(
                chat_id=message_self.chat.id,
                message_id=message_self.id,
                caption=caption,
                **kwargs
            )
        
        async def edit_media(message_self, media: Union[str, BinaryIO], **kwargs):
            """Edit media pesan ini"""
            return await self.edit_pesan_media(
                chat_id=message_self.chat.id,
                message_id=message_self.id,
                media=media,
                **kwargs
            )
        
        async def delete_message(message_self, revoke: bool = True):
            """Hapus pesan ini"""
            return await self.hapus_pesan(
                chat_id=message_self.chat.id,
                message_ids=[message_self.id],
                revoke=revoke
            )
        
        async def forward_message(message_self, to_chat_id: Union[int, str], **kwargs):
            """Forward pesan ini"""
            return await self.forward_pesan(
                chat_id=to_chat_id,
                from_chat_id=message_self.chat.id,
                message_ids=[message_self.id],
                **kwargs
            )
        
        async def copy_message(message_self, to_chat_id: Union[int, str], **kwargs):
            """Copy pesan ini"""
            return await self.copy_pesan(
                chat_id=to_chat_id,
                from_chat_id=message_self.chat.id,
                message_id=message_self.id,
                **kwargs
            )
        
        async def pin_message(message_self, disable_notification: bool = False, both_sides: bool = False):
            """Pin pesan ini"""
            return await self.pin_pesan_chat(
                chat_id=message_self.chat.id,
                message_id=message_self.id,
                disable_notification=disable_notification,
                both_sides=both_sides
            )
        
        async def unpin_message(message_self):
            """Unpin pesan ini"""
            return await self.unpin_pesan_chat(
                chat_id=message_self.chat.id,
                message_id=message_self.id
            )
        
        async def download_media(message_self, file_name: str = None, **kwargs):
            """Download media dari pesan ini"""
            return await self.download_media_extended(
                message=message_self,
                file_name=file_name,
                **kwargs
            )
        
        async def click_inline_button(message_self, button_text: str = None, button_data: str = None):
            """Klik inline button pada pesan ini"""
            if not message_self.reply_markup:
                return False
            
            for row in message_self.reply_markup.inline_keyboard:
                for button in row:
                    if button_text and button.text == button_text:
                        return await self.jawab_callback_query(
                            callback_query_id=button.callback_data,
                            text="Button clicked"
                        )
                    elif button_data and button.callback_data == button_data:
                        return await self.jawab_callback_query(
                            callback_query_id=button.callback_data,
                            text="Button clicked"
                        )
            return False
        
        # Bind methods ke Message type
        types.Message.reply_text = reply_text
        types.Message.reply_photo = reply_photo
        types.Message.reply_video = reply_video
        types.Message.reply_audio = reply_audio
        types.Message.reply_document = reply_document
        types.Message.edit_text = edit_text
        types.Message.edit_caption = edit_caption
        types.Message.edit_media = edit_media
        types.Message.delete_message = delete_message
        types.Message.forward_message = forward_message
        types.Message.copy_message = copy_message
        types.Message.pin_message = pin_message
        types.Message.unpin_message = unpin_message
        types.Message.download_media = download_media
        types.Message.click_inline_button = click_inline_button
    
    def _setup_user_bound_methods(self):
        """Setup bound methods untuk User type"""
        
        async def get_common_chats(user_self):
            """Dapatkan chat bersama dengan user ini"""
            return await self.get_common_chats(user_self.id)
        
        async def get_profile_photos(user_self, limit: int = 100, offset: int = 0):
            """Dapatkan foto profil user ini"""
            return await self.get_profile_photos(user_self.id, limit=limit, offset=offset)
        
        async def block_user(user_self):
            """Block user ini"""
            return await self.block_user(user_self.id)
        
        async def unblock_user(user_self):
            """Unblock user ini"""
            return await self.unblock_user(user_self.id)
        
        async def send_message(user_self, text: str, **kwargs):
            """Kirim pesan ke user ini"""
            return await self.kirim_pesan(
                chat_id=user_self.id,
                text=text,
                **kwargs
            )
        
        async def send_photo(user_self, photo: Union[str, BinaryIO], caption: str = None, **kwargs):
            """Kirim foto ke user ini"""
            return await self.kirim_foto(
                chat_id=user_self.id,
                photo=photo,
                caption=caption,
                **kwargs
            )
        
        # Bind methods ke User type
        types.User.get_common_chats = get_common_chats
        types.User.get_profile_photos = get_profile_photos
        types.User.block_user = block_user
        types.User.unblock_user = unblock_user
        types.User.send_message = send_message
        types.User.send_photo = send_photo
    
    def _setup_inline_query_bound_methods(self):
        """Setup bound methods untuk InlineQuery type"""
        
        async def answer_inline_query(inline_query_self, results: List[types.InlineQueryResult], **kwargs):
            """Jawab inline query ini"""
            return await self.jawab_inline_query(
                inline_query_id=inline_query_self.id,
                results=results,
                **kwargs
            )
        
        # Bind methods ke InlineQuery type
        types.InlineQuery.answer_inline_query = answer_inline_query
    
    def _setup_chat_join_request_bound_methods(self):
        """Setup bound methods untuk ChatJoinRequest type"""
        
        async def approve_join_request(join_request_self):
            """Setujui permintaan join ini"""
            return await self.approve_chat_join_request(
                chat_id=join_request_self.chat.id,
                user_id=join_request_self.from_user.id
            )
        
        async def decline_join_request(join_request_self):
            """Tolak permintaan join ini"""
            return await self.decline_chat_join_request(
                chat_id=join_request_self.chat.id,
                user_id=join_request_self.from_user.id
            )
        
        # Bind methods ke ChatJoinRequest type
        types.ChatJoinRequest.approve_join_request = approve_join_request
        types.ChatJoinRequest.decline_join_request = decline_join_request
    
    # ==================== CHAT JOIN REQUEST METHODS ====================
    
    async def approve_chat_join_request(self, 
                                       chat_id: Union[int, str], 
                                       user_id: Union[int, str],
                                       **kwargs) -> bool:
        """
        Setujui permintaan bergabung ke chat.
        
        Args:
            chat_id: ID chat
            user_id: ID user yang meminta join
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.approve_chat_join_request(
                chat_id=chat_id,
                user_id=user_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menyetujui permintaan join: {e}")
            raise
    
    async def decline_chat_join_request(self, 
                                       chat_id: Union[int, str], 
                                       user_id: Union[int, str],
                                       **kwargs) -> bool:
        """
        Tolak permintaan bergabung ke chat.
        
        Args:
            chat_id: ID chat
            user_id: ID user yang meminta join
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.decline_chat_join_request(
                chat_id=chat_id,
                user_id=user_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menolak permintaan join: {e}")
            raise
    
    async def approve_all_chat_join_requests(self, 
                                            chat_id: Union[int, str],
                                            **kwargs) -> bool:
        """
        Setujui semua permintaan bergabung ke chat.
        
        Args:
            chat_id: ID chat
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.approve_all_chat_join_requests(
                chat_id=chat_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menyetujui semua permintaan join: {e}")
            raise
    
    async def decline_all_chat_join_requests(self, 
                                            chat_id: Union[int, str],
                                            **kwargs) -> bool:
        """
        Tolak semua permintaan bergabung ke chat.
        
        Args:
            chat_id: ID chat
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.decline_all_chat_join_requests(
                chat_id=chat_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menolak semua permintaan join: {e}")
            raise
    
    # ==================== ADDITIONAL BOUND METHODS ====================
    
    async def get_common_chats(self, user_id: Union[int, str]) -> List[types.Chat]:
        """
        Dapatkan chat bersama dengan user.
        
        Args:
            user_id: ID user
            
        Returns:
            List[Chat]: Daftar chat bersama
        """
        try:
            return await self.get_common_chats(user_id=user_id)
        except Exception as e:
            console.error(f"Error mendapatkan chat bersama: {e}")
            raise
    
    async def get_profile_photos(self, 
                                user_id: Union[int, str], 
                                limit: int = 100, 
                                offset: int = 0) -> List[types.Photo]:
        """
        Dapatkan foto profil user.
        
        Args:
            user_id: ID user
            limit: Jumlah foto maksimal
            offset: Offset untuk paginasi
            
        Returns:
            List[Photo]: Daftar foto profil
        """
        try:
            return await self.get_profile_photos(
                user_id=user_id,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            console.error(f"Error mendapatkan foto profil: {e}")
            raise
    
    async def block_user(self, user_id: Union[int, str]) -> bool:
        """
        Block user.
        
        Args:
            user_id: ID user yang akan diblock
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.block_user(user_id=user_id)
        except Exception as e:
            console.error(f"Error memblokir user: {e}")
            raise
    
    async def unblock_user(self, user_id: Union[int, str]) -> bool:
        """
        Unblock user.
        
        Args:
            user_id: ID user yang akan diunblock
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.unblock_user(user_id=user_id)
        except Exception as e:
            console.error(f"Error membuka blokir user: {e}")
            raise 