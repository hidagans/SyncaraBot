"""
Compatibility layer untuk berbagai versi Pyrogram.
"""

from pyrogram import types
import sys

# Check available types untuk kompatibilitas
AVAILABLE_TYPES = {}

def check_type_availability():
    """Check ketersediaan types di versi Pyrogram yang digunakan"""
    global AVAILABLE_TYPES
    
    # Core types yang biasanya tersedia
    AVAILABLE_TYPES['Message'] = hasattr(types, 'Message')
    AVAILABLE_TYPES['Chat'] = hasattr(types, 'Chat')
    AVAILABLE_TYPES['User'] = hasattr(types, 'User')
    AVAILABLE_TYPES['InlineKeyboardMarkup'] = hasattr(types, 'InlineKeyboardMarkup')
    AVAILABLE_TYPES['InlineKeyboardButton'] = hasattr(types, 'InlineKeyboardButton')
    AVAILABLE_TYPES['ReplyKeyboardMarkup'] = hasattr(types, 'ReplyKeyboardMarkup')
    AVAILABLE_TYPES['KeyboardButton'] = hasattr(types, 'KeyboardButton')
    
    # Advanced types yang mungkin tidak tersedia di versi lama
    AVAILABLE_TYPES['ChatPermissions'] = hasattr(types, 'ChatPermissions')
    AVAILABLE_TYPES['ChatPrivileges'] = hasattr(types, 'ChatPrivileges')
    AVAILABLE_TYPES['BotCommand'] = hasattr(types, 'BotCommand')
    AVAILABLE_TYPES['BotCommandScope'] = hasattr(types, 'BotCommandScope')
    AVAILABLE_TYPES['ChatAdministratorRights'] = hasattr(types, 'ChatAdministratorRights')
    AVAILABLE_TYPES['MenuButton'] = hasattr(types, 'MenuButton')
    AVAILABLE_TYPES['ReplyParameters'] = hasattr(types, 'ReplyParameters')
    AVAILABLE_TYPES['MessageEntity'] = hasattr(types, 'MessageEntity')
    AVAILABLE_TYPES['InputMedia'] = hasattr(types, 'InputMedia')
    AVAILABLE_TYPES['InputMessageContent'] = hasattr(types, 'InputMessageContent')
    AVAILABLE_TYPES['InlineQueryResult'] = hasattr(types, 'InlineQueryResult')
    AVAILABLE_TYPES['InlineQueryResultArticle'] = hasattr(types, 'InlineQueryResultArticle')
    AVAILABLE_TYPES['InlineQueryResultPhoto'] = hasattr(types, 'InlineQueryResultPhoto')
    AVAILABLE_TYPES['InlineQueryResultVideo'] = hasattr(types, 'InlineQueryResultVideo')
    AVAILABLE_TYPES['InlineQueryResultAudio'] = hasattr(types, 'InlineQueryResultAudio')
    AVAILABLE_TYPES['InlineQueryResultDocument'] = hasattr(types, 'InlineQueryResultDocument')
    AVAILABLE_TYPES['InlineQueryResultContact'] = hasattr(types, 'InlineQueryResultContact')
    AVAILABLE_TYPES['InlineQueryResultLocation'] = hasattr(types, 'InlineQueryResultLocation')
    AVAILABLE_TYPES['Poll'] = hasattr(types, 'Poll')
    AVAILABLE_TYPES['Location'] = hasattr(types, 'Location')
    AVAILABLE_TYPES['BotResults'] = hasattr(types, 'BotResults')
    AVAILABLE_TYPES['ForceReply'] = hasattr(types, 'ForceReply')
    AVAILABLE_TYPES['ReplyKeyboardRemove'] = hasattr(types, 'ReplyKeyboardRemove')
    
    return AVAILABLE_TYPES

def get_type_safe(type_name: str, fallback=None):
    """
    Mendapatkan type dengan safe fallback jika tidak tersedia.
    
    Args:
        type_name: Nama type yang ingin digunakan
        fallback: Fallback value jika type tidak tersedia
        
    Returns:
        Type object atau fallback
    """
    if AVAILABLE_TYPES.get(type_name, False):
        return getattr(types, type_name)
    return fallback

