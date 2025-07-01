# syncara/userbot/handlers.py
from pyrogram import filters
from . import get_userbot, get_all_userbots
from syncara import bot, console
from syncara.modules.process_shortcode import process_shortcode

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
            
        elif action == "BROADCAST":
            # Send message to all chats (format: message_text)
            # WARNING: Use with caution!
            async for dialog in userbot.get_dialogs():
                try:
                    await userbot.send_message(dialog.chat.id, params)
                except Exception as e:
                    console.error(f"Error sending broadcast to {dialog.chat.id}: {str(e)}")
            return True
            
        # Add more userbot actions as needed
            
        return False
    except Exception as e:
        console.error(f"Error in userbot action {action}: {str(e)}")
        return False

async def broadcast_to_all_userbots(message_text, chat_ids=None):
    """
    Broadcast a message using all available userbots
    
    Args:
        message_text: Text to send
        chat_ids: List of chat IDs to send to (if None, sends to all dialogs)
    """
    userbots = get_all_userbots()
    if not userbots:
        console.warning("No userbots available for broadcast")
        return False
        
    success_count = 0
    
    for userbot in userbots:
        try:
            if chat_ids:
                for chat_id in chat_ids:
                    await userbot.send_message(chat_id, message_text)
                    success_count += 1
            else:
                async for dialog in userbot.get_dialogs():
                    try:
                        await userbot.send_message(dialog.chat.id, message_text)
                        success_count += 1
                    except Exception as e:
                        console.error(f"Error sending broadcast to {dialog.chat.id}: {str(e)}")
        except Exception as e:
            console.error(f"Error in broadcast with userbot {userbot.name}: {str(e)}")
            
    return success_count > 0
