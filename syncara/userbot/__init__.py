# syncara/userbot/__init__.py
from pyrogram import Client
from config.config import USERBOTS
from syncara import console
from typing import Dict, Optional, List

# Dictionary untuk menyimpan instance userbot
userbots: Dict[str, Client] = {}

async def initialize_userbots() -> Dict[str, Client]:
    """Initialize all userbot clients"""
    global userbots
    
    if not USERBOTS:
        console.warning("No userbots configured")
        return {}
    
    console.info(f"Initializing {len(USERBOTS)} userbots...")
    
    for config in USERBOTS:
        try:
            name = config.get("name", "unnamed")
            session_string = config.get("session_string")
            
            if not session_string:
                console.warning(f"No session string for userbot '{name}', skipping")
                continue
                
            client = Client(
                name=name,
                api_id=config.get("api_id"),
                api_hash=config.get("api_hash"),
                session_string=session_string,
                in_memory=True
            )
            
            await client.start()
            me = await client.get_me()
            userbots[name] = client
            console.info(f"Userbot '{name}' started as @{me.username} ({me.id})")
            
        except Exception as e:
            console.error(f"Failed to initialize userbot '{config.get('name')}': {str(e)}")
    
    console.info(f"Successfully initialized {len(userbots)}/{len(USERBOTS)} userbots")
    return userbots

async def stop_userbots():
    """Stop all userbot clients"""
    global userbots
    
    for name, client in userbots.items():
        try:
            await client.stop()
            console.info(f"Userbot '{name}' stopped")
        except Exception as e:
            console.error(f"Error stopping userbot '{name}': {str(e)}")
    
    userbots = {}

def get_userbot(name: str = None) -> Optional[Client]:
    """
    Get a userbot client by name
    If name is None, returns the first available userbot
    """
    if not userbots:
        return None
        
    if name and name in userbots:
        return userbots[name]
        
    # Return first available userbot if name not specified or not found
    return next(iter(userbots.values()), None)

def get_all_userbots() -> List[Client]:
    """Get all userbot clients"""
    return list(userbots.values())

def get_userbot_names() -> List[str]:
    """Get names of all available userbots"""
    return list(userbots.keys())