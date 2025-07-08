# 📚 Dokumentasi Method Pyrogram SyncaraBot

Dokumentasi lengkap untuk semua method Pyrogram yang tersedia di SyncaraBot dalam bahasa Indonesia.

## 🚀 Cara Penggunaan

Semua method ini tersedia di class `Bot` dan `Ubot` setelah mengimport SyncaraBot:

```python
from syncara import bot, assistant_manager

# Menggunakan Bot Manager
await bot.kirim_pesan(chat_id=123456, text="Halo dari Bot Manager!")

# Menggunakan Assistant
assistant = assistant_manager.get_assistant("AERIS")
await assistant.kirim_foto(chat_id=123456, photo="path/to/photo.jpg", caption="Foto dari Assistant")
```

## 📨 Method Pesan

### `kirim_pesan(chat_id, text, ...)`
Mengirim pesan teks ke chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `text`: Teks pesan yang akan dikirim
- `parse_mode`: Mode parsing (HTML, Markdown, atau None)
- `reply_to_message_id`: ID pesan yang akan direply
- `reply_markup`: Keyboard markup
- `disable_web_page_preview`: Nonaktifkan preview web page
- `disable_notification`: Kirim tanpa notifikasi
- `protect_content`: Lindungi konten dari forward

**Contoh:**
```python
# Kirim pesan biasa
await bot.kirim_pesan(chat_id=123456, text="Halo dunia!")

# Kirim pesan dengan HTML
await bot.kirim_pesan(
    chat_id=123456, 
    text="<b>Pesan tebal</b> dan <i>miring</i>",
    parse_mode=enums.ParseMode.HTML
)

# Kirim pesan reply
await bot.kirim_pesan(
    chat_id=123456,
    text="Ini adalah reply",
    reply_to_message_id=789
)
```

### `edit_pesan(chat_id, message_id, text, ...)`
Mengedit pesan teks yang sudah dikirim.

**Parameter:**
- `chat_id`: ID chat atau username
- `message_id`: ID pesan yang akan diedit
- `text`: Teks baru
- `parse_mode`: Mode parsing
- `reply_markup`: Keyboard markup baru

**Contoh:**
```python
# Edit pesan
await bot.edit_pesan(
    chat_id=123456,
    message_id=789,
    text="Pesan yang sudah diedit"
)
```

### `hapus_pesan(chat_id, message_ids, ...)`
Menghapus pesan.

**Parameter:**
- `chat_id`: ID chat atau username
- `message_ids`: ID pesan atau list ID pesan yang akan dihapus
- `revoke`: Hapus untuk semua user (True) atau hanya untuk bot (False)

**Contoh:**
```python
# Hapus satu pesan
await bot.hapus_pesan(chat_id=123456, message_ids=789)

# Hapus beberapa pesan
await bot.hapus_pesan(chat_id=123456, message_ids=[789, 790, 791])
```

### `forward_pesan(chat_id, from_chat_id, message_ids, ...)`
Mem-forward pesan dari chat lain.

**Parameter:**
- `chat_id`: ID chat tujuan
- `from_chat_id`: ID chat sumber
- `message_ids`: ID pesan atau list ID pesan yang akan di-forward
- `disable_notification`: Kirim tanpa notifikasi
- `protect_content`: Lindungi konten dari forward

**Contoh:**
```python
# Forward pesan
await bot.forward_pesan(
    chat_id=123456,
    from_chat_id=654321,
    message_ids=789
)
```

### `copy_pesan(chat_id, from_chat_id, message_id, ...)`
Menyalin pesan dari chat lain.

**Parameter:**
- `chat_id`: ID chat tujuan
- `from_chat_id`: ID chat sumber
- `message_id`: ID pesan yang akan disalin
- `caption`: Caption baru (untuk media)
- `parse_mode`: Mode parsing
- `reply_to_message_id`: ID pesan yang akan direply

