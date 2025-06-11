# handlers/ai_handler.py
from pyrogram import Client, filters
from pyrogram.types import Message
from services.replicate import ReplicateAPI

# Inisialisasi Replicate API
replicate_api = ReplicateAPI()

# Filter untuk pesan yang ditujukan ke bot (mention atau reply)
def is_bot_mentioned(_, __, message):
    # Cek jika bot di-mention
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention" and message.text[entity.offset:entity.offset+entity.length] == "@your_bot_username":
                return True
    
    # Cek jika pesan adalah reply ke pesan bot
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot and message.reply_to_message.from_user.username == "your_bot_username":
            return True
    
    return False

# Buat filter kustom
bot_mentioned = filters.create(is_bot_mentioned)

async def process_ai_response(client, message, prompt, system_prompt=None):
    """Process AI response and handle shortcodes"""
    # Kirim indikator "typing..."
    await client.send_chat_action(message.chat.id, "typing")
    
    # Generate response dari Replicate API
    response = await replicate_api.generate_response(prompt, system_prompt)
    
    # Kirim respons ke pengguna
    await message.reply(response)
    
    # Proses shortcode jika ada dalam respons
    # Ini akan diimplementasikan di shortcode_handler.py

# Handler untuk pesan yang ditujukan ke bot
@filters.command("ask")
async def ask_command(client, message):
    # Ekstrak prompt dari pesan
    if len(message.command) < 2:
        await message.reply("Silakan berikan pertanyaan setelah perintah /ask")
        return
    
    prompt = message.text.split("/ask ", 1)[1]
    system_prompt = "Kamu adalah SyncaraBot, asisten AI yang membantu pengguna dengan berbagai tugas."
    
    await process_ai_response(client, message, prompt, system_prompt)

# Handler untuk pesan yang menyebut bot
@bot_mentioned
async def mentioned_handler(client, message):
    # Ekstrak prompt dari pesan (hapus mention bot jika ada)
    prompt = message.text
    system_prompt = "Kamu adalah SyncaraBot, asisten AI yang membantu pengguna dengan berbagai tugas."
    
    await process_ai_response(client, message, prompt, system_prompt)
