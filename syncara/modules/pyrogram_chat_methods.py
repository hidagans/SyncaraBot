"""
Chat management methods untuk Pyrogram.
Berisi semua method untuk mengelola chat, member, dan administrasi.
"""

from pyrogram import types, enums
from pyrogram.errors import RPCError
from typing import Union, List, Optional, AsyncGenerator, Any
from syncara.console import console
from .pyrogram_compatibility import (
    AVAILABLE_TYPES, 
    create_chat_permissions, 
    create_chat_privileges,
    DEFAULT_CHAT_PERMISSIONS,
    DEFAULT_ADMIN_PRIVILEGES
)

class ChatMethods:
    """
    Mixin class untuk method-method chat management.
    """
    
    # ==================== CHAT MANAGEMENT ====================
    
    async def gabung_chat(self, 
                         chat_id: Union[int, str],
                         **kwargs) -> types.Chat:
        """
        Bergabung ke grup atau channel.
        
        Args:
            chat_id: ID chat atau username
            
        Returns:
            Chat: Objek chat yang dimasuki
        """
        try:
            return await self.join_chat(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error bergabung ke chat: {e}")
            raise
    
    async def keluar_chat(self, 
                         chat_id: Union[int, str],
                         delete: bool = False,
                         **kwargs) -> bool:
        """
        Keluar dari grup atau channel.
        
        Args:
            chat_id: ID chat atau username
            delete: Hapus chat dari daftar (untuk bot)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.leave_chat(chat_id=chat_id, delete=delete, **kwargs)
        except Exception as e:
            console.error(f"Error keluar dari chat: {e}")
            raise
    
    async def get_info_chat(self, 
                           chat_id: Union[int, str],
                           **kwargs) -> types.Chat:
        """
        Mendapatkan informasi chat.
        
        Args:
            chat_id: ID chat atau username
            
        Returns:
            Chat: Objek informasi chat
        """
        try:
            return await self.get_chat(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error mendapatkan info chat: {e}")
            raise
    
    async def set_judul_chat(self, 
                            chat_id: Union[int, str],
                            title: str,
                            **kwargs) -> bool:
        """
        Mengubah judul chat.
        
        Args:
            chat_id: ID chat atau username
            title: Judul baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_chat_title(chat_id=chat_id, title=title, **kwargs)
        except Exception as e:
            console.error(f"Error mengubah judul chat: {e}")
            raise
    
    async def set_deskripsi_chat(self, 
                                chat_id: Union[int, str],
                                description: str,
                                **kwargs) -> bool:
        """
        Mengubah deskripsi chat.
        
        Args:
            chat_id: ID chat atau username
            description: Deskripsi baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_chat_description(chat_id=chat_id, description=description, **kwargs)
        except Exception as e:
            console.error(f"Error mengubah deskripsi chat: {e}")
            raise
    
    async def set_foto_chat(self, 
                           chat_id: Union[int, str],
                           photo: Union[str, bytes],
                           **kwargs) -> bool:
        """
        Mengubah foto chat.
        
        Args:
            chat_id: ID chat atau username
            photo: File foto (path atau bytes)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_chat_photo(chat_id=chat_id, photo=photo, **kwargs)
        except Exception as e:
            console.error(f"Error mengubah foto chat: {e}")
            raise
    
    async def hapus_foto_chat(self, 
                             chat_id: Union[int, str],
                             **kwargs) -> bool:
        """
        Menghapus foto chat.
        
        Args:
            chat_id: ID chat atau username
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.delete_chat_photo(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error menghapus foto chat: {e}")
            raise
    
    async def set_izin_chat(self, 
                           chat_id: Union[int, str],
                           permissions: Union[dict, Any] = None,
                           **kwargs) -> bool:
        """
        Mengatur izin default untuk semua member chat.
        
        Args:
            chat_id: ID chat atau username
            permissions: Objek izin chat atau dict
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Handle permissions dengan compatibility check
            if permissions is None:
                permissions = create_chat_permissions(**DEFAULT_CHAT_PERMISSIONS)
            elif isinstance(permissions, dict):
                permissions = create_chat_permissions(**permissions)
            
            return await self.set_chat_permissions(chat_id=chat_id, permissions=permissions, **kwargs)
        except Exception as e:
            console.error(f"Error mengatur izin chat: {e}")
            raise
    
    # ==================== MEMBER MANAGEMENT ====================
    
    async def get_member_chat(self, 
                             chat_id: Union[int, str],
                             user_id: Union[int, str],
                             **kwargs) -> types.ChatMember:
        """
        Mendapatkan informasi member chat.
        
        Args:
            chat_id: ID chat atau username
            user_id: ID user atau username
            
        Returns:
            ChatMember: Objek member chat
        """
        try:
            return await self.get_chat_member(chat_id=chat_id, user_id=user_id, **kwargs)
        except Exception as e:
            console.error(f"Error mendapatkan info member: {e}")
            raise
    
    async def get_daftar_member(self, 
                               chat_id: Union[int, str],
                               limit: int = 0,
                               filter: enums.ChatMembersFilter = enums.ChatMembersFilter.RECENT,
                               **kwargs) -> AsyncGenerator[types.ChatMember, None]:
        """
        Mendapatkan daftar member chat.
        
        Args:
            chat_id: ID chat atau username
            limit: Batas jumlah member (0 = tidak terbatas)
            filter: Filter member (RECENT, ADMINISTRATORS, SEARCH, etc.)
            
        Yields:
            ChatMember: Objek member chat
        """
        try:
            async for member in self.get_chat_members(chat_id=chat_id, limit=limit, filter=filter, **kwargs):
                yield member
        except Exception as e:
            console.error(f"Error mendapatkan daftar member: {e}")
            raise
    
    async def tambah_member_chat(self, 
                                chat_id: Union[int, str],
                                user_ids: Union[int, str, List[Union[int, str]]],
                                **kwargs) -> bool:
        """
        Menambahkan member ke chat.
        
        Args:
            chat_id: ID chat atau username
            user_ids: ID user atau list ID user yang akan ditambahkan
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.add_chat_members(chat_id=chat_id, user_ids=user_ids, **kwargs)
        except Exception as e:
            console.error(f"Error menambah member: {e}")
            raise
    
    async def ban_member_chat(self, 
                             chat_id: Union[int, str],
                             user_id: Union[int, str],
                             until_date: Optional[int] = None,
                             revoke_messages: bool = False,
                             **kwargs) -> bool:
        """
        Memban member dari chat.
        
        Args:
            chat_id: ID chat atau username
            user_id: ID user atau username yang akan diban
            until_date: Timestamp kapan ban berakhir (None = permanent)
            revoke_messages: Hapus pesan user yang diban
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                until_date=until_date,
                revoke_messages=revoke_messages,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error memban member: {e}")
            raise
    
    async def unban_member_chat(self, 
                               chat_id: Union[int, str],
                               user_id: Union[int, str],
                               only_if_banned: bool = False,
                               **kwargs) -> bool:
        """
        Membuka ban member di chat.
        
        Args:
            chat_id: ID chat atau username
            user_id: ID user atau username yang akan di-unban
            only_if_banned: Hanya unban jika user sedang dalam status banned
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.unban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                only_if_banned=only_if_banned,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membuka ban member: {e}")
            raise
    
    async def batasi_member_chat(self, 
                                chat_id: Union[int, str],
                                user_id: Union[int, str],
                                permissions: Union[dict, Any] = None,
                                until_date: Optional[int] = None,
                                use_independent_chat_permissions: bool = False,
                                **kwargs) -> bool:
        """
        Membatasi member di chat.
        
        Args:
            chat_id: ID chat atau username
            user_id: ID user atau username yang akan dibatasi
            permissions: Izin yang diberikan kepada user atau dict
            until_date: Timestamp kapan pembatasan berakhir (None = permanent)
            use_independent_chat_permissions: Gunakan izin independen
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Handle permissions dengan compatibility check
            if permissions is None:
                # Default restricted permissions
                restricted_permissions = DEFAULT_CHAT_PERMISSIONS.copy()
                restricted_permissions.update({
                    "can_send_messages": False,
                    "can_send_media_messages": False,
                    "can_send_polls": False,
                    "can_send_other_messages": False,
                    "can_add_web_page_previews": False
                })
                permissions = create_chat_permissions(**restricted_permissions)
            elif isinstance(permissions, dict):
                permissions = create_chat_permissions(**permissions)
            
            return await self.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions,
                until_date=until_date,
                use_independent_chat_permissions=use_independent_chat_permissions,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membatasi member: {e}")
            raise
    
    async def promosi_member_chat(self, 
                                 chat_id: Union[int, str],
                                 user_id: Union[int, str],
                                 privileges: Union[dict, Any] = None,
                                 **kwargs) -> bool:
        """
        Mempromosikan member menjadi admin.
        
        Args:
            chat_id: ID chat atau username
            user_id: ID user atau username yang akan dipromosikan
            privileges: Hak akses admin yang diberikan atau dict
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Handle privileges dengan compatibility check
            if privileges is None:
                privileges = create_chat_privileges(**DEFAULT_ADMIN_PRIVILEGES)
            elif isinstance(privileges, dict):
                privileges = create_chat_privileges(**privileges)
            
            return await self.promote_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                privileges=privileges,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mempromosikan member: {e}")
            raise
    
    async def set_gelar_admin(self, 
                             chat_id: Union[int, str],
                             user_id: Union[int, str],
                             title: str,
                             **kwargs) -> bool:
        """
        Mengatur gelar custom untuk admin.
        
        Args:
            chat_id: ID chat atau username
            user_id: ID user atau username admin
            title: Gelar custom
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_administrator_title(
                chat_id=chat_id,
                user_id=user_id,
                title=title,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengatur gelar admin: {e}")
            raise
    
    # ==================== CHAT ACTIONS ====================
    
    async def kirim_aksi_chat(self, 
                             chat_id: Union[int, str],
                             action: enums.ChatAction,
                             **kwargs) -> bool:
        """
        Mengirim aksi chat (typing, upload photo, dll).
        
        Args:
            chat_id: ID chat atau username
            action: Jenis aksi (TYPING, UPLOAD_PHOTO, RECORD_AUDIO, dll)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.send_chat_action(chat_id=chat_id, action=action, **kwargs)
        except Exception as e:
            console.error(f"Error mengirim aksi chat: {e}")
            raise
    
    async def pin_pesan_chat(self, 
                            chat_id: Union[int, str],
                            message_id: int,
                            disable_notification: bool = False,
                            **kwargs) -> bool:
        """
        Mem-pin pesan di chat.
        
        Args:
            chat_id: ID chat atau username
            message_id: ID pesan yang akan di-pin
            disable_notification: Pin tanpa notifikasi
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.pin_chat_message(
                chat_id=chat_id,
                message_id=message_id,
                disable_notification=disable_notification,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mem-pin pesan: {e}")
            raise
    
    async def unpin_pesan_chat(self, 
                              chat_id: Union[int, str],
                              message_id: Optional[int] = None,
                              **kwargs) -> bool:
        """
        Membuka pin pesan di chat.
        
        Args:
            chat_id: ID chat atau username
            message_id: ID pesan yang akan di-unpin (None = semua)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.unpin_chat_message(
                chat_id=chat_id,
                message_id=message_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membuka pin pesan: {e}")
            raise
    
    async def unpin_semua_pesan(self, 
                               chat_id: Union[int, str],
                               **kwargs) -> bool:
        """
        Membuka pin semua pesan di chat.
        
        Args:
            chat_id: ID chat atau username
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.unpin_all_chat_messages(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error membuka pin semua pesan: {e}")
            raise 