**Contoh:**
```python
# Copy pesan
await bot.copy_pesan(
    chat_id=123456,
    from_chat_id=654321,
    message_id=789,
    caption="Caption baru"
)
```

## 🖼️ Method Media

### `kirim_foto(chat_id, photo, ...)`
Mengirim foto.

**Parameter:**
- `chat_id`: ID chat atau username
- `photo`: File foto (path, URL, atau file object)
- `caption`: Caption foto
- `parse_mode`: Mode parsing
- `has_spoiler`: Tandai sebagai spoiler
- `disable_notification`: Kirim tanpa notifikasi
- `reply_to_message_id`: ID pesan yang akan direply

**Contoh:**
```python
# Kirim foto dari file
await bot.kirim_foto(
    chat_id=123456,
    photo="path/to/photo.jpg",
    caption="Foto yang bagus!"
)

# Kirim foto dari URL
await bot.kirim_foto(
    chat_id=123456,
    photo="https://example.com/photo.jpg",
    caption="Foto dari internet"
)

# Kirim foto dengan spoiler
await bot.kirim_foto(
    chat_id=123456,
    photo="photo.jpg",
    caption="Foto spoiler",
    has_spoiler=True
)
```

### `kirim_video(chat_id, video, ...)`
Mengirim video.

**Parameter:**
- `chat_id`: ID chat atau username
- `video`: File video (path, URL, atau file object)
- `duration`: Durasi video dalam detik
- `width`: Lebar video
- `height`: Tinggi video
- `thumb`: Thumbnail video
- `caption`: Caption video
- `has_spoiler`: Tandai sebagai spoiler
- `supports_streaming`: Mendukung streaming

**Contoh:**
```python
# Kirim video
await bot.kirim_video(
    chat_id=123456,
    video="video.mp4",
    caption="Video keren",
    duration=60,
    width=1280,
    height=720
)
```

### `kirim_audio(chat_id, audio, ...)`
Mengirim file audio.

**Parameter:**
- `chat_id`: ID chat atau username
- `audio`: File audio (path, URL, atau file object)
- `caption`: Caption audio
- `duration`: Durasi audio dalam detik
- `performer`: Nama artis/performer
- `title`: Judul lagu
- `thumb`: Thumbnail audio

**Contoh:**
```python
# Kirim audio
await bot.kirim_audio(
    chat_id=123456,
    audio="song.mp3",
    caption="Lagu favorit",
    performer="Artis",
    title="Judul Lagu",
    duration=240
)
```

### `kirim_dokumen(chat_id, document, ...)`
Mengirim dokumen.

**Parameter:**
- `chat_id`: ID chat atau username
- `document`: File dokumen (path, URL, atau file object)
- `thumb`: Thumbnail dokumen
- `caption`: Caption dokumen
- `file_name`: Nama file custom
- `disable_content_type_detection`: Nonaktifkan deteksi tipe konten

**Contoh:**
```python
# Kirim dokumen
await bot.kirim_dokumen(
    chat_id=123456,
    document="document.pdf",
    caption="Dokumen penting",
    file_name="Dokumen_Penting.pdf"
)
```

## 💬 Method Chat

### `gabung_chat(chat_id)`
Bergabung ke grup atau channel.

**Parameter:**
- `chat_id`: ID chat atau username

**Contoh:**
```python
# Gabung ke grup
await bot.gabung_chat(chat_id="@nama_grup")

# Gabung ke channel
await bot.gabung_chat(chat_id="@nama_channel")
```

### `keluar_chat(chat_id, delete=False)`
Keluar dari grup atau channel.

**Parameter:**
- `chat_id`: ID chat atau username
- `delete`: Hapus chat dari daftar (untuk bot)

**Contoh:**
```python
# Keluar dari grup
await bot.keluar_chat(chat_id=123456)

# Keluar dan hapus dari daftar
await bot.keluar_chat(chat_id=123456, delete=True)
```

