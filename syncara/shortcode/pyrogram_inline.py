# syncara/shortcode/pyrogram_inline.py
"""
Shortcode untuk inline mode methods Pyrogram.
"""

from syncara.shortcode import shortcode
from syncara.console import console
from pyrogram.types import InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
import json

@shortcode("buat_hasil_artikel")
async def buat_hasil_artikel_shortcode(client, message, args):
    """[buat_hasil_artikel:id:title:text:description] - Membuat hasil inline artikel"""
    if len(args) < 3:
        return "❌ Usage: [buat_hasil_artikel:id:title:text:description(opsional)]"
    
    try:
        result_id = args[0]
        title = args[1]
        text = args[2]
        description = args[3] if len(args) > 3 else None
        
        input_content = InputTextMessageContent(message_text=text)
        
        artikel = client.buat_hasil_artikel(
            id=result_id,
            title=title,
            input_message_content=input_content,
            description=description
        )
        
        return f"✅ **Hasil Artikel Dibuat**\n🆔 ID: `{result_id}`\n📝 Title: {title}\n💬 Text: {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("buat_hasil_foto")
async def buat_hasil_foto_shortcode(client, message, args):
    """[buat_hasil_foto:id:photo_url:thumb_url:title:caption] - Membuat hasil inline foto"""
    if len(args) < 3:
        return "❌ Usage: [buat_hasil_foto:id:photo_url:thumb_url:title(opsional):caption(opsional)]"
    
    try:
        result_id = args[0]
        photo_url = args[1]
        thumb_url = args[2]
        title = args[3] if len(args) > 3 else None
        caption = args[4] if len(args) > 4 else None
        
        foto = client.buat_hasil_foto(
            id=result_id,
            photo_url=photo_url,
            thumb_url=thumb_url,
            title=title,
            caption=caption
        )
        
        return f"✅ **Hasil Foto Dibuat**\n🆔 ID: `{result_id}`\n🖼️ URL: {photo_url[:50]}{'...' if len(photo_url) > 50 else ''}\n📝 Title: {title or 'N/A'}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("buat_hasil_video")
async def buat_hasil_video_shortcode(client, message, args):
    """[buat_hasil_video:id:video_url:mime_type:thumb_url:title] - Membuat hasil inline video"""
    if len(args) < 5:
        return "❌ Usage: [buat_hasil_video:id:video_url:mime_type:thumb_url:title]"
    
    try:
        result_id = args[0]
        video_url = args[1]
        mime_type = args[2]
        thumb_url = args[3]
        title = args[4]
        
        video = client.buat_hasil_video(
            id=result_id,
            video_url=video_url,
            mime_type=mime_type,
            thumb_url=thumb_url,
            title=title
        )
        
        return f"✅ **Hasil Video Dibuat**\n🆔 ID: `{result_id}`\n🎥 URL: {video_url[:50]}{'...' if len(video_url) > 50 else ''}\n📝 Title: {title}\n🔧 Type: {mime_type}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("buat_hasil_audio")
async def buat_hasil_audio_shortcode(client, message, args):
    """[buat_hasil_audio:id:audio_url:title:performer:duration] - Membuat hasil inline audio"""
    if len(args) < 3:
        return "❌ Usage: [buat_hasil_audio:id:audio_url:title:performer(opsional):duration(opsional)]"
    
    try:
        result_id = args[0]
        audio_url = args[1]
        title = args[2]
        performer = args[3] if len(args) > 3 else None
        duration = int(args[4]) if len(args) > 4 and args[4].isdigit() else None
        
        audio = client.buat_hasil_audio(
            id=result_id,
            audio_url=audio_url,
            title=title,
            performer=performer,
            audio_duration=duration
        )
        
        return f"✅ **Hasil Audio Dibuat**\n🆔 ID: `{result_id}`\n🎵 URL: {audio_url[:50]}{'...' if len(audio_url) > 50 else ''}\n📝 Title: {title}\n👨‍🎤 Performer: {performer or 'N/A'}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("buat_hasil_dokumen")
async def buat_hasil_dokumen_shortcode(client, message, args):
    """[buat_hasil_dokumen:id:title:document_url:mime_type:description] - Membuat hasil inline dokumen"""
    if len(args) < 4:
        return "❌ Usage: [buat_hasil_dokumen:id:title:document_url:mime_type:description(opsional)]"
    
    try:
        result_id = args[0]
        title = args[1]
        document_url = args[2]
        mime_type = args[3]
        description = args[4] if len(args) > 4 else None
        
        dokumen = client.buat_hasil_dokumen(
            id=result_id,
            title=title,
            document_url=document_url,
            mime_type=mime_type,
            description=description
        )
        
        return f"✅ **Hasil Dokumen Dibuat**\n🆔 ID: `{result_id}`\n📄 Title: {title}\n📎 URL: {document_url[:50]}{'...' if len(document_url) > 50 else ''}\n🔧 Type: {mime_type}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("buat_hasil_kontak")
