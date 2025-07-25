# syncara/shortcode/__init__.py
import os
import importlib
import inspect
from typing import Dict, Callable
from config.config import OWNER_ID

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
            self.descriptions.update(group_shortcode.descriptions)
            self.descriptions.update(users_shortcode.descriptions)
            self.descriptions.update(userbot_shortcode.descriptions)
            self.descriptions.update(image_shortcode.descriptions)
            self.descriptions.update(canvas_shortcode.descriptions)
            self.descriptions.update(python_shortcode.descriptions)
            self.descriptions.update(file_search_shortcode.descriptions)
            self.descriptions.update(todo_shortcode.descriptions)
            self.descriptions.update(channel_shortcode.descriptions)
            
            # Register Pyrogram descriptions from all handlers
            self.descriptions.update(pyrogram_manager.advanced_handler.descriptions)
            self.descriptions.update(pyrogram_manager.utilities_handler.descriptions)
            self.descriptions.update(pyrogram_manager.inline_handler.descriptions)
            self.descriptions.update(pyrogram_manager.bound_handler.descriptions)
            
            self._initialized = True
            print(f"✅ Loaded {len(self.shortcodes)} shortcode handlers")
            print(f"✅ Loaded {len(self.descriptions)} shortcode descriptions")
            
        except Exception as e:
            print(f"❌ Error loading shortcodes: {e}")
            # Fallback to manual registration
            self._load_shortcodes_fallback()
    
    def _load_shortcodes_fallback(self):
        """Fallback method to load shortcodes manually"""
        try:
            # Manual registration of basic shortcodes
            self.shortcodes = {
                'GROUP:INFO': self._dummy_handler,
                'USER:INFO': self._dummy_handler,
                'USERBOT:STATUS': self._dummy_handler,
                'IMAGE:GEN': self._dummy_handler,
                'CHANNEL:STATUS': self._dummy_handler,
            }
            
            self.descriptions = {
                'GROUP:INFO': 'Get group information',
                'USER:INFO': 'Get user information',
                'USERBOT:STATUS': 'Get userbot status',
                'IMAGE:GEN': 'Generate image from text prompt. Usage: [IMAGE:GEN:prompt]',
                'CHANNEL:STATUS': 'Get channel status',
            }
            
            self._initialized = True
            print("✅ Loaded fallback shortcodes")
            
        except Exception as e:
            print(f"❌ Error in fallback shortcode loading: {e}")
            self._initialized = True
    
    async def _dummy_handler(self, client, message, params):
        """Dummy handler for fallback shortcodes"""
        return True

    def get_shortcode_docs(self) -> str:
        """Generate documentation for all registered shortcodes"""
        if not self._initialized:
            self._load_shortcodes()
            
        docs = ["Available Shortcodes:"]
        
        # Group shortcodes by category
        categories = {}
        for shortcode, desc in self.descriptions.items():
            category = shortcode.split(':')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((shortcode, desc))
        
        # Generate formatted documentation
        for category, shortcodes in sorted(categories.items()):
            docs.append(f"\n{category}:")
            for shortcode, desc in sorted(shortcodes):
                docs.append(f"- [{shortcode}] - {desc}")
        
        # Add execution order notes
        docs.append("\n⚠️ Important Notes:")
        docs.append("- CANVAS:CREATE must be executed before CANVAS:EXPORT")
        docs.append("- CANVAS:SHOW and CANVAS:EDIT require file to exist first")
        docs.append("- USER management commands require admin privileges")
        docs.append("- GROUP management commands require admin privileges")
        docs.append("- CHANNEL management commands require owner privileges")
        docs.append("- PYROGRAM: prefix untuk semua fungsi Pyrogram method")
        
        return "\n".join(docs)

    def validate_shortcode_order(self, shortcodes_in_text: list) -> dict:
        """Validate the execution order of shortcodes in text"""
        if not self._initialized:
            self._load_shortcodes()
            
        issues = []
        
        # Check for CANVAS operations
        canvas_operations = [s for s in shortcodes_in_text if s.startswith('CANVAS:')]
        for operation in canvas_operations:
            if operation.startswith('CANVAS:EXPORT') or operation.startswith('CANVAS:SHOW') or operation.startswith('CANVAS:EDIT'):
                # Check if there's a CREATE operation for the same file
                filename = operation.split(':')[2] if len(operation.split(':')) > 2 else None
                if filename:
                    create_op = f"CANVAS:CREATE:{filename}"
                    if not any(create_op in s for s in shortcodes_in_text):
                        issues.append(f"⚠️ {operation} requires file to be created first with CANVAS:CREATE")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'suggestions': [
                "Always create files before trying to export/show/edit them",
                "Use CANVAS:LIST to check available files first",
                "Use PYROGRAM: prefix for all Pyrogram method calls",
                "Use CHANNEL: prefix for channel management commands",
                "Channel management requires owner privileges"
            ]
        }

    async def execute_shortcode(self, shortcode: str, client, message, params):
        """Execute a registered shortcode"""
        if not self._initialized:
            self._load_shortcodes()
            
        if shortcode in self.shortcodes:
            return await self.shortcodes[shortcode](client, message, params)
        return False

    def ensure_loaded(self):
        """Ensure shortcodes are loaded"""
        if not self._initialized:
            self._load_shortcodes()

# Create singleton instance
registry = ShortcodeRegistry()

# Load shortcodes on import (synchronously)
registry.ensure_loaded()