### `get_info_chat(chat_id)`
Mendapatkan informasi chat.

**Parameter:**
- `chat_id`: ID chat atau username

**Contoh:**
```python
# Get info chat
chat_info = await bot.get_info_chat(chat_id=123456)
print(f"Judul: {chat_info.title}")
print(f"Deskripsi: {chat_info.description}")
print(f"Member: {chat_info.members_count}")
```

### `set_judul_chat(chat_id, title)`
Mengubah judul chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `title`: Judul baru

**Contoh:**
```python
# Ubah judul grup
await bot.set_judul_chat(chat_id=123456, title="Grup Baru")
```

### `set_deskripsi_chat(chat_id, description)`
Mengubah deskripsi chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `description`: Deskripsi baru

**Contoh:**
```python
# Ubah deskripsi grup
await bot.set_deskripsi_chat(
    chat_id=123456,
    description="Deskripsi grup yang baru"
)
```

### `set_foto_chat(chat_id, photo)`
Mengubah foto chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `photo`: File foto (path atau bytes)

**Contoh:**
```python
# Ubah foto grup
await bot.set_foto_chat(chat_id=123456, photo="group_photo.jpg")
```

### `hapus_foto_chat(chat_id)`
Menghapus foto chat.

**Parameter:**
- `chat_id`: ID chat atau username

**Contoh:**
```python
# Hapus foto grup
await bot.hapus_foto_chat(chat_id=123456)
```

## 👥 Method Member

### `get_member_chat(chat_id, user_id)`
Mendapatkan informasi member chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `user_id`: ID user atau username

**Contoh:**
```python
# Get info member
member = await bot.get_member_chat(chat_id=123456, user_id=789)
print(f"Status: {member.status}")
print(f"Nama: {member.user.first_name}")
```

### `get_daftar_member(chat_id, limit=0, filter=RECENT)`
Mendapatkan daftar member chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `limit`: Batas jumlah member (0 = tidak terbatas)
- `filter`: Filter member (RECENT, ADMINISTRATORS, SEARCH, etc.)

**Contoh:**
```python
# Get daftar member
async for member in bot.get_daftar_member(chat_id=123456, limit=100):
    print(f"Member: {member.user.first_name}")

# Get daftar admin
async for admin in bot.get_daftar_member(
    chat_id=123456,
    filter=enums.ChatMembersFilter.ADMINISTRATORS
):
    print(f"Admin: {admin.user.first_name}")
```

### `tambah_member_chat(chat_id, user_ids)`
Menambahkan member ke chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `user_ids`: ID user atau list ID user yang akan ditambahkan

**Contoh:**
```python
# Tambah satu member
await bot.tambah_member_chat(chat_id=123456, user_ids=789)

# Tambah beberapa member
await bot.tambah_member_chat(chat_id=123456, user_ids=[789, 790, 791])
```

### `ban_member_chat(chat_id, user_id, until_date=None, revoke_messages=False)`
Memban member dari chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `user_id`: ID user atau username yang akan diban
- `until_date`: Timestamp kapan ban berakhir (None = permanent)
- `revoke_messages`: Hapus pesan user yang diban

**Contoh:**
```python
# Ban permanent
await bot.ban_member_chat(chat_id=123456, user_id=789)

# Ban sementara (1 hari)
import time
until = int(time.time()) + 86400  # 24 jam
await bot.ban_member_chat(
    chat_id=123456,
    user_id=789,
    until_date=until,
    revoke_messages=True
)
```

### `unban_member_chat(chat_id, user_id, only_if_banned=False)`
Membuka ban member di chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `user_id`: ID user atau username yang akan di-unban
- `only_if_banned`: Hanya unban jika user sedang dalam status banned

**Contoh:**
```python
# Unban member
await bot.unban_member_chat(chat_id=123456, user_id=789)
```

