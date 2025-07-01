# syncara/modules/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, console
from .system_prompt import SystemPrompt
from .process_shortcode import process_shortcode
from syncara.userbot import get_userbot, get_all_userbots

# Inisialisasi komponen
system_prompt = SystemPrompt()
replicate_api = ReplicateAPI()  # Pastikan ini sesuai dengan implementasi yang ada

@bot.on_message(filters.mentioned | filters.reply | filters.private)
async def ask_command(client, message):
    """Handle AI requests and process them using userbot"""
    try:
        # Get text from either message text or caption
        text = message.text or message.caption
        
        if not text:
            await message.reply_text("Silakan berikan pertanyaan")
            return
        
        # Get photo if exists
        photo_file_id = None
        if message.photo:
            photo_file_id = message.photo.file_id
        
        # Get userbot to process the request
        userbot = get_userbot()
        if not userbot:
            await message.reply_text("Tidak ada userbot yang tersedia untuk memproses permintaan")
            return
        
        # Send typing action
        await message.reply_chat_action(enums.ChatAction.TYPING)
        
        # Process AI response using userbot
        await process_ai_response_with_userbot(client, userbot, message, text, photo_file_id)
        
    except Exception as e:
        console.error(f"Error in ask_command: {str(e)}")
        await message.reply_text("Maaf, terjadi kesalahan dalam memproses permintaan Anda.")

async def process_ai_response_with_userbot(client, userbot, message, prompt, photo_file_id=None):
    """Process AI response using userbot"""
    try:
        # Get bot information
        bot_info = await client.get_me()
        
        # Prepare context
        context = {
            'bot_name': bot_info.first_name,
            'bot_username': bot_info.username,
            'user_id': message.from_user.id,
            'chat_id': message.chat.id
        }
        
        # Get formatted system prompt
        formatted_prompt = system_prompt.get_chat_prompt(context)
        
        # Generate AI response
        response = await replicate_api.generate_response(
            prompt=prompt,
            system_prompt=formatted_prompt,
            image_file_id=photo_file_id,
            client=client
        )
        
        # Process shortcodes in response
        processed_response = await process_shortcode(client, message, response)
        
        # Send response using userbot if not empty
        if processed_response.strip():
            # Check if we're in a group or private chat
            if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                # In groups, reply to the original message
                await userbot.send_message(
                    chat_id=message.chat.id,
                    text=processed_response,
                    reply_to_message_id=message.id
                )
            else:
                # In private chats, just send the message
                await userbot.send_message(
                    chat_id=message.chat.id,
                    text=processed_response
                )
        
    except Exception as e:
        console.error(f"Error in AI response with userbot: {str(e)}")
        # Send error message using the main bot
        await message.reply_text("Maaf, terjadi kesalahan dalam memproses permintaan Anda.")