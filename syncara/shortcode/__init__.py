# syncara/shortcode/__init__.py
import os
import importlib
import inspect
from typing import Dict, Callable
from syncara.shortcode.dynamic_handler import create_and_register_handler, request_handler_approval, approve_handler, reject_handler
from config.config import OWNER_ID

class ShortcodeRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.shortcodes = {}
            cls._instance.descriptions = {}
            cls._instance._load_shortcodes()
        return cls._instance

    def _load_shortcodes(self):
        """Load all shortcode handlers from files in the shortcode directory"""
        try:
            # Direct import approach - more reliable
            from syncara.shortcode.group_management import GroupManagementShortcode
            from syncara.shortcode.users_management import UserManagementShortcode
            from syncara.shortcode.userbot_management import UserbotManagementShortcode
            from syncara.shortcode.image_generation import ImageGenerationShortcode
            from syncara.shortcode.canvas_management import CanvasManagementShortcode
            
            # Create instances
            group_shortcode = GroupManagementShortcode()
            user_shortcode = UserManagementShortcode()
            userbot_shortcode = UserbotManagementShortcode()
            image_shortcode = ImageGenerationShortcode()
            canvas_shortcode = CanvasManagementShortcode()
            
            # Register handlers
            self.shortcodes.update(group_shortcode.handlers)
            self.shortcodes.update(user_shortcode.handlers)
            self.shortcodes.update(userbot_shortcode.handlers)
            self.shortcodes.update(image_shortcode.handlers)
            self.shortcodes.update(canvas_shortcode.handlers)
            
            # Register descriptions
            self.descriptions.update(group_shortcode.descriptions)
            self.descriptions.update(user_shortcode.descriptions)
            self.descriptions.update(userbot_shortcode.descriptions)
            self.descriptions.update(image_shortcode.descriptions)
            self.descriptions.update(canvas_shortcode.descriptions)
            
            print(f"Loaded {len(self.shortcodes)} shortcode handlers")
            print(f"Loaded {len(self.descriptions)} shortcode descriptions")
            
        except Exception as e:
            print(f"Error loading shortcodes: {e}")
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
            }
            
            self.descriptions = {
                'GROUP:INFO': 'Get group information',
                'USER:INFO': 'Get user information',
                'USERBOT:STATUS': 'Get userbot status',
                'IMAGE:GEN': 'Generate image from text prompt. Usage: [IMAGE:GEN:prompt]',
            }
            
            print("Loaded fallback shortcodes")
            
        except Exception as e:
            print(f"Error in fallback shortcode loading: {e}")
    
    async def _dummy_handler(self, client, message, params):
        """Dummy handler for fallback shortcodes"""
        return True

    def get_shortcode_docs(self) -> str:
        """Generate documentation for all registered shortcodes"""
        docs = ["Available Shortcodes:"]
        
        # Group shortcodes by category
        categories = {}
        for shortcode, desc in self.descriptions.items():
            category = shortcode.split(':')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((shortcode, desc))
        
        # Generate formatted documentation
        for category, shortcodes in categories.items():
            docs.append(f"\n{category}:")
            for shortcode, desc in shortcodes:
                docs.append(f"- [{shortcode}] - {desc}")
        
        return "\n".join(docs)

    async def execute_shortcode(self, shortcode: str, client, message, params):
        """Execute a registered shortcode. Jika tidak ada, buat handler dinamis (hanya OWNER, butuh approval)."""
        # Deteksi format NEWCMD: untuk handler baru
        if shortcode.startswith('NEWCMD:'):
            # Extract nama handler dari NEWCMD:NAMA_HANDLER:deskripsi
            parts = shortcode.split(':', 2)
            if len(parts) >= 2:
                handler_name = parts[1]  # NAMA_HANDLER
                description = parts[2] if len(parts) > 2 else params  # deskripsi
                # Request approval untuk handler baru
                await request_handler_approval(handler_name, description, message)
                return True
        
        if shortcode in self.shortcodes:
            return await self.shortcodes[shortcode](client, message, params)
        # Command approval
        if hasattr(message, 'text') and message.text:
            if message.text.startswith('/approve '):
                sc = message.text.split(' ', 1)[1].strip()
                ok, msg = approve_handler(sc, registry=self.shortcodes)
                await message.reply(msg)
                return ok
            if message.text.startswith('/reject '):
                sc = message.text.split(' ', 1)[1].strip()
                ok, msg = reject_handler(sc)
                await message.reply(msg)
                return ok
        # Hanya izinkan owner request handler baru
        if hasattr(message, 'from_user') and getattr(message.from_user, 'id', None) == OWNER_ID:
            desc = getattr(message, 'caption', None) or getattr(message, 'text', None) or ''
            await request_handler_approval(shortcode, desc, message)
            return False
        return False

# Create singleton instance
registry = ShortcodeRegistry()