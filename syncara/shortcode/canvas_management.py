from syncara.modules.canvas_manager import canvas_manager
from syncara.console import console
from io import BytesIO
import asyncio

class CanvasManagementShortcode:
    def __init__(self):
        self.handlers = {
            'CANVAS:CREATE': self.create_file,
            'CANVAS:SHOW': self.show_file,
            'CANVAS:EDIT': self.edit_file,
            'CANVAS:LIST': self.list_files,
            'CANVAS:EXPORT': self.export_file,
            'CANVAS:DELETE': self.delete_file,
            'CANVAS:HISTORY': self.show_history,
            'CANVAS:CLEAR': self.clear_files,
        }
        self.descriptions = {
            'CANVAS:CREATE': 'Buat file virtual. Usage: [CANVAS:CREATE:filename:type:isi]',
            'CANVAS:SHOW': 'Tampilkan isi file virtual. Usage: [CANVAS:SHOW:filename]',
            'CANVAS:EDIT': 'Edit isi file virtual. Usage: [CANVAS:EDIT:filename:isi_baru]',
            'CANVAS:LIST': 'List semua file virtual. Usage: [CANVAS:LIST]',
            'CANVAS:EXPORT': 'Export isi file virtual. Usage: [CANVAS:EXPORT:filename]',
            'CANVAS:DELETE': 'Hapus file virtual. Usage: [CANVAS:DELETE:filename]',
            'CANVAS:HISTORY': 'Tampilkan history file virtual. Usage: [CANVAS:HISTORY:filename]',
            'CANVAS:CLEAR': 'Hapus semua file virtual. Usage: [CANVAS:CLEAR]',
        }

    async def create_file(self, client, message, params):
        # [CANVAS:CREATE:filename:type:isi]
        try:
            console.info(f"CANVAS:CREATE called with params: {params}")
            
            parts = params.split(':', 2)
            if len(parts) < 2:
                error_msg = 'Format: [CANVAS:CREATE:filename:type:isi]'
                console.error(f"Invalid format: {error_msg}")
                return False
                
            filename = parts[0].strip()
            filetype = parts[1].strip() if len(parts) > 1 else 'txt'
            content = parts[2].strip() if len(parts) > 2 else ''
            
            console.info(f"Creating file: {filename} with type: {filetype}")
            console.info(f"Content length: {len(content)}")
            
            # Create file in canvas manager with chat_id
            file = await canvas_manager.create_file(filename, filetype, content, message.chat.id)
            
            if not file:
                console.error(f"Failed to create file: {filename}")
                return False
            
            # Verify file was created
            verification = await canvas_manager.get_file(filename, message.chat.id)
            if not verification:
                console.error(f"File {filename} cannot be verified after creation")
                return False
                
            console.info(f"File {filename} created and verified successfully")
            return True
                
        except Exception as e:
            console.error(f"Error in create_file: {str(e)}")
            return False

    async def show_file(self, client, message, params):
        try:
            filename = params.strip()
            console.info(f"CANVAS:SHOW called for file: {filename}")
            
            file = await canvas_manager.get_file(filename, message.chat.id)
            if file:
                console.info(f"File {filename} found, sending content")
                
                try:
                    file_content = file.get_content()
                    file_bytes = BytesIO(file_content.encode('utf-8'))
                    file_bytes.name = filename
                    
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=file_bytes,
                        caption=f'📄 Isi file `{filename}`\n\nPreview: {file_content[:100]}{"..." if len(file_content) > 100 else ""}',
                        reply_to_message_id=message.id
                    )
                    return True
                    
                except Exception as doc_error:
                    console.error(f"Error sending document: {str(doc_error)}")
                    # Fallback to text message
                    await client.send_message(
                        chat_id=message.chat.id,
                        text=f'📄 Isi file `{filename}`:\n\n{file.get_content()[:1000]}{"..." if len(file.get_content()) > 1000 else ""}',
                        reply_to_message_id=message.id
                    )
                    return True
                    
            else:
                console.warning(f"File {filename} not found")
                available_files = await canvas_manager.list_files(message.chat.id)
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'❌ File `{filename}` tidak ditemukan.\n\nFile tersedia: {", ".join(available_files) if available_files else "Tidak ada"}',
                    reply_to_message_id=message.id
                )
                return False
                
        except Exception as e:
            console.error(f"Error in show_file: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal menampilkan file: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

    async def edit_file(self, client, message, params):
        # [CANVAS:EDIT:filename:isi_baru]
        try:
            console.info(f"CANVAS:EDIT called with params: {params}")
            
            parts = params.split(':', 1)
            if len(parts) < 2:
                error_msg = 'Format: [CANVAS:EDIT:filename:isi_baru]'
                console.error(f"Invalid format: {error_msg}")
                await client.send_message(
                    chat_id=message.chat.id,
                    text=error_msg,
                    reply_to_message_id=message.id
                )
                return False
                
            filename = parts[0].strip()
            new_content = parts[1].strip()
            
            console.info(f"Editing file: {filename}")
            
            # Update file using canvas manager
            file = await canvas_manager.update_file(filename, new_content, message.chat.id)
            if file:
                console.info(f"File {filename} updated successfully")
                
                try:
                    file_content = file.get_content()
                    file_bytes = BytesIO(file_content.encode('utf-8'))
                    file_bytes.name = filename
                    
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=file_bytes,
                        caption=f'✏️ File `{filename}` berhasil diupdate!\n\nPreview: {file_content[:100]}{"..." if len(file_content) > 100 else ""}',
                        reply_to_message_id=message.id
                    )
                    return True
                    
                except Exception as doc_error:
                    console.error(f"Error sending document: {str(doc_error)}")
                    # Fallback to text message
                    await client.send_message(
                        chat_id=message.chat.id,
                        text=f'✏️ File `{filename}` berhasil diupdate!\n\nContent:\n{file.get_content()[:500]}{"..." if len(file.get_content()) > 500 else ""}',
                        reply_to_message_id=message.id
                    )
                    return True
                    
            else:
                console.warning(f"File {filename} not found for editing")
                available_files = await canvas_manager.list_files(message.chat.id)
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'❌ File `{filename}` tidak ditemukan.\n\nFile tersedia: {", ".join(available_files) if available_files else "Tidak ada"}',
                    reply_to_message_id=message.id
                )
                return False
                
        except Exception as e:
            console.error(f"Error in edit_file: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal edit file: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

    async def list_files(self, client, message, params):
        try:
            console.info("CANVAS:LIST called")
            
            files = await canvas_manager.list_files(message.chat.id)
            console.info(f"Found {len(files)} files")
            
            if files:
                response = '📂 Daftar file virtual:\n'
                for file_name in files:
                    file_obj = await canvas_manager.get_file(file_name, message.chat.id)
                    if file_obj:
                        content_preview = file_obj.get_content()[:50] + "..." if len(file_obj.get_content()) > 50 else file_obj.get_content()
                        response += f'• {file_name} ({file_obj.filetype}) - {content_preview}\n'
                    else:
                        response += f'• {file_name} (error loading)\n'
                        
                await client.send_message(
                    chat_id=message.chat.id,
                    text=response,
                    reply_to_message_id=message.id
                )
            else:
                await client.send_message(
                    chat_id=message.chat.id,
                    text='📂 Belum ada file virtual yang dibuat.',
                    reply_to_message_id=message.id
                )
            return True
            
        except Exception as e:
            console.error(f"Error in list_files: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal list files: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

    async def export_file(self, client, message, params):
        try:
            filename = params.strip()
            console.info(f"CANVAS:EXPORT called for file: {filename}")
            
            # Add small delay to ensure file is fully created
            await asyncio.sleep(0.1)
            
            file = await canvas_manager.get_file(filename, message.chat.id)
            if file:
                console.info(f"File {filename} found, checking export status...")
                
                # Check if file was already auto-exported during creation
                if hasattr(file, 'auto_exported') and file.auto_exported:
                    console.info(f"File {filename} was already auto-exported during creation, skipping duplicate export")
                    return True  # Return success since file was already sent
                
                console.info(f"File {filename} not yet exported, proceeding with export...")
                
                try:
                    file_content = file.export()
                    file_bytes = BytesIO(file_content.encode('utf-8'))
                    file_bytes.name = filename
                    
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=file_bytes,
                        caption=f'📤 **File Export Complete!**\n\n**Filename:** `{filename}`\n**Size:** {len(file_content)} characters\n\n**Status:** Ready for download',
                        reply_to_message_id=message.id
                    )
                    
                    console.info(f"Successfully exported file: {filename}")
                    
                    # Mark as exported
                    file.auto_exported = True
                    # Update in database
                    await canvas_manager._save_file_to_db(file)
                    
                    return True
                    
                except Exception as doc_error:
                    console.error(f"Error sending document: {str(doc_error)}")
                    # Fallback to text message
                    await client.send_message(
                        chat_id=message.chat.id,
                        text=f'📤 Export file `{filename}`:\n\n{file.export()[:1000]}{"..." if len(file.export()) > 1000 else ""}',
                        reply_to_message_id=message.id
                    )
                    return True
                    
            else:
                console.warning(f"File {filename} not found for export")
                available_files = await canvas_manager.list_files(message.chat.id)
                console.info(f"Available files: {available_files}")
                # DON'T send error message to chat - just log it
                # This prevents the "File tidak ditemukan" message from appearing
                return False
                
        except Exception as e:
            console.error(f"Error in export_file: {str(e)}")
            # DON'T send error message to chat - just log it
            return False

    async def delete_file(self, client, message, params):
        try:
            filename = params.strip()
            console.info(f"CANVAS:DELETE called for file: {filename}")
            
            if not filename:
                await client.send_message(
                    chat_id=message.chat.id,
                    text='❌ Nama file tidak boleh kosong!\nContoh: [CANVAS:DELETE:filename]',
                    reply_to_message_id=message.id
                )
                return False
            
            # Check if file exists first
            file = await canvas_manager.get_file(filename, message.chat.id)
            if not file:
                available_files = await canvas_manager.list_files(message.chat.id)
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'❌ File `{filename}` tidak ditemukan.\n\nFile tersedia: {", ".join(available_files) if available_files else "Tidak ada"}',
                    reply_to_message_id=message.id
                )
                return False
            
            # Delete file
            success = await canvas_manager.delete_file(filename, message.chat.id)
            if success:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'🗑️ File `{filename}` berhasil dihapus!',
                    reply_to_message_id=message.id
                )
                return True
            else:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'❌ Gagal menghapus file `{filename}`',
                    reply_to_message_id=message.id
                )
                return False
                
        except Exception as e:
            console.error(f"Error in delete_file: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal menghapus file: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

    async def show_history(self, client, message, params):
        try:
            filename = params.strip()
            console.info(f"CANVAS:HISTORY called for file: {filename}")
            
            if not filename:
                await client.send_message(
                    chat_id=message.chat.id,
                    text='❌ Nama file tidak boleh kosong!\nContoh: [CANVAS:HISTORY:filename]',
                    reply_to_message_id=message.id
                )
                return False
            
            # Get file history
            history = await canvas_manager.get_file_history(filename, message.chat.id)
            
            if not history:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'📄 File `{filename}` tidak memiliki history atau tidak ditemukan.',
                    reply_to_message_id=message.id
                )
                return False
            
            # Format history
            response = f'📜 **History untuk file `{filename}`:**\n\n'
            for i, entry in enumerate(history[-5:], 1):  # Show last 5 entries
                timestamp = entry.get('timestamp', 'Unknown')
                content_preview = entry.get('content', '')[:100] + "..." if len(entry.get('content', '')) > 100 else entry.get('content', '')
                response += f'**{i}.** {timestamp}\n```\n{content_preview}\n```\n\n'
            
            if len(history) > 5:
                response += f'... dan {len(history) - 5} entry lainnya'
            
            await client.send_message(
                chat_id=message.chat.id,
                text=response,
                reply_to_message_id=message.id
            )
            return True
            
        except Exception as e:
            console.error(f"Error in show_history: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal menampilkan history: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

    async def clear_files(self, client, message, params):
        try:
            console.info("CANVAS:CLEAR called")
            
            # Get current file count
            files = await canvas_manager.list_files(message.chat.id)
            file_count = len(files)
            
            if file_count == 0:
                await client.send_message(
                    chat_id=message.chat.id,
                    text='📂 Tidak ada file virtual untuk dihapus.',
                    reply_to_message_id=message.id
                )
                return True
            
            # Clear all files
            await canvas_manager.clear_files(message.chat.id)
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f'🗑️ **{file_count} file virtual telah dihapus!**\n\n✨ Canvas sudah bersih!',
                reply_to_message_id=message.id
            )
            return True
            
        except Exception as e:
            console.error(f"Error in clear_files: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal menghapus semua file: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

# Create instance untuk diimpor oleh __init__.py
canvas_shortcode = CanvasManagementShortcode() 