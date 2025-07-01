# syncara/modules/process_shortcode.py
from pyrogram import Client
import re
from syncara import console
from syncara.userbot import get_userbot

async def handle_group_action(client, message, action, params):
    """Handle group-related actions"""
    chat_id = message.chat.id
    
    try:
        if action == "PIN_MESSAGE":
            await client.pin_chat_message(
                chat_id=chat_id,
                message_id=int(params),
                disable_notification=False
            )
            return True
            
        elif action == "UNPIN_MESSAGE":
            await client.unpin_chat_message(
                chat_id=chat_id,
                message_id=int(params)
            )
            return True
            
        elif action == "DELETE_MESSAGE":
            await client.delete_messages(
                chat_id=chat_id,
                message_ids=[int(params)]
            )
            return True
            
        # Tambahkan action lain sesuai kebutuhan
        return False
            
    except Exception as e:
        console.error(f"Error in handle_group_action: {str(e)}")
        return False

async def handle_user_action(client, message, action, params):
    """Handle user-related actions"""
    try:
        if action == "BAN":
            await client.ban_chat_member(
                chat_id=message.chat.id,
                user_id=int(params)
            )
            return True
            
        elif action == "UNBAN":
            await client.unban_chat_member(
                chat_id=message.chat.id,
                user_id=int(params)
            )
            return True
            
        # Tambahkan action lain sesuai kebutuhan
        return False
            
    except Exception as e:
        console.error(f"Error in handle_user_action: {str(e)}")
        return False

async def handle_userbot_action(action, params, context=None):
    """
    Handle actions that should be performed by userbot
    
    Args:
        action: Action to perform
        params: Parameters for the action
        context: Additional context (message, chat_id, etc)
    
    Returns:
        bool: Success status
    """
    try:
        # Parse userbot name if specified
        userbot_name = None
        if '.' in action:
            parts = action.split('.')
            userbot_name = parts[0]
            action = parts[1]
        
        # Get appropriate userbot
        userbot = get_userbot(userbot_name)
        if not userbot:
            console.warning(f"No userbot available for action {action}")
            return False
            
        if action == "SEND_MESSAGE":
            # Format: chat_id|message_text
            chat_id, text = params.split('|', 1)
            await userbot.send_message(
                chat_id=int(chat_id),
                text=text
            )
            return True
            
        elif action == "JOIN_CHAT":
            # Join chat using invite link or username
            if params.startswith("https://t.me/"):
                await userbot.join_chat(params)
            else:
                await userbot.join_chat(params)
            return True
            
        elif action == "LEAVE_CHAT":
            await userbot.leave_chat(int(params))
            return True
            
        elif action == "FORWARD_MESSAGE":
            # Format: from_chat_id|message_id|to_chat_id
            from_chat, msg_id, to_chat = params.split('|')
            await userbot.forward_messages(
                chat_id=int(to_chat),
                from_chat_id=int(from_chat),
                message_ids=int(msg_id)
            )
            return True
            
        elif action == "REACT":
            # Format: chat_id|message_id|emoji
            chat_id, msg_id, emoji = params.split('|')
            await userbot.send_reaction(
                chat_id=int(chat_id),
                message_id=int(msg_id),
                emoji=emoji
            )
            return True
            
        # Add more userbot actions as needed
            
        return False
    except Exception as e:
        console.error(f"Error in userbot action {action}: {str(e)}")
        return False

async def process_shortcode(client, message, text):
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
                
                success = False
                
                # Process berdasarkan category
                if category == "GROUP":
                    success = await handle_group_action(client, message, action, params)
                elif category == "USER":
                    success = await handle_user_action(client, message, action, params)
                elif category == "USERBOT":
                    success = await handle_userbot_action(action, params, {"message": message})
                # Tambahkan category lain sesuai kebutuhan
                
                # Hapus shortcode dari text jika berhasil diproses
                if success:
                    text = text.replace(full_match, '')
                
            except Exception as e:
                console.error(f"Error processing shortcode {match.group(0)}: {str(e)}")
                continue
        
        # Bersihkan multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
        
    except Exception as e:
        console.error(f"Error in process_shortcode: {str(e)}")
        return text