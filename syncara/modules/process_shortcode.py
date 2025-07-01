# syncara/modules/process_shortcode.py
from pyrogram import Client
import re
from typing import Union, List, Tuple
from ..shortcode import registry
from ..userbot.handlers import handle_userbot_action

async def process_shortcode(client: Client, message, text: str) -> str:
    """
    Process shortcodes found in AI response text
    Returns: Processed text with executed shortcodes removed
    """
    try:
        # Pattern untuk mendeteksi shortcode [CATEGORY:ACTION:PARAMS]
        pattern = r'\[(.*?):(.*?):(.*?)\]'
        
        # Temukan semua shortcode dalam text
        matches = re.finditer(pattern, text)
        
        for match in matches:
            try:
                full_match = match.group(0)  # Shortcode lengkap [CATEGORY:ACTION:PARAMS]
                category = match.group(1)    # Contoh: GROUP
                action = match.group(2)      # Contoh: PIN_MESSAGE
                params = match.group(3)      # Contoh: message_id atau parameter lainnya
                
                # Handle current_message_id
                if "current_message_id" in params:
                    params = params.replace("current_message_id", str(message.id))
                
                # Process berdasarkan category
                if category == "GROUP":
                    await handle_group_action(client, message, action, params)
                elif category == "USER":
                    await handle_user_action(client, message, action, params)
                elif category == "USERBOT":
                    await handle_userbot_action(action, params, {"message": message})
                # Tambahkan category lain sesuai kebutuhan
                
                # Hapus shortcode dari text
                text = text.replace(full_match, '')
                
            except Exception as e:
                print(f"Error processing shortcode {match.group(0)}: {str(e)}")
                continue
        
        # Bersihkan multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
        
    except Exception as e:
        print(f"Error in process_shortcode: {str(e)}")
        return text

# ... rest of the code remains the same
