# module/ai_handler.py
from pyrogram import filters
from services.replicate import ReplicateAPI
from .. import bot, console

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

# Custom filter for bot mentions
bot_mentioned = filters.create(is_bot_mentioned)

async def process_ai_response(message, prompt):
    """Process and send AI response"""
    try:
        # Send typing action
        await message.chat.send_chat_action("typing")
        
        # Generate AI response
        response = await replicate_api.generate_response(
            prompt=prompt,
            system_prompt="Kamu adalah SyncaraBot, asisten AI yang membantu pengguna dengan berbagai tugas."
        )
        
        # Send response
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in AI response: {str(e)}")
        await message.reply_text("Maaf, terjadi kesalahan saat memproses permintaan Anda.")

@bot.on_message(filters.command("ask"))
async def ask_command(client, message):
    """Handle /ask command"""
    if len(message.command) < 2:
        await message.reply_text("Silakan berikan pertanyaan setelah perintah /ask")
        return
    
    prompt = message.text.split("/ask ", 1)[1]
    await process_ai_response(message, prompt)

@bot.on_message(bot_mentioned)
async def handle_mention(client, message):
    """Handle bot mentions and replies"""
    # Extract prompt (remove bot mention if exists)
    prompt = message.text
    if bot.me.username:
        prompt = prompt.replace(f"@{bot.me.username}", "").strip()
    
    await process_ai_response(message, prompt)

@bot.on_message(filters.private & ~filters.command)
async def handle_private(client, message):
    """Handle private messages"""
    if message.text:
        await process_ai_response(message, message.text)