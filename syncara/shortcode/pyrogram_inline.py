# syncara/shortcode/pyrogram_inline.py
"""
Shortcode untuk inline mode methods Pyrogram.
"""

from syncara.console import console
from pyrogram.types import InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
import json

class PyrogramInlineShortcode:
    def __init__(self):
        self.handlers = {
            'PYROGRAM:BUAT_HASIL_ARTIKEL': self.buat_hasil_artikel,
            'PYROGRAM:BUAT_HASIL_FOTO': self.buat_hasil_foto,
            'PYROGRAM:BUAT_HASIL_VIDEO': self.buat_hasil_video,
            'PYROGRAM:BUAT_HASIL_AUDIO': self.buat_hasil_audio,
            'PYROGRAM:BUAT_HASIL_DOKUMEN': self.buat_hasil_dokumen,
            'PYROGRAM:BUAT_HASIL_KONTAK': self.buat_hasil_kontak,
            'PYROGRAM:BUAT_HASIL_LOKASI': self.buat_hasil_lokasi,
            'PYROGRAM:EDIT_CAPTION_INLINE': self.edit_caption_inline,
            'PYROGRAM:EDIT_REPLY_MARKUP_INLINE': self.edit_reply_markup_inline,
            'PYROGRAM:TEMPLATE_INLINE_KEYBOARD': self.template_inline_keyboard,
            'PYROGRAM:DEMO_INLINE_QUERY': self.demo_inline_query,
            'PYROGRAM:TEST_INLINE_RESULT': self.test_inline_result,
            'PYROGRAM:INLINE_HELP': self.inline_help,
        }
        
        self.descriptions = {
            'PYROGRAM:BUAT_HASIL_ARTIKEL': 'Membuat hasil inline artikel. Usage: [PYROGRAM:BUAT_HASIL_ARTIKEL:id:title:text:description]',
            'PYROGRAM:BUAT_HASIL_FOTO': 'Membuat hasil inline foto. Usage: [PYROGRAM:BUAT_HASIL_FOTO:id:photo_url:thumb_url:title:caption]',
            'PYROGRAM:BUAT_HASIL_VIDEO': 'Membuat hasil inline video. Usage: [PYROGRAM:BUAT_HASIL_VIDEO:id:video_url:mime_type:thumb_url:title]',
            'PYROGRAM:BUAT_HASIL_AUDIO': 'Membuat hasil inline audio. Usage: [PYROGRAM:BUAT_HASIL_AUDIO:id:audio_url:title:performer:duration]',
            'PYROGRAM:BUAT_HASIL_DOKUMEN': 'Membuat hasil inline dokumen. Usage: [PYROGRAM:BUAT_HASIL_DOKUMEN:id:title:document_url:mime_type:description]',
            'PYROGRAM:BUAT_HASIL_KONTAK': 'Membuat hasil inline kontak. Usage: [PYROGRAM:BUAT_HASIL_KONTAK:id:phone:first_name:last_name]',
            'PYROGRAM:BUAT_HASIL_LOKASI': 'Membuat hasil inline lokasi. Usage: [PYROGRAM:BUAT_HASIL_LOKASI:id:latitude:longitude:title:live_period]',
            'PYROGRAM:EDIT_CAPTION_INLINE': 'Edit caption pesan inline. Usage: [PYROGRAM:EDIT_CAPTION_INLINE:inline_message_id:caption]',
            'PYROGRAM:EDIT_REPLY_MARKUP_INLINE': 'Edit reply markup inline. Usage: [PYROGRAM:EDIT_REPLY_MARKUP_INLINE:inline_message_id:keyboard_json]',
            'PYROGRAM:TEMPLATE_INLINE_KEYBOARD': 'Membuat template inline keyboard. Usage: [PYROGRAM:TEMPLATE_INLINE_KEYBOARD:template_name]',
            'PYROGRAM:DEMO_INLINE_QUERY': 'Demo inline query response. Usage: [PYROGRAM:DEMO_INLINE_QUERY:query]',
            'PYROGRAM:TEST_INLINE_RESULT': 'Test inline result berbagai tipe. Usage: [PYROGRAM:TEST_INLINE_RESULT:type]',
            'PYROGRAM:INLINE_HELP': 'Bantuan inline methods. Usage: [PYROGRAM:INLINE_HELP:method_name]',
        }
        
        self.pending_responses = {}

    async def buat_hasil_artikel(self, client, message, params):
        """Membuat hasil inline artikel"""
        try:
            parts = params.split(':')
            if len(parts) < 3:
                return "❌ Usage: [PYROGRAM:BUAT_HASIL_ARTIKEL:id:title:text:description]"
            
            result_id = parts[0]
            title = parts[1]
            text = parts[2]
            description = parts[3] if len(parts) > 3 else None
            
            input_content = InputTextMessageContent(message_text=text)
            
            artikel = await client.buat_hasil_artikel(
                id=result_id,
                title=title,
                input_message_content=input_content,
                description=description
            )
            
            response_id = f"buat_hasil_artikel_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Hasil Artikel Dibuat**\n🆔 ID: `{result_id}`\n📝 Title: {title}\n💬 Text: {text[:50]}{'...' if len(text) > 50 else ''}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_HASIL_ARTIKEL] Created article result: {title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_HASIL_ARTIKEL] Error: {e}")
            response_id = f"buat_hasil_artikel_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat artikel: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def buat_hasil_foto(self, client, message, params):
        """Membuat hasil inline foto"""
        try:
            parts = params.split(':')
            if len(parts) < 3:
                return "❌ Usage: [PYROGRAM:BUAT_HASIL_FOTO:id:photo_url:thumb_url:title:caption]"
            
            result_id = parts[0]
            photo_url = parts[1]
            thumb_url = parts[2]
            title = parts[3] if len(parts) > 3 else None
            caption = parts[4] if len(parts) > 4 else None
            
            foto = await client.buat_hasil_foto(
                id=result_id,
                photo_url=photo_url,
                thumb_url=thumb_url,
                title=title,
                caption=caption
            )
            
            response_id = f"buat_hasil_foto_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Hasil Foto Dibuat**\n🆔 ID: `{result_id}`\n🖼️ URL: {photo_url[:50]}{'...' if len(photo_url) > 50 else ''}\n📝 Title: {title or 'N/A'}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_HASIL_FOTO] Created photo result: {title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_HASIL_FOTO] Error: {e}")
            response_id = f"buat_hasil_foto_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat foto: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def buat_hasil_video(self, client, message, params):
        """Membuat hasil inline video"""
        try:
            parts = params.split(':')
            if len(parts) < 5:
                return "❌ Usage: [PYROGRAM:BUAT_HASIL_VIDEO:id:video_url:mime_type:thumb_url:title]"
            
            result_id = parts[0]
            video_url = parts[1]
            mime_type = parts[2]
            thumb_url = parts[3]
            title = parts[4]
            
            video = await client.buat_hasil_video(
                id=result_id,
                video_url=video_url,
                mime_type=mime_type,
                thumb_url=thumb_url,
                title=title
            )
            
            response_id = f"buat_hasil_video_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Hasil Video Dibuat**\n🆔 ID: `{result_id}`\n🎥 URL: {video_url[:50]}{'...' if len(video_url) > 50 else ''}\n📝 Title: {title}\n🔧 Type: {mime_type}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_HASIL_VIDEO] Created video result: {title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_HASIL_VIDEO] Error: {e}")
            response_id = f"buat_hasil_video_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat video: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def buat_hasil_audio(self, client, message, params):
        """Membuat hasil inline audio"""
        try:
            parts = params.split(':')
            if len(parts) < 3:
                return "❌ Usage: [PYROGRAM:BUAT_HASIL_AUDIO:id:audio_url:title:performer:duration]"
            
            result_id = parts[0]
            audio_url = parts[1]
            title = parts[2]
            performer = parts[3] if len(parts) > 3 else None
            duration = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None
            
            audio = await client.buat_hasil_audio(
                id=result_id,
                audio_url=audio_url,
                title=title,
                performer=performer,
                audio_duration=duration
            )
            
            response_id = f"buat_hasil_audio_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Hasil Audio Dibuat**\n🆔 ID: `{result_id}`\n🎵 URL: {audio_url[:50]}{'...' if len(audio_url) > 50 else ''}\n📝 Title: {title}\n👨‍🎤 Performer: {performer or 'N/A'}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_HASIL_AUDIO] Created audio result: {title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_HASIL_AUDIO] Error: {e}")
            response_id = f"buat_hasil_audio_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat audio: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def buat_hasil_dokumen(self, client, message, params):
        """Membuat hasil inline dokumen"""
        try:
            parts = params.split(':')
            if len(parts) < 4:
                return "❌ Usage: [PYROGRAM:BUAT_HASIL_DOKUMEN:id:title:document_url:mime_type:description]"
            
            result_id = parts[0]
            title = parts[1]
            document_url = parts[2]
            mime_type = parts[3]
            description = parts[4] if len(parts) > 4 else None
            
            dokumen = await client.buat_hasil_dokumen(
                id=result_id,
                title=title,
                document_url=document_url,
                mime_type=mime_type,
                description=description
            )
            
            response_id = f"buat_hasil_dokumen_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Hasil Dokumen Dibuat**\n🆔 ID: `{result_id}`\n📄 Title: {title}\n📎 URL: {document_url[:50]}{'...' if len(document_url) > 50 else ''}\n🔧 Type: {mime_type}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_HASIL_DOKUMEN] Created document result: {title}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_HASIL_DOKUMEN] Error: {e}")
            response_id = f"buat_hasil_dokumen_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat dokumen: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def buat_hasil_kontak(self, client, message, params):
        """Membuat hasil inline kontak"""
        try:
            parts = params.split(':')
            if len(parts) < 3:
                return "❌ Usage: [PYROGRAM:BUAT_HASIL_KONTAK:id:phone:first_name:last_name]"
            
            result_id = parts[0]
            phone_number = parts[1]
            first_name = parts[2]
            last_name = parts[3] if len(parts) > 3 else None
            
            kontak = await client.buat_hasil_kontak(
                id=result_id,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name
            )
            
            full_name = f"{first_name} {last_name}".strip() if last_name else first_name
            
            response_id = f"buat_hasil_kontak_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Hasil Kontak Dibuat**\n🆔 ID: `{result_id}`\n👤 Nama: {full_name}\n📞 Phone: {phone_number}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_HASIL_KONTAK] Created contact result: {full_name}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_HASIL_KONTAK] Error: {e}")
            response_id = f"buat_hasil_kontak_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat kontak: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def buat_hasil_lokasi(self, client, message, params):
        """Membuat hasil inline lokasi"""
        try:
            parts = params.split(':')
            if len(parts) < 4:
                return "❌ Usage: [PYROGRAM:BUAT_HASIL_LOKASI:id:latitude:longitude:title:live_period]"
            
            result_id = parts[0]
            latitude = float(parts[1])
            longitude = float(parts[2])
            title = parts[3]
            live_period = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None
            
            lokasi = await client.buat_hasil_lokasi(
                id=result_id,
                latitude=latitude,
                longitude=longitude,
                title=title,
                live_period=live_period
            )
            
            response_id = f"buat_hasil_lokasi_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Hasil Lokasi Dibuat**\n🆔 ID: `{result_id}`\n📍 Title: {title}\n🌐 Koordinat: {latitude}, {longitude}\n⏱️ Live: {live_period or 'Static'}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:BUAT_HASIL_LOKASI] Created location result: {title}")
            return response_id
            
        except ValueError:
            response_id = f"buat_hasil_lokasi_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Latitude dan longitude harus berupa angka",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:BUAT_HASIL_LOKASI] Error: {e}")
            response_id = f"buat_hasil_lokasi_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat lokasi: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def edit_caption_inline(self, client, message, params):
        """Edit caption pesan inline"""
        try:
            parts = params.split(':')
            if len(parts) < 2:
                return "❌ Usage: [PYROGRAM:EDIT_CAPTION_INLINE:inline_message_id:caption]"
            
            inline_message_id = parts[0]
            caption = parts[1]
            
            result = await client.edit_caption_inline(
                inline_message_id=inline_message_id,
                caption=caption
            )
            
            response_id = f"edit_caption_inline_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Caption inline berhasil diubah!" if result else "❌ Gagal mengubah caption inline",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:EDIT_CAPTION_INLINE] Edited caption: {inline_message_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:EDIT_CAPTION_INLINE] Error: {e}")
            response_id = f"edit_caption_inline_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error edit caption: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def edit_reply_markup_inline(self, client, message, params):
        """Edit reply markup inline"""
        try:
            parts = params.split(':')
            if len(parts) < 2:
                return "❌ Usage: [PYROGRAM:EDIT_REPLY_MARKUP_INLINE:inline_message_id:keyboard_json]"
            
            inline_message_id = parts[0]
            keyboard_json = parts[1]
            
            # Parse keyboard JSON
            keyboard_data = json.loads(keyboard_json)
            keyboard = InlineKeyboardMarkup(keyboard_data)
            
            result = await client.edit_reply_markup_inline(
                inline_message_id=inline_message_id,
                reply_markup=keyboard
            )
            
            response_id = f"edit_reply_markup_inline_{message.id}"
            self.pending_responses[response_id] = {
                'text': "✅ Reply markup inline berhasil diubah!" if result else "❌ Gagal mengubah reply markup inline",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:EDIT_REPLY_MARKUP_INLINE] Edited reply markup: {inline_message_id}")
            return response_id
            
        except json.JSONDecodeError:
            response_id = f"edit_reply_markup_inline_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': "❌ Error: Format JSON keyboard tidak valid",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
        except Exception as e:
            console.error(f"[PYROGRAM:EDIT_REPLY_MARKUP_INLINE] Error: {e}")
            response_id = f"edit_reply_markup_inline_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error edit reply markup: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def template_inline_keyboard(self, client, message, params):
        """Membuat template inline keyboard"""
        try:
            template_name = params.strip() if params.strip() else "basic"
            
            templates = {
                "basic": [
                    [InlineKeyboardButton("Button 1", callback_data="btn1")],
                    [InlineKeyboardButton("Button 2", callback_data="btn2")]
                ],
                "url": [
                    [InlineKeyboardButton("Website", url="https://example.com")],
                    [InlineKeyboardButton("Telegram", url="https://t.me/example")]
                ],
                "mixed": [
                    [InlineKeyboardButton("Callback", callback_data="cb1"), InlineKeyboardButton("URL", url="https://example.com")],
                    [InlineKeyboardButton("Switch Inline", switch_inline_query="query")]
                ]
            }
            
            if template_name not in templates:
                available = ", ".join(templates.keys())
                return f"❌ Template tidak tersedia. Tersedia: {available}"
            
            keyboard = InlineKeyboardMarkup(templates[template_name])
            keyboard_json = json.dumps(templates[template_name], indent=2)
            
            response_id = f"template_inline_keyboard_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Template Inline Keyboard: {template_name}**\n\n```json\n{keyboard_json}\n```",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id,
                'reply_markup': keyboard
            }
            
            console.info(f"[PYROGRAM:TEMPLATE_INLINE_KEYBOARD] Created template: {template_name}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:TEMPLATE_INLINE_KEYBOARD] Error: {e}")
            response_id = f"template_inline_keyboard_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error membuat template: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def demo_inline_query(self, client, message, params):
        """Demo inline query response"""
        try:
            query = params.strip() if params.strip() else "demo"
            
            # Simulasi hasil inline query
            results = [
                {
                    'type': 'article',
                    'id': 'demo1',
                    'title': f'Demo Article - {query}',
                    'input_message_content': {
                        'message_text': f'Ini adalah demo artikel untuk query: {query}'
                    },
                    'description': f'Deskripsi untuk {query}'
                },
                {
                    'type': 'article',
                    'id': 'demo2',
                    'title': f'Demo Article 2 - {query}',
                    'input_message_content': {
                        'message_text': f'Ini adalah demo artikel kedua untuk query: {query}'
                    },
                    'description': f'Deskripsi kedua untuk {query}'
                }
            ]
            
            response_id = f"demo_inline_query_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Demo Inline Query**\n🔍 Query: `{query}`\n📝 Results: {len(results)} artikel\n\n**Contoh Response:**\n```json\n{json.dumps(results, indent=2)}\n```",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:DEMO_INLINE_QUERY] Created demo for query: {query}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:DEMO_INLINE_QUERY] Error: {e}")
            response_id = f"demo_inline_query_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error demo inline query: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def test_inline_result(self, client, message, params):
        """Test inline result berbagai tipe"""
        try:
            result_type = params.strip() if params.strip() else "article"
            
            test_results = {
                'article': {
                    'type': 'article',
                    'id': 'test_article',
                    'title': 'Test Article',
                    'description': 'Ini adalah test artikel inline'
                },
                'photo': {
                    'type': 'photo',
                    'id': 'test_photo',
                    'photo_url': 'https://example.com/photo.jpg',
                    'thumb_url': 'https://example.com/thumb.jpg'
                },
                'video': {
                    'type': 'video',
                    'id': 'test_video',
                    'video_url': 'https://example.com/video.mp4',
                    'mime_type': 'video/mp4',
                    'thumb_url': 'https://example.com/thumb.jpg',
                    'title': 'Test Video'
                },
                'audio': {
                    'type': 'audio',
                    'id': 'test_audio',
                    'audio_url': 'https://example.com/audio.mp3',
                    'title': 'Test Audio'
                },
                'document': {
                    'type': 'document',
                    'id': 'test_document',
                    'title': 'Test Document',
                    'document_url': 'https://example.com/document.pdf',
                    'mime_type': 'application/pdf'
                }
            }
            
            if result_type not in test_results:
                available = ", ".join(test_results.keys())
                return f"❌ Tipe tidak tersedia. Tersedia: {available}"
            
            test_data = test_results[result_type]
            
            response_id = f"test_inline_result_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Test Inline Result - {result_type}**\n\n```json\n{json.dumps(test_data, indent=2)}\n```\n\n💡 **Cara penggunaan:**\n- Gunakan data ini sebagai template untuk membuat inline result\n- Sesuaikan URL dan parameter sesuai kebutuhan",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:TEST_INLINE_RESULT] Created test for type: {result_type}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:TEST_INLINE_RESULT] Error: {e}")
            response_id = f"test_inline_result_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error test inline result: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def inline_help(self, client, message, params):
        """Bantuan inline methods"""
        try:
            method_name = params.strip() if params.strip() else None
            
            if method_name is None:
                # General help
                help_text = """🔮 **Bantuan Inline Methods**

📝 **Membuat Hasil Inline:**
• `PYROGRAM:BUAT_HASIL_ARTIKEL` - Artikel teks
• `PYROGRAM:BUAT_HASIL_FOTO` - Foto/gambar
• `PYROGRAM:BUAT_HASIL_VIDEO` - Video
• `PYROGRAM:BUAT_HASIL_AUDIO` - Audio/musik
• `PYROGRAM:BUAT_HASIL_DOKUMEN` - Dokumen/file
• `PYROGRAM:BUAT_HASIL_KONTAK` - Kontak/nomor
• `PYROGRAM:BUAT_HASIL_LOKASI` - Lokasi/koordinat

✏️ **Edit Inline:**
• `PYROGRAM:EDIT_CAPTION_INLINE` - Edit caption
• `PYROGRAM:EDIT_REPLY_MARKUP_INLINE` - Edit keyboard

🛠️ **Utilities:**
• `PYROGRAM:TEMPLATE_INLINE_KEYBOARD` - Template keyboard
• `PYROGRAM:DEMO_INLINE_QUERY` - Demo inline query
• `PYROGRAM:TEST_INLINE_RESULT` - Test result types

💡 **Cara penggunaan:**
`[PYROGRAM:INLINE_HELP:method_name]` untuk bantuan spesifik"""
            else:
                # Specific method help
                method_helps = {
                    'buat_hasil_artikel': """📝 **BUAT_HASIL_ARTIKEL**
**Usage:** `[PYROGRAM:BUAT_HASIL_ARTIKEL:id:title:text:description]`
**Parameter:**
• `id` - ID unik hasil
• `title` - Judul artikel
• `text` - Isi artikel
• `description` - Deskripsi (opsional)

**Contoh:**
`[PYROGRAM:BUAT_HASIL_ARTIKEL:art1:Hello World:Ini adalah artikel pertama:Deskripsi singkat]`""",
                    'buat_hasil_foto': """🖼️ **BUAT_HASIL_FOTO**
**Usage:** `[PYROGRAM:BUAT_HASIL_FOTO:id:photo_url:thumb_url:title:caption]`
**Parameter:**
• `id` - ID unik hasil
• `photo_url` - URL foto
• `thumb_url` - URL thumbnail
• `title` - Judul (opsional)
• `caption` - Caption (opsional)

**Contoh:**
`[PYROGRAM:BUAT_HASIL_FOTO:photo1:https://example.com/photo.jpg:https://example.com/thumb.jpg:My Photo:Caption foto]`""",
                    'edit_caption_inline': """✏️ **EDIT_CAPTION_INLINE**
**Usage:** `[PYROGRAM:EDIT_CAPTION_INLINE:inline_message_id:caption]`
**Parameter:**
• `inline_message_id` - ID pesan inline
• `caption` - Caption baru

**Contoh:**
`[PYROGRAM:EDIT_CAPTION_INLINE:AAB123:Caption yang sudah diubah]`"""
                }
                
                help_text = method_helps.get(method_name.lower(), f"❌ Bantuan untuk `{method_name}` tidak tersedia")
            
            response_id = f"inline_help_{message.id}"
            self.pending_responses[response_id] = {
                'text': help_text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[PYROGRAM:INLINE_HELP] Provided help for: {method_name or 'general'}")
            return response_id
            
        except Exception as e:
            console.error(f"[PYROGRAM:INLINE_HELP] Error: {e}")
            response_id = f"inline_help_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Error bantuan inline: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id

    async def send_pending_responses(self, client, response_ids):
        """Kirim pending responses"""
        for response_id in response_ids:
            if response_id in self.pending_responses:
                response = self.pending_responses[response_id]
                try:
                    await client.kirim_pesan(
                        chat_id=response['chat_id'],
                        text=response['text'],
                        reply_to_message_id=response.get('reply_to_message_id'),
                        reply_markup=response.get('reply_markup')
                    )
                    del self.pending_responses[response_id]
                except Exception as e:
                    console.error(f"Error sending pending response {response_id}: {e}") 