async def buat_hasil_kontak_shortcode(client, message, args):
    """[buat_hasil_kontak:id:phone:first_name:last_name] - Membuat hasil inline kontak"""
    if len(args) < 3:
        return "❌ Usage: [buat_hasil_kontak:id:phone:first_name:last_name(opsional)]"
    
    try:
        result_id = args[0]
        phone_number = args[1]
        first_name = args[2]
        last_name = args[3] if len(args) > 3 else None
        
        kontak = client.buat_hasil_kontak(
            id=result_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name
        )
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        return f"✅ **Hasil Kontak Dibuat**\n🆔 ID: `{result_id}`\n👤 Nama: {full_name}\n📞 Phone: {phone_number}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("buat_hasil_lokasi")
async def buat_hasil_lokasi_shortcode(client, message, args):
    """[buat_hasil_lokasi:id:lat:lon:title:live_period] - Membuat hasil inline lokasi"""
    if len(args) < 4:
        return "❌ Usage: [buat_hasil_lokasi:id:latitude:longitude:title:live_period(opsional)]"
    
    try:
        result_id = args[0]
        latitude = float(args[1])
        longitude = float(args[2])
        title = args[3]
        live_period = int(args[4]) if len(args) > 4 and args[4].isdigit() else None
        
        lokasi = client.buat_hasil_lokasi(
            id=result_id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            live_period=live_period
        )
        
        return f"✅ **Hasil Lokasi Dibuat**\n🆔 ID: `{result_id}`\n📍 Title: {title}\n🌐 Koordinat: {latitude}, {longitude}\n⏱️ Live: {live_period or 'Static'}"
    except ValueError:
        return "❌ Error: Latitude dan longitude harus berupa angka"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("edit_caption_inline")
async def edit_caption_inline_shortcode(client, message, args):
    """[edit_caption_inline:inline_message_id:caption] - Edit caption pesan inline"""
    if len(args) < 2:
        return "❌ Usage: [edit_caption_inline:inline_message_id:caption]"
    
    try:
        inline_message_id = args[0]
        caption = args[1]
        
        result = await client.edit_caption_inline(
            inline_message_id=inline_message_id,
            caption=caption
        )
        
        return f"✅ Caption inline berhasil diedit!" if result else "❌ Gagal mengedit caption inline"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("edit_reply_markup_inline")
async def edit_reply_markup_inline_shortcode(client, message, args):
    """[edit_reply_markup_inline:inline_message_id:button_json] - Edit keyboard inline"""
    if len(args) < 1:
        return "❌ Usage: [edit_reply_markup_inline:inline_message_id:button_json(opsional)]"
    
    try:
        inline_message_id = args[0]
        
        # Parse button JSON if provided
        reply_markup = None
        if len(args) > 1:
            try:
                button_data = json.loads(args[1])
                reply_markup = client.buat_keyboard_inline(button_data)
            except json.JSONDecodeError:
                return "❌ Error: Format JSON button tidak valid"
        
        result = await client.edit_reply_markup_inline(
            inline_message_id=inline_message_id,
            reply_markup=reply_markup
        )
        
        return f"✅ Keyboard inline berhasil diedit!" if result else "❌ Gagal mengedit keyboard inline"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("template_inline_keyboard")
async def template_inline_keyboard_shortcode(client, message, args):
    """[template_inline_keyboard] - Contoh template untuk inline keyboard"""
    template = {
        "simple": [
            [{"text": "Tombol 1", "callback_data": "btn1"}],
            [{"text": "Tombol 2", "callback_data": "btn2"}]
        ],
        "with_url": [
            [{"text": "Website", "url": "https://example.com"}],
            [{"text": "Callback", "callback_data": "data"}]
        ],
        "complex": [
            [{"text": "✅ Ya", "callback_data": "yes"}, {"text": "❌ Tidak", "callback_data": "no"}],
            [{"text": "💬 Chat", "url": "https://t.me/username"}],
            [{"text": "🔙 Kembali", "callback_data": "back"}]
        ]
    }
    
    template_name = args[0] if args else "simple"
    
    if template_name in template:
        keyboard_json = json.dumps(template[template_name], indent=2)
        return f"📋 **Template Inline Keyboard: {template_name}**\n\n```json\n{keyboard_json}\n```\n\n💡 Copy JSON di atas untuk digunakan dengan shortcode keyboard"
    else:
        available = ", ".join(template.keys())
        return f"❌ Template tidak ditemukan.\n📚 Template tersedia: {available}"

