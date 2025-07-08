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
            from syncara.shortcode.python_execution import PythonExecutionShortcode
            from syncara.shortcode.file_search import FileSearchShortcode
            from syncara.shortcode.todo_management import TodoManagementShortcode
            
            # Create instances
            group_shortcode = GroupManagementShortcode()
            user_shortcode = UserManagementShortcode()
            userbot_shortcode = UserbotManagementShortcode()
            image_shortcode = ImageGenerationShortcode()
            canvas_shortcode = CanvasManagementShortcode()
            python_shortcode = PythonExecutionShortcode()
            search_shortcode = FileSearchShortcode()
            todo_shortcode = TodoManagementShortcode()
            
            # Register handlers
            self.shortcodes.update(group_shortcode.handlers)
            self.shortcodes.update(user_shortcode.handlers)
            self.shortcodes.update(userbot_shortcode.handlers)
            self.shortcodes.update(image_shortcode.handlers)
            self.shortcodes.update(canvas_shortcode.handlers)
            self.shortcodes.update(python_shortcode.handlers)
            self.shortcodes.update(search_shortcode.handlers)
            self.shortcodes.update(todo_shortcode.handlers)
            
            # Register descriptions
            self.descriptions.update(group_shortcode.descriptions)
            self.descriptions.update(user_shortcode.descriptions)
            self.descriptions.update(userbot_shortcode.descriptions)
            self.descriptions.update(image_shortcode.descriptions)
            self.descriptions.update(canvas_shortcode.descriptions)
            self.descriptions.update(python_shortcode.descriptions)
            self.descriptions.update(search_shortcode.descriptions)
            self.descriptions.update(todo_shortcode.descriptions)
            
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
        
        # Add execution order notes
        docs.append("\n⚠️ Important Notes:")
        docs.append("- CANVAS:CREATE must be executed before CANVAS:EXPORT")
        docs.append("- CANVAS:SHOW and CANVAS:EDIT require file to exist first")
        docs.append("- USER management commands require admin privileges")
        docs.append("- GROUP management commands require admin privileges")
        
        return "\n".join(docs)

    def validate_shortcode_order(self, shortcodes_in_text: list) -> dict:
        """Validate the execution order of shortcodes in text"""
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
                "Use CANVAS:LIST to check available files first"
            ]
        }

    async def execute_shortcode(self, shortcode: str, client, message, params):
        """Execute a registered shortcode"""
        if shortcode in self.shortcodes:
            return await self.shortcodes[shortcode](client, message, params)
        return False

# Create singleton instance
registry = ShortcodeRegistry()