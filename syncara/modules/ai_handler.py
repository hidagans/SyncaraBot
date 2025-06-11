# module/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, console

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

async def process_ai_response(client, message, prompt):
    try:
        # Send typing action
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        
        # Generate AI response
        response = await replicate_api.generate_response(
            prompt=prompt,
            system_prompt="Kamu adalah SyncaraBot, asisten AI yang membantu pengguna dengan berbagai tugas."
        )
        
        # Ensure response is a string and not empty
        if not isinstance(response, str):
            response = str(response)
            
        if not response.strip():  # Check if response is empty or just whitespace
            response = "Maaf, saya tidak dapat menghasilkan respons yang valid. Silakan coba lagi."
            
        # Send response
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in AI response: {str(e)}")
        await message.reply_text("Maaf, terjadi kesalahan saat memproses permintaan Anda.")

@bot.on_message(filters.command(["ask"]))
async def ask_command(client, message):
    # Get text from either message text or caption
    text = message.text or message.caption
    
    if not text:
        await message.reply_text("Silakan berikan pertanyaan setelah perintah /ask")
        return
        
    # Check if command has arguments
    if len(message.command) < 2:
        await message.reply_text("Silakan berikan pertanyaan setelah perintah /ask")
        return
    
    # Extract prompt from text/caption
    prompt = text.split("/ask ", 1)[1]
    
    # If there's a photo, add it to the prompt
    if message.photo:
        # Get the photo file ID
        photo = message.photo.file_id
        prompt = f"[Image attached] {prompt}"
        
    await process_ai_response(client, message, prompt)

@bot.on_message(filters.private & filters.command)
async def handle_private(client, message):
    """Handle private messages"""
    if message.text:
        await process_ai_response(client, message, message.text)
