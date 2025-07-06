# syncara/shortcode/__init__.py
import os
import importlib
import inspect
from typing import Dict, Callable

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
            
            # Create instances
            group_shortcode = GroupManagementShortcode()
            user_shortcode = UserManagementShortcode()
            userbot_shortcode = UserbotManagementShortcode()
            image_shortcode = ImageGenerationShortcode()
            
            # Register handlers
            self.shortcodes.update(group_shortcode.handlers)
            self.shortcodes.update(user_shortcode.handlers)
            self.shortcodes.update(userbot_shortcode.handlers)
            self.shortcodes.update(image_shortcode.handlers)
            
            # Register descriptions
            self.descriptions.update(group_shortcode.descriptions)
            self.descriptions.update(user_shortcode.descriptions)
            self.descriptions.update(userbot_shortcode.descriptions)
            self.descriptions.update(image_shortcode.descriptions)
            
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
        """Execute a registered shortcode"""
        if shortcode in self.shortcodes:
            return await self.shortcodes[shortcode](client, message, params)
        return False

# Create singleton instance
registry = ShortcodeRegistry()