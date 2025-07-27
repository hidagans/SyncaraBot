# syncara/shortcode/__init__.py
import os
import importlib
import inspect
from typing import Dict, Callable
from config.config import OWNER_ID

# Import trigger function
async def _trigger_user_save(client, message):
    """Universal trigger untuk save user data di semua shortcode"""
    try:
        if message and message.from_user:
            from syncara.modules.assistant_memory import kenalan_dan_update
            await kenalan_dan_update(client, message.from_user, send_greeting=False)
    except Exception as e:
        # Jangan biarkan error trigger mengganggu shortcode execution
        from syncara.console import console
        console.error(f"Error in user save trigger: {e}")

class ShortcodeRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.shortcodes = {}
            cls._instance.descriptions = {}
            cls._instance._initialized = False
        return cls._instance

    def _load_shortcodes(self):
        """Load all shortcode handlers from files in the shortcode directory"""
        if self._initialized:
            return
            
        try:
            # Import all shortcode handlers
            from .canvas_management import canvas_shortcode
            from .file_search import file_search_shortcode
            from .group_management import group_shortcode
            from .image_generation import image_shortcode
            from .python_execution import python_shortcode
            from .todo_management import todo_shortcode
            from .users_management import users_shortcode
            from .userbot_management import userbot_shortcode
            from .pyrogram_manager import pyrogram_manager
            from .multi_step_management import multi_step_shortcode
            from .channel_management import channel_shortcode
            
            # Register all shortcodes
            self.shortcodes.update(canvas_shortcode.handlers)
            self.shortcodes.update(file_search_shortcode.handlers)
            self.shortcodes.update(group_shortcode.handlers)
            self.shortcodes.update(image_shortcode.handlers)
            self.shortcodes.update(python_shortcode.handlers)
            self.shortcodes.update(todo_shortcode.handlers)
            self.shortcodes.update(users_shortcode.handlers)
            self.shortcodes.update(userbot_shortcode.handlers)
            self.shortcodes.update(pyrogram_manager.handlers)
            self.shortcodes.update(multi_step_shortcode.handlers)
            self.shortcodes.update(channel_shortcode.handlers)
            
            # Register descriptions
            all_shortcode_handlers = [
                canvas_shortcode, file_search_shortcode, group_shortcode,
                image_shortcode, python_shortcode, todo_shortcode,
                users_shortcode, userbot_shortcode, pyrogram_manager,
                multi_step_shortcode, channel_shortcode
            ]
            
            for handler in all_shortcode_handlers:
                if hasattr(handler, 'descriptions'):
                    self.descriptions.update(handler.descriptions)
                    
            # Add fallback descriptions for any missing ones
            for key in self.shortcodes.keys():
                if key not in self.descriptions:
                    if key.startswith('OWNER:'):
                        self.descriptions[key] = 'Owner-only command'
                    else:
                        self.descriptions[key] = 'Shortcode command'
            
            # Add dummy handlers for any patterns that might be expected
            dummy_patterns = [
                'USERBOT:STATUS', 'USERBOT:INFO', 'USERBOT:JOIN', 'USERBOT:LEAVE', 'USERBOT:SEND',
                'USER:BAN', 'USER:UNBAN', 'USER:KICK', 'USER:MUTE', 'USER:UNMUTE',
                'TODO:CREATE', 'TODO:LIST', 'TODO:COMPLETE', 'TODO:DELETE',
                'CANVAS:CREATE', 'CANVAS:LIST', 'CANVAS:READ', 'CANVAS:UPDATE',
                'IMAGE:GENERATE', 'IMAGE:HISTORY', 'IMAGE:STATS',
                'GROUP:INFO', 'GROUP:MEMBERS', 'GROUP:STATS',
                'PYTHON:EXEC', 'PYTHON:EVAL'
            ]
            
            for pattern in dummy_patterns:
                if pattern not in self.shortcodes:
                    self.shortcodes[pattern] = self._dummy_handler
                    if pattern not in self.descriptions:
                        self.descriptions[pattern] = f'Handler for {pattern.lower().replace(":", " ")}'
            
            self._initialized = True
            
        except Exception as e:
            print(f"Error loading shortcodes: {e}")

    async def _dummy_handler(self, client, message, params):
        """Dummy handler untuk shortcode yang belum diimplementasi"""
        return "⚠️ Shortcode handler belum diimplementasi"

    async def execute_shortcode(self, shortcode_pattern, client, message, params=""):
        """Execute a shortcode with universal user trigger"""
        try:
            # 🚀 UNIVERSAL TRIGGER: Save user data untuk SEMUA shortcode executions
            await _trigger_user_save(client, message)
            
            # Load shortcodes if not already loaded
            if not self._initialized:
                self._load_shortcodes()
            
            # Find matching shortcode handler
            handler = None
            matched_pattern = None
            
            # Exact match first
            if shortcode_pattern in self.shortcodes:
                handler = self.shortcodes[shortcode_pattern]
                matched_pattern = shortcode_pattern
            else:
                # Try pattern matching
                for pattern, func in self.shortcodes.items():
                    if shortcode_pattern.startswith(pattern.split(':')[0]):
                        handler = func
                        matched_pattern = pattern
                        break
            
            if handler:
                try:
                    # Execute the shortcode handler
                    result = await handler(client, message, params)
                    return result if result is not None else "✅ Shortcode executed successfully"
                except Exception as e:
                    error_msg = f"❌ Error executing {matched_pattern}: {str(e)}"
                    # Log error untuk debugging
                    try:
                        from syncara.console import console
                        console.error(f"Shortcode execution error: {e}")
                    except:
                        print(f"Shortcode execution error: {e}")
                    return error_msg
            else:
                return f"❌ Unknown shortcode: {shortcode_pattern}"
                
        except Exception as e:
            return f"❌ Critical shortcode error: {str(e)}"

    def get_shortcode_list(self):
        """Get list of available shortcodes"""
        if not self._initialized:
            self._load_shortcodes()
        return list(self.shortcodes.keys())

    def get_shortcode_descriptions(self):
        """Get descriptions of all shortcodes"""
        if not self._initialized:
            self._load_shortcodes()
        return self.descriptions.copy()

# Create global registry instance
registry = ShortcodeRegistry()