# syncara/modules/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, console
from .system_prompt import SystemPrompt
from .process_shortcode import process_shortcode
from syncara.userbot import get_userbot, get_all_userbots

# Inisialisasi komponen
system_prompt = SystemPrompt()
replicate_api = ReplicateAPI()

# Bot manager hanya menerima perintah dari owner
@bot.on_message(filters.command(["start", "help"]))
async def start_command(client, message):
    """Handle start command for the manager bot"""
    await message.reply_text(
        "👋 Halo! Saya adalah bot manager untuk SyncaraBot.\n\n"
        "Bot ini mengelola userbot assistant yang melayani permintaan AI.\n\n"
        "Gunakan userbot assistant untuk berinteraksi dengan AI."
    )

# Userbot assistant menangani semua interaksi AI
async def setup_userbot_handlers():
    """Setup handlers for userbot assistant"""
    try:
        # Get primary userbot
        userbot = get_userbot()
        if not userbot:
            console.error("No userbot available to set up handlers")
            return
            
        # Set up message handler for the userbot
        @userbot.on_message(filters.text | filters.photo)
        async def userbot_message_handler(client, message):
            """Handle all messages for userbot assistant"""
            try:
                # Skip messages from bots
                if message.from_user and message.from_user.is_bot:
                    return
                    
                # Get text from either message text or caption
                text = message.text or message.caption
                
                if not text:
                    return
                
                # Get photo if exists
                photo_file_id = None
                if message.photo:
                    photo_file_id = message.photo.file_id
                
                # Send typing action
                await client.send_chat_action(
                    chat_id=message.chat.id,
                    action=enums.ChatAction.TYPING
                )
                
                # Process AI response
                await process_ai_response(client, message, text, photo_file_id)
                
            except Exception as e:
                console.error(f"Error in userbot message handler: {str(e)}")
        
        console.info(f"Userbot assistant handlers set up successfully")
        
    except Exception as e:
        console.error(f"Error setting up userbot handlers: {str(e)}")

async def process_ai_response(client, message, prompt, photo_file_id=None):
    """Process AI response for userbot assistant"""
    try:
        # Get userbot information
        me = await client.get_me()
        
        # Prepare context
        context = {
            'bot_name': me.first_name,
            'bot_username': me.username,
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
        
        # Send response if not empty
        if processed_response.strip():
            await client.send_message(
                chat_id=message.chat.id,
                text=processed_response,
                reply_to_message_id=message.id
            )
        
    except Exception as e:
        console.error(f"Error in AI response: {str(e)}")
        await client.send_message(
            chat_id=message.chat.id,
            text="Maaf, terjadi kesalahan dalam memproses permintaan Anda.",
            reply_to_message_id=message.id
        )