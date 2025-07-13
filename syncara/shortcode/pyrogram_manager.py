# syncara/shortcode/pyrogram_manager.py
"""
Main shortcode manager untuk semua Pyrogram shortcode handlers.
"""

from syncara.console import console
import asyncio
from typing import Dict, Any, Optional, List
from .pyrogram_advanced import PyrogramAdvancedShortcode
from .pyrogram_utilities import PyrogramUtilitiesShortcode
from .pyrogram_inline import PyrogramInlineShortcode
from .pyrogram_bound import PyrogramBoundShortcode

class PyrogramShortcodeManager:
    """
    Manager utama untuk semua shortcode Pyrogram.
    """
    
    def __init__(self):
        self.handlers = {}
        self.advanced_handler = PyrogramAdvancedShortcode()
        self.utilities_handler = PyrogramUtilitiesShortcode()
        self.inline_handler = PyrogramInlineShortcode()
        self.bound_handler = PyrogramBoundShortcode()
        
        # Create wrapper handlers for registry compatibility
        self._create_wrapper_handlers()
        
        console.info(f"✅ Pyrogram Shortcode Manager initialized with {len(self.handlers)} handlers")
    
    def _create_wrapper_handlers(self):
        """Create wrapper handlers that are compatible with registry signature"""
        # Advanced handlers
        for shortcode, handler in self.advanced_handler.handlers.items():
            self.handlers[shortcode] = self._create_wrapper(shortcode, handler, self.advanced_handler)
        
        # Utilities handlers
        for shortcode, handler in self.utilities_handler.handlers.items():
            self.handlers[shortcode] = self._create_wrapper(shortcode, handler, self.utilities_handler)
        
        # Inline handlers
        for shortcode, handler in self.inline_handler.handlers.items():
            self.handlers[shortcode] = self._create_wrapper(shortcode, handler, self.inline_handler)
        
        # Bound handlers
        for shortcode, handler in self.bound_handler.handlers.items():
            self.handlers[shortcode] = self._create_wrapper(shortcode, handler, self.bound_handler)
    
    def _create_wrapper(self, shortcode, handler, handler_instance):
        """Create a wrapper function that converts registry signature to handler signature"""
        async def wrapper(client, message, params):
            try:
                # Extract user_id and chat_id from message
                user_id = message.from_user.id if message.from_user else 0
                chat_id = message.chat.id
                
                # Check which handler instance this belongs to and call with appropriate signature
                if handler_instance == self.bound_handler:
                    # Bound handlers expect (user_id, chat_id, client, message, **kwargs)
                    result = await handler(user_id, chat_id, client, message, params=params)
                else:
                    # Advanced, Utilities, and Inline handlers expect (client, message, params)
                    result = await handler(client, message, params)
                
                return result
            except Exception as e:
                console.error(f"Error in wrapper for {shortcode}: {e}")
                return f"❌ Error menjalankan shortcode '{shortcode}': {str(e)}"
        
        return wrapper
    
    def get_available_shortcodes(self) -> List[str]:
        """
        Mendapatkan daftar semua shortcode yang tersedia.
        """
        return list(self.handlers.keys())
    
    def get_shortcode_categories(self) -> Dict[str, List[str]]:
        """
        Mendapatkan kategori shortcode yang tersedia.
        """
        categories = {
            'Advanced Methods': [],
            'Utilities': [],
            'Inline Methods': [],
            'Bound Methods': []
        }
        
        for shortcode in self.handlers.keys():
            if shortcode in self.advanced_handler.handlers:
                categories['Advanced Methods'].append(shortcode)
            elif shortcode in self.utilities_handler.handlers:
                categories['Utilities'].append(shortcode)
            elif shortcode in self.inline_handler.handlers:
                categories['Inline Methods'].append(shortcode)
            elif shortcode in self.bound_handler.handlers:
                categories['Bound Methods'].append(shortcode)
        
        return categories
    
    def get_shortcode_help(self, shortcode: str = None) -> str:
        """
        Mendapatkan bantuan untuk shortcode.
        """
        if shortcode is None:
            # Return general help
            categories = self.get_shortcode_categories()
            help_text = "📚 **Pyrogram Shortcode Help**\n\n"
            
            for category, shortcodes in categories.items():
                if shortcodes:
                    help_text += f"**{category}:**\n"
                    for sc in shortcodes[:5]:  # Limit to 5 per category
                        help_text += f"• `{sc}`\n"
                    if len(shortcodes) > 5:
                        help_text += f"• ... dan {len(shortcodes) - 5} lainnya\n"
                    help_text += "\n"
            
            help_text += "💡 **Cara Penggunaan:**\n"
            help_text += "• Kirim pesan dengan format: `PYROGRAM:SHORTCODE_NAME`\n"
            help_text += "• Untuk bantuan spesifik: `PYROGRAM:HELP:SHORTCODE_NAME`\n"
            help_text += f"• Total shortcode tersedia: {len(self.handlers)}\n"
            
            return help_text
        
        # Return specific shortcode help
        if shortcode not in self.handlers:
            return f"❌ Shortcode '{shortcode}' tidak ditemukan"
        
        # Get shortcode documentation
        shortcode_info = self._get_shortcode_info(shortcode)
        
        help_text = f"📖 **Help untuk {shortcode}**\n\n"
        help_text += f"**Deskripsi:** {shortcode_info['description']}\n"
        help_text += f"**Kategori:** {shortcode_info['category']}\n"
        help_text += f"**Parameter:** {shortcode_info['parameters']}\n"
        help_text += f"**Contoh:** `{shortcode_info['example']}`\n"
        
        return help_text
    
    def _get_shortcode_info(self, shortcode: str) -> Dict[str, str]:
        """
        Mendapatkan informasi detail tentang shortcode.
        """
        # Mapping shortcode ke informasi
        shortcode_info = {
            'PYROGRAM:BUAT_CHANNEL': {
                'description': 'Membuat channel broadcast baru',
                'category': 'Advanced Methods',
                'parameters': 'title, description (optional)',
                'example': 'PYROGRAM:BUAT_CHANNEL title="My Channel" description="Channel Description"'
            },
            'PYROGRAM:BUAT_GRUP': {
                'description': 'Membuat grup chat baru',
                'category': 'Advanced Methods',
                'parameters': 'title, user_ids (list)',
                'example': 'PYROGRAM:BUAT_GRUP title="My Group" user_ids=[123456, 789012]'
            },
            'PYROGRAM:MULAI_BOT': {
                'description': 'Memulai bot/userbot',
                'category': 'Utilities',
                'parameters': 'Tidak ada',
                'example': 'PYROGRAM:MULAI_BOT'
            },
            'PYROGRAM:HENTIKAN_BOT': {
                'description': 'Menghentikan bot/userbot',
                'category': 'Utilities',
                'parameters': 'Tidak ada',
                'example': 'PYROGRAM:HENTIKAN_BOT'
            },
            'PYROGRAM:CHAT_ARSIP': {
                'description': 'Arsipkan chat ini',
                'category': 'Bound Methods',
                'parameters': 'Tidak ada',
                'example': 'PYROGRAM:CHAT_ARSIP'
            },
            'PYROGRAM:MESSAGE_REPLY_TEXT': {
                'description': 'Reply pesan dengan teks',
                'category': 'Bound Methods',
                'parameters': 'text',
                'example': 'PYROGRAM:MESSAGE_REPLY_TEXT text="Hello World"'
            },
            'PYROGRAM:INLINE_ANSWER': {
                'description': 'Jawab inline query',
                'category': 'Inline Methods',
                'parameters': 'results (list)',
                'example': 'PYROGRAM:INLINE_ANSWER results=[...]'
            }
        }
        
        return shortcode_info.get(shortcode, {
            'description': 'Tidak ada deskripsi',
            'category': 'Unknown',
            'parameters': 'Tidak diketahui',
            'example': f'{shortcode}'
        })
    
    async def batch_execute_shortcodes(self, shortcodes: List[str], client, message, params_list: List[str] = None) -> List[str]:
        """
        Execute multiple shortcodes dalam batch.
        """
        results = []
        
        for i, shortcode in enumerate(shortcodes):
            try:
                params = params_list[i] if params_list and i < len(params_list) else ""
                if shortcode in self.handlers:
                    result = await self.handlers[shortcode](client, message, params)
                    results.append(f"✅ {shortcode}: {result}")
                else:
                    results.append(f"❌ {shortcode}: Shortcode tidak ditemukan")
            except Exception as e:
                results.append(f"❌ {shortcode}: {str(e)}")
        
        return results
    
    def get_shortcode_stats(self) -> Dict[str, Any]:
        """
        Mendapatkan statistik shortcode.
        """
        categories = self.get_shortcode_categories()
        
        return {
            'total_shortcodes': len(self.handlers),
            'categories': {
                category: len(shortcodes) 
                for category, shortcodes in categories.items()
            },
            'most_used_category': max(categories.keys(), key=lambda k: len(categories[k])),
            'available_handlers': [
                'Advanced Methods',
                'Utilities',
                'Inline Methods',
                'Bound Methods'
            ]
        }
    
    async def validate_shortcode_permissions(self, shortcode: str, message) -> bool:
        """
        Validasi apakah user memiliki permission untuk menggunakan shortcode.
        """
        # TODO: Implement proper permission system
        # For now, allow all shortcodes
        return True
    
    async def log_shortcode_usage(self, shortcode: str, message, success: bool, **kwargs):
        """
        Log penggunaan shortcode untuk analytics.
        """
        user_id = message.from_user.id if message.from_user else 0
        chat_id = message.chat.id
        
        log_entry = {
            'shortcode': shortcode,
            'user_id': user_id,
            'chat_id': chat_id,
            'success': success,
            'timestamp': asyncio.get_event_loop().time(),
            'metadata': kwargs
        }
        
        console.info(f"Shortcode usage: {shortcode} by {user_id} in {chat_id} - {'Success' if success else 'Failed'}")
        
        # TODO: Store to database for analytics
    
    def search_shortcodes(self, query: str) -> List[str]:
        """
        Cari shortcode berdasarkan query.
        """
        query = query.lower()
        matching_shortcodes = []
        
        for shortcode in self.handlers.keys():
            if query in shortcode.lower():
                matching_shortcodes.append(shortcode)
        
        return matching_shortcodes
    
    def get_shortcode_usage_examples(self) -> Dict[str, str]:
        """
        Mendapatkan contoh penggunaan shortcode.
        """
        examples = {
            'Channel Management': 'PYROGRAM:BUAT_CHANNEL title="My Channel"',
            'Group Management': 'PYROGRAM:BUAT_GRUP title="My Group"',
            'Bot Control': 'PYROGRAM:MULAI_BOT',
            'Chat Operations': 'PYROGRAM:CHAT_ARSIP',
            'Message Operations': 'PYROGRAM:MESSAGE_REPLY_TEXT text="Hello"',
            'Inline Operations': 'PYROGRAM:INLINE_ANSWER results=[...]',
            'Utilities': 'PYROGRAM:EXPORT_SESSION'
        }
        
        return examples

# Global instance
pyrogram_shortcode_manager = PyrogramShortcodeManager() 