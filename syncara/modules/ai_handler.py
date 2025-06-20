# module/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, console
from .system_prompt import SystemPrompt

# Inisialisasi
system_prompt = SystemPrompt()

# Inisialisasi Replicate API
replicate_api = ReplicateAPI()

def is_bot_mentioned(_, __, message):
    """Check if bot is mentioned or replied to"""
    # Check if message is a reply to bot's message
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id == bot.me.id:
            return True

    # Check if bot is mentioned
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention = message.text[entity.offset:entity.offset+entity.length]
                if mention == f"@{bot.me.username}":
                    return True
    return False

async def process_ai_response(client, message, prompt, photo_file_id=None):
    try:
        # Get bot information
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        bot = await client.get_me()
        
        # Prepare context
        context = {
            'bot_name': bot.first_name,
            'bot_username': bot.username,
            'user_id': message.from_user.id  # Telegram user ID
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
        
        # Send response
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in AI response: {str(e)}")
        await message.reply_text("Maaf, terjadi kesalahan dalam memproses permintaan Anda.")

@bot.on_message(filters.mentioned|filters.reply|filters.private)
async def ask_command(client, message):
    # Get text from either message text or caption
    text = message.text or message.caption
    
    if not text:
        await message.reply_text("Silakan berikan pertanyaan setelah perintah /ask")
        return
    
    # Get photo if exists
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo.file_id
    
    await process_ai_response(client, message, text, photo_file_id)
