from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio

class VirtualFile:
    def __init__(self, name, filetype="txt", content="", chat_id=None):
        self.name = name
        self.filetype = filetype
        # Process newline characters in content
        self.content = content.replace('\\n', '\n') if content else ""
        self.history = []
        self.auto_exported = False  # Track if file was auto-exported during creation
        self.chat_id = chat_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_content(self, new_content):
        self.history.append({
            "content": self.content,
            "timestamp": datetime.utcnow()
        })
        # Process newline characters in new content
        self.content = new_content.replace('\\n', '\n') if new_content else ""
        self.updated_at = datetime.utcnow()

    def append_content(self, addition):
        self.history.append({
            "content": self.content,
            "timestamp": datetime.utcnow()
        })
        # Process newline characters in addition
        processed_addition = addition.replace('\\n', '\n') if addition else ""
        self.content += processed_addition
        self.updated_at = datetime.utcnow()

    def get_content(self):
        return self.content

    def export(self):
        return self.content  # Bisa diubah ke format file sesuai filetype

    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            "filename": self.name,
            "filetype": self.filetype,
            "content": self.content,
            "chat_id": self.chat_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history": self.history,
            "auto_exported": self.auto_exported
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create VirtualFile from dictionary"""
        file = cls(
            name=data["filename"],
            filetype=data["filetype"],
            content=data["content"],
            chat_id=data.get("chat_id")
        )
        file.created_at = data.get("created_at", datetime.utcnow())
        file.updated_at = data.get("updated_at", datetime.utcnow())
        file.history = data.get("history", [])
        file.auto_exported = data.get("auto_exported", False)
        return file

class CanvasManager:
    def __init__(self):
        self.files = {}  # In-memory cache
        self._db_initialized = False

    async def _ensure_db_connection(self):
        """Ensure database connection is available"""
        if not self._db_initialized:
            try:
                from syncara.database import canvas_files, log_system_event
                self.canvas_files = canvas_files
                self.log_system_event = log_system_event
                self._db_initialized = True
            except ImportError:
                from syncara.console import console
                console.error("Database not available for canvas persistence")

    async def create_file(self, name, filetype="txt", content="", chat_id=None):
        """Create a virtual file with database persistence"""
        try:
            from syncara.console import console
            console.info(f"Creating file: {name} with type: {filetype}")
            
            # Process content to handle newlines
            processed_content = content.replace('\\n', '\n') if content else ""
            
            # Create virtual file
            virtual_file = VirtualFile(name, filetype, processed_content, chat_id)
            
            # Store in memory cache
            cache_key = f"{chat_id}:{name}" if chat_id else name
            self.files[cache_key] = virtual_file
            
            # Save to database
            await self._save_file_to_db(virtual_file)
            
            console.info(f"File created successfully: {name}")
            console.info(f"Current files in canvas: {list(self.files.keys())}")
            
            return virtual_file
            
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error creating file {name}: {str(e)}")
                await self._log_error("canvas_manager", f"Error creating file {name}", str(e))
            except:
                print(f"Error creating file {name}: {str(e)}")
            return None

    async def get_file(self, name, chat_id=None):
        """Get a virtual file from cache or database"""
        try:
            from syncara.console import console
            console.info(f"Getting file: {name}")
            
            cache_key = f"{chat_id}:{name}" if chat_id else name
            
            # Check memory cache first
            if cache_key in self.files:
                console.info(f"File {name} found in cache")
                return self.files[cache_key]
            
            # Load from database
            virtual_file = await self._load_file_from_db(name, chat_id)
            if virtual_file:
                # Cache in memory
                self.files[cache_key] = virtual_file
                console.info(f"File {name} loaded from database")
                return virtual_file
            
            console.warning(f"File {name} not found")
            return None
            
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error getting file {name}: {str(e)}")
                await self._log_error("canvas_manager", f"Error getting file {name}", str(e))
            except:
                print(f"Error getting file {name}: {str(e)}")
            return None

    async def list_files(self, chat_id=None):
        """List all virtual files for a chat"""
        try:
            from syncara.console import console
            
            # Get files from database
            files = await self._get_files_from_db(chat_id)
            
            console.info(f"Listing files for chat {chat_id}: {files}")
            return files
            
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error listing files: {str(e)}")
                await self._log_error("canvas_manager", "Error listing files", str(e))
            except:
                print(f"Error listing files: {str(e)}")
            return []

    async def delete_file(self, name, chat_id=None):
        """Delete a virtual file"""
        try:
            from syncara.console import console
            console.info(f"Deleting file: {name}")
            
            cache_key = f"{chat_id}:{name}" if chat_id else name
            
            # Remove from memory cache
            if cache_key in self.files:
                del self.files[cache_key]
            
            # Remove from database
            await self._delete_file_from_db(name, chat_id)
            
            console.info(f"File {name} deleted successfully")
            return True
            
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error deleting file {name}: {str(e)}")
                await self._log_error("canvas_manager", f"Error deleting file {name}", str(e))
            except:
                print(f"Error deleting file {name}: {str(e)}")
            return False

    async def update_file(self, name, new_content, chat_id=None):
        """Update a virtual file"""
        try:
            virtual_file = await self.get_file(name, chat_id)
            if virtual_file:
                virtual_file.update_content(new_content)
                await self._save_file_to_db(virtual_file)
                return virtual_file
            return None
            
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error updating file {name}: {str(e)}")
                await self._log_error("canvas_manager", f"Error updating file {name}", str(e))
            except:
                print(f"Error updating file {name}: {str(e)}")
            return None

    async def clear_files(self, chat_id=None):
        """Clear all files from canvas"""
        try:
            from syncara.console import console
            console.info(f"Clearing all files for chat {chat_id}")
            
            # Clear memory cache
            if chat_id:
                keys_to_remove = [k for k in self.files.keys() if k.startswith(f"{chat_id}:")]
                for key in keys_to_remove:
                    del self.files[key]
            else:
                self.files.clear()
            
            # Clear from database
            await self._clear_files_from_db(chat_id)
            
            console.info("Files cleared successfully")
            
        except Exception as e:
            try:
                from syncara.console import console
                console.error(f"Error clearing files: {str(e)}")
                await self._log_error("canvas_manager", "Error clearing files", str(e))
            except:
                print(f"Error clearing files: {str(e)}")

    async def get_file_history(self, name, chat_id=None):
        """Get file history from database"""
        try:
            await self._ensure_db_connection()
            
            query = {"filename": name}
            if chat_id:
                query["chat_id"] = chat_id
            
            file_data = await self.canvas_files.find_one(query)
            if file_data:
                return file_data.get("history", [])
            return []
            
        except Exception as e:
            return []

    # ==================== DATABASE OPERATIONS ====================
    
    async def _save_file_to_db(self, virtual_file: VirtualFile):
        """Save virtual file to database"""
        try:
            await self._ensure_db_connection()
            
            await self.canvas_files.update_one(
                {
                    "filename": virtual_file.name,
                    "chat_id": virtual_file.chat_id
                },
                {"$set": virtual_file.to_dict()},
                upsert=True
            )
            
            await self.log_system_event("info", "canvas_manager", f"File saved: {virtual_file.name}")
            
        except Exception as e:
            await self._log_error("canvas_manager", f"Error saving file to DB: {virtual_file.name}", str(e))

    async def _load_file_from_db(self, name: str, chat_id: int = None) -> Optional[VirtualFile]:
        """Load virtual file from database"""
        try:
            await self._ensure_db_connection()
            
            query = {"filename": name}
            if chat_id:
                query["chat_id"] = chat_id
            
            file_data = await self.canvas_files.find_one(query)
            if file_data:
                return VirtualFile.from_dict(file_data)
            return None
            
        except Exception as e:
            await self._log_error("canvas_manager", f"Error loading file from DB: {name}", str(e))
            return None

    async def _get_files_from_db(self, chat_id: int = None) -> List[str]:
        """Get list of files from database"""
        try:
            await self._ensure_db_connection()
            
            query = {}
            if chat_id:
                query["chat_id"] = chat_id
            
            files = await self.canvas_files.find(query, {"filename": 1}).to_list(length=None)
            return [file["filename"] for file in files]
            
        except Exception as e:
            await self._log_error("canvas_manager", "Error getting files from DB", str(e))
            return []

    async def _delete_file_from_db(self, name: str, chat_id: int = None):
        """Delete virtual file from database"""
        try:
            await self._ensure_db_connection()
            
            query = {"filename": name}
            if chat_id:
                query["chat_id"] = chat_id
            
            await self.canvas_files.delete_one(query)
            await self.log_system_event("info", "canvas_manager", f"File deleted: {name}")
            
        except Exception as e:
            await self._log_error("canvas_manager", f"Error deleting file from DB: {name}", str(e))

    async def _clear_files_from_db(self, chat_id: int = None):
        """Clear files from database"""
        try:
            await self._ensure_db_connection()
            
            query = {}
            if chat_id:
                query["chat_id"] = chat_id
            
            result = await self.canvas_files.delete_many(query)
            await self.log_system_event("info", "canvas_manager", f"Cleared {result.deleted_count} files")
            
        except Exception as e:
            await self._log_error("canvas_manager", "Error clearing files from DB", str(e))

    async def _log_error(self, module: str, message: str, error: str):
        """Log error to database"""
        try:
            from syncara.database import log_error
            await log_error(module, message, error)
        except:
            pass

# Create singleton instance
canvas_manager = CanvasManager() 