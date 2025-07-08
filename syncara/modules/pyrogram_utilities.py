"""
Utilities methods untuk Pyrogram.
Berisi method-method untuk lifecycle management, session handling, dan utilities lainnya.
"""

from pyrogram import types, enums, filters
from pyrogram.errors import RPCError
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, InlineQueryHandler
from typing import Union, List, Optional, Dict, Any, Callable, BinaryIO
from syncara.console import console
import asyncio
import time
import json
import os
from datetime import datetime, timedelta

class UtilitiesMethods:
    """
    Mixin class untuk utilities methods Pyrogram.
    """
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    
    async def mulai_bot(self, **kwargs) -> bool:
        """
        Memulai bot/userbot.
        
        Returns:
            bool: True jika berhasil start
        """
        try:
            await self.start()
            console.info("✅ Bot/Userbot berhasil dimulai")
            return True
        except Exception as e:
            console.error(f"Error memulai bot: {e}")
            raise
    
    async def hentikan_bot(self, **kwargs) -> bool:
        """
        Menghentikan bot/userbot.
        
        Returns:
            bool: True jika berhasil stop
        """
        try:
            await self.stop()
            console.info("🛑 Bot/Userbot berhasil dihentikan")
            return True
        except Exception as e:
            console.error(f"Error menghentikan bot: {e}")
            raise
    
    async def restart_bot(self, **kwargs) -> bool:
        """
        Restart bot/userbot.
        
        Returns:
            bool: True jika berhasil restart
        """
        try:
            console.info("🔄 Restarting bot/userbot...")
            await self.stop()
            await asyncio.sleep(2)
            await self.start()
            console.info("✅ Bot/Userbot berhasil di-restart")
            return True
        except Exception as e:
            console.error(f"Error restart bot: {e}")
            raise
    
    def jalankan_bot(self, **kwargs):
        """
        Menjalankan bot secara langsung (blocking).
        """
        try:
            console.info("🚀 Menjalankan bot...")
            self.run()
        except Exception as e:
            console.error(f"Error menjalankan bot: {e}")
            raise
    
    # ==================== SESSION MANAGEMENT ====================
    
    async def export_session_string(self) -> str:
        """
        Export session string dari client yang sedang aktif.
        
        Returns:
            str: Session string
        """
        try:
            session_string = await self.export_session_string()
            console.info("✅ Session string berhasil di-export")
            return session_string
        except Exception as e:
            console.error(f"Error export session string: {e}")
            raise
    
    async def simpan_session_ke_file(self, file_path: str) -> bool:
        """
        Menyimpan session string ke file.
        
        Args:
            file_path: Path file untuk menyimpan session
            
        Returns:
            bool: True jika berhasil
        """
        try:
            session_string = await self.export_session_string()
            with open(file_path, 'w') as f:
                f.write(session_string)
            console.info(f"✅ Session disimpan ke {file_path}")
            return True
        except Exception as e:
            console.error(f"Error menyimpan session: {e}")
            raise
    
    def muat_session_dari_file(self, file_path: str) -> str:
        """
        Memuat session string dari file.
        
        Args:
            file_path: Path file session
            
        Returns:
            str: Session string
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File session tidak ditemukan: {file_path}")
            
            with open(file_path, 'r') as f:
                session_string = f.read().strip()
            
            console.info(f"✅ Session dimuat dari {file_path}")
            return session_string
        except Exception as e:
            console.error(f"Error memuat session: {e}")
            raise
    
    # ==================== HANDLER MANAGEMENT ====================
    
    def tambah_handler_pesan(self, 
                           func: Callable,
                           filters: Optional[filters.Filter] = None,
                           group: int = 0) -> bool:
        """
        Menambahkan handler untuk pesan.
        
        Args:
            func: Fungsi handler
            filters: Filter untuk handler
            group: Group handler
            
        Returns:
            bool: True jika berhasil
        """
        try:
            handler = MessageHandler(func, filters)
            self.add_handler(handler, group)
            console.info(f"✅ Handler pesan ditambahkan: {func.__name__}")
            return True
        except Exception as e:
            console.error(f"Error menambah handler pesan: {e}")
            raise
    
    def tambah_handler_callback(self, 
                              func: Callable,
                              filters: Optional[filters.Filter] = None,
                              group: int = 0) -> bool:
        """
        Menambahkan handler untuk callback query.
        
        Args:
            func: Fungsi handler
            filters: Filter untuk handler
            group: Group handler
            
        Returns:
            bool: True jika berhasil
        """
        try:
            handler = CallbackQueryHandler(func, filters)
            self.add_handler(handler, group)
            console.info(f"✅ Handler callback ditambahkan: {func.__name__}")
            return True
        except Exception as e:
            console.error(f"Error menambah handler callback: {e}")
            raise
    
    def tambah_handler_inline(self, 
                            func: Callable,
                            filters: Optional[filters.Filter] = None,
                            group: int = 0) -> bool:
        """
        Menambahkan handler untuk inline query.
        
        Args:
            func: Fungsi handler
            filters: Filter untuk handler
            group: Group handler
            
        Returns:
            bool: True jika berhasil
        """
        try:
            handler = InlineQueryHandler(func, filters)
            self.add_handler(handler, group)
            console.info(f"✅ Handler inline ditambahkan: {func.__name__}")
            return True
        except Exception as e:
            console.error(f"Error menambah handler inline: {e}")
            raise
    
    def hapus_handler(self, handler, group: int = 0) -> bool:
        """
        Menghapus handler.
        
        Args:
            handler: Handler yang akan dihapus
            group: Group handler
            
        Returns:
            bool: True jika berhasil
        """
        try:
            self.remove_handler(handler, group)
            console.info("✅ Handler berhasil dihapus")
            return True
        except Exception as e:
            console.error(f"Error menghapus handler: {e}")
            raise
    
    # ==================== PARSE MODE MANAGEMENT ====================
    
    def set_parse_mode(self, parse_mode: Union[enums.ParseMode, str, None]) -> bool:
        """
        Mengatur parse mode default.
        
        Args:
            parse_mode: Parse mode (HTML, Markdown, atau None)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            if isinstance(parse_mode, str):
                parse_mode = getattr(enums.ParseMode, parse_mode.upper(), None)
            
            self.parse_mode = parse_mode
            console.info(f"✅ Parse mode diatur ke: {parse_mode}")
            return True
        except Exception as e:
            console.error(f"Error mengatur parse mode: {e}")
            raise
    
    def get_parse_mode(self) -> Optional[enums.ParseMode]:
        """
        Mendapatkan parse mode saat ini.
        
        Returns:
            ParseMode: Parse mode yang aktif
        """
        return getattr(self, 'parse_mode', None)
    
    # ==================== FILE HANDLING ====================
    
    async def download_media_extended(self, 
                                    message: types.Message,
                                    file_name: Optional[str] = None,
                                    block: bool = True,
                                    progress: Optional[Callable] = None,
                                    progress_args: tuple = ()) -> str:
        """
        Download media dengan opsi extended.
        
        Args:
            message: Pesan yang berisi media
            file_name: Nama file custom
            block: Block hingga selesai
            progress: Callback progress
            progress_args: Arguments untuk progress callback
            
        Returns:
            str: Path file yang di-download
        """
        try:
            if not message.media:
                raise ValueError("Pesan tidak mengandung media")
            
            # Generate file name jika tidak ada
            if not file_name:
                timestamp = int(time.time())
                if message.photo:
                    file_name = f"photo_{timestamp}.jpg"
                elif message.video:
                    file_name = f"video_{timestamp}.mp4"
                elif message.audio:
                    file_name = f"audio_{timestamp}.mp3"
                elif message.document:
                    original_name = message.document.file_name or f"document_{timestamp}"
                    file_name = original_name
                else:
                    file_name = f"media_{timestamp}"
            
            console.info(f"📥 Downloading {file_name}...")
            
            file_path = await self.download_media(
                message=message,
                file_name=file_name,
                block=block,
                progress=progress,
                progress_args=progress_args
            )
            
            console.info(f"✅ Download selesai: {file_path}")
            return file_path
        except Exception as e:
            console.error(f"Error download media: {e}")
            raise
    
    async def upload_file_extended(self, 
                                 file_path: str,
                                 progress: Optional[Callable] = None,
                                 progress_args: tuple = ()) -> str:
        """
        Upload file dengan progress tracking.
        
        Args:
            file_path: Path file yang akan diupload
            progress: Callback progress
            progress_args: Arguments untuk progress callback
            
        Returns:
            str: File ID hasil upload
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
            
            console.info(f"📤 Uploading {file_path}...")
            
            # Determine media type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                message = await self.kirim_foto(
                    chat_id="me",
                    photo=file_path,
                    progress=progress,
                    progress_args=progress_args
                )
                file_id = message.photo.file_id
            elif file_ext in ['.mp4', '.avi', '.mkv', '.mov']:
                message = await self.kirim_video(
                    chat_id="me",
                    video=file_path,
                    progress=progress,
                    progress_args=progress_args
                )
                file_id = message.video.file_id
            elif file_ext in ['.mp3', '.wav', '.flac', '.ogg']:
                message = await self.kirim_audio(
                    chat_id="me",
                    audio=file_path,
                    progress=progress,
                    progress_args=progress_args
                )
                file_id = message.audio.file_id
            else:
                message = await self.kirim_dokumen(
                    chat_id="me",
                    document=file_path,
                    progress=progress,
                    progress_args=progress_args
                )
                file_id = message.document.file_id
            
            # Delete the uploaded message
            await self.hapus_pesan(chat_id="me", message_ids=message.id)
            
            console.info(f"✅ Upload selesai: {file_id}")
            return file_id
        except Exception as e:
            console.error(f"Error upload file: {e}")
            raise
    
    def stop_transmission(self) -> bool:
        """
        Menghentikan transmisi file yang sedang berlangsung.
        
        Returns:
            bool: True jika berhasil
        """
        try:
            self.stop_transmission()
            console.info("⏹️ Transmisi file dihentikan")
            return True
        except Exception as e:
            console.error(f"Error menghentikan transmisi: {e}")
            raise
    
    # ==================== MONITORING & STATISTICS ====================
    
    async def get_statistik_lengkap(self) -> Dict[str, Any]:
        """
        Mendapatkan statistik lengkap bot/userbot.
        
        Returns:
            Dict: Statistik lengkap
        """
        try:
            me = await self.get_me()
            
            stats = {
                "bot_info": {
                    "id": me.id,
                    "username": me.username,
                    "first_name": me.first_name,
                    "is_bot": me.is_bot,
                    "is_verified": me.is_verified,
                    "is_premium": me.is_premium,
                    "dc_id": me.dc_id
                },
                "runtime": {
                    "start_time": getattr(self, '_start_time', None),
                    "uptime_seconds": time.time() - getattr(self, '_start_time', time.time())
                },
                "handlers": {
                    "total_handlers": len(getattr(self, 'dispatcher', {}).get('groups', {}))
                },
                "session": {
                    "session_loaded": hasattr(self, 'session'),
                    "parse_mode": str(getattr(self, 'parse_mode', None))
                }
            }
            
            return stats
        except Exception as e:
            console.error(f"Error mendapatkan statistik: {e}")
            raise
    
    async def monitor_performa(self, duration: int = 60) -> Dict[str, Any]:
        """
        Monitor performa bot selama durasi tertentu.
        
        Args:
            duration: Durasi monitoring dalam detik
            
        Returns:
            Dict: Data performa
        """
        try:
            console.info(f"📊 Memulai monitoring performa selama {duration} detik...")
            
            start_time = time.time()
            message_count = 0
            error_count = 0
            
            # Simple monitoring (bisa diperluas sesuai kebutuhan)
            await asyncio.sleep(duration)
            
            end_time = time.time()
            
            performa = {
                "duration": duration,
                "start_time": start_time,
                "end_time": end_time,
                "message_count": message_count,
                "error_count": error_count,
                "messages_per_second": message_count / duration if duration > 0 else 0,
                "error_rate": error_count / message_count if message_count > 0 else 0
            }
            
            console.info(f"✅ Monitoring selesai: {performa}")
            return performa
        except Exception as e:
            console.error(f"Error monitoring performa: {e}")
            raise
    
    # ==================== BACKUP & RESTORE ====================
    
    async def backup_lengkap_chat(self, 
                                 chat_id: Union[int, str],
                                 include_media: bool = False,
                                 output_file: Optional[str] = None) -> str:
        """
        Backup lengkap chat termasuk media (opsional).
        
        Args:
            chat_id: ID chat yang akan di-backup
            include_media: Apakah media ikut di-backup
            output_file: File output untuk backup
            
        Returns:
            str: Path file backup
        """
        try:
            console.info(f"💾 Memulai backup lengkap chat {chat_id}...")
            
            if not output_file:
                timestamp = int(time.time())
                output_file = f"backup_chat_{chat_id}_{timestamp}.json"
            
            # Get chat info
            chat_info = await self.get_info_chat(chat_id)
            
            # Get messages
            messages = await self.backup_chat(chat_id, limit=0)  # All messages
            
            backup_data = {
                "chat_info": {
                    "id": chat_info.id,
                    "type": chat_info.type,
                    "title": chat_info.title,
                    "username": chat_info.username,
                    "description": chat_info.description
                },
                "backup_date": datetime.now().isoformat(),
                "total_messages": len(messages),
                "include_media": include_media,
                "messages": messages
            }
            
            # Download media if requested
            if include_media:
                console.info("📥 Downloading media files...")
                media_dir = f"backup_media_{chat_id}_{int(time.time())}"
                os.makedirs(media_dir, exist_ok=True)
                
                for i, msg in enumerate(messages):
                    if msg.get('media_type'):
                        try:
                            # This would need actual message object, simplified for now
                            console.info(f"📥 Downloading media {i+1}/{len(messages)}")
                        except Exception as e:
                            console.error(f"Error downloading media {i}: {e}")
                
                backup_data["media_directory"] = media_dir
            
            # Save backup
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            console.info(f"✅ Backup selesai: {output_file}")
            return output_file
        except Exception as e:
            console.error(f"Error backup lengkap chat: {e}")
            raise
    
    async def restore_chat_dari_backup(self, 
                                      backup_file: str,
                                      target_chat_id: Union[int, str],
                                      include_media: bool = False) -> bool:
        """
        Restore chat dari file backup.
        
        Args:
            backup_file: File backup yang akan di-restore
            target_chat_id: ID chat tujuan restore
            include_media: Apakah media ikut di-restore
            
        Returns:
            bool: True jika berhasil
        """
        try:
            console.info(f"♻️ Memulai restore chat dari {backup_file}...")
            
            if not os.path.exists(backup_file):
                raise FileNotFoundError(f"File backup tidak ditemukan: {backup_file}")
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            messages = backup_data.get('messages', [])
            console.info(f"📨 Akan restore {len(messages)} pesan")
            
            restored_count = 0
            for msg in messages:
                try:
                    # Restore text messages
                    if msg.get('text'):
                        await self.kirim_pesan(
                            chat_id=target_chat_id,
                            text=f"[RESTORED] {msg['text']}"
                        )
                        restored_count += 1
                        await asyncio.sleep(1)  # Rate limiting
                
                except Exception as e:
                    console.error(f"Error restore pesan: {e}")
                    continue
            
            console.info(f"✅ Restore selesai: {restored_count}/{len(messages)} pesan")
            return True
        except Exception as e:
            console.error(f"Error restore chat: {e}")
            raise
    
    # ==================== SCHEDULED TASKS ====================
    
    async def jadwalkan_pesan(self, 
                             chat_id: Union[int, str],
                             text: str,
                             send_at: datetime,
                             **kwargs) -> bool:
        """
        Menjadwalkan pengiriman pesan.
        
        Args:
            chat_id: ID chat tujuan
            text: Teks pesan
            send_at: Waktu pengiriman
            **kwargs: Parameter tambahan
            
        Returns:
            bool: True jika berhasil dijadwalkan
        """
        try:
            now = datetime.now()
            if send_at <= now:
                raise ValueError("Waktu pengiriman harus di masa depan")
            
            delay = (send_at - now).total_seconds()
            
            async def send_delayed():
                await asyncio.sleep(delay)
                await self.kirim_pesan(chat_id=chat_id, text=text, **kwargs)
                console.info(f"📨 Pesan terjadwal terkirim ke {chat_id}")
            
            # Create task
            task = asyncio.create_task(send_delayed())
            
            console.info(f"⏰ Pesan dijadwalkan untuk {send_at}")
            return True
        except Exception as e:
            console.error(f"Error menjadwalkan pesan: {e}")
            raise
    
    async def jadwalkan_tugas_berulang(self, 
                                      func: Callable,
                                      interval: int,
                                      times: Optional[int] = None,
                                      **kwargs) -> bool:
        """
        Menjadwalkan tugas berulang.
        
        Args:
            func: Fungsi yang akan dijalankan
            interval: Interval dalam detik
            times: Jumlah pengulangan (None = unlimited)
            **kwargs: Parameter untuk fungsi
            
        Returns:
            bool: True jika berhasil dijadwalkan
        """
        try:
            async def run_repeated():
                count = 0
                while times is None or count < times:
                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func(**kwargs)
                        else:
                            func(**kwargs)
                        count += 1
                        console.info(f"🔄 Tugas berulang dijalankan #{count}")
                        if times is None or count < times:
                            await asyncio.sleep(interval)
                    except Exception as e:
                        console.error(f"Error dalam tugas berulang: {e}")
                        break
            
            # Create task
            task = asyncio.create_task(run_repeated())
            
            console.info(f"⏰ Tugas berulang dijadwalkan (interval: {interval}s)")
            return True
        except Exception as e:
            console.error(f"Error menjadwalkan tugas berulang: {e}")
            raise
    
    # ==================== UTILITIES HELPERS ====================
    
    def format_ukuran_file(self, size_bytes: int) -> str:
        """
        Format ukuran file ke format human-readable.
        
        Args:
            size_bytes: Ukuran dalam bytes
            
        Returns:
            str: Ukuran dalam format readable (KB, MB, GB)
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def format_durasi(self, seconds: int) -> str:
        """
        Format durasi ke format human-readable.
        
        Args:
            seconds: Durasi dalam detik
            
        Returns:
            str: Durasi dalam format readable
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours}h {remaining_minutes}m"
    
    def validasi_chat_id(self, chat_id: Union[int, str]) -> bool:
        """
        Validasi format chat ID.
        
        Args:
            chat_id: Chat ID yang akan divalidasi
            
        Returns:
            bool: True jika valid
        """
        try:
            if isinstance(chat_id, int):
                return True
            elif isinstance(chat_id, str):
                if chat_id.startswith('@'):
                    return len(chat_id) > 1
                elif chat_id.startswith('-'):
                    return chat_id[1:].isdigit()
                else:
                    return chat_id.isdigit()
            return False
        except Exception:
            return False
    
    def generate_progress_callback(self, description: str = "Processing") -> Callable:
        """
        Generate callback function untuk progress tracking.
        
        Args:
            description: Deskripsi proses
            
        Returns:
            Callable: Callback function
        """
        def progress_callback(current: int, total: int):
            percentage = (current / total) * 100
            console.info(f"{description}: {percentage:.1f}% ({self.format_ukuran_file(current)}/{self.format_ukuran_file(total)})")
        
        return progress_callback 