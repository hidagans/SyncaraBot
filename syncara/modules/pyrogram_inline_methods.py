# syncara/modules/pyrogram_inline_methods.py
"""
Inline mode methods untuk Pyrogram.
Berisi semua method untuk menangani inline queries dan hasil inline.
"""

from pyrogram import types, enums
from pyrogram.errors import RPCError
from typing import Union, List, Optional, Dict, Any
from syncara.console import console

class InlineMethods:
    """
    Mixin class untuk method-method inline mode.
    """
    
    # ==================== INLINE QUERY METHODS ====================
    
    async def jawab_inline_query(self, 
                                inline_query_id: str,
                                results: List[types.InlineQueryResult],
                                cache_time: int = 300,
                                is_personal: bool = False,
                                next_offset: Optional[str] = None,
                                switch_pm_text: Optional[str] = None,
                                switch_pm_parameter: Optional[str] = None,
                                switch_pm_deep_link: Optional[str] = None,
                                **kwargs) -> bool:
        """
        Menjawab inline query.
        
        Args:
            inline_query_id: ID inline query
            results: List hasil inline query
            cache_time: Waktu cache dalam detik
            is_personal: Apakah hasil bersifat personal
            next_offset: Offset untuk hasil berikutnya
            switch_pm_text: Teks tombol switch ke PM
            switch_pm_parameter: Parameter untuk switch PM
            switch_pm_deep_link: Deep link untuk switch PM
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.answer_inline_query(
                inline_query_id=inline_query_id,
                results=results,
                cache_time=cache_time,
                is_personal=is_personal,
                next_offset=next_offset,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter=switch_pm_parameter,
                switch_pm_deep_link=switch_pm_deep_link,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menjawab inline query: {e}")
            raise
    
    async def get_hasil_inline_bot(self, 
                                  bot_username: str,
                                  query: str,
                                  offset: str = "",
                                  location: Optional[types.Location] = None,
                                  **kwargs) -> types.BotResults:
        """
        Mendapatkan hasil inline query dari bot.
        
        Args:
            bot_username: Username bot
            query: Query string
            offset: Offset untuk pagination
            location: Lokasi user
            
        Returns:
            BotResults: Hasil inline query
        """
        try:
            return await self.get_inline_bot_results(
                bot=bot_username,
                query=query,
                offset=offset,
                location=location,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mendapatkan hasil inline bot: {e}")
            raise
    
    async def kirim_hasil_inline_bot(self, 
                                    chat_id: Union[int, str],
                                    query_id: int,
                                    result_id: str,
                                    disable_notification: bool = False,
                                    reply_to_message_id: Optional[int] = None,
                                    **kwargs) -> types.Message:
        """
        Mengirim hasil inline bot.
        
        Args:
            chat_id: ID chat tujuan
            query_id: ID query dari get_inline_bot_results
            result_id: ID hasil yang dipilih
            disable_notification: Kirim tanpa notifikasi
            reply_to_message_id: ID pesan yang akan direply
            
        Returns:
            Message: Pesan yang dikirim
        """
        try:
            return await self.send_inline_bot_result(
                chat_id=chat_id,
                query_id=query_id,
                result_id=result_id,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim hasil inline bot: {e}")
            raise
    
    # ==================== INLINE RESULT BUILDERS ====================
    
    def buat_hasil_artikel(self, 
                          id: str,
                          title: str,
                          input_message_content: types.InputMessageContent,
                          url: Optional[str] = None,
                          hide_url: bool = False,
                          description: Optional[str] = None,
                          thumb_url: Optional[str] = None,
                          thumb_width: Optional[int] = None,
                          thumb_height: Optional[int] = None,
                          reply_markup: Optional[types.InlineKeyboardMarkup] = None) -> types.InlineQueryResultArticle:
        """
        Membuat hasil inline query berupa artikel.
        
        Args:
            id: ID unik hasil
            title: Judul artikel
            input_message_content: Konten pesan yang akan dikirim
            url: URL artikel
            hide_url: Sembunyikan URL
            description: Deskripsi artikel
            thumb_url: URL thumbnail
            thumb_width: Lebar thumbnail
            thumb_height: Tinggi thumbnail
            reply_markup: Keyboard markup
            
        Returns:
            InlineQueryResultArticle: Hasil artikel
        """
        try:
            return types.InlineQueryResultArticle(
                id=id,
                title=title,
                input_message_content=input_message_content,
                url=url,
                hide_url=hide_url,
                description=description,
                thumb_url=thumb_url,
                thumb_width=thumb_width,
                thumb_height=thumb_height,
                reply_markup=reply_markup
            )
        except Exception as e:
            console.error(f"Error membuat hasil artikel: {e}")
            raise
    
    def buat_hasil_foto(self, 
                       id: str,
                       photo_url: str,
                       thumb_url: str,
                       photo_width: Optional[int] = None,
                       photo_height: Optional[int] = None,
                       title: Optional[str] = None,
                       description: Optional[str] = None,
                       caption: Optional[str] = None,
                       parse_mode: Optional[enums.ParseMode] = None,
                       caption_entities: Optional[List[types.MessageEntity]] = None,
                       reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                       input_message_content: Optional[types.InputMessageContent] = None) -> types.InlineQueryResultPhoto:
        """
        Membuat hasil inline query berupa foto.
        
        Args:
            id: ID unik hasil
            photo_url: URL foto
            thumb_url: URL thumbnail
            photo_width: Lebar foto
            photo_height: Tinggi foto
            title: Judul foto
            description: Deskripsi foto
            caption: Caption foto
            parse_mode: Mode parsing
            caption_entities: Entities caption
            reply_markup: Keyboard markup
            input_message_content: Konten pesan custom
            
        Returns:
            InlineQueryResultPhoto: Hasil foto
        """
        try:
            return types.InlineQueryResultPhoto(
                id=id,
                photo_url=photo_url,
                thumb_url=thumb_url,
                photo_width=photo_width,
                photo_height=photo_height,
                title=title,
                description=description,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                reply_markup=reply_markup,
                input_message_content=input_message_content
            )
        except Exception as e:
            console.error(f"Error membuat hasil foto: {e}")
            raise
    
    def buat_hasil_video(self, 
                        id: str,
                        video_url: str,
                        mime_type: str,
                        thumb_url: str,
                        title: str,
                        video_width: Optional[int] = None,
                        video_height: Optional[int] = None,
                        video_duration: Optional[int] = None,
                        description: Optional[str] = None,
                        caption: Optional[str] = None,
                        parse_mode: Optional[enums.ParseMode] = None,
                        caption_entities: Optional[List[types.MessageEntity]] = None,
                        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                        input_message_content: Optional[types.InputMessageContent] = None) -> types.InlineQueryResultVideo:
        """
        Membuat hasil inline query berupa video.
        
        Args:
            id: ID unik hasil
            video_url: URL video
            mime_type: Tipe MIME video
            thumb_url: URL thumbnail
            title: Judul video
            video_width: Lebar video
            video_height: Tinggi video
            video_duration: Durasi video
            description: Deskripsi video
            caption: Caption video
            parse_mode: Mode parsing
            caption_entities: Entities caption
            reply_markup: Keyboard markup
            input_message_content: Konten pesan custom
            
        Returns:
            InlineQueryResultVideo: Hasil video
        """
        try:
            return types.InlineQueryResultVideo(
                id=id,
                video_url=video_url,
                mime_type=mime_type,
                thumb_url=thumb_url,
                title=title,
                video_width=video_width,
                video_height=video_height,
                video_duration=video_duration,
                description=description,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                reply_markup=reply_markup,
                input_message_content=input_message_content
            )
        except Exception as e:
            console.error(f"Error membuat hasil video: {e}")
            raise
    
    def buat_hasil_audio(self, 
                        id: str,
                        audio_url: str,
                        title: str,
                        caption: Optional[str] = None,
                        parse_mode: Optional[enums.ParseMode] = None,
                        caption_entities: Optional[List[types.MessageEntity]] = None,
                        performer: Optional[str] = None,
                        audio_duration: Optional[int] = None,
                        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                        input_message_content: Optional[types.InputMessageContent] = None) -> types.InlineQueryResultAudio:
        """
        Membuat hasil inline query berupa audio.
        
        Args:
            id: ID unik hasil
            audio_url: URL audio
            title: Judul audio
            caption: Caption audio
            parse_mode: Mode parsing
            caption_entities: Entities caption
            performer: Nama artis
            audio_duration: Durasi audio
            reply_markup: Keyboard markup
            input_message_content: Konten pesan custom
            
        Returns:
            InlineQueryResultAudio: Hasil audio
        """
        try:
            return types.InlineQueryResultAudio(
                id=id,
                audio_url=audio_url,
                title=title,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                performer=performer,
                audio_duration=audio_duration,
                reply_markup=reply_markup,
                input_message_content=input_message_content
            )
        except Exception as e:
            console.error(f"Error membuat hasil audio: {e}")
            raise
    
    def buat_hasil_dokumen(self, 
                          id: str,
                          title: str,
                          document_url: str,
                          mime_type: str,
                          caption: Optional[str] = None,
                          parse_mode: Optional[enums.ParseMode] = None,
                          caption_entities: Optional[List[types.MessageEntity]] = None,
                          description: Optional[str] = None,
                          reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                          input_message_content: Optional[types.InputMessageContent] = None,
                          thumb_url: Optional[str] = None,
                          thumb_width: Optional[int] = None,
                          thumb_height: Optional[int] = None) -> types.InlineQueryResultDocument:
        """
        Membuat hasil inline query berupa dokumen.
        
        Args:
            id: ID unik hasil
            title: Judul dokumen
            document_url: URL dokumen
            mime_type: Tipe MIME dokumen
            caption: Caption dokumen
            parse_mode: Mode parsing
            caption_entities: Entities caption
            description: Deskripsi dokumen
            reply_markup: Keyboard markup
            input_message_content: Konten pesan custom
            thumb_url: URL thumbnail
            thumb_width: Lebar thumbnail
            thumb_height: Tinggi thumbnail
            
        Returns:
            InlineQueryResultDocument: Hasil dokumen
        """
        try:
            return types.InlineQueryResultDocument(
                id=id,
                title=title,
                document_url=document_url,
                mime_type=mime_type,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                description=description,
                reply_markup=reply_markup,
                input_message_content=input_message_content,
                thumb_url=thumb_url,
                thumb_width=thumb_width,
                thumb_height=thumb_height
            )
        except Exception as e:
            console.error(f"Error membuat hasil dokumen: {e}")
            raise
    
    def buat_hasil_kontak(self, 
                         id: str,
                         phone_number: str,
                         first_name: str,
                         last_name: Optional[str] = None,
                         vcard: Optional[str] = None,
                         reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                         input_message_content: Optional[types.InputMessageContent] = None,
                         thumb_url: Optional[str] = None,
                         thumb_width: Optional[int] = None,
                         thumb_height: Optional[int] = None) -> types.InlineQueryResultContact:
        """
        Membuat hasil inline query berupa kontak.
        
        Args:
            id: ID unik hasil
            phone_number: Nomor telepon
            first_name: Nama depan
            last_name: Nama belakang
            vcard: VCard
            reply_markup: Keyboard markup
            input_message_content: Konten pesan custom
            thumb_url: URL thumbnail
            thumb_width: Lebar thumbnail
            thumb_height: Tinggi thumbnail
            
        Returns:
            InlineQueryResultContact: Hasil kontak
        """
        try:
            return types.InlineQueryResultContact(
                id=id,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                vcard=vcard,
                reply_markup=reply_markup,
                input_message_content=input_message_content,
                thumb_url=thumb_url,
                thumb_width=thumb_width,
                thumb_height=thumb_height
            )
        except Exception as e:
            console.error(f"Error membuat hasil kontak: {e}")
            raise
    
    def buat_hasil_lokasi(self, 
                         id: str,
                         latitude: float,
                         longitude: float,
                         title: str,
                         live_period: Optional[int] = None,
                         heading: Optional[int] = None,
                         proximity_alert_radius: Optional[int] = None,
                         reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                         input_message_content: Optional[types.InputMessageContent] = None,
                         thumb_url: Optional[str] = None,
                         thumb_width: Optional[int] = None,
                         thumb_height: Optional[int] = None) -> types.InlineQueryResultLocation:
        """
        Membuat hasil inline query berupa lokasi.
        
        Args:
            id: ID unik hasil
            latitude: Latitude
            longitude: Longitude
            title: Judul lokasi
            live_period: Durasi live location
            heading: Arah (0-360)
            proximity_alert_radius: Radius alert kedekatan
            reply_markup: Keyboard markup
            input_message_content: Konten pesan custom
            thumb_url: URL thumbnail
            thumb_width: Lebar thumbnail
            thumb_height: Tinggi thumbnail
            
        Returns:
            InlineQueryResultLocation: Hasil lokasi
        """
        try:
            return types.InlineQueryResultLocation(
                id=id,
                latitude=latitude,
                longitude=longitude,
                title=title,
                live_period=live_period,
                heading=heading,
                proximity_alert_radius=proximity_alert_radius,
                reply_markup=reply_markup,
                input_message_content=input_message_content,
                thumb_url=thumb_url,
                thumb_width=thumb_width,
                thumb_height=thumb_height
            )
        except Exception as e:
            console.error(f"Error membuat hasil lokasi: {e}")
            raise 