def create_safe_type_annotation(type_name: str, fallback_annotation: str = "Any"):
    """
    Membuat type annotation yang safe untuk berbagai versi Pyrogram.
    
    Args:
        type_name: Nama type Pyrogram
        fallback_annotation: Annotation fallback jika type tidak tersedia
        
    Returns:
        String annotation yang safe
    """
    if AVAILABLE_TYPES.get(type_name, False):
        return f"types.{type_name}"
    return fallback_annotation

# Compatibility functions untuk membuat objects
def create_chat_permissions(**kwargs):
    """Create ChatPermissions object dengan compatibility check"""
    if AVAILABLE_TYPES.get('ChatPermissions', False):
        return types.ChatPermissions(**kwargs)
    else:
        # Fallback untuk versi lama - return kwargs saja
        return kwargs

def create_chat_privileges(**kwargs):
    """Create ChatPrivileges object dengan compatibility check"""
    if AVAILABLE_TYPES.get('ChatPrivileges', False):
        return types.ChatPrivileges(**kwargs)
    else:
        # Fallback untuk versi lama
        return kwargs

def create_bot_command(command: str, description: str):
    """Create BotCommand object dengan compatibility check"""
    if AVAILABLE_TYPES.get('BotCommand', False):
        return types.BotCommand(command=command, description=description)
    else:
        # Fallback untuk versi lama
        return {"command": command, "description": description}

def create_inline_keyboard_markup(inline_keyboard):
    """Create InlineKeyboardMarkup dengan compatibility check"""
    if AVAILABLE_TYPES.get('InlineKeyboardMarkup', False):
        return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    else:
        # Fallback minimal
        return {"inline_keyboard": inline_keyboard}

def create_reply_keyboard_markup(keyboard, **kwargs):
    """Create ReplyKeyboardMarkup dengan compatibility check"""
    if AVAILABLE_TYPES.get('ReplyKeyboardMarkup', False):
        return types.ReplyKeyboardMarkup(keyboard=keyboard, **kwargs)
    else:
        # Fallback minimal
        return {"keyboard": keyboard, **kwargs}

def safe_type_check(obj, type_name: str) -> bool:
    """
    Safely check if object is instance of Pyrogram type.
    
    Args:
        obj: Object to check
        type_name: Pyrogram type name
        
    Returns:
        bool: True if object is instance of type
    """
    if not AVAILABLE_TYPES.get(type_name, False):
        return False
    
    try:
        return isinstance(obj, getattr(types, type_name))
    except:
        return False

# Default permissions untuk backward compatibility
DEFAULT_CHAT_PERMISSIONS = {
    "can_send_messages": True,
    "can_send_media_messages": True,
    "can_send_polls": True,
    "can_send_other_messages": True,
    "can_add_web_page_previews": True,
    "can_change_info": False,
    "can_invite_users": False,
    "can_pin_messages": False
}

DEFAULT_ADMIN_PRIVILEGES = {
    "can_manage_chat": True,
    "can_delete_messages": True,
    "can_manage_video_chats": True,
    "can_restrict_members": True,
    "can_promote_members": False,
    "can_change_info": True,
    "can_invite_users": True,
    "can_pin_messages": True,
    "can_manage_topics": False
}

# Initialize compatibility check
check_type_availability()

# Print compatibility info
def print_compatibility_info():
    """Print informasi kompatibilitas untuk debugging"""
    from syncara.console import console
    
    console.info("🔍 Pyrogram Compatibility Check:")
    available_count = sum(1 for available in AVAILABLE_TYPES.values() if available)
    total_count = len(AVAILABLE_TYPES)
    
    console.info(f"✅ Available Types: {available_count}/{total_count}")
    
    # Show missing types
    missing_types = [type_name for type_name, available in AVAILABLE_TYPES.items() if not available]
    if missing_types:
        console.warning(f"⚠️ Missing Types: {', '.join(missing_types)}")
        console.info("📝 Using fallback implementations for missing types")
    else:
        console.info("🎉 All types available - full compatibility!")

# Export untuk kemudahan penggunaan
__all__ = [
    'AVAILABLE_TYPES',
    'check_type_availability',
    'get_type_safe',
    'create_safe_type_annotation',
    'create_chat_permissions',
    'create_chat_privileges', 
    'create_bot_command',
    'create_inline_keyboard_markup',
    'create_reply_keyboard_markup',
    'safe_type_check',
    'DEFAULT_CHAT_PERMISSIONS',
    'DEFAULT_ADMIN_PRIVILEGES',
    'print_compatibility_info'
] 