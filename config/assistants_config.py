# config/assistants_config.py
import os
from typing import Dict, Optional

# Assistant Session Strings Configuration
ASSISTANT_SESSIONS = {
    "AERIS": os.getenv("AERIS_SESSION_STRING", os.getenv("SESSION_STRING")),  # Default session
    "KAIROS": os.getenv("KAIROS_SESSION_STRING"),
    "ZEKE": os.getenv("ZEKE_SESSION_STRING"), 
    "NOVA": os.getenv("NOVA_SESSION_STRING"),
    "LYRA": os.getenv("LYRA_SESSION_STRING")
}

# Assistant Configuration dengan personality mapping
ASSISTANT_CONFIG = {
    "AERIS": {
        "name": "AERIS",
        "username": "Aeris_sync",
        "personality": "AERIS",
        "description": "Default assistant",
        "session_string": ASSISTANT_SESSIONS["AERIS"],
        "enabled": bool(ASSISTANT_SESSIONS["AERIS"]),
        "emoji": "🤖",
        "color": "blue",
        "temperature": 0.7,
        "top_p": 0.95,
        "presence_penalty": 0.6,
        "frequency_penalty": 0.8
    },
    "KAIROS": {
        "name": "KAIROS", 
        "username": "Kairos_sync",
        "personality": "KAIROS",
        "description": "Assistant Second",
        "session_string": ASSISTANT_SESSIONS["KAIROS"],
        "enabled": bool(ASSISTANT_SESSIONS["KAIROS"]),
        "emoji": "⏰",
        "color": "green",
        "temperature": 0.8,
        "presence_penalty": 0.5,
        "frequency_penalty": 0.2
    },
    "ZEKE": {
        "name": "ZEKE",
        "username": "zeke_sync", 
        "personality": "ZEKE",
        "description": "Assistant Third",
        "session_string": ASSISTANT_SESSIONS["ZEKE"],
        "enabled": bool(ASSISTANT_SESSIONS["ZEKE"]),
        "emoji": "🧠",
        "color": "purple",
        "temperature": 0.6,
        "presence_penalty": 0.3,
        "frequency_penalty": 0.1
    },
    "NOVA": {
        "name": "NOVA",
        "username": "Nova_sync",
        "personality": "NOVA", 
        "description": "Assistant Fourth",
        "session_string": ASSISTANT_SESSIONS["NOVA"],
        "enabled": bool(ASSISTANT_SESSIONS["NOVA"]),
        "emoji": "✨",
        "color": "pink",
        "temperature": 1.0,
        "presence_penalty": 0.7,
        "frequency_penalty": 0.5
    },
    "LYRA": {
        "name": "LYRA",
        "username": "Lyra_sync",
        "personality": "LYRA",
        "description": "Assistant Fifth",
        "session_string": ASSISTANT_SESSIONS["LYRA"],
        "enabled": bool(ASSISTANT_SESSIONS["LYRA"]),
        "emoji": "🎵",
        "color": "orange",
        "temperature": 0.9,
        "presence_penalty": 0.2,
        "frequency_penalty": 0.4
    }
}

def get_assistant_config(assistant_id: str) -> Optional[Dict]:
    """Get konfigurasi assistant berdasarkan ID"""
    return ASSISTANT_CONFIG.get(assistant_id.upper())

def get_enabled_assistants() -> Dict:
    """Get semua assistant yang enabled"""
    return {k: v for k, v in ASSISTANT_CONFIG.items() if v["enabled"]}

def get_assistant_by_username(username: str) -> Optional[str]:
    """Get assistant ID berdasarkan username"""
    for assistant_id, config in ASSISTANT_CONFIG.items():
        if config["username"] == username:
            return assistant_id
    return None

def get_assistant_by_personality(personality: str) -> Optional[str]:
    """Get assistant ID berdasarkan personality"""
    for assistant_id, config in ASSISTANT_CONFIG.items():
        if config["personality"] == personality.upper():
            return assistant_id
    return None

def update_assistant_session(assistant_id: str, session_string: str) -> bool:
    """Update session string untuk assistant tertentu"""
    assistant_id = assistant_id.upper()
    if assistant_id in ASSISTANT_CONFIG:
        ASSISTANT_CONFIG[assistant_id]["session_string"] = session_string
        ASSISTANT_CONFIG[assistant_id]["enabled"] = bool(session_string)
        return True
    return False

def get_assistant_status() -> Dict:
    """Get status semua assistant"""
    status = {}
    for assistant_id, config in ASSISTANT_CONFIG.items():
        status[assistant_id] = {
            "name": config["name"],
            "username": config["username"],
            "enabled": config["enabled"],
            "has_session": bool(config["session_string"]),
            "emoji": config["emoji"],
            "description": config["description"]
        }
    return status

# Helper untuk generate session string
def generate_session_instructions():
    """Generate instruksi untuk membuat session string"""
    return """
📱 **Cara Membuat Session String untuk Assistant:**

1. **Buat Akun Telegram Baru** untuk setiap assistant
2. **Dapatkan API Credentials** dari https://my.telegram.org
3. **Generate Session String** dengan script generate_session.py

**Environment Variables yang Diperlukan:**
```env
# Assistant Session Strings
AERIS_SESSION_STRING=your_aeris_session_string
KAIROS_SESSION_STRING=your_kairos_session_string  
ZEKE_SESSION_STRING=your_zeke_session_string
NOVA_SESSION_STRING=your_nova_session_string
LYRA_SESSION_STRING=your_lyra_session_string
```

**Atau gunakan SESSION_STRING untuk AERIS (default):**
```env
SESSION_STRING=your_default_session_string
```

**Username yang Disarankan:**
- AERIS: @Aeris_sync
- KAIROS: @Kairos_sync  
- ZEKE: @Zeke_sync
- NOVA: @Nova_sync
- LYRA: @Lyra_sync
""" 