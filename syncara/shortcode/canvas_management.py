from syncara.modules.canvas_manager import canvas_manager

class CanvasManagementShortcode:
    def __init__(self):
        self.handlers = {
            'CANVAS:CREATE': self.create_file,
            'CANVAS:SHOW': self.show_file,
            'CANVAS:EDIT': self.edit_file,
            'CANVAS:LIST': self.list_files,
            'CANVAS:EXPORT': self.export_file,
        }
        self.descriptions = {
            'CANVAS:CREATE': 'Buat file virtual. Usage: [CANVAS:CREATE:filename:type:isi]',
            'CANVAS:SHOW': 'Tampilkan isi file virtual. Usage: [CANVAS:SHOW:filename]',
            'CANVAS:EDIT': 'Edit isi file virtual. Usage: [CANVAS:EDIT:filename:isi_baru]',
            'CANVAS:LIST': 'List semua file virtual. Usage: [CANVAS:LIST]',
            'CANVAS:EXPORT': 'Export isi file virtual. Usage: [CANVAS:EXPORT:filename]',
        }

    async def create_file(self, client, message, params):
        # [CANVAS:CREATE:filename:type:isi]
        try:
            parts = params.split(':', 2)
            if len(parts) < 2:
                await message.reply('Format: [CANVAS:CREATE:filename:type:isi]')
                return False
            filename = parts[0].strip()
            filetype = parts[1].strip() if len(parts) > 1 else 'txt'
            content = parts[2].strip() if len(parts) > 2 else ''
            file = canvas_manager.create_file(filename, filetype, content)
            await message.reply(f'✅ File `{filename}` berhasil dibuat!\n\n{file.get_content() or "(kosong)"}')
            return True
        except Exception as e:
            await message.reply(f'❌ Gagal membuat file: {e}')
            return False

    async def show_file(self, client, message, params):
        filename = params.strip()
        file = canvas_manager.get_file(filename)
        if file:
            await message.reply(f'📄 Isi file `{filename}`:\n\n{file.get_content()}')
            return True
        else:
            await message.reply('File tidak ditemukan.')
            return False

    async def edit_file(self, client, message, params):
        # [CANVAS:EDIT:filename:isi_baru]
        try:
            parts = params.split(':', 1)
            if len(parts) < 2:
                await message.reply('Format: [CANVAS:EDIT:filename:isi_baru]')
                return False
            filename = parts[0].strip()
            new_content = parts[1].strip()
            file = canvas_manager.get_file(filename)
            if file:
                file.update_content(new_content)
                await message.reply(f'✏️ File `{filename}` berhasil diupdate!\n\n{file.get_content()}')
                return True
            else:
                await message.reply('File tidak ditemukan.')
                return False
        except Exception as e:
            await message.reply(f'❌ Gagal edit file: {e}')
            return False

    async def list_files(self, client, message, params):
        files = canvas_manager.list_files()
        if files:
            await message.reply('📂 Daftar file virtual:\n' + '\n'.join(f'- {f}' for f in files))
        else:
            await message.reply('Belum ada file virtual yang dibuat.')
        return True

    async def export_file(self, client, message, params):
        filename = params.strip()
        file = canvas_manager.get_file(filename)
        if file:
            await message.reply(f'📤 Export file `{filename}`:\n\n{file.export()}')
            return True
        else:
            await message.reply('File tidak ditemukan.')
            return False 