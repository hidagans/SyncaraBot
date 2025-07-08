# syncara/modules/pyrogram_callback_methods.py
"""
Callback query dan bot management methods untuk Pyrogram.
Berisi semua method untuk menangani callback queries dan manajemen bot.
"""

from pyrogram import types, enums
from pyrogram.errors import RPCError
from typing import Union, List, Optional, Dict, Any
from syncara.console import console
from .pyrogram_compatibility import (
    AVAILABLE_TYPES,
    create_bot_command,
    create_inline_keyboard_markup,
    create_reply_keyboard_markup
)

class CallbackMethods:
    """
    Mixin class untuk method-method callback query dan bot management.
    """
    
    # ==================== CALLBACK QUERY METHODS ====================
    
    async def jawab_callback_query(self, 
                                  callback_query_id: str,
                                  text: Optional[str] = None,
                                  show_alert: bool = False,
                                  url: Optional[str] = None,
                                  cache_time: int = 0,
                                  **kwargs) -> bool:
        """
        Menjawab callback query dari inline keyboard.
        
        Args:
            callback_query_id: ID callback query
            text: Teks notifikasi (maks 200 karakter)
            show_alert: Tampilkan sebagai alert popup
            url: URL untuk membuka (untuk game callback)
            cache_time: Waktu cache dalam detik
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.answer_callback_query(
                callback_query_id=callback_query_id,
                text=text,
                show_alert=show_alert,
                url=url,
                cache_time=cache_time,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menjawab callback query: {e}")
            raise
    
    async def minta_jawaban_callback(self, 
                                    chat_id: Union[int, str],
                                    message_id: int,
                                    callback_data: Union[str, bytes],
                                    timeout: int = 10,
                                    **kwargs) -> bool:
        """
        Meminta jawaban callback dari bot.
        
        Args:
            chat_id: ID chat
            message_id: ID pesan dengan inline keyboard
            callback_data: Data callback
            timeout: Timeout dalam detik
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.request_callback_answer(
                chat_id=chat_id,
                message_id=message_id,
                callback_data=callback_data,
                timeout=timeout,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error meminta jawaban callback: {e}")
            raise
    
    # ==================== BOT MANAGEMENT METHODS ====================
    
    async def set_perintah_bot(self, 
                              commands: List[Union[dict, Any]],
                              scope: Optional[Any] = None,
                              language_code: Optional[str] = None,
                              **kwargs) -> bool:
        """
        Mengatur daftar perintah bot.
        
        Args:
            commands: List perintah bot (dict atau BotCommand objects)
            scope: Scope perintah (default, chat, user, dll)
            language_code: Kode bahasa
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Handle commands dengan compatibility check
            processed_commands = []
            for cmd in commands:
                if isinstance(cmd, dict):
                    processed_commands.append(create_bot_command(cmd.get('command', ''), cmd.get('description', '')))
                else:
                    processed_commands.append(cmd)
            
            return await self.set_bot_commands(
                commands=processed_commands,
                scope=scope,
                language_code=language_code,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengatur perintah bot: {e}")
            raise
    
    async def get_perintah_bot(self, 
                              scope: Optional[Any] = None,
                              language_code: Optional[str] = None,
                              **kwargs) -> List[Any]:
        """
        Mendapatkan daftar perintah bot.
        
        Args:
            scope: Scope perintah
            language_code: Kode bahasa
            
        Returns:
            List[BotCommand]: List perintah bot
        """
        try:
            return await self.get_bot_commands(
                scope=scope,
                language_code=language_code,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mendapatkan perintah bot: {e}")
            raise
    
    async def hapus_perintah_bot(self, 
                                scope: Optional[Any] = None,
                                language_code: Optional[str] = None,
                                **kwargs) -> bool:
        """
        Menghapus perintah bot.
        
        Args:
            scope: Scope perintah
            language_code: Kode bahasa
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.delete_bot_commands(
                scope=scope,
                language_code=language_code,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menghapus perintah bot: {e}")
            raise
    
    async def set_hak_akses_bot(self, 
                               privileges: Union[dict, Any],
                               for_channels: Optional[bool] = None,
                               **kwargs) -> bool:
        """
        Mengatur hak akses default bot.
        
        Args:
            privileges: Hak akses administrator
            for_channels: Untuk channel (True) atau grup (False)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_bot_default_privileges(
                privileges=privileges,
                for_channels=for_channels,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengatur hak akses bot: {e}")
            raise
    
    async def get_hak_akses_bot(self, 
                               for_channels: Optional[bool] = None,
                               **kwargs) -> Any:
        """
        Mendapatkan hak akses default bot.
        
        Args:
            for_channels: Untuk channel (True) atau grup (False)
            
        Returns:
            ChatAdministratorRights: Hak akses bot
        """
        try:
            return await self.get_bot_default_privileges(
                for_channels=for_channels,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mendapatkan hak akses bot: {e}")
            raise
    
    async def set_tombol_menu_chat(self, 
                                  chat_id: Optional[Union[int, str]] = None,
                                  menu_button: Optional[Any] = None,
                                  **kwargs) -> bool:
        """
        Mengatur tombol menu bot di chat.
        
        Args:
            chat_id: ID chat (None untuk default)
            menu_button: Tombol menu
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.set_chat_menu_button(
                chat_id=chat_id,
                menu_button=menu_button,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengatur tombol menu: {e}")
            raise
    
    async def get_tombol_menu_chat(self, 
                                  chat_id: Optional[Union[int, str]] = None,
                                  **kwargs) -> Any:
        """
        Mendapatkan tombol menu bot di chat.
        
        Args:
            chat_id: ID chat (None untuk default)
            
        Returns:
            MenuButton: Tombol menu
        """
        try:
            return await self.get_chat_menu_button(
                chat_id=chat_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mendapatkan tombol menu: {e}")
            raise
    
    # ==================== GAME METHODS ====================
    
    async def kirim_game(self, 
                        chat_id: Union[int, str],
                        game_short_name: str,
                        disable_notification: bool = False,
                        protect_content: bool = False,
                        reply_to_message_id: Optional[int] = None,
                        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                        **kwargs) -> types.Message:
        """
        Mengirim game.
        
        Args:
            chat_id: ID chat
            game_short_name: Nama pendek game
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten
            reply_to_message_id: ID pesan reply
            reply_markup: Keyboard markup
            
        Returns:
            Message: Pesan game
        """
        try:
            return await self.send_game(
                chat_id=chat_id,
                game_short_name=game_short_name,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim game: {e}")
            raise
    
    async def set_skor_game(self, 
                           user_id: Union[int, str],
                           score: int,
                           force: bool = False,
                           disable_edit_message: bool = False,
                           chat_id: Optional[Union[int, str]] = None,
                           message_id: Optional[int] = None,
                           inline_message_id: Optional[str] = None,
                           **kwargs) -> Union[types.Message, bool]:
        """
        Mengatur skor game user.
        
        Args:
            user_id: ID user
            score: Skor baru
            force: Paksa update meskipun skor lebih rendah
            disable_edit_message: Jangan edit pesan
            chat_id: ID chat (untuk pesan biasa)
            message_id: ID pesan (untuk pesan biasa)
            inline_message_id: ID pesan inline (untuk inline message)
            
        Returns:
            Message atau bool: Pesan yang diedit atau True jika berhasil
        """
        try:
            return await self.set_game_score(
                user_id=user_id,
                score=score,
                force=force,
                disable_edit_message=disable_edit_message,
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengatur skor game: {e}")
            raise
    
    async def get_skor_tinggi_game(self, 
                                  user_id: Union[int, str],
                                  chat_id: Optional[Union[int, str]] = None,
                                  message_id: Optional[int] = None,
                                  inline_message_id: Optional[str] = None,
                                  **kwargs) -> List[types.GameHighScore]:
        """
        Mendapatkan skor tinggi game.
        
        Args:
            user_id: ID user
            chat_id: ID chat (untuk pesan biasa)
            message_id: ID pesan (untuk pesan biasa)
            inline_message_id: ID pesan inline (untuk inline message)
            
        Returns:
            List[GameHighScore]: List skor tinggi
        """
        try:
            return await self.get_game_high_scores(
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mendapatkan skor tinggi game: {e}")
            raise
    
    # ==================== WEB APP METHODS ====================
    
    async def jawab_web_app_query(self, 
                                 web_app_query_id: str,
                                 result: types.InlineQueryResult,
                                 **kwargs) -> bool:
        """
        Menjawab web app query.
        
        Args:
            web_app_query_id: ID web app query
            result: Hasil query
            
        Returns:
            bool: True jika berhasil
        """
        try:
            return await self.answer_web_app_query(
                web_app_query_id=web_app_query_id,
                result=result,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menjawab web app query: {e}")
            raise
    
    # ==================== KEYBOARD BUILDER HELPERS ====================
    
    def buat_keyboard_inline(self, 
                           buttons: List[List[Dict[str, Any]]]) -> Any:
        """
        Membuat inline keyboard markup.
        
        Args:
            buttons: List tombol dalam format [
                [{"text": "Tombol1", "callback_data": "data1"}, {"text": "Tombol2", "url": "https://example.com"}],
                [{"text": "Tombol3", "callback_data": "data3"}]
            ]
            
        Returns:
            InlineKeyboardMarkup: Keyboard markup
        """
        try:
            keyboard = []
            for row in buttons:
                keyboard_row = []
                for button in row:
                    if AVAILABLE_TYPES.get('InlineKeyboardButton', False):
                        keyboard_row.append(types.InlineKeyboardButton(**button))
                    else:
                        keyboard_row.append(button)
                keyboard.append(keyboard_row)
            return create_inline_keyboard_markup(keyboard)
        except Exception as e:
            console.error(f"Error membuat keyboard inline: {e}")
            raise
    
    def buat_keyboard_reply(self, 
                          buttons: List[List[str]],
                          resize_keyboard: bool = True,
                          one_time_keyboard: bool = False,
                          selective: bool = False,
                          placeholder: Optional[str] = None) -> Any:
        """
        Membuat reply keyboard markup.
        
        Args:
            buttons: List tombol dalam format [["Tombol1", "Tombol2"], ["Tombol3"]]
            resize_keyboard: Resize keyboard otomatis
            one_time_keyboard: Sembunyikan setelah digunakan
            selective: Keyboard hanya untuk user tertentu
            placeholder: Placeholder untuk input field
            
        Returns:
            ReplyKeyboardMarkup: Keyboard markup
        """
        try:
            keyboard = []
            for row in buttons:
                keyboard_row = []
                for button_text in row:
                    if AVAILABLE_TYPES.get('KeyboardButton', False):
                        keyboard_row.append(types.KeyboardButton(button_text))
                    else:
                        keyboard_row.append(button_text)
                keyboard.append(keyboard_row)
            return create_reply_keyboard_markup(
                keyboard=keyboard,
                resize_keyboard=resize_keyboard,
                one_time_keyboard=one_time_keyboard,
                selective=selective,
                input_field_placeholder=placeholder
            )
        except Exception as e:
            console.error(f"Error membuat keyboard reply: {e}")
            raise
    
    def hapus_keyboard(self, 
                      selective: bool = False) -> Any:
        """
        Menghapus keyboard.
        
        Args:
            selective: Hapus hanya untuk user tertentu
            
        Returns:
            ReplyKeyboardRemove: Markup untuk menghapus keyboard
        """
        try:
            if AVAILABLE_TYPES.get('ReplyKeyboardRemove', False):
                return types.ReplyKeyboardRemove(selective=selective)
            else:
                return {"remove_keyboard": True, "selective": selective}
        except Exception as e:
            console.error(f"Error menghapus keyboard: {e}")
            raise
    
    def paksa_reply(self, 
                   selective: bool = False,
                   placeholder: Optional[str] = None) -> Any:
        """
        Memaksa user untuk reply.
        
        Args:
            selective: Paksa reply hanya untuk user tertentu
            placeholder: Placeholder untuk input field
            
        Returns:
            ForceReply: Markup untuk memaksa reply
        """
        try:
            if AVAILABLE_TYPES.get('ForceReply', False):
                return types.ForceReply(
                    selective=selective,
                    input_field_placeholder=placeholder
                )
            else:
                return {
                    "force_reply": True,
                    "selective": selective,
                    "input_field_placeholder": placeholder
                }
        except Exception as e:
            console.error(f"Error memaksa reply: {e}")
            raise 