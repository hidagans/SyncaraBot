import asyncio
from datetime import datetime
from bson import ObjectId
from syncara.console import console
from syncara.database import db

class TodoManagementShortcode:
    def __init__(self):
        self.pending_responses = {}
        
        self.handlers = {
            'TODO:CREATE': self.create_todo,
            'TODO:ADD': self.create_todo,
            'TODO:NEW': self.create_todo,
            'TODO:LIST': self.list_todos,
            'TODO:SHOW': self.list_todos,
            'TODO:VIEW': self.list_todos,
            'TODO:COMPLETE': self.complete_todo,
            'TODO:DONE': self.complete_todo,
            'TODO:FINISH': self.complete_todo,
            'TODO:DELETE': self.delete_todo,
            'TODO:REMOVE': self.delete_todo,
            'TODO:UPDATE': self.update_todo,
            'TODO:EDIT': self.update_todo,
            'TODO:CLEAR': self.clear_completed,
            'TODO:CLEANUP': self.clear_completed,
            'TODO:STATS': self.get_stats,
            'TODO:STATUS': self.get_stats
        }
        
        self.descriptions = {
            'TODO:CREATE': 'Create a new todo item. Usage: [TODO:CREATE:task_description]',
            'TODO:ADD': 'Add a new todo item. Usage: [TODO:ADD:task_description]',
            'TODO:NEW': 'Create a new todo item. Usage: [TODO:NEW:task_description]',
            'TODO:LIST': 'List all todos. Usage: [TODO:LIST:] or [TODO:LIST:status] (pending/completed/all)',
            'TODO:SHOW': 'Show all todos. Usage: [TODO:SHOW:] or [TODO:SHOW:status]',
            'TODO:VIEW': 'View all todos. Usage: [TODO:VIEW:] or [TODO:VIEW:status]',
            'TODO:COMPLETE': 'Mark todo as completed. Usage: [TODO:COMPLETE:todo_id] or [TODO:COMPLETE:task_number]',
            'TODO:DONE': 'Mark todo as done. Usage: [TODO:DONE:todo_id] or [TODO:DONE:task_number]',
            'TODO:FINISH': 'Mark todo as finished. Usage: [TODO:FINISH:todo_id] or [TODO:FINISH:task_number]',
            'TODO:DELETE': 'Delete a todo. Usage: [TODO:DELETE:todo_id] or [TODO:DELETE:task_number]',
            'TODO:REMOVE': 'Remove a todo. Usage: [TODO:REMOVE:todo_id] or [TODO:REMOVE:task_number]',
            'TODO:UPDATE': 'Update todo description. Usage: [TODO:UPDATE:todo_id:new_description]',
            'TODO:EDIT': 'Edit todo description. Usage: [TODO:EDIT:todo_id:new_description]',
            'TODO:CLEAR': 'Clear all completed todos. Usage: [TODO:CLEAR:]',
            'TODO:CLEANUP': 'Clean up completed todos. Usage: [TODO:CLEANUP:]',
            'TODO:STATS': 'Show todo statistics. Usage: [TODO:STATS:]',
            'TODO:STATUS': 'Show todo status summary. Usage: [TODO:STATUS:]'
        }
        
        console.info("Todo Management Shortcode initialized")
    
    async def get_todos_collection(self, chat_id):
        """Get MongoDB collection for todos"""
        try:
            collection_name = f"todos_{chat_id}"
            return db[collection_name]
        except Exception as e:
            console.error(f"Error getting todos collection: {str(e)}")
            return None
    
    async def create_todo(self, client, message, params):
        """Create a new todo item"""
        try:
            if not params or not params.strip():
                response_id = f"todo_create_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Deskripsi todo tidak boleh kosong!\nContoh: [TODO:CREATE:Belajar Python]",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            collection = await self.get_todos_collection(message.chat.id)
            if collection is None:
                response_id = f"todo_create_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Database tidak tersedia",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Create todo document
            todo_doc = {
                'description': params.strip(),
                'status': 'pending',
                'created_at': datetime.now(),
                'created_by': message.from_user.id,
                'chat_id': message.chat.id,
                'completed_at': None
            }
            
            result = await collection.insert_one(todo_doc)
            todo_id = str(result.inserted_id)
            
            # Get todo number (position in list)
            todo_count = await collection.count_documents({'status': 'pending'})
            
            response_id = f"todo_create_success_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Todo #{todo_count} dibuat!**\n📝 {params.strip()}\n🆔 ID: `{todo_id}`",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"Created todo: {params.strip()} (ID: {todo_id})")
            return response_id
            
        except Exception as e:
            console.error(f"[TODO:CREATE] Error: {str(e)}")
            response_id = f"todo_create_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal membuat todo: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def list_todos(self, client, message, params):
        """List all todos or filter by status"""
        try:
            collection = await self.get_todos_collection(message.chat.id)
            if collection is None:
                response_id = f"todo_list_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Database tidak tersedia",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Determine filter
            filter_status = params.strip().lower() if params.strip() else 'all'
            
            if filter_status == 'pending':
                query = {'status': 'pending', 'chat_id': message.chat.id}
            elif filter_status == 'completed':
                query = {'status': 'completed', 'chat_id': message.chat.id}
            else:
                query = {'chat_id': message.chat.id}
            
            # Get todos
            todos = await collection.find(query).sort('created_at', 1).to_list(length=None)
            
            if not todos:
                status_text = {
                    'pending': 'pending',
                    'completed': 'completed', 
                    'all': ''
                }.get(filter_status, '')
                
                response_id = f"todo_list_empty_{message.id}"
                self.pending_responses[response_id] = {
                    'text': f"📝 **Tidak ada todo {status_text}**\n\nGunakan [TODO:CREATE:deskripsi] untuk membuat todo baru!",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Format todo list
            response_text = f"📝 **Daftar Todo ({filter_status.title()})**\n\n"
            
            pending_todos = [t for t in todos if t['status'] == 'pending']
            completed_todos = [t for t in todos if t['status'] == 'completed']
            
            if filter_status in ['pending', 'all'] and pending_todos:
                response_text += "🔄 **Pending:**\n"
                for i, todo in enumerate(pending_todos, 1):
                    created_time = todo['created_at'].strftime('%d/%m %H:%M')
                    response_text += f"{i}. {todo['description']}\n"
                    response_text += f"   📅 {created_time} | 🆔 `{str(todo['_id'])}`\n\n"
            
            if filter_status in ['completed', 'all'] and completed_todos:
                response_text += "✅ **Completed:**\n"
                for i, todo in enumerate(completed_todos, 1):
                    completed_time = todo['completed_at'].strftime('%d/%m %H:%M') if todo['completed_at'] else 'N/A'
                    response_text += f"{i}. ~~{todo['description']}~~\n"
                    response_text += f"   ✅ {completed_time} | 🆔 `{str(todo['_id'])}`\n\n"
            
            # Add statistics
            total_pending = len(pending_todos)
            total_completed = len(completed_todos)
            response_text += f"📊 **Total: {total_pending + total_completed}** (Pending: {total_pending}, Completed: {total_completed})"
            
            response_id = f"todo_list_success_{message.id}"
            self.pending_responses[response_id] = {
                'text': response_text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"Listed todos: {len(todos)} items")
            return response_id
            
        except Exception as e:
            console.error(f"[TODO:LIST] Error: {str(e)}")
            response_id = f"todo_list_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal mengambil todo list: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def complete_todo(self, client, message, params):
        """Mark todo as completed"""
        try:
            if not params or not params.strip():
                response_id = f"todo_complete_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ ID todo tidak boleh kosong!\nContoh: [TODO:COMPLETE:todo_id] atau [TODO:COMPLETE:1]",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            collection = await self.get_todos_collection(message.chat.id)
            if collection is None:
                response_id = f"todo_complete_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Database tidak tersedia",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            todo_identifier = params.strip()
            
            # Try to find todo by ObjectId or by number
            todo = None
            
            # First try as ObjectId
            if len(todo_identifier) == 24:
                try:
                    todo = await collection.find_one({
                        '_id': ObjectId(todo_identifier),
                        'chat_id': message.chat.id
                    })
                except:
                    pass
            
            # If not found, try as number
            if not todo:
                try:
                    todo_number = int(todo_identifier)
                    pending_todos = await collection.find({
                        'status': 'pending',
                        'chat_id': message.chat.id
                    }).sort('created_at', 1).to_list(length=None)
                    
                    if 1 <= todo_number <= len(pending_todos):
                        todo = pending_todos[todo_number - 1]
                except ValueError:
                    pass
            
            if not todo:
                response_id = f"todo_complete_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': f"❌ Todo dengan ID '{todo_identifier}' tidak ditemukan",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            if todo['status'] == 'completed':
                response_id = f"todo_complete_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': f"✅ Todo '{todo['description']}' sudah completed sebelumnya",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Update todo status
            await collection.update_one(
                {'_id': todo['_id']},
                {
                    '$set': {
                        'status': 'completed',
                        'completed_at': datetime.now(),
                        'completed_by': message.from_user.id
                    }
                }
            )
            
            response_id = f"todo_complete_success_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ **Todo completed!**\n~~{todo['description']}~~\n\n🎉 Great job!",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"Completed todo: {todo['description']} (ID: {str(todo['_id'])})")
            return response_id
            
        except Exception as e:
            console.error(f"[TODO:COMPLETE] Error: {str(e)}")
            response_id = f"todo_complete_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal menyelesaikan todo: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def delete_todo(self, client, message, params):
        """Delete a todo"""
        try:
            if not params or not params.strip():
                response_id = f"todo_delete_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ ID todo tidak boleh kosong!\nContoh: [TODO:DELETE:todo_id] atau [TODO:DELETE:1]",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            collection = await self.get_todos_collection(message.chat.id)
            if collection is None:
                response_id = f"todo_delete_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Database tidak tersedia",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            todo_identifier = params.strip()
            
            # Try to find todo by ObjectId or by number
            todo = None
            
            # First try as ObjectId
            if len(todo_identifier) == 24:
                try:
                    todo = await collection.find_one({
                        '_id': ObjectId(todo_identifier),
                        'chat_id': message.chat.id
                    })
                except:
                    pass
            
            # If not found, try as number
            if not todo:
                try:
                    todo_number = int(todo_identifier)
                    all_todos = await collection.find({
                        'chat_id': message.chat.id
                    }).sort('created_at', 1).to_list(length=None)
                    
                    if 1 <= todo_number <= len(all_todos):
                        todo = all_todos[todo_number - 1]
                except ValueError:
                    pass
            
            if not todo:
                response_id = f"todo_delete_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': f"❌ Todo dengan ID '{todo_identifier}' tidak ditemukan",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Delete todo
            await collection.delete_one({'_id': todo['_id']})
            
            response_id = f"todo_delete_success_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"🗑️ **Todo dihapus!**\n~~{todo['description']}~~",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"Deleted todo: {todo['description']} (ID: {str(todo['_id'])})")
            return response_id
            
        except Exception as e:
            console.error(f"[TODO:DELETE] Error: {str(e)}")
            response_id = f"todo_delete_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal menghapus todo: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def update_todo(self, client, message, params):
        """Update todo description"""
        try:
            if not params or ':' not in params:
                response_id = f"todo_update_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Format salah!\nContoh: [TODO:UPDATE:todo_id:deskripsi_baru]",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Parse parameters
            parts = params.split(':', 1)
            if len(parts) != 2:
                response_id = f"todo_update_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Format salah!\nContoh: [TODO:UPDATE:todo_id:deskripsi_baru]",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            todo_identifier = parts[0].strip()
            new_description = parts[1].strip()
            
            if not new_description:
                response_id = f"todo_update_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Deskripsi baru tidak boleh kosong!",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            collection = await self.get_todos_collection(message.chat.id)
            if collection is None:
                response_id = f"todo_update_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Database tidak tersedia",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Find todo
            todo = None
            
            # First try as ObjectId
            if len(todo_identifier) == 24:
                try:
                    todo = await collection.find_one({
                        '_id': ObjectId(todo_identifier),
                        'chat_id': message.chat.id
                    })
                except:
                    pass
            
            # If not found, try as number
            if not todo:
                try:
                    todo_number = int(todo_identifier)
                    all_todos = await collection.find({
                        'chat_id': message.chat.id
                    }).sort('created_at', 1).to_list(length=None)
                    
                    if 1 <= todo_number <= len(all_todos):
                        todo = all_todos[todo_number - 1]
                except ValueError:
                    pass
            
            if not todo:
                response_id = f"todo_update_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': f"❌ Todo dengan ID '{todo_identifier}' tidak ditemukan",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            old_description = todo['description']
            
            # Update todo
            await collection.update_one(
                {'_id': todo['_id']},
                {
                    '$set': {
                        'description': new_description,
                        'updated_at': datetime.now(),
                        'updated_by': message.from_user.id
                    }
                }
            )
            
            response_id = f"todo_update_success_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✏️ **Todo diupdate!**\n\n**Sebelum:** {old_description}\n**Sesudah:** {new_description}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"Updated todo: {old_description} -> {new_description}")
            return response_id
            
        except Exception as e:
            console.error(f"[TODO:UPDATE] Error: {str(e)}")
            response_id = f"todo_update_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal mengupdate todo: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def clear_completed(self, client, message, params):
        """Clear all completed todos"""
        try:
            collection = await self.get_todos_collection(message.chat.id)
            if collection is None:
                response_id = f"todo_clear_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Database tidak tersedia",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Count completed todos
            completed_count = await collection.count_documents({
                'status': 'completed',
                'chat_id': message.chat.id
            })
            
            if completed_count == 0:
                response_id = f"todo_clear_empty_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "📝 Tidak ada todo completed untuk dihapus",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Delete all completed todos
            await collection.delete_many({
                'status': 'completed',
                'chat_id': message.chat.id
            })
            
            response_id = f"todo_clear_success_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"🗑️ **{completed_count} completed todo dihapus!**\n\n✨ Todo list sudah bersih!",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"Cleared {completed_count} completed todos")
            return response_id
            
        except Exception as e:
            console.error(f"[TODO:CLEAR] Error: {str(e)}")
            response_id = f"todo_clear_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal menghapus completed todos: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def get_stats(self, client, message, params):
        """Get todo statistics"""
        try:
            collection = await self.get_todos_collection(message.chat.id)
            if collection is None:
                response_id = f"todo_stats_error_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "❌ Database tidak tersedia",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Get statistics
            total_count = await collection.count_documents({'chat_id': message.chat.id})
            pending_count = await collection.count_documents({'status': 'pending', 'chat_id': message.chat.id})
            completed_count = await collection.count_documents({'status': 'completed', 'chat_id': message.chat.id})
            
            if total_count == 0:
                response_id = f"todo_stats_empty_{message.id}"
                self.pending_responses[response_id] = {
                    'text': "📊 **Todo Statistics**\n\n📝 Belum ada todo yang dibuat\n\nGunakan [TODO:CREATE:deskripsi] untuk membuat todo pertama!",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                return response_id
            
            # Calculate completion percentage
            completion_percentage = (completed_count / total_count) * 100 if total_count > 0 else 0
            
            # Get recent activity
            recent_todos = await collection.find({
                'chat_id': message.chat.id
            }).sort('created_at', -1).limit(3).to_list(length=None)
            
            response_text = f"📊 **Todo Statistics**\n\n"
            response_text += f"📝 **Total:** {total_count}\n"
            response_text += f"🔄 **Pending:** {pending_count}\n"
            response_text += f"✅ **Completed:** {completed_count}\n"
            response_text += f"📈 **Completion Rate:** {completion_percentage:.1f}%\n\n"
            
            if recent_todos:
                response_text += "🕒 **Recent Activity:**\n"
                for todo in recent_todos:
                    status_icon = "✅" if todo['status'] == 'completed' else "🔄"
                    created_time = todo['created_at'].strftime('%d/%m %H:%M')
                    response_text += f"{status_icon} {todo['description'][:50]}{'...' if len(todo['description']) > 50 else ''}\n"
                    response_text += f"   📅 {created_time}\n"
            
            response_id = f"todo_stats_success_{message.id}"
            self.pending_responses[response_id] = {
                'text': response_text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"Generated todo stats: {total_count} total, {pending_count} pending, {completed_count} completed")
            return response_id
            
        except Exception as e:
            console.error(f"[TODO:STATS] Error: {str(e)}")
            response_id = f"todo_stats_error_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"❌ Gagal mengambil statistik: {str(e)}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            return response_id
    
    async def send_pending_results(self, client, pending_results):
        """Send pending TODO results with delay"""
        if not pending_results:
            return
            
        try:
            await asyncio.sleep(1)  # Delay to ensure AI response is sent first
            
            for result_id in pending_results:
                if result_id in self.pending_responses:
                    response_data = self.pending_responses[result_id]
                    
                    await client.send_message(
                        chat_id=response_data['chat_id'],
                        text=response_data['text'],
                        reply_to_message_id=response_data.get('reply_to_message_id'),
                        parse_mode='markdown'
                    )
                    
                    # Remove from pending
                    del self.pending_responses[result_id]
                    console.info(f"Sent delayed TODO result: {result_id}")
                    
        except Exception as e:
            console.error(f"Error sending pending TODO results: {str(e)}")

# Create instance untuk diimpor oleh __init__.py
todo_shortcode = TodoManagementShortcode() 