### `batasi_member_chat(chat_id, user_id, permissions, until_date=None)`
Membatasi member di chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `user_id`: ID user atau username yang akan dibatasi
- `permissions`: Izin yang diberikan kepada user
- `until_date`: Timestamp kapan pembatasan berakhir (None = permanent)

**Contoh:**
```python
# Batasi member (hanya bisa baca)
from pyrogram.types import ChatPermissions
permissions = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)
await bot.batasi_member_chat(
    chat_id=123456,
    user_id=789,
    permissions=permissions
)
```

### `promosi_member_chat(chat_id, user_id, privileges)`
Mempromosikan member menjadi admin.

**Parameter:**
- `chat_id`: ID chat atau username
- `user_id`: ID user atau username yang akan dipromosikan
- `privileges`: Hak akses admin yang diberikan

**Contoh:**
```python
# Promosi member menjadi admin
from pyrogram.types import ChatPrivileges
privileges = ChatPrivileges(
    can_manage_chat=True,
    can_delete_messages=True,
    can_manage_video_chats=True,
    can_restrict_members=True,
    can_promote_members=False,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True
)
await bot.promosi_member_chat(
    chat_id=123456,
    user_id=789,
    privileges=privileges
)
```

### `set_gelar_admin(chat_id, user_id, title)`
Mengatur gelar custom untuk admin.

**Parameter:**
- `chat_id`: ID chat atau username
- `user_id`: ID user atau username admin
- `title`: Gelar custom

**Contoh:**
```python
# Set gelar admin
await bot.set_gelar_admin(
    chat_id=123456,
    user_id=789,
    title="Moderator"
)
```

## 🎬 Method Aksi

### `kirim_aksi_chat(chat_id, action)`
Mengirim aksi chat (typing, upload photo, dll).

**Parameter:**
- `chat_id`: ID chat atau username
- `action`: Jenis aksi (TYPING, UPLOAD_PHOTO, RECORD_AUDIO, dll)

**Contoh:**
```python
# Kirim aksi typing
await bot.kirim_aksi_chat(chat_id=123456, action=enums.ChatAction.TYPING)

# Kirim aksi upload foto
await bot.kirim_aksi_chat(chat_id=123456, action=enums.ChatAction.UPLOAD_PHOTO)

# Kirim aksi record audio
await bot.kirim_aksi_chat(chat_id=123456, action=enums.ChatAction.RECORD_AUDIO)
```

### `pin_pesan_chat(chat_id, message_id, disable_notification=False)`
Mem-pin pesan di chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `message_id`: ID pesan yang akan di-pin
- `disable_notification`: Pin tanpa notifikasi

**Contoh:**
```python
# Pin pesan
await bot.pin_pesan_chat(chat_id=123456, message_id=789)

# Pin pesan tanpa notifikasi
await bot.pin_pesan_chat(
    chat_id=123456,
    message_id=789,
    disable_notification=True
)
```

### `unpin_pesan_chat(chat_id, message_id=None)`
Membuka pin pesan di chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `message_id`: ID pesan yang akan di-unpin (None = semua)

**Contoh:**
```python
# Unpin pesan tertentu
await bot.unpin_pesan_chat(chat_id=123456, message_id=789)

# Unpin pesan terakhir yang di-pin
await bot.unpin_pesan_chat(chat_id=123456)
```

### `unpin_semua_pesan(chat_id)`
Membuka pin semua pesan di chat.

**Parameter:**
- `chat_id`: ID chat atau username

**Contoh:**
```python
# Unpin semua pesan
await bot.unpin_semua_pesan(chat_id=123456)
```

## 🔘 Method Inline Mode

### `jawab_inline_query(inline_query_id, results, ...)`
Menjawab inline query.

**Parameter:**
- `inline_query_id`: ID inline query
- `results`: List hasil inline query
- `cache_time`: Waktu cache dalam detik
- `is_personal`: Apakah hasil bersifat personal
- `next_offset`: Offset untuk hasil berikutnya

