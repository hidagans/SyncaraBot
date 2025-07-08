# syncara/modules/pyrogram_integration.py
"""
Integrasi semua method Pyrogram ke dalam class Bot dan Ubot.
File ini menggabungkan semua mixin class method Pyrogram.
"""

from .pyrogram_methods import PyrogramMethods
from .pyrogram_chat_methods import ChatMethods
from .pyrogram_inline_methods import InlineMethods
from .pyrogram_callback_methods import CallbackMethods
from .pyrogram_advanced_methods import AdvancedMethods
from .pyrogram_utilities import UtilitiesMethods
from .pyrogram_bound_methods import PyrogramBoundMethods
from .pyrogram_helpers import PyrogramHelpers, pyrogram_helpers
from .pyrogram_scheduler import PyrogramScheduler, pyrogram_scheduler
from syncara.console import console

class CompletePyrogramMethods(PyrogramMethods, ChatMethods, InlineMethods, CallbackMethods, AdvancedMethods, UtilitiesMethods, PyrogramBoundMethods):
    """
    Class yang menggabungkan semua method Pyrogram dalam satu tempat.
    Class ini akan digunakan sebagai mixin untuk Bot dan Ubot.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize helpers and scheduler
        self.helpers = pyrogram_helpers
        self.scheduler = pyrogram_scheduler
        console.info("✅ Semua method Pyrogram telah dimuat dengan helpers, cache system, dan scheduler")
    
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
    
    # ==================== SCHEDULER METHODS ====================
    
    async def jadwalkan_pesan(self, 
                             chat_id: Union[int, str],
                             text: str,
                             send_time: datetime,
                             task_id: str = None,
                             **kwargs) -> bool:
        """
        Jadwalkan pengiriman pesan.
        
        Args:
            chat_id: ID chat tujuan
            text: Teks pesan
            send_time: Waktu pengiriman
            task_id: ID task (optional)
            
        Returns:
            bool: True jika berhasil dijadwalkan
        """
        return await self.scheduler.schedule_message(
            client=self,
            chat_id=chat_id,
            text=text,
            send_time=send_time,
            task_id=task_id,
            **kwargs
        )
    
    async def jadwalkan_backup(self,
                              chat_id: Union[int, str],
                              backup_interval_hours: int = 24,
                              task_id: str = None) -> bool:
        """
        Jadwalkan backup chat otomatis.
        
        Args:
            chat_id: ID chat yang akan di-backup
            backup_interval_hours: Interval backup dalam jam
            task_id: ID task (optional)
            
        Returns:
            bool: True jika berhasil dijadwalkan
        """
        return await self.scheduler.schedule_backup(
            client=self,
            chat_id=chat_id,
            backup_interval_hours=backup_interval_hours,
            task_id=task_id
        )
    
    async def jadwalkan_cleanup(self,
                               chat_id: Union[int, str],
                               cleanup_interval_hours: int = 168,
                               max_age_days: int = 30,
                               task_id: str = None) -> bool:
        """
        Jadwalkan cleanup pesan lama.
        
        Args:
            chat_id: ID chat yang akan di-cleanup
            cleanup_interval_hours: Interval cleanup dalam jam
            max_age_days: Umur maksimal pesan (hari)
            task_id: ID task (optional)
            
        Returns:
            bool: True jika berhasil dijadwalkan
        """
        return await self.scheduler.schedule_cleanup(
            client=self,
            chat_id=chat_id,
            cleanup_interval_hours=cleanup_interval_hours,
            max_age_days=max_age_days,
            task_id=task_id
        )
    
    async def jadwalkan_laporan_analytics(self,
                                         report_chat_id: Union[int, str],
                                         report_interval_hours: int = 24,
                                         task_id: str = None) -> bool:
        """
        Jadwalkan laporan analytics.
        
        Args:
            report_chat_id: ID chat tujuan laporan
            report_interval_hours: Interval laporan dalam jam
            task_id: ID task (optional)
            
        Returns:
            bool: True jika berhasil dijadwalkan
        """
        return await self.scheduler.schedule_analytics_report(
            client=self,
            report_chat_id=report_chat_id,
            report_interval_hours=report_interval_hours,
            task_id=task_id
        )
    
    async def start_scheduler(self) -> bool:
        """
        Memulai scheduler.
        
        Returns:
            bool: True jika berhasil
        """
        await self.scheduler.start()
        return True
    
    async def stop_scheduler(self) -> bool:
        """
        Menghentikan scheduler.
        
        Returns:
            bool: True jika berhasil
        """
        await self.scheduler.stop()
        return True
    
    def add_scheduled_task(self, 
                          task_id: str,
                          name: str,
                          func: Callable,
                          args: tuple = (),
                          kwargs: dict = None,
                          cron_expression: str = None,
                          interval_seconds: int = None,
                          **options) -> bool:
        """
        Menambahkan task ke scheduler.
        
        Args:
            task_id: ID unik task
            name: Nama task
            func: Fungsi yang akan dijalankan
            args: Arguments untuk fungsi
            kwargs: Keyword arguments untuk fungsi
            cron_expression: Ekspresi cron (optional)
            interval_seconds: Interval dalam detik (optional)
            
        Returns:
            bool: True jika berhasil
        """
        return self.scheduler.add_task(
            task_id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
            **options
        )
    
    def remove_scheduled_task(self, task_id: str) -> bool:
        """
        Menghapus task dari scheduler.
        
        Args:
            task_id: ID task yang akan dihapus
            
        Returns:
            bool: True jika berhasil
        """
        return self.scheduler.remove_task(task_id)
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar semua scheduled tasks.
        
        Returns:
            List[Dict]: Daftar task
        """
        return self.scheduler.get_all_tasks()
    
    # ==================== HELPER METHODS ====================
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Mendapatkan statistik cache.
        
        Returns:
            Dict: Statistik cache
        """
        return self.helpers.get_cache_stats()
    
    async def cleanup_cache(self) -> Dict[str, int]:
        """
        Membersihkan cache.
        
        Returns:
            Dict: Jumlah cache yang dibersihkan
        """
        return await self.helpers.cleanup_cache()
    
    async def batch_operation(self, operations: List[Callable], batch_size: int = 10, delay: float = 0.1) -> List[Any]:
        """
        Menjalankan operasi secara batch.
        
        Args:
            operations: Daftar operasi
            batch_size: Ukuran batch
            delay: Delay antar batch
            
        Returns:
            List: Hasil operasi
        """
        return await self.helpers.batch_operation(operations, batch_size, delay)
    
    async def safe_execute(self, operation: Callable, max_retries: int = 3, delay: float = 1.0) -> Any:
        """
        Menjalankan operasi dengan safety dan retry.
        
        Args:
            operation: Operasi yang akan dijalankan
            max_retries: Maksimal retry
            delay: Delay antar retry
            
        Returns:
            Any: Hasil operasi
        """
        return await self.helpers.safe_execute(operation, max_retries, delay)
    
    def create_progress_callback(self, total_items: int, description: str = "Processing") -> Callable:
        """
        Membuat callback untuk progress tracking.
        
        Args:
            total_items: Total item yang akan diproses
            description: Deskripsi proses
            
        Returns:
            Callable: Callback function
        """
        return self.helpers.create_progress_callback(total_items, description)
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Format ukuran file dalam format yang mudah dibaca.
        
        Args:
            size_bytes: Ukuran dalam bytes
            
        Returns:
            str: Ukuran terformat
        """
        return self.helpers.format_file_size(size_bytes)
    
    def format_duration(self, seconds: float) -> str:
        """
        Format durasi dalam format yang mudah dibaca.
        
        Args:
            seconds: Durasi dalam detik
            
        Returns:
            str: Durasi terformat
        """
        return self.helpers.format_duration(seconds)
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Ekstrak mentions dari teks.
        
        Args:
            text: Teks yang akan diproses
            
        Returns:
            List[str]: Daftar mentions
        """
        return self.helpers.extract_mentions(text)
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Ekstrak hashtags dari teks.
        
        Args:
            text: Teks yang akan diproses
            
        Returns:
            List[str]: Daftar hashtags
        """
        return self.helpers.extract_hashtags(text)
    
    async def compress_image(self, input_path: str, output_path: str, quality: int = 85) -> bool:
        """
        Kompres gambar.
        
        Args:
            input_path: Path input gambar
            output_path: Path output gambar
            quality: Kualitas kompresi (1-100)
            
        Returns:
            bool: True jika berhasil
        """
        return await self.helpers.compress_image(input_path, output_path, quality)
    
    async def create_thumbnail(self, input_path: str, output_path: str, size: tuple = (200, 200)) -> bool:
        """
        Membuat thumbnail dari gambar.
        
        Args:
            input_path: Path input gambar
            output_path: Path output thumbnail
            size: Ukuran thumbnail (width, height)
            
        Returns:
            bool: True jika berhasil
        """
        return await self.helpers.create_thumbnail(input_path, output_path, size)
    
    async def get_media_info(self, file_path: str) -> Dict[str, Any]:
        """
        Mendapatkan informasi media file.
        
        Args:
            file_path: Path file media
            
        Returns:
            Dict: Informasi media
        """
        return await self.helpers.get_media_info(file_path)
    
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
                "copy_pesan", "kirim_pesan_terjadwal", "get_pesan_spesifik",
                "get_grup_media", "kirim_bulk_pesan", "forward_bulk_pesan"
            ],
            "media": [
                "kirim_foto", "kirim_video", "kirim_audio", "kirim_dokumen",
                "edit_pesan_media", "download_media_extended", "upload_file_extended"
            ],
            "chat": [
                "gabung_chat", "keluar_chat", "get_info_chat", "set_judul_chat",
                "set_deskripsi_chat", "set_foto_chat", "hapus_foto_chat",
                "set_izin_chat", "backup_chat", "get_statistik_chat",
                "buat_channel", "buat_grup", "buat_supergroup", "hapus_channel",
                "hapus_supergroup", "arsip_chat", "unarsip_chat"
            ],
            "member": [
                "get_member_chat", "get_daftar_member", "tambah_member_chat",
                "ban_member_chat", "unban_member_chat", "batasi_member_chat",
                "promosi_member_chat", "set_gelar_admin", "hapus_riwayat_user"
            ],
            "aksi": [
                "kirim_aksi_chat", "pin_pesan_chat", "unpin_pesan_chat",
                "unpin_semua_pesan", "tandai_chat_belum_dibaca", "baca_riwayat_chat"
            ],
            "advanced_chat": [
                "set_mode_lambat", "get_log_event_chat", "hitung_member_online",
                "get_daftar_send_as", "set_send_as_chat", "set_konten_terlindungi",
                "export_chat_invite_link", "create_chat_invite_link", 
                "edit_chat_invite_link", "revoke_chat_invite_link"
            ],
            "riwayat": [
                "get_riwayat_chat", "hitung_riwayat_chat", "baca_riwayat_chat",
                "backup_lengkap_chat", "restore_chat_dari_backup"
            ],
            "inline": [
                "jawab_inline_query", "get_hasil_inline_bot", "kirim_hasil_inline_bot",
                "buat_hasil_artikel", "buat_hasil_foto", "buat_hasil_video",
                "buat_hasil_audio", "buat_hasil_dokumen", "buat_hasil_kontak",
                "buat_hasil_lokasi", "edit_caption_inline", "edit_media_inline",
                "edit_reply_markup_inline"
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
                "kirim_polling", "hentikan_polling", "vote_polling"
            ],
            "lifecycle": [
                "mulai_bot", "hentikan_bot", "restart_bot", "jalankan_bot"
            ],
            "scheduler": [
                "jadwalkan_pesan", "jadwalkan_backup", "jadwalkan_cleanup",
                "jadwalkan_laporan_analytics", "start_scheduler", "stop_scheduler",
                "add_scheduled_task", "remove_scheduled_task", "get_scheduled_tasks"
            ],
            "helpers": [
                "get_cache_stats", "cleanup_cache", "batch_operation",
                "safe_execute", "create_progress_callback", "format_file_size",
                "format_duration", "extract_mentions", "extract_hashtags",
                "compress_image", "create_thumbnail", "get_media_info"
            ],
            "bound_methods": [
                "chat_bound_methods", "message_bound_methods", "user_bound_methods",
                "inline_query_bound_methods", "join_request_bound_methods"
            ],
            "session": [
                "export_session_string", "simpan_session_ke_file", 
                "muat_session_dari_file"
            ],
            "handler": [
                "tambah_handler_pesan", "tambah_handler_callback", 
                "tambah_handler_inline", "hapus_handler"
            ],
            "file": [
                "download_media_extended", "upload_file_extended", "stop_transmission"
            ],
            "monitoring": [
                "get_statistik_lengkap", "monitor_performa"
            ],
            "scheduler": [
                "jadwalkan_pesan", "jadwalkan_tugas_berulang"
            ],
            "utility": [
                "get_info_diri", "cek_status_online", "get_statistik_chat",
                "backup_chat", "daftar_method_tersedia", "set_parse_mode",
                "get_parse_mode", "format_ukuran_file", "format_durasi",
                "validasi_chat_id", "generate_progress_callback"
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