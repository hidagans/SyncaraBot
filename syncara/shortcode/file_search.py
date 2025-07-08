# syncara/shortcode/file_search.py
from syncara.console import console
import os
import asyncio
import re
from pathlib import Path

class FileSearchShortcode:
    def __init__(self):
        self.handlers = {
            'SEARCH:FILE': self.search_files,
            'FILE:SEARCH': self.search_files,
            'FIND:FILE': self.search_files,
            'SEARCH:CHAT': self.search_chat_history,
            'CHAT:SEARCH': self.search_chat_history,
        }
        
        self.descriptions = {
            'SEARCH:FILE': 'Search files in workspace. Usage: [SEARCH:FILE:filename or pattern]',
            'FILE:SEARCH': 'Search files in workspace. Usage: [FILE:SEARCH:*.py]',
            'FIND:FILE': 'Find files in workspace. Usage: [FIND:FILE:config]',
            'SEARCH:CHAT': 'Search chat history. Usage: [SEARCH:CHAT:keyword]',
            'CHAT:SEARCH': 'Search chat history. Usage: [CHAT:SEARCH:message content]',
        }
        
        self.pending_results = {}
        
        # Workspace base path
        self.workspace_path = Path.cwd()
        
        # Excluded directories for security
        self.excluded_dirs = {
            '.git', '__pycache__', '.venv', 'venv', 'node_modules', 
            '.pytest_cache', '.coverage', 'dist', 'build', '.tox'
        }
        
        # Common file extensions to search
        self.searchable_extensions = {
            '.py', '.txt', '.md', '.json', '.yaml', '.yml', '.ini', 
            '.cfg', '.conf', '.log', '.csv', '.xml', '.html', '.js', '.ts'
        }

    async def search_files(self, client, message, params):
        """Search for files in workspace"""
        try:
            query = params.strip()
            if not query:
                console.error("[SEARCH:FILE] Empty search query")
                return False
            
            console.info(f"[SEARCH:FILE] Searching files for: {query}")
            
            # Perform file search
            search_results = await self._search_files_in_workspace(query)
            
            # Store result for delayed sending
            result_id = f"file_search_{message.id}"
            
            if search_results['files']:
                result_text = f"📁 **File Search Results**\n\n"
                result_text += f"**Query:** `{query}`\n"
                result_text += f"**Found:** {len(search_results['files'])} files\n\n"
                
                for i, file_info in enumerate(search_results['files'][:20], 1):  # Limit to 20 results
                    relative_path = file_info['path']
                    size = file_info['size']
                    result_text += f"{i}. `{relative_path}` ({size})\n"
                
                if len(search_results['files']) > 20:
                    result_text += f"\n... and {len(search_results['files']) - 20} more files"
                
                result_text += f"\n\n**Search time:** {search_results['duration']:.2f}s"
                
            else:
                result_text = f"📁 **File Search Results**\n\n"
                result_text += f"**Query:** `{query}`\n"
                result_text += f"❌ No files found matching pattern\n\n"
                result_text += f"**Search time:** {search_results['duration']:.2f}s"
            
            self.pending_results[result_id] = {
                'text': result_text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[SEARCH:FILE] Search completed: {result_id}")
            return result_id
            
        except Exception as e:
            console.error(f"[SEARCH:FILE] Error: {e}")
            return False

    async def search_chat_history(self, client, message, params):
        """Search chat history for keywords"""
        try:
            query = params.strip()
            if not query:
                console.error("[SEARCH:CHAT] Empty search query")
                return False
            
            console.info(f"[SEARCH:CHAT] Searching chat history for: {query}")
            
            # Get chat history
            chat_results = await self._search_chat_messages(client, message, query)
            
            # Store result for delayed sending
            result_id = f"chat_search_{message.id}"
            
            if chat_results['messages']:
                result_text = f"💬 **Chat Search Results**\n\n"
                result_text += f"**Query:** `{query}`\n"
                result_text += f"**Found:** {len(chat_results['messages'])} messages\n\n"
                
                for i, msg_info in enumerate(chat_results['messages'][:10], 1):  # Limit to 10 results
                    user = msg_info['user']
                    text = msg_info['text'][:100] + "..." if len(msg_info['text']) > 100 else msg_info['text']
                    date = msg_info['date']
                    result_text += f"{i}. **{user}** ({date}):\n   `{text}`\n\n"
                
                if len(chat_results['messages']) > 10:
                    result_text += f"... and {len(chat_results['messages']) - 10} more messages"
                
            else:
                result_text = f"💬 **Chat Search Results**\n\n"
                result_text += f"**Query:** `{query}`\n"
                result_text += f"❌ No messages found containing keyword\n\n"
                result_text += "Try different keywords or check spelling"
            
            self.pending_results[result_id] = {
                'text': result_text,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[SEARCH:CHAT] Chat search completed: {result_id}")
            return result_id
            
        except Exception as e:
            console.error(f"[SEARCH:CHAT] Error: {e}")
            return False

    async def _search_files_in_workspace(self, query):
        """Search for files matching the query"""
        import time
        start_time = time.time()
        
        found_files = []
        
        try:
            # Convert query to regex pattern
            if '*' in query or '?' in query:
                # Wildcard pattern
                pattern = query.replace('*', '.*').replace('?', '.')
                regex = re.compile(pattern, re.IGNORECASE)
                use_regex = True
            else:
                # Simple substring search
                use_regex = False
            
            # Walk through workspace
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.workspace_path)
                    
                    # Check if file matches search criteria
                    match = False
                    if use_regex:
                        match = regex.search(str(relative_path))
                    else:
                        match = query.lower() in str(relative_path).lower()
                    
                    if match:
                        try:
                            size = file_path.stat().st_size
                            size_str = self._format_file_size(size)
                            
                            found_files.append({
                                'path': str(relative_path),
                                'size': size_str,
                                'size_bytes': size
                            })
                        except Exception:
                            pass  # Skip files that can't be accessed
            
            # Sort by size (smaller first)
            found_files.sort(key=lambda x: x['size_bytes'])
            
            duration = time.time() - start_time
            
            return {
                'files': found_files,
                'duration': duration
            }
            
        except Exception as e:
            console.error(f"Error searching files: {e}")
            return {'files': [], 'duration': time.time() - start_time}

    async def _search_chat_messages(self, client, message, query):
        """Search chat messages for keywords"""
        found_messages = []
        
        try:
            # Get recent chat history
            from syncara.modules.ai_handler import get_chat_history
            
            chat_history = await get_chat_history(client, message.chat.id, limit=500)
            
            query_lower = query.lower()
            
            for msg in chat_history:
                if msg.text and query_lower in msg.text.lower():
                    user_name = "Unknown"
                    if msg.from_user:
                        if msg.from_user.first_name:
                            user_name = msg.from_user.first_name
                        if msg.from_user.username:
                            user_name = f"@{msg.from_user.username}"
                    
                    # Format date
                    date_str = msg.date.strftime("%m/%d %H:%M") if msg.date else "Unknown"
                    
                    found_messages.append({
                        'user': user_name,
                        'text': msg.text,
                        'date': date_str,
                        'message_id': msg.id
                    })
            
            # Sort by most recent first
            found_messages.reverse()
            
            return {
                'messages': found_messages
            }
            
        except Exception as e:
            console.error(f"Error searching chat messages: {e}")
            return {'messages': []}

    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f}MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f}GB"

    async def send_pending_results(self, client, result_ids):
        """Send pending search results"""
        sent_results = []
        
        for result_id in result_ids:
            if result_id in self.pending_results:
                result_data = self.pending_results[result_id]
                
                try:
                    await client.send_message(
                        chat_id=result_data['chat_id'],
                        text=result_data['text'],
                        reply_to_message_id=result_data['reply_to_message_id']
                    )
                    sent_results.append(result_id)
                    console.info(f"[FILE:SEARCH] Sent result: {result_id}")
                    
                except Exception as e:
                    console.error(f"[FILE:SEARCH] Error sending result {result_id}: {e}")
                    
                # Clean up
                del self.pending_results[result_id]
                
        return sent_results 