**Contoh:**
```python
# Jawab inline query
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

results = [
    InlineQueryResultArticle(
        id="1",
        title="Hasil 1",
        input_message_content=InputTextMessageContent(
            message_text="Pesan dari hasil 1"
        )
    ),
    InlineQueryResultArticle(
        id="2",
        title="Hasil 2",
        input_message_content=InputTextMessageContent(
            message_text="Pesan dari hasil 2"
        )
    )
]

await bot.jawab_inline_query(
    inline_query_id="query_123",
    results=results,
    cache_time=300,
    is_personal=True
)
```

### `buat_hasil_artikel(id, title, input_message_content, ...)`
Membuat hasil inline query berupa artikel.

**Parameter:**
- `id`: ID unik hasil
- `title`: Judul artikel
- `input_message_content`: Konten pesan yang akan dikirim
- `description`: Deskripsi artikel
- `thumb_url`: URL thumbnail

**Contoh:**
```python
# Buat hasil artikel
artikel = bot.buat_hasil_artikel(
    id="artikel_1",
    title="Artikel Menarik",
    input_message_content=InputTextMessageContent(
        message_text="Ini adalah artikel yang menarik"
    ),
    description="Deskripsi artikel",
    thumb_url="https://example.com/thumb.jpg"
)
```

### `buat_hasil_foto(id, photo_url, thumb_url, ...)`
Membuat hasil inline query berupa foto.

**Parameter:**
- `id`: ID unik hasil
- `photo_url`: URL foto
- `thumb_url`: URL thumbnail
- `caption`: Caption foto
- `title`: Judul foto

**Contoh:**
```python
# Buat hasil foto
foto = bot.buat_hasil_foto(
    id="foto_1",
    photo_url="https://example.com/photo.jpg",
    thumb_url="https://example.com/thumb.jpg",
    caption="Foto yang bagus",
    title="Foto Menarik"
)
```

## 🎮 Method Callback

### `jawab_callback_query(callback_query_id, text=None, show_alert=False)`
Menjawab callback query dari inline keyboard.

**Parameter:**
- `callback_query_id`: ID callback query
- `text`: Teks notifikasi (maks 200 karakter)
- `show_alert`: Tampilkan sebagai alert popup
- `url`: URL untuk membuka (untuk game callback)

**Contoh:**
```python
# Jawab callback query biasa
await bot.jawab_callback_query(
    callback_query_id="callback_123",
    text="Tombol berhasil ditekan!"
)

# Jawab dengan alert
await bot.jawab_callback_query(
    callback_query_id="callback_123",
    text="Ini adalah alert!",
    show_alert=True
)
```

### `buat_keyboard_inline(buttons)`
Membuat inline keyboard markup.

**Parameter:**
- `buttons`: List tombol dalam format nested list

**Contoh:**
```python
# Buat keyboard inline
keyboard = bot.buat_keyboard_inline([
    [{"text": "Tombol 1", "callback_data": "btn1"}],
    [{"text": "Tombol 2", "callback_data": "btn2"}, {"text": "Tombol 3", "callback_data": "btn3"}],
    [{"text": "Buka Link", "url": "https://example.com"}]
])

# Gunakan keyboard
await bot.kirim_pesan(
    chat_id=123456,
    text="Pilih salah satu:",
    reply_markup=keyboard
)
```

### `buat_keyboard_reply(buttons, ...)`
Membuat reply keyboard markup.

**Parameter:**
- `buttons`: List tombol dalam format nested list
- `resize_keyboard`: Resize keyboard otomatis
- `one_time_keyboard`: Sembunyikan setelah digunakan