@shortcode("demo_inline_query")
async def demo_inline_query_shortcode(client, message, args):
    """[demo_inline_query] - Demo cara membuat inline query response"""
    demo_code = """
# Contoh handler untuk inline query
@client.on_inline_query()
async def handle_inline_query(client, inline_query):
    query = inline_query.query
    
    results = []
    
    # Hasil artikel
    results.append(
        client.buat_hasil_artikel(
            id="artikel_1",
            title=f"Pencarian: {query}",
            input_message_content=InputTextMessageContent(
                message_text=f"Hasil pencarian untuk: {query}"
            ),
            description="Klik untuk mengirim hasil pencarian"
        )
    )
    
    # Hasil foto (jika ada query)
    if query:
        results.append(
            client.buat_hasil_foto(
                id="foto_1",
                photo_url="https://picsum.photos/800/600",
                thumb_url="https://picsum.photos/200/200",
                title=f"Foto: {query}",
                caption=f"Foto random untuk: {query}"
            )
        )
    
    # Jawab inline query
    await client.jawab_inline_query(
        inline_query_id=inline_query.id,
        results=results,
        cache_time=300,
        is_personal=True
    )
"""
    
    return f"📖 **Demo Inline Query Handler**\n\n```python{demo_code}```\n\n💡 Simpan kode di atas sebagai handler inline query"

@shortcode("test_inline_result")
async def test_inline_result_shortcode(client, message, args):
    """[test_inline_result:type:...] - Test pembuatan hasil inline"""
    if len(args) < 1:
        return "❌ Usage: [test_inline_result:type] - type: artikel/foto/video/audio/dokumen/kontak/lokasi"
    
    result_type = args[0].lower()
    
    try:
        if result_type == "artikel":
            result = client.buat_hasil_artikel(
                id="test_artikel",
                title="Test Artikel",
                input_message_content=InputTextMessageContent(
                    message_text="Ini adalah test artikel inline"
                ),
                description="Deskripsi test artikel"
            )
            return "✅ Test artikel inline berhasil dibuat!"
            
        elif result_type == "foto":
            result = client.buat_hasil_foto(
                id="test_foto",
                photo_url="https://picsum.photos/800/600",
                thumb_url="https://picsum.photos/200/200",
                title="Test Foto",
                caption="Test foto inline"
            )
            return "✅ Test foto inline berhasil dibuat!"
            
        elif result_type == "kontak":
            result = client.buat_hasil_kontak(
                id="test_kontak",
                phone_number="+1234567890",
                first_name="Test",
                last_name="User"
            )
            return "✅ Test kontak inline berhasil dibuat!"
            
        elif result_type == "lokasi":
            result = client.buat_hasil_lokasi(
                id="test_lokasi",
                latitude=-6.2088,
                longitude=106.8456,
                title="Jakarta, Indonesia"
            )
            return "✅ Test lokasi inline berhasil dibuat!"
            
        else:
            return f"❌ Tipe '{result_type}' tidak didukung.\n📚 Tipe tersedia: artikel, foto, video, audio, dokumen, kontak, lokasi"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

@shortcode("inline_help")
async def inline_help_shortcode(client, message, args):
    """[inline_help] - Bantuan untuk inline mode"""
    help_text = """
🔘 **Bantuan Inline Mode**

📋 **Shortcode Tersedia:**
• `[buat_hasil_artikel]` - Buat hasil artikel
• `[buat_hasil_foto]` - Buat hasil foto  
• `[buat_hasil_video]` - Buat hasil video
• `[buat_hasil_audio]` - Buat hasil audio
• `[buat_hasil_dokumen]` - Buat hasil dokumen
• `[buat_hasil_kontak]` - Buat hasil kontak
• `[buat_hasil_lokasi]` - Buat hasil lokasi
• `[edit_caption_inline]` - Edit caption inline
• `[edit_reply_markup_inline]` - Edit keyboard inline
• `[template_inline_keyboard]` - Template keyboard
• `[demo_inline_query]` - Demo inline query handler
• `[test_inline_result]` - Test hasil inline

📖 **Cara Menggunakan:**
1. Buat hasil inline dengan shortcode yang sesuai
2. Gunakan dalam handler inline query
3. Jawab inline query dengan `jawab_inline_query`

💡 **Tips:**
• Gunakan ID unik untuk setiap hasil
• URL foto/video harus dapat diakses publik
• Maksimal 50 hasil per inline query
• Cache time mempengaruhi performa
"""
    
    return help_text 