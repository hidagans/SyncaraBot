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
            console.info(f"CANVAS:CREATE called with params: {params}")
            
            parts = params.split(':', 2)
            if len(parts) < 2:
                error_msg = 'Format: [CANVAS:CREATE:filename:type:isi]'
                console.error(f"Invalid format: {error_msg}")
                await client.send_message(
                    chat_id=message.chat.id,
                    text=error_msg,
                    reply_to_message_id=message.id
                )
                return False
                
            filename = parts[0].strip()
            filetype = parts[1].strip() if len(parts) > 1 else 'txt'
            content = parts[2].strip() if len(parts) > 2 else ''
            
            console.info(f"Creating file: {filename} with type: {filetype}")
            console.info(f"Content length: {len(content)}")
            
            # Create file in canvas manager
            file = canvas_manager.create_file(filename, filetype, content)
            
            if not file:
                error_msg = f'❌ Gagal membuat file: {filename}'
                console.error(error_msg)
                await client.send_message(
                    chat_id=message.chat.id,
                    text=error_msg,
                    reply_to_message_id=message.id
                )
                return False
            
            # Verify file was created
            verification = canvas_manager.get_file(filename)
            if not verification:
                error_msg = f'❌ File {filename} tidak dapat diverifikasi setelah dibuat'
                console.error(error_msg)
                await client.send_message(
                    chat_id=message.chat.id,
                    text=error_msg,
                    reply_to_message_id=message.id
                )
                return False
                
            console.info(f"File {filename} created and verified successfully")
            
            # Send file as document
            try:
                file_content = file.get_content()
                file_bytes = BytesIO(file_content.encode('utf-8'))
                file_bytes.name = filename
                
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_bytes,
                    caption=f'✅ File `{filename}` berhasil dibuat!\n\nPreview content: {file_content[:100]}{"..." if len(file_content) > 100 else ""}',
                    reply_to_message_id=message.id
                )
                
                console.info(f"File {filename} document sent successfully")
                return True
                
            except Exception as doc_error:
                console.error(f"Error sending document: {str(doc_error)}")
                # Fallback to text message
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'✅ File `{filename}` berhasil dibuat!\n\nContent:\n{file.get_content()[:500]}{"..." if len(file.get_content()) > 500 else ""}',
                    reply_to_message_id=message.id
                )
                return True
                
        except Exception as e:
            console.error(f"Error in create_file: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal membuat file: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

    async def show_file(self, client, message, params):
        try:
            filename = params.strip()
            console.info(f"CANVAS:SHOW called for file: {filename}")
            
            file = canvas_manager.get_file(filename)
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
                available_files = canvas_manager.list_files()
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
            
            file = canvas_manager.get_file(filename)
            if file:
                console.info(f"File {filename} found, updating content")
                file.update_content(new_content)
                
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
                available_files = canvas_manager.list_files()
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
            
            files = canvas_manager.list_files()
            console.info(f"Found {len(files)} files")
            
            if files:
                response = '📂 Daftar file virtual:\n'
                for file_name in files:
                    file_obj = canvas_manager.get_file(file_name)
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
            
            file = canvas_manager.get_file(filename)
            if file:
                console.info(f"File {filename} found, exporting...")
                
                try:
                    file_content = file.export()
                    file_bytes = BytesIO(file_content.encode('utf-8'))
                    file_bytes.name = filename
                    
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=file_bytes,
                        caption=f'📤 Export file `{filename}`\n\nSize: {len(file_content)} characters',
                        reply_to_message_id=message.id
                    )
                    
                    console.info(f"Successfully exported file: {filename}")
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
                available_files = canvas_manager.list_files()
                console.info(f"Available files: {available_files}")
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f'❌ File `{filename}` tidak ditemukan.\n\nFile tersedia: {", ".join(available_files) if available_files else "Tidak ada"}',
                    reply_to_message_id=message.id
                )
                return False
                
        except Exception as e:
            console.error(f"Error in export_file: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal export file: {str(e)}',
                reply_to_message_id=message.id
            )
            return False 