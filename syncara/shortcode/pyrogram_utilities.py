# syncara/shortcode/pyrogram_utilities.py
"""
Shortcode untuk utilities methods Pyrogram.
"""

from syncara.console import console
import asyncio
import json
import os
from datetime import datetime, timedelta

class PyrogramUtilitiesShortcode:
    def __init__(self):
        self.handlers = {
            'PYROGRAM:RESTART_BOT': self.restart_bot,
            'PYROGRAM:EXPORT_SESSION': self.export_session,
            'PYROGRAM:SIMPAN_SESSION': self.simpan_session,
            'PYROGRAM:STATISTIK_LENGKAP': self.statistik_lengkap,
            'PYROGRAM:MONITOR_PERFORMA': self.monitor_performa,
            'PYROGRAM:DOWNLOAD_MEDIA': self.download_media,
            'PYROGRAM:UPLOAD_FILE': self.upload_file,
            'PYROGRAM:SET_PARSE_MODE': self.set_parse_mode,
            'PYROGRAM:GET_PARSE_MODE': self.get_parse_mode,
            'PYROGRAM:BACKUP_LENGKAP': self.backup_lengkap,
            'PYROGRAM:JADWAL_PESAN': self.jadwal_pesan,
            'PYROGRAM:FORMAT_UKURAN': self.format_ukuran,
            'PYROGRAM:FORMAT_DURASI': self.format_durasi,
            'PYROGRAM:VALIDASI_CHAT_ID': self.validasi_chat_id,
            'PYROGRAM:STOP_TRANSMISSION': self.stop_transmission,
            'PYROGRAM:DAFTAR_METHOD': self.daftar_method,
            'PYROGRAM:BANTUAN_METHOD': self.bantuan_method,
        }
        
        self.descriptions = {
            'PYROGRAM:RESTART_BOT': 'Restart bot/userbot. Usage: [PYROGRAM:RESTART_BOT:]',
            'PYROGRAM:EXPORT_SESSION': 'Export session string. Usage: [PYROGRAM:EXPORT_SESSION:]',
            'PYROGRAM:SIMPAN_SESSION': 'Simpan session ke file. Usage: [PYROGRAM:SIMPAN_SESSION:filename]',
            'PYROGRAM:STATISTIK_LENGKAP': 'Lihat statistik lengkap bot. Usage: [PYROGRAM:STATISTIK_LENGKAP:]',
            'PYROGRAM:MONITOR_PERFORMA': 'Monitor performa bot. Usage: [PYROGRAM:MONITOR_PERFORMA:duration]',
            'PYROGRAM:DOWNLOAD_MEDIA': 'Download media dari pesan reply. Usage: [PYROGRAM:DOWNLOAD_MEDIA:filename]',
            'PYROGRAM:UPLOAD_FILE': 'Upload file ke Telegram. Usage: [PYROGRAM:UPLOAD_FILE:file_path]',
            'PYROGRAM:SET_PARSE_MODE': 'Set parse mode. Usage: [PYROGRAM:SET_PARSE_MODE:html/markdown/none]',
            'PYROGRAM:GET_PARSE_MODE': 'Lihat parse mode saat ini. Usage: [PYROGRAM:GET_PARSE_MODE:]',
            'PYROGRAM:BACKUP_LENGKAP': 'Backup lengkap chat. Usage: [PYROGRAM:BACKUP_LENGKAP:include_media]',
            'PYROGRAM:JADWAL_PESAN': 'Jadwalkan pengiriman pesan. Usage: [PYROGRAM:JADWAL_PESAN:delay_minutes:text]',
            'PYROGRAM:FORMAT_UKURAN': 'Format ukuran file ke human-readable. Usage: [PYROGRAM:FORMAT_UKURAN:bytes]',
            'PYROGRAM:FORMAT_DURASI': 'Format durasi ke human-readable. Usage: [PYROGRAM:FORMAT_DURASI:seconds]',
            'PYROGRAM:VALIDASI_CHAT_ID': 'Validasi format chat ID. Usage: [PYROGRAM:VALIDASI_CHAT_ID:chat_id]',
            'PYROGRAM:STOP_TRANSMISSION': 'Hentikan transmisi file. Usage: [PYROGRAM:STOP_TRANSMISSION:]',
            'PYROGRAM:DAFTAR_METHOD': 'Lihat daftar method yang tersedia. Usage: [PYROGRAM:DAFTAR_METHOD:kategori]',
            'PYROGRAM:BANTUAN_METHOD': 'Lihat bantuan untuk method tertentu. Usage: [PYROGRAM:BANTUAN_METHOD:method_name]',
        }
        
        self.pending_responses = {}
    
    async def restart_bot(self, client, message, params):
        """Restart bot/userbot"""
        try:
            await client.kirim_pesan(
                chat_id=message.chat.id,
                text="🔄 Restarting bot...",
                reply_to_message_id=message.id
            )
            
            result = await client.restart_bot()
            
            response_id = f"restart_bot_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Bot berhasil di-restart!" if result else "❌ Gagal restart bot",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:RESTART_BOT] Restarted bot")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:RESTART_BOT] Error: {e}")
            response_id = f"restart_bot_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error restart bot: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def export_session(self, client, message, params):
        """Export session string"""
        try:
            session_string = await client.export_session_string()
            
            # Jangan tampilkan session string lengkap untuk keamanan
            masked_session = session_string[:20] + "..." + session_string[-20:]
            
            response_id = f"export_session_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"🔑 **Session String Exported**\n📝 Preview: `{masked_session}`\n\n⚠️ **PERINGATAN**: Session string telah dikirim ke log bot. Jangan bagikan ke orang lain!",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:EXPORT_SESSION] Exported session string")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:EXPORT_SESSION] Error: {e}")
            response_id = f"export_session_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error export session: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def simpan_session(self, client, message, params):
        """Simpan session ke file"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:SIMPAN_SESSION:filename]"
            
            filename = params.strip()
            if not filename.endswith('.session'):
                filename += '.session'
            
            result = await client.simpan_session_ke_file(filename)
            
            response_id = f"simpan_session_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"💾 Session berhasil disimpan ke `{filename}`!" if result else "❌ Gagal menyimpan session",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:SIMPAN_SESSION] Saved session to {filename}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:SIMPAN_SESSION] Error: {e}")
            response_id = f"simpan_session_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error simpan session: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def statistik_lengkap(self, client, message, params):
        """Lihat statistik lengkap bot"""
        try:
            stats = await client.get_statistik_lengkap()
            
            bot_info = stats.get('bot_info', {})
            runtime = stats.get('runtime', {})
            handlers = stats.get('handlers', {})
            session = stats.get('session', {})
            
            text = "📊 **Statistik Lengkap Bot**\n\n"
            
            text += "🤖 **Info Bot:**\n"
            text += f"🆔 ID: `{bot_info.get('id', 'N/A')}`\n"
            text += f"👤 Username: @{bot_info.get('username', 'N/A')}\n"
            text += f"📛 Nama: {bot_info.get('first_name', 'N/A')}\n"
            text += f"🤖 Is Bot: {'Ya' if bot_info.get('is_bot') else 'Tidak'}\n"
            text += f"✅ Verified: {'Ya' if bot_info.get('is_verified') else 'Tidak'}\n"
            text += f"💎 Premium: {'Ya' if bot_info.get('is_premium') else 'Tidak'}\n"
            text += f"🌐 DC ID: {bot_info.get('dc_id', 'N/A')}\n\n"
            
            uptime_seconds = runtime.get('uptime_seconds', 0)
            uptime_formatted = client.format_durasi(int(uptime_seconds))
            text += f"⏱️ **Runtime:**\n"
            text += f"🕐 Uptime: {uptime_formatted}\n\n"
            
            text += f"🔧 **Handlers:**\n"
            text += f"📝 Total: {handlers.get('total_handlers', 0)}\n\n"
            
            text += f"🔑 **Session:**\n"
            text += f"📱 Loaded: {'Ya' if session.get('session_loaded') else 'Tidak'}\n"
            text += f"📝 Parse Mode: {session.get('parse_mode', 'None')}\n"
            
            response_id = f"statistik_lengkap_{message.id}"
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:STATISTIK_LENGKAP] Retrieved complete statistics")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:STATISTIK_LENGKAP] Error: {e}")
            response_id = f"statistik_lengkap_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error mendapatkan statistik: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def monitor_performa(self, client, message, params):
        """Monitor performa bot"""
        try:
            duration = int(params.strip()) if params.strip() and params.strip().isdigit() else 60
            
            if duration > 300:  # Max 5 minutes
                return "❌ Durasi maksimal 300 detik (5 menit)"
            
            await client.kirim_pesan(
                chat_id=message.chat.id,
                text=f"📊 Memulai monitoring performa selama {duration} detik...",
                reply_to_message_id=message.id
            )
            
            performa = await client.monitor_performa(duration=duration)
            
            text = f"📊 **Hasil Monitoring Performa**\n\n"
            text += f"⏱️ Durasi: {performa.get('duration', 0)} detik\n"
            text += f"📨 Pesan: {performa.get('message_count', 0)}\n"
            text += f"❌ Error: {performa.get('error_count', 0)}\n"
            text += f"📈 Rate: {performa.get('messages_per_second', 0):.2f} msg/s\n"
            text += f"📉 Error Rate: {performa.get('error_rate', 0):.2f}%\n"
            
            response_id = f"monitor_performa_{message.id}"
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:MONITOR_PERFORMA] Monitoring completed")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:MONITOR_PERFORMA] Error: {e}")
            response_id = f"monitor_performa_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error monitor performa: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def download_media(self, client, message, params):
        """Download media dari pesan reply"""
        try:
            if not message.reply_to_message:
                return "❌ Reply ke pesan yang berisi media"
            
            filename = params.strip() if params.strip() else None
            
            if not message.reply_to_message.media:
                return "❌ Pesan reply tidak mengandung media"
            
            # Send progress message
            progress_msg = await client.kirim_pesan(
                chat_id=message.chat.id,
                text="📥 Memulai download...",
                reply_to_message_id=message.id
            )
            
            # Create progress callback
            def progress_callback(current, total):
                percentage = (current / total) * 100
                # Update progress every 10%
                if percentage % 10 < 1:
                    asyncio.create_task(client.edit_pesan(
                        chat_id=message.chat.id,
                        message_id=progress_msg.id,
                        text=f"📥 Download: {percentage:.1f}% ({client.format_ukuran_file(current)}/{client.format_ukuran_file(total)})"
                    ))
            
            file_path = await client.download_media_extended(
                message=message.reply_to_message,
                file_name=filename,
                progress=progress_callback
            )
            
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            await client.edit_pesan(
                chat_id=message.chat.id,
                message_id=progress_msg.id,
                text=f"✅ **Download Selesai**\n📁 File: `{os.path.basename(file_path)}`\n📊 Ukuran: {client.format_ukuran_file(file_size)}"
            )
            
            console.info(f"[PYROGRAM:DOWNLOAD_MEDIA] Downloaded media: {file_path}")
            return ""  # Empty return since we already sent the response
            
        except Exception as e:
            console.error(f"[PYROGRAM:DOWNLOAD_MEDIA] Error: {e}")
            response_id = f"download_media_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error download media: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def upload_file(self, client, message, params):
        """Upload file ke Telegram"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:UPLOAD_FILE:file_path]"
            
            file_path = params.strip()
            
            if not os.path.exists(file_path):
                return f"❌ File tidak ditemukan: {file_path}"
            
            file_size = os.path.getsize(file_path)
            
            # Send progress message
            progress_msg = await client.kirim_pesan(
                chat_id=message.chat.id,
                text=f"📤 Memulai upload `{os.path.basename(file_path)}` ({client.format_ukuran_file(file_size)})...",
                reply_to_message_id=message.id
            )
            
            # Create progress callback
            def progress_callback(current, total):
                percentage = (current / total) * 100
                # Update progress every 10%
                if percentage % 10 < 1:
                    asyncio.create_task(client.edit_pesan(
                        chat_id=message.chat.id,
                        message_id=progress_msg.id,
                        text=f"📤 Upload: {percentage:.1f}% ({client.format_ukuran_file(current)}/{client.format_ukuran_file(total)})"
                    ))
            
            file_id = await client.upload_file_extended(
                file_path=file_path,
                progress=progress_callback
            )
            
            await client.edit_pesan(
                chat_id=message.chat.id,
                message_id=progress_msg.id,
                text=f"✅ **Upload Selesai**\n📁 File: `{os.path.basename(file_path)}`\n🆔 File ID: `{file_id}`"
            )
            
            console.info(f"[PYROGRAM:UPLOAD_FILE] Uploaded file: {file_path}")
            return ""  # Empty return since we already sent the response
            
        except Exception as e:
            console.error(f"[PYROGRAM:UPLOAD_FILE] Error: {e}")
            response_id = f"upload_file_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error upload file: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def set_parse_mode(self, client, message, params):
        """Set parse mode"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:SET_PARSE_MODE:html/markdown/none]"
            
            mode = params.strip().lower()
            
            if mode == 'none':
                parse_mode = None
            elif mode in ['html', 'markdown']:
                parse_mode = mode.upper()
            else:
                return "❌ Mode harus: html, markdown, atau none"
            
            result = client.set_parse_mode(parse_mode)
            
            response_id = f"set_parse_mode_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Parse mode diatur ke: {mode}" if result else "❌ Gagal mengatur parse mode",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:SET_PARSE_MODE] Parse mode set to: {mode}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:SET_PARSE_MODE] Error: {e}")
            response_id = f"set_parse_mode_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error set parse mode: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def get_parse_mode(self, client, message, params):
        """Lihat parse mode saat ini"""
        try:
            parse_mode = client.get_parse_mode()
            mode_str = str(parse_mode).split('.')[-1] if parse_mode else "None"
            
            response_id = f"get_parse_mode_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"📝 Parse mode saat ini: **{mode_str}**",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:GET_PARSE_MODE] Current parse mode: {mode_str}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:GET_PARSE_MODE] Error: {e}")
            response_id = f"get_parse_mode_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error get parse mode: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def backup_lengkap(self, client, message, params):
        """Backup lengkap chat"""
        try:
            include_media = params.strip().lower() in ['true', '1', 'ya', 'yes'] if params.strip() else False
            
            # Send progress message
            progress_msg = await client.kirim_pesan(
                chat_id=message.chat.id,
                text="💾 Memulai backup lengkap chat...",
                reply_to_message_id=message.id
            )
            
            backup_file = await client.backup_lengkap_chat(
                chat_id=message.chat.id,
                include_media=include_media
            )
            
            file_size = os.path.getsize(backup_file) if os.path.exists(backup_file) else 0
            
            await client.edit_pesan(
                chat_id=message.chat.id,
                message_id=progress_msg.id,
                text=f"✅ **Backup Selesai**\n📁 File: `{os.path.basename(backup_file)}`\n📊 Ukuran: {client.format_ukuran_file(file_size)}\n📱 Include Media: {'Ya' if include_media else 'Tidak'}"
            )
            
            console.info(f"[PYROGRAM:BACKUP_LENGKAP] Backup completed: {backup_file}")
            return ""  # Empty return since we already sent the response
            
        except Exception as e:
            console.error(f"[PYROGRAM:BACKUP_LENGKAP] Error: {e}")
            response_id = f"backup_lengkap_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error backup lengkap: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def jadwal_pesan(self, client, message, params):
        """Jadwalkan pengiriman pesan"""
        try:
            parts = params.split(':')
            if len(parts) < 2:
                return "❌ Usage: [PYROGRAM:JADWAL_PESAN:delay_minutes:text]"
            
            delay_minutes = int(parts[0])
            text = parts[1]
            
            if delay_minutes <= 0:
                return "❌ Delay harus lebih dari 0 menit"
            
            send_at = datetime.now() + timedelta(minutes=delay_minutes)
            
            result = await client.jadwalkan_pesan(
                chat_id=message.chat.id,
                text=text,
                send_at=send_at
            )
            
            response_id = f"jadwal_pesan_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"⏰ Pesan dijadwalkan untuk dikirim dalam {delay_minutes} menit\n📅 Waktu: {send_at.strftime('%d/%m/%Y %H:%M')}" if result else "❌ Gagal menjadwalkan pesan",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:JADWAL_PESAN] Scheduled message for {send_at}")
            return response_id
            
        except ValueError:
            response_id = f"jadwal_pesan_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Delay harus berupa angka (menit)",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:JADWAL_PESAN] Error: {e}")
            response_id = f"jadwal_pesan_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error jadwal pesan: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def format_ukuran(self, client, message, params):
        """Format ukuran file ke human-readable"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:FORMAT_UKURAN:bytes]"
            
            size_bytes = int(params.strip())
            formatted = client.format_ukuran_file(size_bytes)
            
            response_id = f"format_ukuran_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"📊 **Format Ukuran**\n📏 {size_bytes:,} bytes = **{formatted}**",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:FORMAT_UKURAN] Formatted size: {size_bytes} -> {formatted}")
            return response_id
            
        except ValueError:
            response_id = f"format_ukuran_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Size harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:FORMAT_UKURAN] Error: {e}")
            response_id = f"format_ukuran_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error format ukuran: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def format_durasi(self, client, message, params):
        """Format durasi ke human-readable"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:FORMAT_DURASI:seconds]"
            
            seconds = int(params.strip())
            formatted = client.format_durasi(seconds)
            
            response_id = f"format_durasi_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"⏱️ **Format Durasi**\n🕐 {seconds:,} detik = **{formatted}**",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:FORMAT_DURASI] Formatted duration: {seconds} -> {formatted}")
            return response_id
            
        except ValueError:
            response_id = f"format_durasi_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Seconds harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:FORMAT_DURASI] Error: {e}")
            response_id = f"format_durasi_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error format durasi: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def validasi_chat_id(self, client, message, params):
        """Validasi format chat ID"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:VALIDASI_CHAT_ID:chat_id]"
            
            chat_id = params.strip()
            
            # Try to convert to int if it's numeric
            if chat_id.lstrip('-').isdigit():
                chat_id = int(chat_id)
            
            is_valid = client.validasi_chat_id(chat_id)
            
            response_id = f"validasi_chat_id_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"🔍 **Validasi Chat ID**\n📝 Input: `{params.strip()}`\n✅ Valid: {'Ya' if is_valid else 'Tidak'}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:VALIDASI_CHAT_ID] Validated chat ID: {params.strip()} -> {is_valid}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:VALIDASI_CHAT_ID] Error: {e}")
            response_id = f"validasi_chat_id_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error validasi chat ID: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def stop_transmission(self, client, message, params):
        """Hentikan transmisi file yang sedang berlangsung"""
        try:
            result = client.stop_transmission()
            
            response_id = f"stop_transmission_{message.id}"
            self.pending_responses[response_id] = {
                'text': "⏹️ Transmisi file dihentikan!" if result else "❌ Gagal menghentikan transmisi",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:STOP_TRANSMISSION] Stopped transmission")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:STOP_TRANSMISSION] Error: {e}")
            response_id = f"stop_transmission_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error stop transmission: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def daftar_method(self, client, message, params):
        """Lihat daftar method yang tersedia"""
        try:
            kategori = params.strip() if params.strip() else None
            
            methods = client.daftar_method_tersedia()
            
            if kategori:
                if kategori in methods:
                    method_list = methods[kategori]
                    text = f"📋 **Method {kategori.title()}** ({len(method_list)} method)\n\n"
                    for i, method in enumerate(method_list, 1):
                        text += f"{i}. `{method}`\n"
                else:
                    available_categories = ", ".join(methods.keys())
                    text = f"❌ Kategori tidak ditemukan.\n📚 Kategori tersedia: {available_categories}"
            else:
                text = "📋 **Daftar Kategori Method**\n\n"
                for category, method_list in methods.items():
                    text += f"📁 **{category.title()}**: {len(method_list)} method\n"
                
                text += "\n💡 Gunakan `[PYROGRAM:DAFTAR_METHOD:kategori]` untuk melihat detail"
            
            response_id = f"daftar_method_{message.id}"
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:DAFTAR_METHOD] Listed methods for category: {kategori or 'all'}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:DAFTAR_METHOD] Error: {e}")
            response_id = f"daftar_method_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error daftar method: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def bantuan_method(self, client, message, params):
        """Lihat bantuan untuk method tertentu"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:BANTUAN_METHOD:method_name]"
            
            method_name = params.strip()
            
            help_text = client.bantuan_method(method_name)
            
            if "tidak ditemukan" in help_text.lower():
                text = f"❌ {help_text}\n\n💡 Gunakan `[PYROGRAM:DAFTAR_METHOD]` untuk melihat method yang tersedia"
            else:
                text = f"📖 **Bantuan: {method_name}**\n\n{help_text}"
            
            response_id = f"bantuan_method_{message.id}"
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BANTUAN_METHOD] Provided help for: {method_name}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BANTUAN_METHOD] Error: {e}")
            response_id = f"bantuan_method_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error bantuan method: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def send_pending_responses(self, client, response_ids):
        """Send pending responses"""
        for response_id in response_ids:
            if response_id in self.pending_responses:
                try:
                    response_data = self.pending_responses[response_id]
                    await client.send_message(
                        chat_id=response_data['chat_id'],
                        text=response_data['text'],
                        reply_to_message_id=response_data.get('reply_to_message_id')
                    )
                    del self.pending_responses[response_id]
                except Exception as e:
                    console.error(f"Error sending pending response {response_id}: {e}")
        
        return True 