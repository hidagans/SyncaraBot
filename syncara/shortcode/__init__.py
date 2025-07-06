# syncara/shortcode/__init__.py
import os
import importlib
import inspect
from typing import Dict, Callable
from .group_management import GroupManagementShortcode
from .users_management import UserManagementShortcode
from .userbot_management import UserbotManagementShortcode
from .music_management import MusicManagementShortcode

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
            from syncara.shortcode.music_management import MusicManagementShortcode
            
            # Create instances
            group_shortcode = GroupManagementShortcode()
            user_shortcode = UserManagementShortcode()
            userbot_shortcode = UserbotManagementShortcode()
            music_shortcode = MusicManagementShortcode()
            
            # Register handlers
            self.shortcodes.update(group_shortcode.handlers)
            self.shortcodes.update(user_shortcode.handlers)
            self.shortcodes.update(userbot_shortcode.handlers)
            self.shortcodes.update(music_shortcode.handlers)
            
            # Register descriptions
            self.descriptions.update(group_shortcode.descriptions)
            self.descriptions.update(user_shortcode.descriptions)
            self.descriptions.update(userbot_shortcode.descriptions)
            self.descriptions.update(music_shortcode.descriptions)
            
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
                'MUSIC:PLAY': self._dummy_handler,
                'USERBOT:STATUS': self._dummy_handler,
            }
            
            self.descriptions = {
                'GROUP:INFO': 'Get group information',
                'USER:INFO': 'Get user information',
                'MUSIC:PLAY': 'Play music',
                'USERBOT:STATUS': 'Get userbot status',
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
        """Execute a registered shortcode"""
        if shortcode in self.shortcodes:
            return await self.shortcodes[shortcode](client, message, params)
        return False
    
    group_management = GroupManagementShortcode()
    user_management = UserManagementShortcode()
    userbot_management = UserbotManagementShortcode()
    music_management = MusicManagementShortcode()

    # Combine all handlers
    SHORTCODE_HANDLERS = {}
    SHORTCODE_HANDLERS.update(group_management.handlers)
    SHORTCODE_HANDLERS.update(user_management.handlers)
    SHORTCODE_HANDLERS.update(userbot_management.handlers)
    SHORTCODE_HANDLERS.update(music_management.handlers)

    # Combine all descriptions
    SHORTCODE_DESCRIPTIONS = {}
    SHORTCODE_DESCRIPTIONS.update(group_management.descriptions)
    SHORTCODE_DESCRIPTIONS.update(user_management.descriptions)
    SHORTCODE_DESCRIPTIONS.update(userbot_management.descriptions)
    SHORTCODE_DESCRIPTIONS.update(music_management.descriptions)

# Create singleton instance
registry = ShortcodeRegistry()