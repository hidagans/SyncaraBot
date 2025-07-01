# syncara/modules/ai_handler.py
from pyrogram import filters, enums
from syncara.services import ReplicateAPI
from syncara import bot, console
from .system_prompt import SystemPrompt
from .process_shortcode import process_shortcode
from syncara.userbot import get_userbot, get_all_userbots, get_userbot_names
from config.config import OWNER_ID

# Inisialisasi komponen
system_prompt = SystemPrompt()
replicate_api = ReplicateAPI()

# Mapping userbot name to system prompt name
# Default mapping: userbot1 -> AERIS, userbot2 -> KAIROS, etc.
USERBOT_PROMPT_MAPPING = {
    "userbot1": "AERIS",
    "userbot2": "KAIROS",
    "userbot3": "LYRA",
    "userbot4": "NOVA",
    "userbot5": "ZEKE"
}

# Bot manager hanya menerima perintah dari owner
@bot.on_message(filters.command(["start", "help"]))
async def start_command(client, message):
    """Handle start command for the manager bot"""
    await message.reply_text(
        "👋 Halo! Saya adalah bot manager untuk SyncaraBot.\n\n"
        "Bot ini mengelola userbot assistant yang melayani permintaan AI.\n\n"
        "Gunakan userbot assistant untuk berinteraksi dengan AI."
    )

@bot.on_message(filters.command("prompts") & filters.user(OWNER_ID))
async def list_prompts(client, message):
    """List all available system prompts"""
    try:
        available_prompts = system_prompt.get_available_prompts()
        
        if not available_prompts:
            await message.reply_text("Tidak ada system prompt yang tersedia.")
            return
            
        text = "📝 **Daftar System Prompt yang Tersedia:**\n\n"
        
        for i, prompt_name in enumerate(available_prompts, 1):
            text += f"{i}. **{prompt_name}**\n"
            
        # Add mapping info
        text += "\n🔄 **Mapping Userbot ke System Prompt:**\n\n"
        for userbot_name, prompt_name in USERBOT_PROMPT_MAPPING.items():
            text += f"- **{userbot_name}** → {prompt_name}\n"
            
        await message.reply_text(text)
        
    except Exception as e:
        console.error(f"Error in list_prompts: {str(e)}")
        await message.reply_text("Terjadi kesalahan saat mengambil daftar system prompt.")

@bot.on_message(filters.command("setprompt") & filters.user(OWNER_ID))
async def set_prompt_command(client, message):
    """Set system prompt for a userbot"""
    try:
        # Check command format
        if len(message.command) < 3:
            await message.reply_text("Gunakan: /setprompt [userbot_name] [prompt_name]")
            return
            
        # Get userbot name and prompt name
        userbot_name = message.command[1].lower()
        prompt_name = message.command[2].upper()
        
        # Check if userbot exists
        userbot_names = get_userbot_names()
        if userbot_name not in userbot_names:
            await message.reply_text(f"Userbot '{userbot_name}' tidak ditemukan.\n\nUserbot yang tersedia: {', '.join(userbot_names)}")
            return
            
        # Check if prompt exists
        available_prompts = system_prompt.get_available_prompts()
        if prompt_name not in available_prompts:
            await message.reply_text(f"System prompt '{prompt_name}' tidak ditemukan.\n\nPrompt yang tersedia: {', '.join(available_prompts)}")
            return
            
        # Update mapping
        USERBOT_PROMPT_MAPPING[userbot_name] = prompt_name
        await message.reply_text(f"Berhasil mengatur system prompt '{prompt_name}' untuk userbot '{userbot_name}'")
        
    except Exception as e:
        console.error(f"Error in set_prompt_command: {str(e)}")
        await message.reply_text("Terjadi kesalahan saat mengatur system prompt.")

# Userbot assistant menangani interaksi AI hanya ketika di-mention atau di-reply
async def setup_userbot_handlers():
    """Setup handlers for userbot assistant"""
    try:
        # Get all userbots
        userbots = get_all_userbots()
        if not userbots:
            console.error("No userbot available to set up handlers")
            return
            
        # Set up message handler for each userbot
        for userbot in userbots:
            userbot_name = userbot.name
            
            # Create custom filter for this specific userbot
            def create_userbot_filter(userbot_client):
                async def userbot_filter(_, __, message):
                    try:
                        # Skip messages from bots
                        if message.from_user and message.from_user.is_bot:
                            return False
                        
                        # Get userbot info
                        me = await userbot_client.get_me()
                        
                        # Check if in private chat
                        if message.chat.type == enums.ChatType.PRIVATE:
                            return True
                        
                        # Check if message is a reply to userbot's message
                        if message.reply_to_message:
                            if message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id:
                                return True
                        
                        # Check if userbot is mentioned in the message
                        if message.entities:
                            for entity in message.entities:
                                if entity.type == enums.MessageEntityType.MENTION:
                                    # Extract mentioned username
                                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                                    if mentioned_username == f"@{me.username}":
                                        return True
                                elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                                    # Check if mentioned user is this userbot
                                    if entity.user and entity.user.id == me.id:
                                        return True
                        
                        return False
                    except Exception as e:
                        console.error(f"Error in userbot filter: {str(e)}")
                        return False
                
                return filters.create(userbot_filter)
            
            # Apply the custom filter to this userbot
            userbot_filter = create_userbot_filter(userbot)
            
            @userbot.on_message(userbot_filter & (filters.text | filters.photo))
            async def userbot_message_handler(client, message):
                """Handle messages for userbot assistant when mentioned or replied"""
                try:
                    # Get text from either message text or caption
                    text = message.text or message.caption
                    
                    if not text:
                        return
                    
                    # Remove mention from text if exists
                    me = await client.get_me()
                    if f"@{me.username}" in text:
                        text = text.replace(f"@{me.username}", "").strip()
                    
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
            
            console.info(f"Userbot '{userbot_name}' handler set up successfully")
        
    except Exception as e:
        console.error(f"Error setting up userbot handlers: {str(e)}")

async def process_ai_response(client, message, prompt, photo_file_id=None):
    """Process AI response for userbot assistant"""
    try:
        # Get userbot information
        me = await client.get_me()
        userbot_name = client.name
        
        # Set the appropriate system prompt for this userbot
        prompt_name = USERBOT_PROMPT_MAPPING.get(userbot_name, "DEFAULT")
        system_prompt.set_prompt(prompt_name)
        
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