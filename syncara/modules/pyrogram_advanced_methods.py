# syncara/modules/pyrogram_advanced_methods.py
"""
Advanced Pyrogram methods yang belum diimplementasikan sebelumnya.
Berisi method-method untuk management channel, supergroup, dan fitur advanced lainnya.
"""

from pyrogram import types, enums
from pyrogram.errors import RPCError
from typing import Union, List, Optional, Dict, Any, AsyncGenerator
from syncara.console import console
import asyncio
from datetime import datetime, timedelta

class AdvancedMethods:
    """
    Mixin class untuk method-method Pyrogram yang advanced.
    """
    
    # ==================== CHANNEL & GROUP CREATION ====================
    
    async def buat_channel(self, 
                          title: str,
                          description: Optional[str] = None,
                          **kwargs) -> types.Chat:
        """
        Membuat channel broadcast baru.
        
        Args:
            title: Judul channel
            description: Deskripsi channel
            
        Returns:
            Chat: Objek channel yang dibuat
        """
        try:
            return await self.create_channel(
                title=title,
                description=description,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membuat channel: {e}")
            raise
    
    async def buat_grup(self, 
                       title: str,
                       users: List[Union[int, str]],
                       **kwargs) -> types.Chat:
        """
        Membuat grup basic baru.
        
        Args:
            title: Judul grup
            users: List user yang akan ditambahkan
            
        Returns:
            Chat: Objek grup yang dibuat
        """
        try:
            return await self.create_group(
                title=title,
                users=users,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membuat grup: {e}")
            raise
    
    async def buat_supergroup(self, 
                             title: str,
                             description: Optional[str] = None,
                             **kwargs) -> types.Chat:
        """
        Membuat supergroup baru.
        
        Args:
            title: Judul supergroup
            description: Deskripsi supergroup
            
        Returns:
            Chat: Objek supergroup yang dibuat
        """
        try:
            return await self.create_supergroup(
                title=title,
                description=description,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membuat supergroup: {e}")
            raise
    
    async def hapus_channel(self, 
                           chat_id: Union[int, str],
                           **kwargs) -> bool:
        """
        Menghapus channel.
        
        Args:
            chat_id: ID channel yang akan dihapus
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.delete_channel(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error menghapus channel: {e}")
            raise
    
    async def hapus_supergroup(self, 
                              chat_id: Union[int, str],
                              **kwargs) -> bool:
        """
        Menghapus supergroup.
        
        Args:
            chat_id: ID supergroup yang akan dihapus
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.delete_supergroup(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error menghapus supergroup: {e}")
            raise
    
    # ==================== ADVANCED CHAT MANAGEMENT ====================
    
    async def hapus_riwayat_user(self, 
                                chat_id: Union[int, str],
                                user_id: Union[int, str],
                                **kwargs) -> bool:
        """
        Menghapus semua pesan yang dikirim user di supergroup.
        
        Args:
            chat_id: ID chat
            user_id: ID user yang pesannya akan dihapus
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.delete_user_history(
                chat_id=chat_id,
                user_id=user_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menghapus riwayat user: {e}")
            raise
    
    async def set_mode_lambat(self, 
                             chat_id: Union[int, str],
                             seconds: int,
                             **kwargs) -> bool:
        """
        Mengatur interval slow mode untuk chat.
        
        Args:
            chat_id: ID chat
            seconds: Interval dalam detik (0 untuk nonaktifkan)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_slow_mode(
                chat_id=chat_id,
                seconds=seconds,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengatur mode lambat: {e}")
            raise
    
    async def tandai_chat_belum_dibaca(self, 
                                      chat_id: Union[int, str],
                                      **kwargs) -> bool:
        """
        Menandai chat sebagai belum dibaca.
        
        Args:
            chat_id: ID chat
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.mark_chat_unread(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error menandai chat belum dibaca: {e}")
            raise
    
    async def get_log_event_chat(self, 
                                chat_id: Union[int, str],
                                limit: int = 100,
                                offset_id: int = 0,
                                **kwargs) -> List[types.ChatEvent]:
        """
        Mendapatkan log event chat dalam 48 jam terakhir.
        
        Args:
            chat_id: ID chat
            limit: Batas jumlah event
            offset_id: Offset ID untuk pagination
            
        Returns:
            List[ChatEvent]: List event chat
        """
        try:
            events = []
            async for event in self.get_chat_event_log(
                chat_id=chat_id,
                limit=limit,
                offset_id=offset_id,
                **kwargs
            ):
                events.append(event)
            return events
        except Exception as e:
            console.error(f"Error mendapatkan log event chat: {e}")
            raise
    
    async def hitung_member_online(self, 
                                  chat_id: Union[int, str],
                                  **kwargs) -> int:
        """
        Menghitung jumlah member yang sedang online di chat.
        
        Args:
            chat_id: ID chat
            
        Returns:
            int: Jumlah member online
        """
        try:
            return await self.get_chat_online_count(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error menghitung member online: {e}")
            raise
    
    async def get_daftar_send_as(self, 
                                chat_id: Union[int, str],
                                **kwargs) -> List[types.Chat]:
        """
        Mendapatkan daftar chat yang bisa digunakan untuk "send as".
        
        Args:
            chat_id: ID chat
            
        Returns:
            List[Chat]: List chat yang tersedia
        """
        try:
            return await self.get_send_as_chats(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error mendapatkan daftar send as: {e}")
            raise
    
    async def set_send_as_chat(self, 
                              chat_id: Union[int, str],
                              send_as_chat_id: Union[int, str],
                              **kwargs) -> bool:
        """
        Mengatur chat default untuk "send as".
        
        Args:
            chat_id: ID chat
            send_as_chat_id: ID chat yang akan digunakan untuk send as
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_send_as_chat(
                chat_id=chat_id,
                send_as_chat_id=send_as_chat_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengatur send as chat: {e}")
            raise
    
    # ==================== MESSAGE HISTORY METHODS ====================
    
    async def get_pesan_spesifik(self, 
                                chat_id: Union[int, str],
                                message_ids: Union[int, List[int]],
                                **kwargs) -> Union[types.Message, List[types.Message]]:
        """
        Mendapatkan pesan spesifik berdasarkan ID.
        
        Args:
            chat_id: ID chat
            message_ids: ID pesan atau list ID pesan
            
        Returns:
            Message atau List[Message]: Pesan yang diminta
        """
        try:
            return await self.get_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mendapatkan pesan spesifik: {e}")
            raise
    
    async def get_grup_media(self, 
                            chat_id: Union[int, str],
                            message_id: int,
                            **kwargs) -> List[types.Message]:
        """
        Mendapatkan grup media (album) berdasarkan message ID.
        
        Args:
            chat_id: ID chat
            message_id: ID salah satu pesan dalam grup media
            
        Returns:
            List[Message]: List pesan dalam grup media
        """
        try:
            return await self.get_media_group(
                chat_id=chat_id,
                message_id=message_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mendapatkan grup media: {e}")
            raise
    
    async def get_riwayat_chat(self, 
                              chat_id: Union[int, str],
                              limit: int = 100,
                              offset: int = 0,
                              offset_id: int = 0,
                              offset_date: Optional[datetime] = None,
                              reverse: bool = False,
                              **kwargs) -> List[types.Message]:
        """
        Mendapatkan riwayat chat dengan parameter lengkap.
        
        Args:
            chat_id: ID chat
            limit: Batas jumlah pesan
            offset: Offset untuk pagination
            offset_id: Offset berdasarkan message ID
            offset_date: Offset berdasarkan tanggal
            reverse: Urutkan terbalik
            
        Returns:
            List[Message]: List pesan riwayat
        """
        try:
            messages = []
            async for message in self.get_chat_history(
                chat_id=chat_id,
                limit=limit,
                offset=offset,
                offset_id=offset_id,
                offset_date=offset_date,
                reverse=reverse,
                **kwargs
            ):
                messages.append(message)
            return messages
        except Exception as e:
            console.error(f"Error mendapatkan riwayat chat: {e}")
            raise
    
    async def hitung_riwayat_chat(self, 
                                 chat_id: Union[int, str],
                                 **kwargs) -> int:
        """
        Menghitung total pesan dalam riwayat chat.
        
        Args:
            chat_id: ID chat
            
        Returns:
            int: Jumlah total pesan
        """
        try:
            return await self.get_chat_history_count(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error menghitung riwayat chat: {e}")
            raise
    
    async def baca_riwayat_chat(self, 
                               chat_id: Union[int, str],
                               max_id: int = 0,
                               **kwargs) -> bool:
        """
        Menandai riwayat chat sebagai sudah dibaca.
        
        Args:
            chat_id: ID chat
            max_id: ID pesan maksimal yang ditandai sudah dibaca
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.read_chat_history(
                chat_id=chat_id,
                max_id=max_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membaca riwayat chat: {e}")
            raise
    
    # ==================== POLLING ADVANCED METHODS ====================
    
    async def vote_polling(self, 
                          chat_id: Union[int, str],
                          message_id: int,
                          options: List[int],
                          **kwargs) -> types.Poll:
        """
        Memberikan vote pada polling.
        
        Args:
            chat_id: ID chat
            message_id: ID pesan polling
            options: List index opsi yang dipilih
            
        Returns:
            Poll: Objek polling yang di-vote
        """
        try:
            return await self.vote_poll(
                chat_id=chat_id,
                message_id=message_id,
                options=options,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error vote polling: {e}")
            raise
    
    # ==================== ARCHIVE METHODS ====================
    
    async def arsip_chat(self, 
                        chat_id: Union[int, str],
                        **kwargs) -> bool:
        """
        Mengarsipkan chat.
        
        Args:
            chat_id: ID chat yang akan diarsipkan
            
        Returns:
            bool: True jika berhasil
        """
        try:
            chat = await self.get_chat(chat_id)
            return await chat.archive(**kwargs)
        except Exception as e:
            console.error(f"Error mengarsipkan chat: {e}")
            raise
    
    async def unarsip_chat(self, 
                          chat_id: Union[int, str],
                          **kwargs) -> bool:
        """
        Membuka arsip chat.
        
        Args:
            chat_id: ID chat yang akan dibuka arsipnya
            
        Returns:
            bool: True jika berhasil
        """
        try:
            chat = await self.get_chat(chat_id)
            return await chat.unarchive(**kwargs)
        except Exception as e:
            console.error(f"Error membuka arsip chat: {e}")
            raise
    
    async def set_konten_terlindungi(self, 
                                    chat_id: Union[int, str],
                                    enabled: bool,
                                    **kwargs) -> bool:
        """
        Mengatur perlindungan konten chat.
        
        Args:
            chat_id: ID chat
            enabled: True untuk mengaktifkan perlindungan
            
        Returns:
            bool: True jika berhasil
        """
        try:
            chat = await self.get_chat(chat_id)
            return await chat.set_protected_content(enabled=enabled, **kwargs)
        except Exception as e:
            console.error(f"Error mengatur konten terlindungi: {e}")
            raise
    
    # ==================== INLINE EDITING METHODS ====================
    
    async def edit_caption_inline(self, 
                                 inline_message_id: str,
                                 caption: str,
                                 parse_mode: Optional[enums.ParseMode] = None,
                                 caption_entities: Optional[List[types.MessageEntity]] = None,
                                 reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                                 **kwargs) -> bool:
        """
        Mengedit caption pesan inline.
        
        Args:
            inline_message_id: ID pesan inline
            caption: Caption baru
            parse_mode: Mode parsing
            caption_entities: Entities caption
            reply_markup: Keyboard markup baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.edit_inline_caption(
                inline_message_id=inline_message_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengedit caption inline: {e}")
            raise
    
    async def edit_media_inline(self, 
                               inline_message_id: str,
                               media: types.InputMedia,
                               reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                               **kwargs) -> bool:
        """
        Mengedit media pesan inline.
        
        Args:
            inline_message_id: ID pesan inline
            media: Media baru
            reply_markup: Keyboard markup baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.edit_inline_media(
                inline_message_id=inline_message_id,
                media=media,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengedit media inline: {e}")
            raise
    
    async def edit_reply_markup_inline(self, 
                                      inline_message_id: str,
                                      reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                                      **kwargs) -> bool:
        """
        Mengedit reply markup pesan inline.
        
        Args:
            inline_message_id: ID pesan inline
            reply_markup: Keyboard markup baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.edit_inline_reply_markup(
                inline_message_id=inline_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengedit reply markup inline: {e}")
            raise
    
    # ==================== BULK OPERATIONS ====================
    
    async def kirim_bulk_pesan(self, 
                              targets: List[Union[int, str]],
                              text: str,
                              delay: float = 1.0,
                              **kwargs) -> List[types.Message]:
        """
        Mengirim pesan ke multiple chat dengan delay.
        
        Args:
            targets: List ID chat target
            text: Teks pesan
            delay: Delay antar pengiriman dalam detik
            **kwargs: Parameter tambahan untuk send_message
            
        Returns:
            List[Message]: List pesan yang berhasil dikirim
        """
        try:
            results = []
            for target in targets:
                try:
                    message = await self.kirim_pesan(
                        chat_id=target,
                        text=text,
                        **kwargs
                    )
                    results.append(message)
                    if delay > 0:
                        await asyncio.sleep(delay)
                except Exception as e:
                    console.error(f"Error mengirim ke {target}: {e}")
                    continue
            
            console.info(f"Berhasil mengirim ke {len(results)}/{len(targets)} target")
            return results
        except Exception as e:
            console.error(f"Error kirim bulk pesan: {e}")
            raise
    
    async def forward_bulk_pesan(self, 
                                targets: List[Union[int, str]],
                                from_chat_id: Union[int, str],
                                message_ids: Union[int, List[int]],
                                delay: float = 1.0,
                                **kwargs) -> List[List[types.Message]]:
        """
        Forward pesan ke multiple chat dengan delay.
        
        Args:
            targets: List ID chat target
            from_chat_id: ID chat sumber
            message_ids: ID pesan yang akan di-forward
            delay: Delay antar pengiriman dalam detik
            **kwargs: Parameter tambahan untuk forward_messages
            
        Returns:
            List[List[Message]]: List hasil forward untuk setiap target
        """
        try:
            results = []
            for target in targets:
                try:
                    forwarded = await self.forward_pesan(
                        chat_id=target,
                        from_chat_id=from_chat_id,
                        message_ids=message_ids,
                        **kwargs
                    )
                    results.append(forwarded)
                    if delay > 0:
                        await asyncio.sleep(delay)
                except Exception as e:
                    console.error(f"Error forward ke {target}: {e}")
                    continue
            
            console.info(f"Berhasil forward ke {len(results)}/{len(targets)} target")
            return results
        except Exception as e:
            console.error(f"Error forward bulk pesan: {e}")
            raise
    
    # ==================== ADVANCED UTILITIES ====================
    
    async def export_chat_invite_link(self, 
                                     chat_id: Union[int, str],
                                     **kwargs) -> str:
        """
        Export invite link chat.
        
        Args:
            chat_id: ID chat
            
        Returns:
            str: Invite link
        """
        try:
            return await self.export_chat_invite_link(chat_id=chat_id, **kwargs)
        except Exception as e:
            console.error(f"Error export invite link: {e}")
            raise
    
    async def create_chat_invite_link(self, 
                                     chat_id: Union[int, str],
                                     name: Optional[str] = None,
                                     expire_date: Optional[int] = None,
                                     member_limit: Optional[int] = None,
                                     creates_join_request: bool = False,
                                     **kwargs) -> types.ChatInviteLink:
        """
        Membuat invite link chat dengan parameter custom.
        
        Args:
            chat_id: ID chat
            name: Nama invite link
            expire_date: Tanggal expire (timestamp)
            member_limit: Batas member
            creates_join_request: Buat join request
            
        Returns:
            ChatInviteLink: Objek invite link
        """
        try:
            return await self.create_chat_invite_link(
                chat_id=chat_id,
                name=name,
                expire_date=expire_date,
                member_limit=member_limit,
                creates_join_request=creates_join_request,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error membuat invite link: {e}")
            raise
    
    async def edit_chat_invite_link(self, 
                                   chat_id: Union[int, str],
                                   invite_link: str,
                                   name: Optional[str] = None,
                                   expire_date: Optional[int] = None,
                                   member_limit: Optional[int] = None,
                                   creates_join_request: Optional[bool] = None,
                                   **kwargs) -> types.ChatInviteLink:
        """
        Mengedit invite link chat.
        
        Args:
            chat_id: ID chat
            invite_link: Link yang akan diedit
            name: Nama baru
            expire_date: Tanggal expire baru
            member_limit: Batas member baru
            creates_join_request: Setting join request baru
            
        Returns:
            ChatInviteLink: Objek invite link yang diedit
        """
        try:
            return await self.edit_chat_invite_link(
                chat_id=chat_id,
                invite_link=invite_link,
                name=name,
                expire_date=expire_date,
                member_limit=member_limit,
                creates_join_request=creates_join_request,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengedit invite link: {e}")
            raise
    
    async def revoke_chat_invite_link(self, 
                                     chat_id: Union[int, str],
                                     invite_link: str,
                                     **kwargs) -> types.ChatInviteLink:
        """
        Mencabut invite link chat.
        
        Args:
            chat_id: ID chat
            invite_link: Link yang akan dicabut
            
        Returns:
            ChatInviteLink: Objek invite link yang dicabut
        """
        try:
            return await self.revoke_chat_invite_link(
                chat_id=chat_id,
                invite_link=invite_link,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mencabut invite link: {e}")
            raise 