**Contoh:**
```python
# Buat keyboard reply
keyboard = bot.buat_keyboard_reply([
    ["Tombol 1", "Tombol 2"],
    ["Tombol 3"],
    ["Batal"]
], resize_keyboard=True, one_time_keyboard=True)

# Gunakan keyboard
await bot.kirim_pesan(
    chat_id=123456,
    text="Pilih opsi:",
    reply_markup=keyboard
)
```

## 🤖 Method Bot

### `set_perintah_bot(commands, scope=None, language_code=None)`
Mengatur daftar perintah bot.

**Parameter:**
- `commands`: List perintah bot
- `scope`: Scope perintah (default, chat, user, dll)
- `language_code`: Kode bahasa

**Contoh:**
```python
# Set perintah bot
from pyrogram.types import BotCommand

commands = [
    BotCommand("start", "Mulai bot"),
    BotCommand("help", "Bantuan"),
    BotCommand("settings", "Pengaturan")
]

await bot.set_perintah_bot(commands=commands)
```

### `get_perintah_bot(scope=None, language_code=None)`
Mendapatkan daftar perintah bot.

**Parameter:**
- `scope`: Scope perintah
- `language_code`: Kode bahasa

**Contoh:**
```python
# Get perintah bot
commands = await bot.get_perintah_bot()
for cmd in commands:
    print(f"/{cmd.command} - {cmd.description}")
```

### `hapus_perintah_bot(scope=None, language_code=None)`
Menghapus perintah bot.

**Parameter:**
- `scope`: Scope perintah
- `language_code`: Kode bahasa

**Contoh:**
```python
# Hapus perintah bot
await bot.hapus_perintah_bot()
```

## 🎯 Method Polling

### `kirim_polling(chat_id, question, options, ...)`
Mengirim polling.

**Parameter:**
- `chat_id`: ID chat atau username
- `question`: Pertanyaan polling
- `options`: List opsi jawaban
- `is_anonymous`: Polling anonim
- `type`: Jenis polling ("regular" atau "quiz")
- `allows_multiple_answers`: Izinkan jawaban ganda

**Contoh:**
```python
# Kirim polling biasa
await bot.kirim_polling(
    chat_id=123456,
    question="Makanan favorit?",
    options=["Nasi", "Mie", "Roti", "Lainnya"],
    is_anonymous=True,
    allows_multiple_answers=False
)

# Kirim quiz
await bot.kirim_polling(
    chat_id=123456,
    question="Ibu kota Indonesia?",
    options=["Jakarta", "Surabaya", "Bandung", "Medan"],
    type="quiz",
    correct_option_id=0,
    explanation="Jakarta adalah ibu kota Indonesia"
)
```

### `hentikan_polling(chat_id, message_id, reply_markup=None)`
Menghentikan polling.

**Parameter:**
- `chat_id`: ID chat atau username
- `message_id`: ID pesan polling
- `reply_markup`: Keyboard markup baru

**Contoh:**
```python
# Hentikan polling
poll = await bot.hentikan_polling(chat_id=123456, message_id=789)
print(f"Polling dihentikan: {poll.question}")
```

## 🛠️ Method Utility

### `get_info_diri()`
Mendapatkan informasi bot/userbot.

**Contoh:**
```python
# Get info diri
info = await bot.get_info_diri()
print(f"ID: {info['id']}")
print(f"Username: {info['username']}")
print(f"Nama: {info['first_name']}")
print(f"Bot: {info['is_bot']}")
```

### `cek_status_online()`
Mengecek apakah bot/userbot sedang online.

**Contoh:**
```python
# Cek status online
is_online = await bot.cek_status_online()
print(f"Status online: {is_online}")
```

### `get_statistik_chat(chat_id)`
Mendapatkan statistik chat.

**Parameter:**
- `chat_id`: ID chat atau username

**Contoh:**
```python
# Get statistik chat
stats = await bot.get_statistik_chat(chat_id=123456)
print(f"Judul: {stats['title']}")
print(f"Tipe: {stats['type']}")
print(f"Member: {stats['member_count']}")
```

