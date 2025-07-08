# syncara/shortcode/pyrogram_advanced.py
"""
Shortcode untuk method-method advanced Pyrogram.
"""

from syncara.console import console
import asyncio
import json
from datetime import datetime

class PyrogramAdvancedShortcode:
    def __init__(self):
        self.handlers = {
            'PYROGRAM:BUAT_CHANNEL': self.buat_channel,
            'PYROGRAM:BUAT_GRUP': self.buat_grup,
            'PYROGRAM:BUAT_SUPERGROUP': self.buat_supergroup,
            'PYROGRAM:HAPUS_CHANNEL': self.hapus_channel,
            'PYROGRAM:HAPUS_SUPERGROUP': self.hapus_supergroup,
            'PYROGRAM:SET_MODE_LAMBAT': self.set_mode_lambat,
            'PYROGRAM:HITUNG_MEMBER_ONLINE': self.hitung_member_online,
            'PYROGRAM:HAPUS_RIWAYAT_USER': self.hapus_riwayat_user,
            'PYROGRAM:TANDAI_BELUM_DIBACA': self.tandai_belum_dibaca,
            'PYROGRAM:LOG_EVENT_CHAT': self.log_event_chat,
            'PYROGRAM:ARSIP_CHAT': self.arsip_chat,
            'PYROGRAM:UNARSIP_CHAT': self.unarsip_chat,
            'PYROGRAM:SET_KONTEN_TERLINDUNGI': self.set_konten_terlindungi,
            'PYROGRAM:GET_PESAN_SPESIFIK': self.get_pesan_spesifik,
            'PYROGRAM:GET_GRUP_MEDIA': self.get_grup_media,
            'PYROGRAM:HITUNG_RIWAYAT': self.hitung_riwayat,
            'PYROGRAM:VOTE_POLL': self.vote_poll,
            'PYROGRAM:BULK_KIRIM': self.bulk_kirim,
            'PYROGRAM:BULK_FORWARD': self.bulk_forward,
        }
        
        self.descriptions = {
            'PYROGRAM:BUAT_CHANNEL': 'Membuat channel baru. Usage: [PYROGRAM:BUAT_CHANNEL:title:description]',
            'PYROGRAM:BUAT_GRUP': 'Membuat grup baru. Usage: [PYROGRAM:BUAT_GRUP:title:user1,user2,...]',
            'PYROGRAM:BUAT_SUPERGROUP': 'Membuat supergroup baru. Usage: [PYROGRAM:BUAT_SUPERGROUP:title:description]',
            'PYROGRAM:HAPUS_CHANNEL': 'Menghapus channel. Usage: [PYROGRAM:HAPUS_CHANNEL:chat_id]',
            'PYROGRAM:HAPUS_SUPERGROUP': 'Menghapus supergroup. Usage: [PYROGRAM:HAPUS_SUPERGROUP:chat_id]',
            'PYROGRAM:SET_MODE_LAMBAT': 'Mengatur slow mode chat. Usage: [PYROGRAM:SET_MODE_LAMBAT:seconds]',
            'PYROGRAM:HITUNG_MEMBER_ONLINE': 'Menghitung member yang sedang online. Usage: [PYROGRAM:HITUNG_MEMBER_ONLINE:]',
            'PYROGRAM:HAPUS_RIWAYAT_USER': 'Menghapus semua pesan user di supergroup. Usage: [PYROGRAM:HAPUS_RIWAYAT_USER:user_id]',
            'PYROGRAM:TANDAI_BELUM_DIBACA': 'Menandai chat sebagai belum dibaca. Usage: [PYROGRAM:TANDAI_BELUM_DIBACA:]',
            'PYROGRAM:LOG_EVENT_CHAT': 'Melihat log event chat (48 jam terakhir). Usage: [PYROGRAM:LOG_EVENT_CHAT:limit]',
            'PYROGRAM:ARSIP_CHAT': 'Mengarsipkan chat. Usage: [PYROGRAM:ARSIP_CHAT:]',
            'PYROGRAM:UNARSIP_CHAT': 'Membuka arsip chat. Usage: [PYROGRAM:UNARSIP_CHAT:]',
            'PYROGRAM:SET_KONTEN_TERLINDUNGI': 'Mengatur perlindungan konten. Usage: [PYROGRAM:SET_KONTEN_TERLINDUNGI:true/false]',
            'PYROGRAM:GET_PESAN_SPESIFIK': 'Mendapatkan pesan berdasarkan ID. Usage: [PYROGRAM:GET_PESAN_SPESIFIK:message_id]',
            'PYROGRAM:GET_GRUP_MEDIA': 'Mendapatkan album media berdasarkan message ID. Usage: [PYROGRAM:GET_GRUP_MEDIA:message_id]',
            'PYROGRAM:HITUNG_RIWAYAT': 'Menghitung total pesan dalam chat. Usage: [PYROGRAM:HITUNG_RIWAYAT:]',
            'PYROGRAM:VOTE_POLL': 'Vote pada polling. Usage: [PYROGRAM:VOTE_POLL:message_id:option_index]',
            'PYROGRAM:BULK_KIRIM': 'Kirim pesan ke multiple chat. Usage: [PYROGRAM:BULK_KIRIM:chat1,chat2,...:text:delay]',
            'PYROGRAM:BULK_FORWARD': 'Forward pesan ke multiple chat. Usage: [PYROGRAM:BULK_FORWARD:chat1,chat2,...:message_id:delay]',
        }
        
        self.pending_responses = {}
    
    async def buat_channel(self, client, message, params):
        """Membuat channel baru"""
        try:
            parts = params.split(':')
            if len(parts) < 1:
                return "❌ Usage: [PYROGRAM:BUAT_CHANNEL:title:description]"
            
            title = parts[0]
            description = parts[1] if len(parts) > 1 else None
            
            channel = await client.buat_channel(title=title, description=description)
            
            response_id = f"buat_channel_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Channel berhasil dibuat!\n📺 **{channel.title}**\n🆔 ID: `{channel.id}`\n🔗 Username: @{channel.username if channel.username else 'Belum ada'}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_CHANNEL] Created channel: {channel.title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_CHANNEL] Error: {e}")
            response_id = f"buat_channel_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat channel: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def buat_grup(self, client, message, params):
        """Membuat grup baru"""
        try:
            parts = params.split(':')
            if len(parts) < 2:
                return "❌ Usage: [PYROGRAM:BUAT_GRUP:title:user1,user2,...]"
            
            title = parts[0]
            users = [user.strip() for user in parts[1].split(',')]
            
            grup = await client.buat_grup(title=title, users=users)
            
            response_id = f"buat_grup_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Grup berhasil dibuat!\n👥 **{grup.title}**\n🆔 ID: `{grup.id}`\n👤 Member: {len(users) + 1}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_GRUP] Created group: {grup.title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_GRUP] Error: {e}")
            response_id = f"buat_grup_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat grup: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def buat_supergroup(self, client, message, params):
        """Membuat supergroup baru"""
        try:
            parts = params.split(':')
            if len(parts) < 1:
                return "❌ Usage: [PYROGRAM:BUAT_SUPERGROUP:title:description]"
            
            title = parts[0]
            description = parts[1] if len(parts) > 1 else None
            
            supergroup = await client.buat_supergroup(title=title, description=description)
            
            response_id = f"buat_supergroup_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Supergroup berhasil dibuat!\n🏢 **{supergroup.title}**\n🆔 ID: `{supergroup.id}`\n🔗 Username: @{supergroup.username if supergroup.username else 'Belum ada'}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_SUPERGROUP] Created supergroup: {supergroup.title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_SUPERGROUP] Error: {e}")
            response_id = f"buat_supergroup_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat supergroup: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def hapus_channel(self, client, message, params):
        """Menghapus channel"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:HAPUS_CHANNEL:chat_id]"
            
            chat_id = params.strip()
            result = await client.hapus_channel(chat_id=chat_id)
            
            response_id = f"hapus_channel_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Channel berhasil dihapus!" if result else "❌ Gagal menghapus channel",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:HAPUS_CHANNEL] Deleted channel: {chat_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:HAPUS_CHANNEL] Error: {e}")
            response_id = f"hapus_channel_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error menghapus channel: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def hapus_supergroup(self, client, message, params):
        """Menghapus supergroup"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:HAPUS_SUPERGROUP:chat_id]"
            
            chat_id = params.strip()
            result = await client.hapus_supergroup(chat_id=chat_id)
            
            response_id = f"hapus_supergroup_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Supergroup berhasil dihapus!" if result else "❌ Gagal menghapus supergroup",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:HAPUS_SUPERGROUP] Deleted supergroup: {chat_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:HAPUS_SUPERGROUP] Error: {e}")
            response_id = f"hapus_supergroup_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error menghapus supergroup: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def set_mode_lambat(self, client, message, params):
        """Mengatur slow mode chat"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:SET_MODE_LAMBAT:seconds] (0 untuk nonaktifkan)"
            
            seconds = int(params.strip())
            result = await client.set_mode_lambat(chat_id=message.chat.id, seconds=seconds)
            
            response_id = f"set_mode_lambat_{message.id}"
            if result:
                if seconds == 0:
                    text = "✅ Slow mode dinonaktifkan"
                else:
                    text = f"✅ Slow mode diatur ke {seconds} detik"
            else:
                text = "❌ Gagal mengatur slow mode"
            
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:SET_MODE_LAMBAT] Set slow mode to {seconds} seconds")
            return response_id
            
        except ValueError:
            response_id = f"set_mode_lambat_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Seconds harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:SET_MODE_LAMBAT] Error: {e}")
            response_id = f"set_mode_lambat_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error mengatur slow mode: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def hitung_member_online(self, client, message, params):
        """Menghitung member yang sedang online"""
        try:
            count = await client.hitung_member_online(chat_id=message.chat.id)
            
            response_id = f"hitung_member_online_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"👥 **Member Online**\n🟢 Sedang online: **{count}** orang",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:HITUNG_MEMBER_ONLINE] Online members: {count}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:HITUNG_MEMBER_ONLINE] Error: {e}")
            response_id = f"hitung_member_online_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error menghitung member online: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def hapus_riwayat_user(self, client, message, params):
        """Menghapus semua pesan user di supergroup"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:HAPUS_RIWAYAT_USER:user_id]"
            
            user_id = params.strip()
            result = await client.hapus_riwayat_user(chat_id=message.chat.id, user_id=user_id)
            
            response_id = f"hapus_riwayat_user_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Riwayat pesan user berhasil dihapus!" if result else "❌ Gagal menghapus riwayat user",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:HAPUS_RIWAYAT_USER] Deleted user history: {user_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:HAPUS_RIWAYAT_USER] Error: {e}")
            response_id = f"hapus_riwayat_user_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error menghapus riwayat user: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def tandai_belum_dibaca(self, client, message, params):
        """Menandai chat sebagai belum dibaca"""
        try:
            result = await client.tandai_chat_belum_dibaca(chat_id=message.chat.id)
            
            response_id = f"tandai_belum_dibaca_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Chat ditandai sebagai belum dibaca" if result else "❌ Gagal menandai chat",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:TANDAI_BELUM_DIBACA] Marked chat as unread")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:TANDAI_BELUM_DIBACA] Error: {e}")
            response_id = f"tandai_belum_dibaca_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error menandai chat: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def log_event_chat(self, client, message, params):
        """Melihat log event chat (48 jam terakhir)"""
        try:
            limit = int(params.strip()) if params.strip() and params.strip().isdigit() else 10
            
            events = await client.get_log_event_chat(chat_id=message.chat.id, limit=limit)
            
            if not events:
                text = "📋 Tidak ada event dalam 48 jam terakhir"
            else:
                text = f"📋 **Log Event Chat** (Limit: {limit})\n\n"
                for i, event in enumerate(events[:10], 1):  # Limit display to 10
                    date_str = event.date.strftime("%d/%m %H:%M") if hasattr(event, 'date') else "N/A"
                    action = event.action if hasattr(event, 'action') else "Unknown"
                    user = event.user.first_name if hasattr(event, 'user') and event.user else "System"
                    text += f"{i}. [{date_str}] **{user}**: {action}\n"
                
                if len(events) > 10:
                    text += f"\n... dan {len(events) - 10} event lainnya"
            
            response_id = f"log_event_chat_{message.id}"
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:LOG_EVENT_CHAT] Retrieved {len(events)} events")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:LOG_EVENT_CHAT] Error: {e}")
            response_id = f"log_event_chat_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error mendapatkan log event: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def arsip_chat(self, client, message, params):
        """Mengarsipkan chat"""
        try:
            result = await client.arsip_chat(chat_id=message.chat.id)
            
            response_id = f"arsip_chat_{message.id}"
            self.pending_responses[response_id] = {
                'text': "📁 Chat berhasil diarsipkan!" if result else "❌ Gagal mengarsipkan chat",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:ARSIP_CHAT] Archived chat")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:ARSIP_CHAT] Error: {e}")
            response_id = f"arsip_chat_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error mengarsipkan chat: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def unarsip_chat(self, client, message, params):
        """Membuka arsip chat"""
        try:
            result = await client.unarsip_chat(chat_id=message.chat.id)
            
            response_id = f"unarsip_chat_{message.id}"
            self.pending_responses[response_id] = {
                'text': "📂 Chat berhasil dibuka dari arsip!" if result else "❌ Gagal membuka arsip chat",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:UNARSIP_CHAT] Unarchived chat")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:UNARSIP_CHAT] Error: {e}")
            response_id = f"unarsip_chat_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuka arsip chat: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def set_konten_terlindungi(self, client, message, params):
        """Mengatur perlindungan konten"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:SET_KONTEN_TERLINDUNGI:true/false]"
            
            enabled = params.strip().lower() in ['true', '1', 'on', 'ya', 'aktif']
            result = await client.set_konten_terlindungi(chat_id=message.chat.id, enabled=enabled)
            
            status = "diaktifkan" if enabled else "dinonaktifkan"
            
            response_id = f"set_konten_terlindungi_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"🔒 Perlindungan konten {status}!" if result else f"❌ Gagal mengatur perlindungan konten",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:SET_KONTEN_TERLINDUNGI] Content protection {status}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:SET_KONTEN_TERLINDUNGI] Error: {e}")
            response_id = f"set_konten_terlindungi_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error mengatur perlindungan konten: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def get_pesan_spesifik(self, client, message, params):
        """Mendapatkan pesan berdasarkan ID"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:GET_PESAN_SPESIFIK:message_id]"
            
            message_id = int(params.strip())
            msg = await client.get_pesan_spesifik(chat_id=message.chat.id, message_ids=message_id)
            
            if msg:
                text = f"📨 **Pesan #{message_id}**\n"
                text += f"👤 Dari: {msg.from_user.first_name if msg.from_user else 'Unknown'}\n"
                text += f"📅 Tanggal: {msg.date.strftime('%d/%m/%Y %H:%M')}\n"
                
                if msg.text:
                    text += f"💬 Teks: {msg.text[:100]}{'...' if len(msg.text) > 100 else ''}\n"
                elif msg.caption:
                    text += f"📝 Caption: {msg.caption[:100]}{'...' if len(msg.caption) > 100 else ''}\n"
                
                if msg.media:
                    text += f"📎 Media: {msg.media.value}\n"
            else:
                text = "❌ Pesan tidak ditemukan"
            
            response_id = f"get_pesan_spesifik_{message.id}"
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:GET_PESAN_SPESIFIK] Retrieved message {message_id}")
            return response_id
            
        except ValueError:
            response_id = f"get_pesan_spesifik_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Message ID harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:GET_PESAN_SPESIFIK] Error: {e}")
            response_id = f"get_pesan_spesifik_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error mendapatkan pesan: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def get_grup_media(self, client, message, params):
        """Mendapatkan album media berdasarkan message ID"""
        try:
            if not params.strip():
                return "❌ Usage: [PYROGRAM:GET_GRUP_MEDIA:message_id]"
            
            message_id = int(params.strip())
            media_group = await client.get_grup_media(chat_id=message.chat.id, message_id=message_id)
            
            if media_group:
                text = f"🖼️ **Album Media** (Total: {len(media_group)})\n\n"
                for i, msg in enumerate(media_group, 1):
                    media_type = msg.media.value if msg.media else 'unknown'
                    caption = msg.caption[:50] + '...' if msg.caption and len(msg.caption) > 50 else msg.caption or ''
                    text += f"{i}. ID: {msg.id} | {media_type.title()}"
                    if caption:
                        text += f" | {caption}"
                    text += "\n"
            else:
                text = "❌ Album media tidak ditemukan"
            
            response_id = f"get_grup_media_{message.id}"
            self.pending_responses[response_id] = {
                'text': text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:GET_GRUP_MEDIA] Retrieved media group for message {message_id}")
            return response_id
            
        except ValueError:
            response_id = f"get_grup_media_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Message ID harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:GET_GRUP_MEDIA] Error: {e}")
            response_id = f"get_grup_media_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error mendapatkan grup media: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def hitung_riwayat(self, client, message, params):
        """Menghitung total pesan dalam chat"""
        try:
            count = await client.hitung_riwayat_chat(chat_id=message.chat.id)
            
            response_id = f"hitung_riwayat_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"📊 **Statistik Chat**\n💬 Total pesan: **{count:,}**",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:HITUNG_RIWAYAT] Message count: {count}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:HITUNG_RIWAYAT] Error: {e}")
            response_id = f"hitung_riwayat_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error menghitung riwayat: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def vote_poll(self, client, message, params):
        """Vote pada polling"""
        try:
            parts = params.split(':')
            if len(parts) < 2:
                return "❌ Usage: [PYROGRAM:VOTE_POLL:message_id:option_index]"
            
            message_id = int(parts[0])
            option_index = int(parts[1])
            
            await client.vote_polling(
                chat_id=message.chat.id,
                message_id=message_id,
                options=[option_index]
            )
            
            response_id = f"vote_poll_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Vote berhasil pada opsi {option_index + 1}!",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:VOTE_POLL] Voted on poll message {message_id}, option {option_index}")
            return response_id
            
        except ValueError:
            response_id = f"vote_poll_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Message ID dan option index harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:VOTE_POLL] Error: {e}")
            response_id = f"vote_poll_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error vote polling: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def bulk_kirim(self, client, message, params):
        """Kirim pesan ke multiple chat"""
        try:
            parts = params.split(':')
            if len(parts) < 2:
                return "❌ Usage: [PYROGRAM:BULK_KIRIM:chat1,chat2,...:text:delay]"
            
            targets = [chat.strip() for chat in parts[0].split(',')]
            text = parts[1]
            delay = float(parts[2]) if len(parts) > 2 and parts[2].replace('.', '').isdigit() else 1.0
            
            results = await client.kirim_bulk_pesan(targets=targets, text=text, delay=delay)
            success_count = len(results)
            total_count = len(targets)
            
            response_id = f"bulk_kirim_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Bulk Send Selesai**\n📨 Berhasil: {success_count}/{total_count}\n⏱️ Delay: {delay}s",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BULK_KIRIM] Sent to {success_count}/{total_count} targets")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BULK_KIRIM] Error: {e}")
            response_id = f"bulk_kirim_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error bulk kirim: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def bulk_forward(self, client, message, params):
        """Forward pesan ke multiple chat"""
        try:
            parts = params.split(':')
            if len(parts) < 2:
                return "❌ Usage: [PYROGRAM:BULK_FORWARD:chat1,chat2,...:message_id:delay]"
            
            targets = [chat.strip() for chat in parts[0].split(',')]
            message_id = int(parts[1])
            delay = float(parts[2]) if len(parts) > 2 and parts[2].replace('.', '').isdigit() else 1.0
            
            results = await client.forward_bulk_pesan(
                targets=targets,
                from_chat_id=message.chat.id,
                message_ids=message_id,
                delay=delay
            )
            success_count = len(results)
            total_count = len(targets)
            
            response_id = f"bulk_forward_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Bulk Forward Selesai**\n📤 Berhasil: {success_count}/{total_count}\n⏱️ Delay: {delay}s",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BULK_FORWARD] Forwarded to {success_count}/{total_count} targets")
            return response_id
            
        except ValueError:
            response_id = f"bulk_forward_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Message ID dan delay harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:BULK_FORWARD] Error: {e}")
            response_id = f"bulk_forward_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error bulk forward: {str(e)}",
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