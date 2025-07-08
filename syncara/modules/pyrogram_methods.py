# syncara/modules/pyrogram_methods.py
"""
Wrapper lengkap untuk semua method Pyrogram yang tersedia.
Module ini menyediakan akses mudah ke semua fitur Pyrogram dalam bahasa Indonesia.
"""

from pyrogram import Client, filters, types, enums
from pyrogram.errors import RPCError
from typing import Union, List, Optional, BinaryIO, Callable, Any, Dict
import asyncio
from syncara.console import console

class PyrogramMethods:
    """
    Wrapper class yang berisi semua method Pyrogram dengan dokumentasi Indonesia.
    Class ini akan digunakan sebagai mixin untuk Bot dan Ubot class.
    """
    
    def __init__(self):
        self.client = None
    
    # ==================== MESSAGE METHODS ====================
    
    async def kirim_pesan(self, 
                         chat_id: Union[int, str], 
                         text: str, 
                         parse_mode: Optional[enums.ParseMode] = None,
                         reply_to_message_id: Optional[int] = None,
                         reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                         disable_web_page_preview: bool = False,
                         disable_notification: bool = False,
                         protect_content: bool = False,
                         message_thread_id: Optional[int] = None,
                         **kwargs) -> types.Message:
        """
        Mengirim pesan teks ke chat.
        
        Args:
            chat_id: ID chat atau username
            text: Teks pesan yang akan dikirim
            parse_mode: Mode parsing (HTML, Markdown, atau None)
            reply_to_message_id: ID pesan yang akan direply
            reply_markup: Keyboard markup
            disable_web_page_preview: Nonaktifkan preview web page
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten dari forward
            message_thread_id: ID thread untuk supergroup
            
        Returns:
            Message: Objek pesan yang dikirim
        """
        try:
            return await self.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                protect_content=protect_content,
                message_thread_id=message_thread_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim pesan: {e}")
            raise
    
    async def edit_pesan(self, 
                        chat_id: Union[int, str], 
                        message_id: int,
                        text: str,
                        parse_mode: Optional[enums.ParseMode] = None,
                        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                        disable_web_page_preview: bool = False,
                        **kwargs) -> types.Message:
        """
        Mengedit pesan teks.
        
        Args:
            chat_id: ID chat atau username
            message_id: ID pesan yang akan diedit
            text: Teks baru
            parse_mode: Mode parsing
            reply_markup: Keyboard markup baru
            disable_web_page_preview: Nonaktifkan preview web page
            
        Returns:
            Message: Objek pesan yang diedit
        """
        try:
            return await self.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengedit pesan: {e}")
            raise
    
    async def hapus_pesan(self, 
                         chat_id: Union[int, str], 
                         message_ids: Union[int, List[int]],
                         revoke: bool = True,
                         **kwargs) -> bool:
        """
        Menghapus pesan.
        
        Args:
            chat_id: ID chat atau username
            message_ids: ID pesan atau list ID pesan yang akan dihapus
            revoke: Hapus untuk semua user (True) atau hanya untuk bot (False)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=revoke,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menghapus pesan: {e}")
            raise
    
    async def forward_pesan(self, 
                           chat_id: Union[int, str],
                           from_chat_id: Union[int, str],
                           message_ids: Union[int, List[int]],
                           disable_notification: bool = False,
                           protect_content: bool = False,
                           **kwargs) -> List[types.Message]:
        """
        Mem-forward pesan dari chat lain.
        
        Args:
            chat_id: ID chat tujuan
            from_chat_id: ID chat sumber
            message_ids: ID pesan atau list ID pesan yang akan di-forward
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten dari forward
            
        Returns:
            List[Message]: List pesan yang di-forward
        """
        try:
            return await self.forward_messages(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_ids=message_ids,
                disable_notification=disable_notification,
                protect_content=protect_content,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mem-forward pesan: {e}")
            raise
    
    async def copy_pesan(self, 
                        chat_id: Union[int, str],
                        from_chat_id: Union[int, str],
                        message_id: int,
                        caption: Optional[str] = None,
                        parse_mode: Optional[enums.ParseMode] = None,
                        caption_entities: Optional[List[types.MessageEntity]] = None,
                        disable_notification: bool = False,
                        protect_content: bool = False,
                        reply_to_message_id: Optional[int] = None,
                        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                        **kwargs) -> types.Message:
        """
        Menyalin pesan dari chat lain.
        
        Args:
            chat_id: ID chat tujuan
            from_chat_id: ID chat sumber
            message_id: ID pesan yang akan disalin
            caption: Caption baru (untuk media)
            parse_mode: Mode parsing
            caption_entities: Entities untuk caption
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten dari forward
            reply_to_message_id: ID pesan yang akan direply
            reply_markup: Keyboard markup
            
        Returns:
            Message: Pesan yang disalin
        """
        try:
            return await self.copy_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menyalin pesan: {e}")
            raise
    
    # ==================== MEDIA METHODS ====================
    
    async def kirim_foto(self, 
                        chat_id: Union[int, str],
                        photo: Union[str, BinaryIO],
                        caption: Optional[str] = None,
                        parse_mode: Optional[enums.ParseMode] = None,
                        caption_entities: Optional[List[types.MessageEntity]] = None,
                        has_spoiler: bool = False,
                        ttl_seconds: Optional[int] = None,
                        disable_notification: bool = False,
                        protect_content: bool = False,
                        reply_to_message_id: Optional[int] = None,
                        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                        **kwargs) -> types.Message:
        """
        Mengirim foto.
        
        Args:
            chat_id: ID chat atau username
            photo: File foto (path, URL, atau file object)
            caption: Caption foto
            parse_mode: Mode parsing
            caption_entities: Entities untuk caption
            has_spoiler: Tandai sebagai spoiler
            ttl_seconds: Waktu hidup foto (untuk chat pribadi)
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten dari forward
            reply_to_message_id: ID pesan yang akan direply
            reply_markup: Keyboard markup
            
        Returns:
            Message: Pesan foto yang dikirim
        """
        try:
            return await self.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                has_spoiler=has_spoiler,
                ttl_seconds=ttl_seconds,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim foto: {e}")
            raise
    
    async def kirim_video(self, 
                         chat_id: Union[int, str],
                         video: Union[str, BinaryIO],
                         duration: Optional[int] = None,
                         width: Optional[int] = None,
                         height: Optional[int] = None,
                         thumb: Optional[Union[str, BinaryIO]] = None,
                         caption: Optional[str] = None,
                         parse_mode: Optional[enums.ParseMode] = None,
                         caption_entities: Optional[List[types.MessageEntity]] = None,
                         has_spoiler: bool = False,
                         ttl_seconds: Optional[int] = None,
                         supports_streaming: bool = True,
                         disable_notification: bool = False,
                         protect_content: bool = False,
                         reply_to_message_id: Optional[int] = None,
                         reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                         **kwargs) -> types.Message:
        """
        Mengirim video.
        
        Args:
            chat_id: ID chat atau username
            video: File video (path, URL, atau file object)
            duration: Durasi video dalam detik
            width: Lebar video
            height: Tinggi video
            thumb: Thumbnail video
            caption: Caption video
            parse_mode: Mode parsing
            caption_entities: Entities untuk caption
            has_spoiler: Tandai sebagai spoiler
            ttl_seconds: Waktu hidup video (untuk chat pribadi)
            supports_streaming: Mendukung streaming
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten dari forward
            reply_to_message_id: ID pesan yang akan direply
            reply_markup: Keyboard markup
            
        Returns:
            Message: Pesan video yang dikirim
        """
        try:
            return await self.send_video(
                chat_id=chat_id,
                video=video,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                has_spoiler=has_spoiler,
                ttl_seconds=ttl_seconds,
                supports_streaming=supports_streaming,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim video: {e}")
            raise
    
    async def kirim_audio(self, 
                         chat_id: Union[int, str],
                         audio: Union[str, BinaryIO],
                         caption: Optional[str] = None,
                         parse_mode: Optional[enums.ParseMode] = None,
                         caption_entities: Optional[List[types.MessageEntity]] = None,
                         duration: Optional[int] = None,
                         performer: Optional[str] = None,
                         title: Optional[str] = None,
                         thumb: Optional[Union[str, BinaryIO]] = None,
                         disable_notification: bool = False,
                         protect_content: bool = False,
                         reply_to_message_id: Optional[int] = None,
                         reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                         **kwargs) -> types.Message:
        """
        Mengirim file audio.
        
        Args:
            chat_id: ID chat atau username
            audio: File audio (path, URL, atau file object)
            caption: Caption audio
            parse_mode: Mode parsing
            caption_entities: Entities untuk caption
            duration: Durasi audio dalam detik
            performer: Nama artis/performer
            title: Judul lagu
            thumb: Thumbnail audio
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten dari forward
            reply_to_message_id: ID pesan yang akan direply
            reply_markup: Keyboard markup
            
        Returns:
            Message: Pesan audio yang dikirim
        """
        try:
            return await self.send_audio(
                chat_id=chat_id,
                audio=audio,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                duration=duration,
                performer=performer,
                title=title,
                thumb=thumb,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim audio: {e}")
            raise
    
    async def kirim_dokumen(self, 
                           chat_id: Union[int, str],
                           document: Union[str, BinaryIO],
                           thumb: Optional[Union[str, BinaryIO]] = None,
                           caption: Optional[str] = None,
                           parse_mode: Optional[enums.ParseMode] = None,
                           caption_entities: Optional[List[types.MessageEntity]] = None,
                           file_name: Optional[str] = None,
                           disable_content_type_detection: bool = False,
                           disable_notification: bool = False,
                           protect_content: bool = False,
                           reply_to_message_id: Optional[int] = None,
                           reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                           **kwargs) -> types.Message:
        """
        Mengirim dokumen.
        
        Args:
            chat_id: ID chat atau username
            document: File dokumen (path, URL, atau file object)
            thumb: Thumbnail dokumen
            caption: Caption dokumen
            parse_mode: Mode parsing
            caption_entities: Entities untuk caption
            file_name: Nama file custom
            disable_content_type_detection: Nonaktifkan deteksi tipe konten
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten dari forward
            reply_to_message_id: ID pesan yang akan direply
            reply_markup: Keyboard markup
            
        Returns:
            Message: Pesan dokumen yang dikirim
        """
        try:
            return await self.send_document(
                chat_id=chat_id,
                document=document,
                thumb=thumb,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                file_name=file_name,
                disable_content_type_detection=disable_content_type_detection,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim dokumen: {e}")
            raise 