### `backup_chat(chat_id, limit=100)`
Backup pesan dari chat.

**Parameter:**
- `chat_id`: ID chat atau username
- `limit`: Jumlah pesan yang akan di-backup

**Contoh:**
```python
# Backup chat
messages = await bot.backup_chat(chat_id=123456, limit=50)
print(f"Berhasil backup {len(messages)} pesan")

# Simpan ke file
import json
with open("backup_chat.json", "w") as f:
    json.dump(messages, f, indent=2, default=str)
```

### `daftar_method_tersedia()`
Mendapatkan daftar semua method yang tersedia.

**Contoh:**
```python
# Lihat daftar method
methods = bot.daftar_method_tersedia()
for category, method_list in methods.items():
    print(f"\n{category.upper()}:")
    for method in method_list:
        print(f"  - {method}")
```

### `bantuan_method(method_name)`
Mendapatkan bantuan untuk method tertentu.

**Parameter:**
- `method_name`: Nama method

**Contoh:**
```python
# Lihat bantuan method
help_text = bot.bantuan_method("kirim_pesan")
print(help_text)
```

## 🎮 Method Game

### `kirim_game(chat_id, game_short_name, ...)`
Mengirim game.

**Parameter:**
- `chat_id`: ID chat
- `game_short_name`: Nama pendek game
- `disable_notification`: Kirim tanpa notifikasi
- `reply_markup`: Keyboard markup

**Contoh:**
```python
# Kirim game
await bot.kirim_game(
    chat_id=123456,
    game_short_name="my_game",
    reply_markup=bot.buat_keyboard_inline([
        [{"text": "🎮 Main Game", "callback_game": ""}]
    ])
)
```

### `set_skor_game(user_id, score, ...)`
Mengatur skor game user.

**Parameter:**
- `user_id`: ID user
- `score`: Skor baru
- `force`: Paksa update meskipun skor lebih rendah
- `chat_id`: ID chat (untuk pesan biasa)
- `message_id`: ID pesan (untuk pesan biasa)

**Contoh:**
```python
# Set skor game
await bot.set_skor_game(
    user_id=123456,
    score=1000,
    chat_id=789,
    message_id=101112
)
```

### `get_skor_tinggi_game(user_id, ...)`
Mendapatkan skor tinggi game.

**Parameter:**
- `user_id`: ID user
- `chat_id`: ID chat (untuk pesan biasa)
- `message_id`: ID pesan (untuk pesan biasa)

**Contoh:**
```python
# Get skor tinggi
scores = await bot.get_skor_tinggi_game(
    user_id=123456,
    chat_id=789,
    message_id=101112
)
for score in scores:
    print(f"User: {score.user.first_name}, Skor: {score.score}")
```

## 📱 Tips Penggunaan

### 1. Error Handling
Selalu gunakan try-catch untuk menangani error:

```python
try:
    await bot.kirim_pesan(chat_id=123456, text="Halo")
except Exception as e:
    print(f"Error: {e}")
```

### 2. Async/Await
Semua method adalah async, jadi harus menggunakan await:

```python
# Benar
await bot.kirim_pesan(chat_id=123456, text="Halo")

# Salah
bot.kirim_pesan(chat_id=123456, text="Halo")
```

### 3. Rate Limiting
Telegram memiliki rate limit, gunakan delay jika mengirim banyak pesan:

```python
import asyncio

for i in range(10):
    await bot.kirim_pesan(chat_id=123456, text=f"Pesan {i}")
    await asyncio.sleep(1)  # Delay 1 detik
```

### 4. File Handling
Untuk file besar, gunakan path file daripada load ke memory:

```python
# Benar - gunakan path
await bot.kirim_foto(chat_id=123456, photo="large_photo.jpg")

# Hindari - load ke memory
with open("large_photo.jpg", "rb") as f:
    await bot.kirim_foto(chat_id=123456, photo=f)
```

