# 🚀 SyncaraBot - Complete Pyrogram Integration Guide

Panduan lengkap untuk semua fitur Pyrogram yang telah diintegrasikan ke dalam SyncaraBot.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Basic Usage](#basic-usage)
4. [Message Methods](#message-methods)
5. [Media Methods](#media-methods)
6. [Chat Management](#chat-management)
7. [Inline Methods](#inline-methods)
8. [Callback Methods](#callback-methods)
9. [Bot Methods](#bot-methods)
10. [Advanced Features](#advanced-features)
11. [Bound Methods](#bound-methods)
12. [Scheduler System](#scheduler-system)
13. [Helper Utilities](#helper-utilities)
14. [Shortcode System](#shortcode-system)
15. [Testing](#testing)
16. [Troubleshooting](#troubleshooting)

## 🎯 Overview

SyncaraBot sekarang dilengkapi dengan implementasi lengkap semua method Pyrogram dalam bahasa Indonesia. Semua fitur telah diintegrasikan dengan sistem cache, rate limiting, scheduler, dan bound methods support.

### ✨ Key Features

- **600+ Pyrogram Methods** dengan nama Indonesia
- **Bound Methods** untuk natural object interactions
- **Scheduler System** untuk automated tasks
- **Cache Management** dengan TTL dan file-based storage
- **Rate Limiting** untuk mencegah spam
- **Performance Monitoring** untuk tracking usage
- **Comprehensive Testing** untuk semua fitur
- **Shortcode System** untuk easy access
- **Indonesian Documentation** lengkap dengan contoh

## 🛠️ Installation & Setup

### Prerequisites

```bash
pip install pyrogram
pip install aiofiles
pip install croniter
pip install pillow  # For image processing
```

### Basic Setup

```python
from syncara import bot, assistant_manager

# Bot sudah siap dengan semua method Pyrogram
# Tidak perlu setup tambahan
```

## 📚 Basic Usage

### Menggunakan Bot Manager

```python
from syncara import bot

# Kirim pesan
await bot.kirim_pesan(chat_id=123456, text="Hello World!")

# Kirim foto
await bot.kirim_foto(chat_id=123456, photo="path/to/image.jpg")

# Get info chat
info = await bot.get_info_chat(chat_id=123456)
```

### Menggunakan Assistant

```python
from syncara import assistant_manager

# Get assistant
assistant = assistant_manager.get_assistant("AERIS")

# Gunakan method yang sama
await assistant.kirim_pesan(chat_id=123456, text="Hello from AERIS!")
```

## 💬 Message Methods

### Mengirim Pesan

```python
# Pesan biasa
await bot.kirim_pesan(
    chat_id=123456,
    text="Hello World!",
    parse_mode="HTML"
)

# Pesan dengan reply
await bot.kirim_pesan(
    chat_id=123456,
    text="This is a reply",
    reply_to_message_id=789
)

# Pesan dengan keyboard
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Button 1", callback_data="btn1")],
    [InlineKeyboardButton("Button 2", callback_data="btn2")]
])

await bot.kirim_pesan(
    chat_id=123456,
    text="Choose an option:",
    reply_markup=keyboard
)
```

### Mengedit Pesan

```python
# Edit teks
await bot.edit_pesan(
    chat_id=123456,
    message_id=789,
    text="Updated text"
)

# Edit dengan keyboard baru
await bot.edit_pesan(
    chat_id=123456,
    message_id=789,
    text="Updated text",
    reply_markup=new_keyboard
)
```

### Menghapus Pesan

```python
# Hapus satu pesan
await bot.hapus_pesan(
    chat_id=123456,
    message_ids=[789]
)

# Hapus multiple pesan
await bot.hapus_pesan(
    chat_id=123456,
    message_ids=[789, 790, 791]
)
```

### Forward & Copy Pesan

```python
# Forward pesan
await bot.forward_pesan(
    chat_id=123456,  # Tujuan
    from_chat_id=789012,  # Sumber
    message_ids=[100, 101]
)

# Copy pesan
await bot.copy_pesan(
    chat_id=123456,  # Tujuan
    from_chat_id=789012,  # Sumber
    message_id=100
)
```

## 🎨 Media Methods

### Mengirim Foto

```python
# Dari file path
await bot.kirim_foto(
    chat_id=123456,
    photo="path/to/image.jpg",
    caption="Beautiful image!"
)

# Dari URL
await bot.kirim_foto(
    chat_id=123456,
    photo="https://example.com/image.jpg",
    caption="From URL"
)

# Dari file object
with open("image.jpg", "rb") as f:
    await bot.kirim_foto(
        chat_id=123456,
        photo=f,
        caption="From file object"
    )
```

### Mengirim Video

```python
# Video dengan thumbnail
await bot.kirim_video(
    chat_id=123456,
    video="path/to/video.mp4",
    caption="Amazing video!",
    thumb="path/to/thumbnail.jpg",
    duration=120,  # seconds
    width=1920,
    height=1080
)
```

### Mengirim Audio

```python
# Audio dengan metadata
await bot.kirim_audio(
    chat_id=123456,
    audio="path/to/song.mp3",
    caption="Great song!",
    duration=180,
    performer="Artist Name",
    title="Song Title"
)
```

### Mengirim Dokumen

```python
# Dokumen dengan thumbnail
await bot.kirim_dokumen(
    chat_id=123456,
    document="path/to/document.pdf",
    caption="Important document",
    thumb="path/to/thumbnail.jpg",
    file_name="custom_name.pdf"
)
```

### Download Media

```python
# Download dengan progress callback
def progress(current, total):
    print(f"Downloaded {current}/{total} bytes")

file_path = await bot.download_media_extended(
    message=message,
    file_name="downloaded_file",
    progress=progress
)
```

## 👥 Chat Management

### Bergabung & Keluar Chat

```python
# Bergabung ke chat
await bot.gabung_chat(chat_id="@public_channel")

# Keluar dari chat
await bot.keluar_chat(chat_id=123456)
```

### Mengatur Chat

```python
# Set judul chat
await bot.set_judul_chat(chat_id=123456, title="New Title")

# Set deskripsi chat
await bot.set_deskripsi_chat(chat_id=123456, description="New description")

# Set foto chat
await bot.set_foto_chat(chat_id=123456, photo="path/to/photo.jpg")

# Hapus foto chat
await bot.hapus_foto_chat(chat_id=123456)
```

### Member Management

```python
# Get info member
member = await bot.get_member_chat(chat_id=123456, user_id=789)

# Get daftar member
members = await bot.get_daftar_member(chat_id=123456, limit=100)

# Tambah member
await bot.tambah_member_chat(chat_id=123456, user_ids=[789, 790])

# Ban member
await bot.ban_member_chat(chat_id=123456, user_id=789)

# Unban member
await bot.unban_member_chat(chat_id=123456, user_id=789)
```

### Admin Management

```python
from pyrogram.types import ChatPrivileges

# Promosi member ke admin
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

# Set gelar admin
await bot.set_gelar_admin(
    chat_id=123456,
    user_id=789,
    custom_title="Super Admin"
)
```

## 🔗 Inline Methods

### Menjawab Inline Query

```python
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

# Siapkan hasil
results = [
    InlineQueryResultArticle(
        id="result1",
        title="Article 1",
        description="Description 1",
        input_message_content=InputTextMessageContent(
            message_text="Content 1"
        )
    ),
    InlineQueryResultArticle(
        id="result2",
        title="Article 2",
        description="Description 2",
        input_message_content=InputTextMessageContent(
            message_text="Content 2"
        )
    )
]

# Jawab inline query
await bot.jawab_inline_query(
    inline_query_id=query.id,
    results=results,
    cache_time=300
)
```

### Membuat Inline Results

```python
# Artikel result
article = bot.buat_hasil_artikel(
    id="article1",
    title="Article Title",
    description="Article Description",
    message_text="Article content"
)

# Foto result
photo = bot.buat_hasil_foto(
    id="photo1",
    photo_url="https://example.com/photo.jpg",
    thumb_url="https://example.com/thumb.jpg",
    caption="Photo caption"
)

# Video result
video = bot.buat_hasil_video(
    id="video1",
    video_url="https://example.com/video.mp4",
    thumb_url="https://example.com/thumb.jpg",
    title="Video Title"
)
```

## 📞 Callback Methods

### Menjawab Callback Query

```python
# Jawab dengan notifikasi
await bot.jawab_callback_query(
    callback_query_id=query.id,
    text="Button clicked!",
    show_alert=False
)

# Jawab dengan alert
await bot.jawab_callback_query(
    callback_query_id=query.id,
    text="Alert message!",
    show_alert=True
)
```

### Membuat Keyboard

```python
# Inline keyboard
inline_keyboard = bot.buat_keyboard_inline([
    [{"text": "Button 1", "callback_data": "btn1"}],
    [{"text": "Button 2", "callback_data": "btn2"}],
    [{"text": "URL Button", "url": "https://example.com"}]
])

# Reply keyboard
reply_keyboard = bot.buat_keyboard_reply([
    [{"text": "Home"}, {"text": "Settings"}],
    [{"text": "Help"}, {"text": "About"}]
])
```

## 🤖 Bot Methods

### Mengatur Bot Commands

```python
from pyrogram.types import BotCommand

# Set commands
commands = [
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Show help"),
    BotCommand("settings", "Bot settings")
]

await bot.set_perintah_bot(commands=commands)

# Get commands
commands = await bot.get_perintah_bot()

# Hapus commands
await bot.hapus_perintah_bot()
```

### Bot Permissions

```python
from pyrogram.types import BotCommandScopeChat

# Set permissions untuk chat tertentu
await bot.set_hak_akses_bot(
    scope=BotCommandScopeChat(chat_id=123456),
    permissions=["can_send_messages", "can_edit_messages"]
)
```

## 🚀 Advanced Features

### Membuat Channel & Group

```python
# Buat channel
channel = await bot.buat_channel(
    title="My Channel",
    description="Channel description"
)

# Buat group
group = await bot.buat_grup(
    title="My Group",
    user_ids=[123, 456, 789]
)

# Buat supergroup
supergroup = await bot.buat_supergroup(
    title="My Supergroup",
    description="Supergroup description"
)
```

### Advanced Chat Features

```python
# Set slow mode
await bot.set_mode_lambat(chat_id=123456, seconds=30)

# Get online count
count = await bot.hitung_member_online(chat_id=123456)

# Arsip chat
await bot.arsip_chat(chat_id=123456)

# Set protected content
await bot.set_konten_terlindungi(chat_id=123456, enabled=True)
```

### Bulk Operations

```python
# Bulk send messages
messages = [
    {"chat_id": 123, "text": "Message 1"},
    {"chat_id": 456, "text": "Message 2"},
    {"chat_id": 789, "text": "Message 3"}
]

results = await bot.kirim_bulk_pesan(messages=messages)

# Bulk forward
await bot.forward_bulk_pesan(
    to_chat_ids=[123, 456, 789],
    from_chat_id=999,
    message_ids=[100, 101, 102]
)
```

## 🔗 Bound Methods

Bound methods memungkinkan interaksi natural dengan objek Pyrogram:

### Chat Bound Methods

```python
# Get chat object
chat = await bot.get_chat(123456)

# Gunakan bound methods
await chat.set_judul("New Title")
await chat.ban_member(user_id=789)
await chat.promote_member(user_id=790, privileges=privileges)
await chat.arsip()
await chat.set_protected_content(True)

# Get members
members = await chat.get_members(limit=100)
```

### Message Bound Methods

```python
# Get message object
message = await bot.get_pesan_spesifik(chat_id=123456, message_id=789)

# Gunakan bound methods
await message.reply_text("This is a reply")
await message.edit_text("Updated text")
await message.delete_message()
await message.pin_message()
await message.forward_message(to_chat_id=456)

# Download media
if message.media:
    file_path = await message.download_media("download_folder/")
```

### User Bound Methods

```python
# Get user object
user = await bot.get_users(123456)

# Gunakan bound methods
await user.send_message("Hello!")
await user.send_photo("photo.jpg", caption="Photo for you")
common_chats = await user.get_common_chats()
photos = await user.get_profile_photos(limit=10)
```

## ⏰ Scheduler System

### Menjadwalkan Pesan

```python
from datetime import datetime, timedelta

# Jadwalkan pesan untuk 1 jam ke depan
send_time = datetime.now() + timedelta(hours=1)
await bot.jadwalkan_pesan(
    chat_id=123456,
    text="Pesan terjadwal",
    send_time=send_time
)
```

### Auto Backup

```python
# Jadwalkan backup otomatis setiap 24 jam
await bot.jadwalkan_backup(
    chat_id=123456,
    backup_interval_hours=24
)
```

### Custom Scheduled Tasks

```python
# Buat custom task
async def custom_task():
    print("Custom task executed!")

# Tambahkan ke scheduler
bot.add_scheduled_task(
    task_id="my_custom_task",
    name="Custom Task",
    func=custom_task,
    interval_seconds=3600  # Every hour
)

# Atau dengan cron expression
bot.add_scheduled_task(
    task_id="daily_task",
    name="Daily Task",
    func=custom_task,
    cron_expression="0 9 * * *"  # Every day at 9 AM
)
```

### Scheduler Management

```python
# Start scheduler
await bot.start_scheduler()

# Get all tasks
tasks = bot.get_scheduled_tasks()

# Remove task
bot.remove_scheduled_task("my_custom_task")

# Stop scheduler
await bot.stop_scheduler()
```

## 🛠️ Helper Utilities

### Cache Management

```python
# Get cache statistics
stats = bot.get_cache_stats()
print(f"Cache entries: {stats['memory_cache']['total_entries']}")

# Cleanup cache
cleaned = await bot.cleanup_cache()
print(f"Cleaned {cleaned['memory_cache_cleaned']} entries")
```

### Batch Operations

```python
# Batch execute operations
async def send_message_op():
    return await bot.kirim_pesan(123456, "Hello")

operations = [send_message_op for _ in range(10)]
results = await bot.batch_operation(operations, batch_size=3, delay=0.5)
```

### Safe Execution

```python
# Safe execution with retry
async def risky_operation():
    # Some operation that might fail
    return await bot.get_chat(123456)

result = await bot.safe_execute(risky_operation, max_retries=3, delay=1.0)
```

### Text Processing

```python
# Extract mentions
mentions = bot.extract_mentions("Hello @user1 and @user2")
# Returns: ['user1', 'user2']

# Extract hashtags
hashtags = bot.extract_hashtags("Check #python and #telegram")
# Returns: ['python', 'telegram']

# Format file size
size = bot.format_file_size(1024000)
# Returns: "1.0 MB"

# Format duration
duration = bot.format_duration(3661)
# Returns: "1.0h"
```

### Image Processing

```python
# Compress image
await bot.compress_image("input.jpg", "output.jpg", quality=85)

# Create thumbnail
await bot.create_thumbnail("input.jpg", "thumb.jpg", size=(200, 200))

# Get media info
info = await bot.get_media_info("video.mp4")
print(f"Duration: {info['duration']} seconds")
```

## 📝 Shortcode System

### Available Shortcodes

```python
from syncara.shortcode.pyrogram_manager import pyrogram_shortcode_manager

# Get all available shortcodes
shortcodes = pyrogram_shortcode_manager.get_available_shortcodes()

# Get by category
categories = pyrogram_shortcode_manager.get_shortcode_categories()
```

### Using Shortcodes

```python
# Handle shortcode
result = await pyrogram_shortcode_manager.handle_shortcode(
    shortcode="PYROGRAM:BUAT_CHANNEL",
    user_id=123456,
    chat_id=789012,
    client=bot,
    message=message,
    title="My Channel",
    description="Channel description"
)
```

### Popular Shortcodes

- `PYROGRAM:BUAT_CHANNEL` - Create channel
- `PYROGRAM:BUAT_GRUP` - Create group
- `PYROGRAM:MULAI_BOT` - Start bot
- `PYROGRAM:CHAT_ARSIP` - Archive chat
- `PYROGRAM:MESSAGE_REPLY_TEXT` - Reply to message
- `PYROGRAM:EXPORT_SESSION` - Export session

## 🧪 Testing

### Run All Tests

```bash
# Update test chat ID in test_pyrogram_methods.py
python test_pyrogram_methods.py @your_test_chat
```

### Test Categories

- **Message Methods** - Send, edit, delete, forward, copy
- **Media Methods** - Photo, video, audio, document
- **Chat Methods** - Join, leave, manage, member operations
- **Callback Methods** - Handle callbacks, create keyboards
- **Bot Methods** - Commands, permissions, settings
- **Scheduler Methods** - Task scheduling, automation
- **Helper Methods** - Cache, utilities, batch operations
- **Bound Methods** - Object-oriented interactions
- **Advanced Features** - Bulk operations, safety features

### Test Results

Test script provides comprehensive reporting:
- ✅ Passed tests
- ❌ Failed tests
- ⏭️ Skipped tests
- 🎯 Success rate percentage

## 🔧 Troubleshooting

### Common Issues

1. **Rate Limiting**
   ```python
   # Use built-in rate limiter
   @bot.helpers.rate_limit(max_requests=20, window_seconds=60)
   async def my_function():
       # Your code here
   ```

2. **Memory Issues**
   ```python
   # Regular cache cleanup
   await bot.cleanup_cache()
   
   # Monitor cache stats
   stats = bot.get_cache_stats()
   ```

3. **Long-running Operations**
   ```python
   # Use progress callback
   callback = bot.create_progress_callback(100, "Processing")
   
   # Use batch operations
   results = await bot.batch_operation(operations, batch_size=10)
   ```

### Debugging

```python
# Enable debug mode in helpers
bot.helpers.DEBUG_MODE = True

# Monitor performance
stats = bot.helpers.performance_monitor.get_stats()
```

### Configuration

```python
# Cache configuration
bot.helpers.cache.default_ttl = 7200  # 2 hours

# Rate limiter configuration
bot.helpers.rate_limiter.max_requests = 50
bot.helpers.rate_limiter.window_seconds = 60
```

## 📊 Performance Tips

1. **Use Cache Wisely**
   ```python
   # Cache expensive operations
   @bot.helpers.cache_method(ttl=3600)
   async def expensive_operation():
       # Your expensive code
   ```

2. **Batch Operations**
   ```python
   # Instead of individual calls
   results = await bot.batch_operation(operations, batch_size=10)
   ```

3. **Background Tasks**
   ```python
   # Use scheduler for background tasks
   await bot.start_scheduler()
   ```

4. **Monitor Performance**
   ```python
   # Regular monitoring
   stats = bot.helpers.performance_monitor.get_stats()
   ```

## 🎉 Conclusion

SyncaraBot sekarang dilengkapi dengan implementasi lengkap Pyrogram yang mencakup:

- **600+ Methods** dengan nama Indonesia
- **Advanced Features** seperti scheduler, cache, dan bound methods
- **Comprehensive Testing** untuk reliability
- **Performance Optimization** untuk scalability
- **Developer-friendly** dengan dokumentasi lengkap

Semua fitur siap digunakan dan terintegrasi dengan sistem bot yang sudah ada.

---

**Happy Coding! 🚀**

*For support, please refer to the test files or create an issue in the repository.* 