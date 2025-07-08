# syncara/modules/pyrogram_integration.py
"""
Integrasi semua method Pyrogram ke dalam class Bot dan Ubot.
File ini menggabungkan semua mixin class method Pyrogram.
"""

from .pyrogram_methods import PyrogramMethods
from .pyrogram_chat_methods import ChatMethods
from .pyrogram_inline_methods import InlineMethods
from .pyrogram_callback_methods import CallbackMethods
from syncara.console import console

class CompletePyrogramMethods(PyrogramMethods, ChatMethods, InlineMethods, CallbackMethods):
    """
    Class yang menggabungkan semua method Pyrogram dalam satu tempat.
    Class ini akan digunakan sebagai mixin untuk Bot dan Ubot.
    """
    
    def __init__(self):
        super().__init__()
        console.info("✅ Semua method Pyrogram telah dimuat")
    
    # ==================== UTILITY METHODS ====================
    
    async def get_info_diri(self) -> dict:
        """
        Mendapatkan informasi bot/userbot.
        
        Returns:
            dict: Informasi lengkap bot/userbot
        """
        try:
            me = await self.get_me()
            return {
                "id": me.id,
                "is_bot": me.is_bot,
                "is_verified": me.is_verified,
                "is_restricted": me.is_restricted,
                "is_scam": me.is_scam,
                "is_fake": me.is_fake,
                "is_premium": me.is_premium,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "language_code": me.language_code,
                "dc_id": me.dc_id,
                "phone_number": me.phone_number,
                "photo": me.photo
            }
        except Exception as e:
            console.error(f"Error mendapatkan info diri: {e}")
            raise
    
    async def cek_status_online(self) -> bool:
        """
        Mengecek apakah bot/userbot sedang online.
        
        Returns:
            bool: True jika online
        """
        try:
            await self.get_me()
            return True
        except Exception as e:
            console.error(f"Error cek status online: {e}")
            return False
    
    async def get_statistik_chat(self, chat_id: Union[int, str]) -> dict:
        """
        Mendapatkan statistik chat.
        
        Args:
            chat_id: ID chat atau username
            
        Returns:
            dict: Statistik chat
        """
        try:
            chat = await self.get_chat(chat_id)
            
            # Hitung jumlah member jika memungkinkan
            member_count = 0
            try:
                if chat.type in ["group", "supergroup"]:
                    member_count = await self.get_chat_members_count(chat_id)
            except:
                pass
            
            return {
                "id": chat.id,
                "type": chat.type,
                "title": chat.title,
                "username": chat.username,
                "first_name": chat.first_name,
                "last_name": chat.last_name,
                "description": chat.description,
                "invite_link": chat.invite_link,
                "pinned_message": chat.pinned_message,
                "member_count": member_count,
                "is_verified": chat.is_verified,
                "is_restricted": chat.is_restricted,
                "is_scam": chat.is_scam,
                "is_fake": chat.is_fake
            }
        except Exception as e:
            console.error(f"Error mendapatkan statistik chat: {e}")
            raise
    
    async def backup_chat(self, chat_id: Union[int, str], limit: int = 100) -> list:
        """
        Backup pesan dari chat.
        
        Args:
            chat_id: ID chat atau username
            limit: Jumlah pesan yang akan di-backup
            
        Returns:
            list: List pesan yang di-backup
        """
        try:
            messages = []
            async for message in self.get_chat_history(chat_id, limit=limit):
                message_data = {
                    "id": message.id,
                    "from_user": {
                        "id": message.from_user.id if message.from_user else None,
                        "first_name": message.from_user.first_name if message.from_user else None,
                        "username": message.from_user.username if message.from_user else None
                    },
                    "date": message.date,
                    "text": message.text,
                    "caption": message.caption,
                    "media_type": message.media.value if message.media else None,
                    "reply_to_message_id": message.reply_to_message_id,
                    "forward_from": {
                        "id": message.forward_from.id if message.forward_from else None,
                        "first_name": message.forward_from.first_name if message.forward_from else None
                    } if message.forward_from else None
                }
                messages.append(message_data)
            
            console.info(f"Berhasil backup {len(messages)} pesan dari chat {chat_id}")
            return messages
        except Exception as e:
            console.error(f"Error backup chat: {e}")
            raise
    
    async def kirim_pesan_terjadwal(self, 
                                   chat_id: Union[int, str],
                                   text: str,
                                   schedule_date: int,
                                   **kwargs) -> types.Message:
        """
        Mengirim pesan terjadwal.
        
        Args:
            chat_id: ID chat atau username
            text: Teks pesan
            schedule_date: Timestamp kapan pesan akan dikirim
            **kwargs: Parameter tambahan untuk send_message
            
        Returns:
            Message: Pesan terjadwal
        """
        try:
            return await self.send_message(
                chat_id=chat_id,
                text=text,
                schedule_date=schedule_date,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim pesan terjadwal: {e}")
            raise
    
    async def edit_pesan_media(self, 
                              chat_id: Union[int, str],
                              message_id: int,
                              media: types.InputMedia,
                              reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                              **kwargs) -> types.Message:
        """
        Mengedit media pesan.
        
        Args:
            chat_id: ID chat atau username
            message_id: ID pesan yang akan diedit
            media: Media baru
            reply_markup: Keyboard markup baru
            **kwargs: Parameter tambahan
            
        Returns:
            Message: Pesan yang diedit
        """
        try:
            return await self.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=media,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengedit media pesan: {e}")
            raise
    
    async def kirim_polling(self, 
                           chat_id: Union[int, str],
                           question: str,
                           options: List[str],
                           is_anonymous: bool = True,
                           type: str = "regular",
                           allows_multiple_answers: bool = False,
                           correct_option_id: Optional[int] = None,
                           explanation: Optional[str] = None,
                           explanation_parse_mode: Optional[str] = None,
                           open_period: Optional[int] = None,
                           close_date: Optional[int] = None,
                           is_closed: bool = False,
                           disable_notification: bool = False,
                           protect_content: bool = False,
                           reply_to_message_id: Optional[int] = None,
                           reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                           **kwargs) -> types.Message:
        """
        Mengirim polling.
        
        Args:
            chat_id: ID chat atau username
            question: Pertanyaan polling
            options: List opsi jawaban
            is_anonymous: Polling anonim
            type: Jenis polling ("regular" atau "quiz")
            allows_multiple_answers: Izinkan jawaban ganda
            correct_option_id: ID opsi yang benar (untuk quiz)
            explanation: Penjelasan jawaban
            explanation_parse_mode: Mode parsing penjelasan
            open_period: Durasi polling terbuka (detik)
            close_date: Timestamp kapan polling ditutup
            is_closed: Polling ditutup
            disable_notification: Kirim tanpa notifikasi
            protect_content: Lindungi konten
            reply_to_message_id: ID pesan reply
            reply_markup: Keyboard markup
            **kwargs: Parameter tambahan
            
        Returns:
            Message: Pesan polling
        """
        try:
            return await self.send_poll(
                chat_id=chat_id,
                question=question,
                options=options,
                is_anonymous=is_anonymous,
                type=type,
                allows_multiple_answers=allows_multiple_answers,
                correct_option_id=correct_option_id,
                explanation=explanation,
                explanation_parse_mode=explanation_parse_mode,
                open_period=open_period,
                close_date=close_date,
                is_closed=is_closed,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error mengirim polling: {e}")
            raise
    
    async def hentikan_polling(self, 
                              chat_id: Union[int, str],
                              message_id: int,
                              reply_markup: Optional[types.InlineKeyboardMarkup] = None,
                              **kwargs) -> types.Poll:
        """
        Menghentikan polling.
        
        Args:
            chat_id: ID chat atau username
            message_id: ID pesan polling
            reply_markup: Keyboard markup baru
            **kwargs: Parameter tambahan
            
        Returns:
            Poll: Polling yang dihentikan
        """
        try:
            return await self.stop_poll(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            console.error(f"Error menghentikan polling: {e}")
            raise
    
    # ==================== BANTUAN DAN DOKUMENTASI ====================
    
    def daftar_method_tersedia(self) -> dict:
        """
        Mendapatkan daftar semua method yang tersedia.
        
        Returns:
            dict: Daftar method berdasarkan kategori
        """
        return {
            "pesan": [
                "kirim_pesan", "edit_pesan", "hapus_pesan", "forward_pesan", 
                "copy_pesan", "kirim_pesan_terjadwal"
            ],
            "media": [
                "kirim_foto", "kirim_video", "kirim_audio", "kirim_dokumen",
                "edit_pesan_media"
            ],
            "chat": [
                "gabung_chat", "keluar_chat", "get_info_chat", "set_judul_chat",
                "set_deskripsi_chat", "set_foto_chat", "hapus_foto_chat",
                "set_izin_chat", "backup_chat", "get_statistik_chat"
            ],
            "member": [
                "get_member_chat", "get_daftar_member", "tambah_member_chat",
                "ban_member_chat", "unban_member_chat", "batasi_member_chat",
                "promosi_member_chat", "set_gelar_admin"
            ],
            "aksi": [
                "kirim_aksi_chat", "pin_pesan_chat", "unpin_pesan_chat",
                "unpin_semua_pesan"
            ],
            "inline": [
                "jawab_inline_query", "get_hasil_inline_bot", "kirim_hasil_inline_bot",
                "buat_hasil_artikel", "buat_hasil_foto", "buat_hasil_video",
                "buat_hasil_audio", "buat_hasil_dokumen", "buat_hasil_kontak",
                "buat_hasil_lokasi"
            ],
            "callback": [
                "jawab_callback_query", "minta_jawaban_callback"
            ],
            "bot": [
                "set_perintah_bot", "get_perintah_bot", "hapus_perintah_bot",
                "set_hak_akses_bot", "get_hak_akses_bot", "set_tombol_menu_chat",
                "get_tombol_menu_chat"
            ],
            "game": [
                "kirim_game", "set_skor_game", "get_skor_tinggi_game"
            ],
            "web_app": [
                "jawab_web_app_query"
            ],
            "keyboard": [
                "buat_keyboard_inline", "buat_keyboard_reply", "hapus_keyboard",
                "paksa_reply"
            ],
            "polling": [
                "kirim_polling", "hentikan_polling"
            ],
            "utility": [
                "get_info_diri", "cek_status_online", "get_statistik_chat",
                "backup_chat", "daftar_method_tersedia"
            ]
        }
    
    def bantuan_method(self, method_name: str) -> str:
        """
        Mendapatkan bantuan untuk method tertentu.
        
        Args:
            method_name: Nama method
            
        Returns:
            str: Dokumentasi method
        """
        method = getattr(self, method_name, None)
        if method and hasattr(method, '__doc__'):
            return method.__doc__ or f"Tidak ada dokumentasi untuk {method_name}"
        return f"Method {method_name} tidak ditemukan" 