# syncara/shortcode/__init__.py
from typing import Dict, List
from ..userbot import get_userbot_names

class ShortcodeRegistry:
    def __init__(self):
        self._shortcodes: Dict[str, str] = {
            # Group management
            'GROUP:PIN_MESSAGE': 'Pin pesan di grup',
            'GROUP:UNPIN_MESSAGE': 'Unpin pesan di grup',
            'GROUP:DELETE_MESSAGE': 'Hapus pesan di grup',
            
            # User management
            'USER:BAN': 'Ban user dari grup',
            'USER:UNBAN': 'Unban user dari grup',
            'USER:MUTE': 'Mute user di grup',
            'USER:UNMUTE': 'Unmute user di grup',
            
            # Userbot actions (general)
            'USERBOT:SEND_MESSAGE': 'Kirim pesan sebagai userbot (format: chat_id|pesan)',
            'USERBOT:JOIN_CHAT': 'Join chat/grup/channel (username atau invite link)',
            'USERBOT:LEAVE_CHAT': 'Leave chat/grup/channel (chat_id)',
            'USERBOT:FORWARD_MESSAGE': 'Forward pesan (format: from_chat_id|message_id|to_chat_id)',
            'USERBOT:REACT': 'Reaksi pada pesan (format: chat_id|message_id|emoji)',
            'USERBOT:BROADCAST': 'Broadcast pesan ke semua chat (format: pesan)',
            
            # Tambahkan shortcode lainnya di sini
        }

    def get_shortcode_docs(self) -> str:
        """Get documentation of all registered shortcodes"""
        docs = ["📝 SHORTCODE YANG TERSEDIA:"]
        
        # Add general shortcodes
        for code, desc in self._shortcodes.items():
            docs.append(f"- [{code}] : {desc}")
        
        # Add userbot-specific shortcodes
        userbot_names = get_userbot_names()
        if userbot_names:
            docs.append("\n🤖 USERBOT SPESIFIK:")
            for name in userbot_names:
                docs.append(f"- [USERBOT:{name}.SEND_MESSAGE:chat_id|pesan] : Kirim pesan menggunakan userbot '{name}'")
                docs.append(f"- [USERBOT:{name}.JOIN_CHAT:username/link] : Join chat menggunakan userbot '{name}'")
        
        return "\n".join(docs)

    def register_shortcode(self, code: str, description: str):
        """Register new shortcode"""
        self._shortcodes[code] = description

registry = ShortcodeRegistry()