### 5. Keyboard Shortcuts
Gunakan helper method untuk membuat keyboard:

```python
# Inline keyboard
keyboard = bot.buat_keyboard_inline([
    [{"text": "Ya", "callback_data": "yes"}, {"text": "Tidak", "callback_data": "no"}]
])

# Reply keyboard
keyboard = bot.buat_keyboard_reply([
    ["Ya", "Tidak"],
    ["Batal"]
])
```

## 🔗 Integrasi dengan Shortcode

Method-method ini bisa digunakan dalam shortcode system SyncaraBot:

```python
# syncara/shortcode/custom_shortcode.py
from syncara.shortcode import shortcode

@shortcode("kirim_foto")
async def kirim_foto_shortcode(client, message, args):
    """[kirim_foto:path_foto:caption] - Kirim foto"""
    if len(args) < 1:
        return "Usage: [kirim_foto:path_foto:caption]"
    
    photo_path = args[0]
    caption = args[1] if len(args) > 1 else ""
    
    try:
        await client.kirim_foto(
            chat_id=message.chat.id,
            photo=photo_path,
            caption=caption
        )
        return "✅ Foto berhasil dikirim!"
    except Exception as e:
        return f"❌ Error: {e}"

@shortcode("statistik_chat")
async def statistik_chat_shortcode(client, message, args):
    """[statistik_chat] - Lihat statistik chat"""
    try:
        stats = await client.get_statistik_chat(chat_id=message.chat.id)
        return f"""
📊 **Statistik Chat**
🏷️ Judul: {stats['title']}
🆔 ID: {stats['id']}
👥 Member: {stats['member_count']}
📝 Tipe: {stats['type']}
✅ Verified: {stats['is_verified']}
        """
    except Exception as e:
        return f"❌ Error: {e}"
```

## 🎨 Contoh Penggunaan Lengkap

```python
# Contoh bot yang menggunakan semua fitur
from syncara import bot

@bot.on_message(filters.command("demo"))
async def demo_command(client, message):
    # Kirim aksi typing
    await client.kirim_aksi_chat(
        chat_id=message.chat.id,
        action=enums.ChatAction.TYPING
    )
    
    # Kirim pesan dengan keyboard
    keyboard = client.buat_keyboard_inline([
        [{"text": "📊 Statistik", "callback_data": "stats"}],
        [{"text": "🖼️ Kirim Foto", "callback_data": "photo"}],
        [{"text": "🎮 Game", "callback_data": "game"}]
    ])
    
    await client.kirim_pesan(
        chat_id=message.chat.id,
        text="🤖 **Demo SyncaraBot**\n\nPilih fitur yang ingin dicoba:",
        reply_markup=keyboard
    )

@bot.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data
    
    if data == "stats":
        # Tampilkan statistik chat
        stats = await client.get_statistik_chat(callback_query.message.chat.id)
        text = f"""
📊 **Statistik Chat**
🏷️ Judul: {stats['title']}
👥 Member: {stats['member_count']}
📝 Tipe: {stats['type']}
        """
        await client.edit_pesan(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.id,
            text=text
        )
    
    elif data == "photo":
        # Kirim foto random
        await client.kirim_foto(
            chat_id=callback_query.message.chat.id,
            photo="https://picsum.photos/800/600",
            caption="🖼️ Foto random dari internet"
        )
    
    elif data == "game":
        # Kirim game
        await client.kirim_game(
            chat_id=callback_query.message.chat.id,
            game_short_name="example_game"
        )
    
    # Jawab callback query
    await client.jawab_callback_query(
        callback_query_id=callback_query.id,
        text="✅ Berhasil!"
    )
```

---

**© 2024 SyncaraBot - Semua method Pyrogram dalam bahasa Indonesia**

Untuk bantuan lebih lanjut, gunakan: `bot.bantuan_method("nama_method")` 