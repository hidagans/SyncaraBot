from syncara.modules.canvas_manager import canvas_manager
from io import BytesIO

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
            file_bytes = BytesIO(file.get_content().encode('utf-8'))
            file_bytes.name = filename
            await client.send_document(
                chat_id=message.chat.id,
                document=file_bytes,
                caption=f'✅ File `{filename}` berhasil dibuat!',
                reply_to_message_id=message.id
            )
            return True
        except Exception as e:
            await message.reply(f'❌ Gagal membuat file: {e}')
            return False

    async def show_file(self, client, message, params):
        filename = params.strip()
        file = canvas_manager.get_file(filename)
        if file:
            file_bytes = BytesIO(file.get_content().encode('utf-8'))
            file_bytes.name = filename
            await client.send_document(
                chat_id=message.chat.id,
                document=file_bytes,
                caption=f'📄 Isi file `{filename}`',
                reply_to_message_id=message.id
            )
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
                file_bytes = BytesIO(file.get_content().encode('utf-8'))
                file_bytes.name = filename
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_bytes,
                    caption=f'✏️ File `{filename}` berhasil diupdate!',
                    reply_to_message_id=message.id
                )
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
        try:
            from syncara.console import console
            filename = params.strip()
            console.info(f"Attempting to export file: {filename}")
            
            file = canvas_manager.get_file(filename)
            if file:
                console.info(f"File {filename} found, exporting...")
                file_bytes = BytesIO(file.export().encode('utf-8'))
                file_bytes.name = filename
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_bytes,
                    caption=f'📤 Export file `{filename}`',
                    reply_to_message_id=message.id
                )
                console.info(f"Successfully exported file: {filename}")
                return True
            else:
                console.warning(f"File {filename} not found for export")
                available_files = canvas_manager.list_files()
                console.info(f"Available files: {available_files}")
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'❌ File `{filename}` tidak ditemukan.\n\nFile tersedia: {", ".join(available_files) if available_files else "Tidak ada"}',
                    reply_to_message_id=message.id
                )
                return False
        except Exception as e:
            from syncara.console import console
            console.error(f"Error in export_file: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal export file: {str(e)}',
                reply_to_message_id=message.id
            )
            return False 