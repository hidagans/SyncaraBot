# Panduan Kompatibilitas Pyrogram SyncaraBot

## Masalah yang Diperbaiki

SyncaraBot telah diperbarui untuk mendukung berbagai versi Pyrogram, termasuk versi lama yang tidak memiliki beberapa types terbaru.

### Error yang Diatasi

```
AttributeError: module 'pyrogram.types' has no attribute 'ReplyParameters'
```

### Types yang Mungkin Tidak Tersedia

- `ReplyParameters` 
- `ChatPermissions`
- `ChatPrivileges`
- `BotCommand`
- `BotCommandScope`
- `ChatAdministratorRights`
- `MenuButton`

## Solusi Kompatibilitas

### 1. Compatibility Layer

File baru: `syncara/modules/pyrogram_compatibility.py`

- Mendeteksi types yang tersedia di versi Pyrogram
- Menyediakan fallback functions untuk types yang tidak tersedia
- Memberikan informasi kompatibilitas saat startup

### 2. Safe Type Creation

```python
# Sebelum (bisa error)
permissions = types.ChatPermissions(can_send_messages=True)

# Setelah (safe)
permissions = create_chat_permissions(can_send_messages=True)
```

### 3. Fallback Implementations

Jika type tidak tersedia, sistem akan menggunakan:
- `dict` objects sebagai fallback
- Default values yang kompatibel
- Graceful degradation

## Fitur Baru

### Compatibility Check

Saat startup, SyncaraBot akan menampilkan:
```
🔍 Pyrogram Compatibility Check:
✅ Available Types: 15/20
⚠️ Missing Types: ReplyParameters, ChatPermissions
📝 Using fallback implementations for missing types
```

### Safe Method Calls

Semua method telah diperbarui untuk menggunakan compatibility functions:

```python
# Chat permissions dengan fallback
async def set_izin_chat(self, chat_id, permissions=None):
    if permissions is None:
        permissions = create_chat_permissions(**DEFAULT_CHAT_PERMISSIONS)
    elif isinstance(permissions, dict):
        permissions = create_chat_permissions(**permissions)
    
    return await self.set_chat_permissions(chat_id=chat_id, permissions=permissions)
```

## Testing

Gunakan script test untuk memverifikasi kompatibilitas:

```bash
cd /path/to/SyncaraBot
python3 test_import.py
```

Script akan:
- Test semua imports
- Menampilkan informasi kompatibilitas
- Test basic functionality
- Menampilkan types yang tidak tersedia

## Upgrade Path

### Untuk Versi Lama Pyrogram

Tetap bisa menggunakan SyncaraBot dengan fallback implementations:
- Keyboard markup akan menggunakan dict format
- Chat permissions akan menggunakan parameter dict
- Bot commands akan menggunakan dict format

### Untuk Versi Baru Pyrogram

Akan menggunakan full type safety dan semua fitur terbaru.

## Penggunaan

### Method yang Sudah Diperbarui

1. **Chat Methods**:
   ```python
   # Menggunakan dict untuk permissions
   await bot.set_izin_chat(chat_id, {
       "can_send_messages": True,
       "can_send_media_messages": False
   })
   
   # Menggunakan dict untuk privileges
   await bot.promosi_member_chat(chat_id, user_id, {
       "can_manage_chat": True,
       "can_delete_messages": True
   })
   ```

2. **Bot Commands**:
   ```python
   # Menggunakan dict untuk commands
   await bot.set_perintah_bot([
       {"command": "start", "description": "Mulai bot"},
       {"command": "help", "description": "Bantuan"}
   ])
   ```

3. **Keyboard Markup**:
   ```python
   # Inline keyboard tetap sama
   keyboard = bot.buat_keyboard_inline([
       [{"text": "Tombol 1", "callback_data": "data1"}],
       [{"text": "Tombol 2", "url": "https://example.com"}]
   ])
   ```

## Debugging

Jika masih ada error kompatibilitas:

1. Jalankan test script: `python3 test_import.py`
2. Periksa output compatibility info
3. Lihat types yang missing
4. Pastikan menggunakan fallback methods

## Migrasi

Tidak ada perubahan API yang breaking - semua method yang ada tetap bekerja dengan signature yang sama. Perbedaannya hanya pada internal implementation yang sekarang lebih robust.

## Dukungan Versi

- ✅ Pyrogram 1.4.x
- ✅ Pyrogram 2.0.x  
- ✅ Pyrogram 2.1.x (dengan full type support)
- ✅ Fork/custom versions

## Troubleshooting

### Import Error
```python
ModuleNotFoundError: No module named 'syncara.modules.pyrogram_compatibility'
```

**Solusi**: Pastikan file `pyrogram_compatibility.py` ada di folder `syncara/modules/`

### Type Error
```python
TypeError: 'dict' object has no attribute 'xxx'
```

**Solusi**: Versi Pyrogram Anda menggunakan fallback dict. Ini normal dan tidak mempengaruhi functionality.

### Method Not Found
```python
AttributeError: 'Client' object has no method 'xxx'
```

**Solusi**: Method tersebut mungkin tidak tersedia di versi Pyrogram Anda. Periksa dokumentasi Pyrogram untuk versi yang Anda gunakan.

---

**Catatan**: Semua perubahan kompatibilitas dilakukan secara backward-compatible. Kode yang ada akan tetap bekerja tanpa perlu diubah. 