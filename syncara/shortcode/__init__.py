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
        # Get the directory where this __init__.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Iterate through all .py files in the directory
        for filename in os.listdir(current_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]  # Remove .py extension
                try:
                    # Import the module dynamically
                    module = importlib.import_module(f'.{module_name}', package='syncara.shortcode')
                    
                    # Look for classes with Shortcode suffix
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and name.endswith('Shortcode'):
                            shortcode_instance = obj()
                            
                            # Register handlers and descriptions
                            if hasattr(shortcode_instance, 'handlers'):
                                self.shortcodes.update(shortcode_instance.handlers)
                            if hasattr(shortcode_instance, 'descriptions'):
                                self.descriptions.update(shortcode_instance.descriptions)
                                
                    print(f"Loaded shortcode module: {module_name}")
                except Exception as e:
                    print(f"Error loading shortcode module {module_name}: {e}")

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