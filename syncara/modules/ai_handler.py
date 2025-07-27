# syncara/modules/ai_handler.py
from pyrogram import filters, enums
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from syncara.services import ReplicateAPI
from syncara import bot, assistant_manager, console
from config.config import OWNER_ID
from datetime import datetime, timedelta
import pytz
import json
from syncara.modules.assistant_memory import (
    kenalan_dan_update, 
    get_user_memory, 
    get_user_context, 
    learn_from_interaction,
    update_user_preferences,
    get_recent_conversations
)
from syncara.modules.ai_learning import ai_learning
from syncara.modules.canvas_manager import canvas_manager
from config.assistants_config import get_assistant_by_username, get_assistant_config
from syncara import autonomous_ai
import asyncio
from syncara.database import autonomous_tasks, user_patterns

# Inisialisasi komponen
replicate_api = ReplicateAPI()

# Cache untuk informasi userbot agar tidak flood API
USERBOT_INFO_CACHE = {}

# Mapping userbot name to system prompt name
USERBOT_PROMPT_MAPPING = {
    "SyncaraUbot": "AERIS",  # Default untuk userbot utama
}

# Konfigurasi untuk mengatur jumlah pesan riwayat
CHAT_HISTORY_CONFIG = {
    "enabled": True,
    "limit": 20,
    "include_media_info": True,
    "include_timestamps": True
}

# Debug logging untuk troubleshooting
DEBUG_MODE = False

def debug_log(message):
    """Debug logging helper"""
    if DEBUG_MODE:
        console.info(f"[DEBUG] {message}")

async def cache_userbot_info():
    """Cache userbot information to avoid API flood"""
    try:
        if not SESSION_STRING:
            console.warning("No session string configured for userbot")
            return None
            
        if userbot.name not in USERBOT_INFO_CACHE:
            me = await userbot.get_me()
            USERBOT_INFO_CACHE[userbot.name] = {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name
            }
            console.info(f"Cached info for userbot: {userbot.name} (@{me.username})")
        return USERBOT_INFO_CACHE[userbot.name]
    except Exception as e:
        console.error(f"Error caching userbot info: {str(e)}")
        return None

# Create custom filter for userbot interactions
async def userbot_filter(_, __, message):
    """Custom filter to detect userbot interactions"""
    try:
        # Skip messages from bots
        if message.from_user and message.from_user.is_bot:
            return False
        
        # Get userbot info from cache
        userbot_info = USERBOT_INFO_CACHE.get(userbot.name)
        if not userbot_info:
            userbot_info = await cache_userbot_info()
            if not userbot_info:
                return False
        
        # Check if in private chat
        if message.chat.type == enums.ChatType.PRIVATE:
            return True
        
        # Check if message is a reply to userbot's message
        if message.reply_to_message:
            if message.reply_to_message.from_user and message.reply_to_message.from_user.id == userbot_info['id']:
                return True
        
        # Check if userbot is mentioned in the message
        if message.entities:
            for entity in message.entities:
                if entity.type == enums.MessageEntityType.MENTION:
                    # Extract mentioned username
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                    if mentioned_username == f"@{userbot_info['username']}":
                        return True
                elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                    # Check if mentioned user is this userbot
                    if entity.user and entity.user.id == userbot_info['id']:
                        return True
        
        return False
    except Exception as e:
        console.error(f"Error in userbot filter: {str(e)}")
        return False

# Create the filter
custom_userbot_filter = filters.create(userbot_filter)

# Test handler untuk memastikan userbot menerima pesan - REMOVED to avoid conflicts
# @userbot.on_message(filters.all)
# async def test_all_messages(client, message):
#     """Test handler to see all messages received by userbot"""
#     try:
#         debug_log(f"🔔 USERBOT RECEIVED MESSAGE:")
#         debug_log(f"   From: {message.from_user.first_name if message.from_user else 'Unknown'}")
#         debug_log(f"   Chat: {message.chat.title if message.chat.title else 'Private'}")
#         debug_log(f"   Text: {message.text[:50] if message.text else 'No text'}...")
#         debug_log(f"   Message ID: {message.id}")
#         
#         # Also log to console for visibility
#         console.info(f"USERBOT MSG: {message.from_user.first_name if message.from_user else 'Unknown'} -> {message.text[:50] if message.text else 'No text'}")
#     except Exception as e:
#         debug_log(f"Error in test handler: {str(e)}")
#         console.error(f"Error in test handler: {str(e)}")

# Debug handler for all bot messages - REMOVED to avoid conflicts
# @bot.on_message(filters.all)
# async def debug_all_bot_messages(client, message):
#     """Debug handler to see all messages received by bot manager"""
#     try:
#         console.info(f"BOT MSG: {message.from_user.first_name if message.from_user else 'Unknown'} -> {message.text[:50] if message.text else 'No text'}")
#         debug_log(f"🔔 BOT RECEIVED MESSAGE:")
#         debug_log(f"   From: {message.from_user.first_name if message.from_user else 'Unknown'}")
#         debug_log(f"   Chat: {message.chat.title if message.chat.title else 'Private'}")
#         debug_log(f"   Text: {message.text[:50] if message.text else 'No text'}...")
#         debug_log(f"   Message ID: {message.id}")
#         
#         # Check if it's a command
#         if message.text and message.text.startswith('/'):
#             debug_log(f"🎯 COMMAND DETECTED: {message.text}")
#             console.info(f"COMMAND: {message.text}")
#     except Exception as e:
#         debug_log(f"Error in bot debug handler: {str(e)}")
#         console.error(f"Error in bot debug handler: {str(e)}")

# Universal trigger helper function
async def _trigger_user_save_for_command(client, message):
    """Universal trigger untuk save user data di bot commands"""
    try:
        if message and message.from_user:
            await kenalan_dan_update(client, message.from_user, send_greeting=False)
    except Exception as e:
        console.error(f"Error in command user save trigger: {e}")

# Bot manager commands
@bot.on_message(filters.command("start") | filters.command("help"))
async def start_command(client, message):
    """Handle start command for the manager bot dengan inline keyboard"""
    try:
        # 🚀 TRIGGER: Save user data for start/help command
        await _trigger_user_save_for_command(client, message)
        
        from syncara.modules.system_prompt import system_prompt
        current_prompt = system_prompt.current_prompt_name

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🧪 Test Bot", callback_data="menu_test"),
                InlineKeyboardButton("🧠 Prompt", callback_data="menu_prompt")
            ],
            [
                InlineKeyboardButton("🔧 Shortcodes", callback_data="menu_shortcodes"),
                InlineKeyboardButton("🛠️ Debug", callback_data="menu_debug")
            ],
            [
                InlineKeyboardButton("👤 Assistants", callback_data="menu_assistants")
            ]
        ])

        await message.reply(
            "🤖 <b>Halo! Saya adalah SyncaraBot Manager</b>\n\n"
            "🎯 Bot ini mengelola userbot assistant yang melayani permintaan AI.\n\n"
            f"🧠 <b>Current AI Personality:</b> {current_prompt}\n\n"
            "Silakan pilih menu di bawah ini:",
            reply_markup=keyboard
        )
    except Exception as e:
        console.error(f"Error in start_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat memproses perintah.")

@bot.on_callback_query()
async def menu_callback_handler(client, callback_query: CallbackQuery):
    """Handler untuk callback query menu utama"""
    data = callback_query.data
    try:
        if data == "menu_test":
            await callback_query.answer("Test command!")
            await callback_query.edit_message_text("✅ Test command berhasil! Bot berfungsi dengan baik.")
        elif data == "menu_prompt":
            from syncara.modules.system_prompt import system_prompt
            available_prompts = system_prompt.get_available_prompts()
            current_prompt = system_prompt.current_prompt_name
            response = f"🤖 <b>System Prompt Manager</b>\n\n"
            response += f"<b>Current:</b> {current_prompt}\n\n"
            response += f"<b>Available Prompts:</b>\n"
            for prompt in available_prompts:
                response += f"• {prompt}\n"
            response += f"\nGunakan perintah: <code>/prompt &lt;prompt_name&gt;</code> untuk mengganti."
            await callback_query.answer("Prompt info!")
            await callback_query.edit_message_text(response)
        elif data == "menu_shortcodes":
            from syncara.shortcode import registry
            response = f"🔧 <b>Shortcode Registry Status</b>\n\n"
            response += f"<b>Handlers:</b> {len(registry.shortcodes)}\n"
            response += f"<b>Descriptions:</b> {len(registry.descriptions)}\n\n"
            if registry.descriptions:
                response += "<b>Available Shortcodes:</b>\n"
                for shortcode, desc in registry.descriptions.items():
                    response += f"• <code>{shortcode}</code> - {desc}\n"
            else:
                response += "❌ No shortcodes available"
            await callback_query.answer("Shortcodes info!")
            await callback_query.edit_message_text(response)
        elif data == "menu_debug":
            debug_info = f"🔍 <b>Debug Info</b>\n\n"
            if USERBOT_INFO_CACHE:
                for name, info in USERBOT_INFO_CACHE.items():
                    debug_info += f"<b>Userbot {name}:</b>\n"
                    debug_info += f"• ID: <code>{info['id']}</code>\n"
                    debug_info += f"• Username: @{info['username']}\n"
                    debug_info += f"• Name: {info['first_name']}\n\n"
            else:
                debug_info += "❌ No userbot info cached\n\n"
            debug_info += f"<b>Prompt Mapping:</b>\n"
            for name, prompt in USERBOT_PROMPT_MAPPING.items():
                debug_info += f"• {name} → {prompt}\n"
            debug_info += f"\n<b>Config:</b>\n"
            debug_info += f"• SESSION_STRING: {'✅ Set' if SESSION_STRING else '❌ Not set'}\n"
            debug_info += f"• Chat History: {'✅ Enabled' if CHAT_HISTORY_CONFIG['enabled'] else '❌ Disabled'}\n"
            debug_info += f"• Debug Mode: {'✅ On' if DEBUG_MODE else '❌ Off'}\n"
            debug_info += f"\n<b>Handlers:</b>\n"
            debug_info += f"• Userbot handlers: {len(userbot.dispatcher.groups) if hasattr(userbot, 'dispatcher') else 'Unknown'}\n"
            debug_info += f"• Bot handlers: {len(callback_query._client.dispatcher.groups) if hasattr(callback_query._client, 'dispatcher') else 'Unknown'}\n"
            await callback_query.answer("Debug info!")
            await callback_query.edit_message_text(debug_info)
        elif data == "menu_assistants":
            from config.assistants_config import get_assistant_status
            status = get_assistant_status()
            response = "👤 <b>Status Semua Assistant</b>\n\n"
            for assistant_id, config in status.items():
                response += f"{config['emoji']} <b>{config['name']}</b> (@{config['username']}) - {'✅ Aktif' if config['enabled'] else '❌ Nonaktif'}\n"
                response += f"{config['description']}\n\n"
            await callback_query.answer("Assistants info!")
            await callback_query.edit_message_text(response)
        else:
            await callback_query.answer("Menu tidak dikenal!", show_alert=True)
    except Exception as e:
        await callback_query.answer("Terjadi error!", show_alert=True)
        await callback_query.edit_message_text(f"❌ Terjadi error: {str(e)}")

@bot.on_message(filters.command("debug") & filters.user(OWNER_ID))
async def debug_command(client, message):
    """Debug command to check AI handler status"""
    try:
        debug_info = f"🔍 **Debug Info:**\n\n"
        
        # Check userbot info cache
        if USERBOT_INFO_CACHE:
            for name, info in USERBOT_INFO_CACHE.items():
                debug_info += f"**Userbot {name}:**\n"
                debug_info += f"• ID: `{info['id']}`\n"
                debug_info += f"• Username: @{info['username']}\n"
                debug_info += f"• Name: {info['first_name']}\n\n"
        else:
            debug_info += "❌ No userbot info cached\n\n"
        
        # Check prompt mapping
        debug_info += f"**Prompt Mapping:**\n"
        for name, prompt in USERBOT_PROMPT_MAPPING.items():
            debug_info += f"• {name} → {prompt}\n"
        
        debug_info += f"\n**Config:**\n"
        debug_info += f"• SESSION_STRING: {'✅ Set' if SESSION_STRING else '❌ Not set'}\n"
        debug_info += f"• Chat History: {'✅ Enabled' if CHAT_HISTORY_CONFIG['enabled'] else '❌ Disabled'}\n"
        debug_info += f"• Debug Mode: {'✅ On' if DEBUG_MODE else '❌ Off'}\n"
        
        # Check handlers
        debug_info += f"\n**Handlers:**\n"
        debug_info += f"• Userbot handlers: {len(userbot.dispatcher.groups) if hasattr(userbot, 'dispatcher') else 'Unknown'}\n"
        debug_info += f"• Bot handlers: {len(client.dispatcher.groups) if hasattr(client, 'dispatcher') else 'Unknown'}\n"
        
        await message.reply_text(debug_info)
        
    except Exception as e:
        console.error(f"Error in debug command: {str(e)}")
        await message.reply_text(f"❌ Debug error: {str(e)}")

@bot.on_message(filters.command("test"))
async def test_command(client, message):
    """Simple test command"""
    try:
        await message.reply_text("✅ Test command berhasil! Bot berfungsi dengan baik.")
    except Exception as e:
        console.error(f"Error in test_command: {str(e)}")

@bot.on_message(filters.command("prompt") & filters.user(OWNER_ID))
async def change_prompt_command(client, message):
    """Change system prompt"""
    try:
        from syncara.modules.system_prompt import system_prompt
        
        # Parse command: /prompt <prompt_name>
        args = message.text.split()
        if len(args) < 2:
            available_prompts = system_prompt.get_available_prompts()
            current_prompt = system_prompt.current_prompt_name
            
            response = f"🤖 **System Prompt Manager**\n\n"
            response += f"**Current:** {current_prompt}\n\n"
            response += f"**Available Prompts:**\n"
            for prompt in available_prompts:
                response += f"• {prompt}\n"
            response += f"\n**Usage:** `/prompt <prompt_name>`"
            
            await message.reply_text(response)
            return
        
        prompt_name = args[1].upper()
        if system_prompt.set_prompt(prompt_name):
            await message.reply_text(f"✅ System prompt changed to: **{prompt_name}**")
        else:
            await message.reply_text(f"❌ Prompt '{prompt_name}' not found!")
            
    except Exception as e:
        console.error(f"Error in change_prompt_command: {str(e)}")
        await message.reply_text("❌ Error changing prompt")

@bot.on_message(filters.command("shortcodes") & filters.user(OWNER_ID))
async def shortcodes_command(client, message):
    """Show available shortcodes"""
    try:
        from syncara.shortcode import registry
        
        response = f"🔧 **Shortcode Registry Status**\n\n"
        response += f"**Handlers:** {len(registry.shortcodes)}\n"
        response += f"**Descriptions:** {len(registry.descriptions)}\n\n"
        
        if registry.descriptions:
            response += "**Available Shortcodes:**\n"
            for shortcode, desc in registry.descriptions.items():
                response += f"• `{shortcode}` - {desc}\n"
        else:
            response += "❌ No shortcodes available"
        
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in shortcodes_command: {str(e)}")
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("test_userbot") & filters.user(OWNER_ID))
async def test_userbot_command(client, message):
    """Test userbot functionality"""
    try:
        if not SESSION_STRING:
            await message.reply_text("⚠️ Userbot tidak dikonfigurasi.")
            return
            
        # Test sending message from userbot
        test_msg = await userbot.send_message(
            chat_id=message.chat.id,
            text="🧪 **Test Message dari Userbot**\n\nJika Anda melihat pesan ini, userbot berfungsi dengan baik!"
        )
        
        await message.reply_text(
            f"✅ **Test berhasil!**\n\n"
            f"Userbot berhasil mengirim pesan dengan ID: `{test_msg.id}`\n\n"
            f"Sekarang coba reply atau mention userbot untuk test AI handler."
        )
        
    except Exception as e:
        console.error(f"Error in test_userbot_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("analytics") & filters.user(OWNER_ID))
async def analytics_command(client, message):
    """Show AI learning analytics"""
    try:
        # Get analytics for all users or specific user
        args = message.text.split()
        if len(args) > 1:
            # Specific user analytics
            try:
                user_id = int(args[1])
                insights = await ai_learning.get_learning_insights(user_id)
                if insights:
                    await message.reply_text(
                        f"📊 **Analytics untuk User {user_id}**\n\n"
                        f"Total Interaksi: {insights['total_interactions']}\n"
                        f"Percakapan: {insights['conversation_count']}\n"
                        f"Patterns: {json.dumps(insights['patterns'], indent=2, default=str)}"
                    )
                else:
                    await message.reply_text(f"❌ Tidak ada data untuk user {user_id}")
            except ValueError:
                await message.reply_text("❌ Format: /analytics [user_id]")
        else:
            # General analytics
            await message.reply_text(
                "📊 **AI Learning Analytics**\n\n"
                "Gunakan:\n"
                "• `/analytics [user_id]` - Lihat analytics user tertentu\n"
                "• `/learning_insights [user_id]` - Lihat insight pembelajaran\n"
                "• `/user_patterns [user_id]` - Lihat pola penggunaan user"
            )
    except Exception as e:
        console.error(f"Error in analytics_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil analytics.")

@bot.on_message(filters.command("learning_insights") & filters.user(OWNER_ID))
async def learning_insights_command(client, message):
    """Show detailed learning insights"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("❌ Format: /learning_insights [user_id]")
            return
        
        user_id = int(args[1])
        insights = await ai_learning.get_learning_insights(user_id)
        
        if not insights:
            await message.reply_text(f"❌ Tidak ada data learning untuk user {user_id}")
            return
        
        patterns = insights.get('patterns', {})
        
        # Format insights
        insight_text = f"🧠 **Learning Insights untuk User {user_id}**\n\n"
        
        # Question patterns
        if patterns.get('question_types'):
            insight_text += "❓ **Tipe Pertanyaan Favorit:**\n"
            for qtype, count in patterns['question_types'][:3]:
                insight_text += f"• {qtype}: {count}x\n"
            insight_text += "\n"
        
        # Topic patterns
        if patterns.get('topics'):
            insight_text += "📚 **Topik yang Disukai:**\n"
            for topic, count in patterns['topics'][:3]:
                insight_text += f"• {topic}: {count}x\n"
            insight_text += "\n"
        
        # Response preferences
        if patterns.get('response_preferences'):
            prefs = patterns['response_preferences']
            insight_text += "💬 **Preferensi Respons:**\n"
            insight_text += f"• Panjang: {prefs.get('preferred_length', 'medium')}\n"
            insight_text += f"• Emoji: {'Ya' if prefs.get('likes_emoji') else 'Tidak'}\n"
            insight_text += "\n"
        
        # Time patterns
        if patterns.get('time_patterns'):
            time_pats = patterns['time_patterns']
            if time_pats.get('peak_hours'):
                insight_text += "⏰ **Jam Puncak Aktivitas:**\n"
                for hour, count in time_pats['peak_hours']:
                    insight_text += f"• Jam {hour}:00 ({count}x)\n"
        
        await message.reply_text(insight_text)
        
    except Exception as e:
        console.error(f"Error in learning_insights_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil learning insights.")

@bot.on_message(filters.command("assistants") & filters.user(OWNER_ID))
async def assistants_command(client, message):
    """Show status semua assistant"""
    try:
        status = get_assistant_status()
        active_assistants = assistant_manager.get_active_assistants()
        
        response = "🤖 **SYNCARABOT ASSISTANTS STATUS**\n\n"
        
        for assistant_id, info in status.items():
            emoji = info["emoji"]
            name = info["name"]
            username = info["username"]
            enabled = "✅" if info["enabled"] else "❌"
            has_session = "✅" if info["has_session"] else "❌"
            active = "🟢" if assistant_id in active_assistants else "🔴"
            description = info["description"]
            
            response += f"{emoji} **{name}** (@{username})\n"
            response += f"   Status: {enabled} Enabled | {has_session} Session | {active} Active\n"
            response += f"   Description: {description}\n\n"
        
        response += f"📊 **Total Active:** {len(active_assistants)}/{len(status)}\n"
        response += f"📋 **Commands:**\n"
        response += f"• `/assistants` - Lihat status assistant\n"
        response += f"• `/assistant_info [ASSISTANT]` - Info detail assistant\n"
        response += f"• `/test_assistant [ASSISTANT]` - Test assistant tertentu"
        
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in assistants_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil status assistant.")

@bot.on_message(filters.command("assistant_info") & filters.user(OWNER_ID))
async def assistant_info_command(client, message):
    """Show info detail assistant tertentu"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("❌ Format: /assistant_info [ASSISTANT]")
            return
        
        assistant_id = args[1].upper()
        assistant = assistant_manager.get_assistant(assistant_id)
        config = assistant_manager.get_assistant_config(assistant_id)
        
        if not config:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak ditemukan!")
            return
        
        response = f"{config['emoji']} **{config['name']} ASSISTANT INFO**\n\n"
        response += f"**Username:** @{config['username']}\n"
        response += f"**Personality:** {config['personality']}\n"
        response += f"**Description:** {config['description']}\n"
        response += f"**Enabled:** {'✅' if config['enabled'] else '❌'}\n"
        response += f"**Has Session:** {'✅' if config['session_string'] else '❌'}\n"
        response += f"**Active:** {'🟢' if assistant else '🔴'}\n\n"
        
        if assistant:
            try:
                me = await assistant.get_me()
                response += f"**Connection Info:**\n"
                response += f"• ID: {me.id}\n"
                response += f"• Name: {me.first_name}\n"
                response += f"• Username: @{me.username}\n"
                response += f"• Status: Online 🟢\n"
            except Exception as e:
                response += f"**Connection Info:**\n"
                response += f"• Status: Error ❌\n"
                response += f"• Error: {str(e)[:50]}...\n"
        
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in assistant_info_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat mengambil info assistant.")

@bot.on_message(filters.command("test_assistant") & filters.user(OWNER_ID))
async def test_assistant_command(client, message):
    """Test assistant tertentu"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("❌ Format: /test_assistant [ASSISTANT]")
            return
        
        assistant_id = args[1].upper()
        assistant = assistant_manager.get_assistant(assistant_id)
        config = assistant_manager.get_assistant_config(assistant_id)
        
        if not config:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak ditemukan!")
            return
        
        if not config["enabled"]:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak enabled!")
            return
        
        if not assistant:
            await message.reply_text(f"❌ Assistant {assistant_id} tidak active!")
            return
        
        # Test sending message
        try:
            test_msg = await assistant.send_message(
                chat_id=message.chat.id,
                text=f"🧪 **Test Message dari {config['name']}**\n\nAssistant ini berfungsi dengan baik! {config['emoji']}"
            )
            
            await message.reply_text(
                f"✅ **Test berhasil!**\n\n"
                f"Assistant {config['name']} berhasil mengirim pesan dengan ID: `{test_msg.id}`\n\n"
                f"Sekarang coba mention @{config['username']} untuk test AI handler."
            )
            
        except Exception as e:
            await message.reply_text(f"❌ Test error: {str(e)}")
        
    except Exception as e:
        console.error(f"Error in test_assistant_command: {str(e)}")
        await message.reply_text("❌ Terjadi kesalahan saat test assistant.")

# Multi-assistant message handler
async def setup_assistant_handlers():
    """Setup handlers untuk semua assistant"""
    try:
        active_assistants = assistant_manager.get_active_assistants()
        
        for assistant_id in active_assistants:
            assistant = assistant_manager.get_assistant(assistant_id)
            config = assistant_manager.get_assistant_config(assistant_id)
            
            if not assistant or not config:
                continue
            
            # Create custom filter untuk assistant ini
            def create_assistant_filter(assistant_config):
                async def assistant_filter(_, __, message):
                    """Custom filter untuk assistant tertentu"""
                    try:
                        # Skip messages from bots
                        if message.from_user and message.from_user.is_bot:
                            return False
                        
                        # Skip messages from other assistants
                        if message.from_user and message.from_user.username:
                            try:
                                # Get all assistant usernames
                                all_assistants = assistant_manager.get_all_assistants()
                                assistant_usernames = []
                                for config in all_assistants.values():
                                    username = config.get("username") if isinstance(config, dict) else getattr(config, "username", None)
                                    if username:
                                        assistant_usernames.append(username)
                                
                                # If message is from another assistant, skip
                                if message.from_user.username in assistant_usernames:
                                    return False
                            except Exception as e:
                                console.error(f"Error checking assistant usernames: {e}")
                        
                        # Check if in private chat
                        if message.chat.type == enums.ChatType.PRIVATE:
                            return True
                        
                        # Check if assistant is mentioned
                        if message.entities:
                            for entity in message.entities:
                                if entity.type == enums.MessageEntityType.MENTION:
                                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                                    if mentioned_username == f"@{assistant_config.get('username', '')}":
                                        return True
                                elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                                    # Check if mentioned user is this assistant
                                    if entity.user and entity.user.username == assistant_config.get('username', ''):
                                        return True
                        
                        # Check if message is a reply to assistant's message
                        if message.reply_to_message:
                            if message.reply_to_message.from_user and message.reply_to_message.from_user.username == assistant_config.get('username', ''):
                                return True
                        
                        return False
                    except Exception as e:
                        console.error(f"Error in assistant filter: {str(e)}")
                        return False
                return assistant_filter
            
            # Create filter instance
            custom_filter = filters.create(create_assistant_filter(config))
            
            # Group message handler
            def create_message_handler(assistant_config):
                async def assistant_message_handler(client, message):
                    """Handle messages for specific assistant"""
                    try:
                        # 🚀 TAMBAH TRIGGER: Auto-kenalan & save user data untuk group messages
                        if message.from_user:
                            await kenalan_dan_update(client, message.from_user, send_greeting=False)
                        
                        # Get text from either message text or caption
                        text = message.text or message.caption
                        
                        if not text:
                            return
                        
                        # Remove assistant mention from text
                        if f"@{assistant_config['username']}" in text:
                            text = text.replace(f"@{assistant_config['username']}", "").strip()
                        
                        # Get photo if exists
                        photo_file_id = None
                        if message.photo:
                            photo_file_id = message.photo.file_id
                        
                        # Send typing action
                        await client.send_chat_action(
                            chat_id=message.chat.id,
                            action=enums.ChatAction.TYPING
                        )
                        
                        # Process AI response with specific personality
                        await process_ai_response_with_personality(client, message, text, photo_file_id, assistant_config['personality'])
                        
                    except Exception as e:
                        console.error(f"Error in {assistant_config['name']} message handler: {str(e)}")
                return assistant_message_handler
            
            # Private message handler
            def create_private_handler(assistant_config):
                async def assistant_private_handler(client, message):
                    """Handler for private messages to specific assistant"""
                    try:
                        # Tambahkan auto-kenalan & ingatan
                        if message.from_user:
                            await kenalan_dan_update(client, message.from_user)
                        
                        # Process AI response with specific personality
                        await process_ai_response_with_personality(client, message, message.text, None, assistant_config['personality'])
                        
                    except Exception as e:
                        console.error(f"Error in {assistant_config['name']} private handler: {str(e)}")
                        # Fallback response
                        await client.send_message(
                            chat_id=message.chat.id,
                            text=f"❌ Maaf, terjadi kesalahan saat memproses pesan Anda. - {assistant_config['name']}",
                            reply_to_message_id=message.id
                        )
                return assistant_private_handler
            
            # Register handlers
            assistant.add_handler(MessageHandler(create_message_handler(config), custom_filter & (filters.text | filters.photo)))
            assistant.add_handler(MessageHandler(create_private_handler(config), filters.text & filters.private))
            
            console.info(f"✅ Handlers setup untuk {config['name']} (@{config['username']})")
        
    except Exception as e:
        console.error(f"Error setting up assistant handlers: {str(e)}")

async def process_ai_response_with_personality(client, message, prompt, photo_file_id=None, personality="AERIS"):
    """Process AI response dengan personality tertentu"""
    try:
        # Set personality untuk response ini
        from syncara.modules.system_prompt import system_prompt
        original_prompt = system_prompt.current_prompt_name
        system_prompt.set_prompt(personality)
        
        # Process AI response seperti biasa
        await process_ai_response(client, message, prompt, photo_file_id)
        
        # Restore original personality
        system_prompt.set_prompt(original_prompt)
        
    except Exception as e:
        console.error(f"Error in process_ai_response_with_personality: {str(e)}")
        await client.send_message(
            chat_id=message.chat.id,
            text="❌ Maaf, terjadi kesalahan saat memproses permintaan Anda.",
            reply_to_message_id=message.id
        )

# Rest of the functions remain the same...
async def get_chat_history(client, chat_id, limit=None):
    """Get chat history with detailed information including message ID, user ID, and reply info"""
    try:
        # Check if history is enabled
        if not CHAT_HISTORY_CONFIG["enabled"]:
            return []
            
        # Use configured limit if not specified
        if limit is None:
            limit = CHAT_HISTORY_CONFIG["limit"]
        
        messages = []
        
        # Get userbot info from cache
        userbot_name = getattr(client, 'name', 'unknown')
        userbot_info = USERBOT_INFO_CACHE.get(userbot_name)
        
        if not userbot_info:
            # Fallback: get info but with rate limiting
            try:
                me = await client.get_me()
                userbot_info = {
                    'id': me.id,
                    'username': me.username,
                    'first_name': me.first_name,
                    'last_name': me.last_name
                }
                USERBOT_INFO_CACHE[userbot_name] = userbot_info
            except Exception as e:
                console.error(f"Error getting userbot info: {str(e)}")
                return []
        
        # Get chat info
        try:
            chat = await client.get_chat(chat_id)
            chat_info = {
                'id': chat.id,
                'title': chat.title if chat.title else "Private Chat",
                'type': chat.type.name,
                'username': chat.username if hasattr(chat, 'username') else None
            }
        except Exception as e:
            console.error(f"Error getting chat info: {str(e)}")
            chat_info = {
                'id': chat_id,
                'title': "Unknown Chat",
                'type': "unknown",
                'username': None
            }
        
        # Get timezone for timestamp formatting
        tz = pytz.timezone('Asia/Jakarta')
        
        async for message in client.get_chat_history(chat_id, limit=limit):
            try:
                # Skip service messages
                if message.service:
                    continue
                
                # Get message content
                content = message.text or message.caption or ""
                
                # Handle media messages
                if not content.strip() and CHAT_HISTORY_CONFIG["include_media_info"]:
                    if message.photo:
                        content = "[Foto]"
                    elif message.video:
                        content = "[Video]"
                    elif message.document:
                        content = f"[Dokumen: {message.document.file_name or 'Unknown'}]"
                    elif message.audio:
                        content = "[Audio]"
                    elif message.voice:
                        content = "[Voice Note]"
                    elif message.sticker:
                        content = f"[Sticker: {message.sticker.emoji or ''}]"
                    elif message.animation:
                        content = "[GIF]"
                    else:
                        content = "[Media]"
                
                # Skip if still empty
                if not content.strip():
                    continue
                
                # Get sender info with detailed information
                sender_info = {
                    'id': None,
                    'name': "Unknown",
                    'username': None,
                    'is_bot': False,
                    'is_assistant': False
                }
                
                if message.from_user:
                    sender_info = {
                        'id': message.from_user.id,
                        'name': message.from_user.first_name or "Unknown",
                        'username': message.from_user.username,
                        'is_bot': message.from_user.is_bot,
                        'is_assistant': message.from_user.id == userbot_info['id']
                    }
                    
                    # Add assistant label
                    if sender_info['is_assistant']:
                        sender_info['display_name'] = f"{userbot_info['first_name']} (Assistant)"
                    else:
                        sender_info['display_name'] = sender_info['name']
                        
                elif message.sender_chat:
                    sender_info = {
                        'id': message.sender_chat.id,
                        'name': message.sender_chat.title or "Channel",
                        'username': message.sender_chat.username,
                        'is_bot': False,
                        'is_assistant': False,
                        'display_name': message.sender_chat.title or "Channel"
                    }
                
                # Get reply info if exists
                reply_info = None
                if message.reply_to_message:
                    reply_msg = message.reply_to_message
                    reply_sender_info = {
                        'id': None,
                        'name': "Unknown",
                        'username': None
                    }
                    
                    if reply_msg.from_user:
                        reply_sender_info = {
                            'id': reply_msg.from_user.id,
                            'name': reply_msg.from_user.first_name or "Unknown",
                            'username': reply_msg.from_user.username
                        }
                        
                        # Check if reply is to assistant
                        if reply_msg.from_user.id == userbot_info['id']:
                            reply_sender_info['display_name'] = f"{userbot_info['first_name']} (Assistant)"
                        else:
                            reply_sender_info['display_name'] = reply_sender_info['name']
                            
                    elif reply_msg.sender_chat:
                        reply_sender_info = {
                            'id': reply_msg.sender_chat.id,
                            'name': reply_msg.sender_chat.title or "Channel",
                            'username': reply_msg.sender_chat.username,
                            'display_name': reply_msg.sender_chat.title or "Channel"
                        }
                    
                    reply_content = reply_msg.text or reply_msg.caption or "[Media]"
                    if len(reply_content) > 100:
                        reply_content = reply_content[:100] + "..."
                    
                    reply_info = {
                        'message_id': reply_msg.id,
                        'sender': reply_sender_info,
                        'content': reply_content
                    }
                
                # Add to messages list with all detailed info
                messages.append({
                    'message_id': message.id,
                    'sender': sender_info,
                    'chat': chat_info,
                    'content': content,
                    'timestamp': message.date.astimezone(tz),
                    'reply_to': reply_info
                })
                
            except Exception as e:
                console.error(f"Error processing message in history: {str(e)}")
                continue
        
        # Reverse to get chronological order (oldest first)
        messages.reverse()
        
        return messages
        
    except Exception as e:
        console.error(f"Error getting chat history: {str(e)}")
        return []

def format_chat_history(messages):
    """Format chat history for AI context with detailed information"""
    try:
        if not messages:
            return ""
        
        # Check if history is enabled
        if not CHAT_HISTORY_CONFIG["enabled"]:
            return ""
        
        # Get chat info from first message if available
        chat_info = None
        if messages and 'chat' in messages[0]:
            chat_info = messages[0]['chat']
        
        formatted_history = []
        
        # Add header with chat information if available
        if chat_info:
            formatted_history.append(f"📍 **Grup:** {chat_info['title']}")
            formatted_history.append(f"🆔 **Chat ID:** `{chat_info['id']}`")
            if chat_info.get('username'):
                formatted_history.append(f"👤 **Username:** @{chat_info['username']}")
            formatted_history.append("─" * 40)
        
        for msg in messages:
            timestamp = msg['timestamp'].strftime("%H:%M") if CHAT_HISTORY_CONFIG["include_timestamps"] else ""
            
            # Build sender info with detailed information
            sender_name = msg['sender']['display_name']
            sender_details = f"[ID:{msg['sender']['id']}"
            if msg['sender']['username']:
                sender_details += f" | @{msg['sender']['username']}"
            sender_details += "]"
            
            # Build message line
            message_line = f"[{timestamp}] "
            
            # Add reply info if exists
            if msg.get('reply_to'):
                reply = msg['reply_to']
                reply_sender = reply['sender']['display_name']
                reply_details = f"[ID:{reply['sender']['id']}"
                if reply['sender']['username']:
                    reply_details += f" | @{reply['sender']['username']}"
                reply_details += "]"
                
                # Truncate reply content
                reply_content = reply['content']
                if len(reply_content) > 50:
                    reply_content = reply_content[:50] + "..."
                
                message_line += f"↪️ Reply to #{reply['message_id']} from {reply_sender} {reply_details}: \"{reply_content}\" → "
            
            # Add main message with message ID
            if 'message_id' in msg:
                message_line += f"#{msg['message_id']} 〈 {sender_name} {sender_details} 〉: {msg['content']}"
            else:
                # Fallback for older format
                message_line += f"〈 {sender_name} {sender_details} 〉: {msg['content']}"
            
            formatted_history.append(message_line)
        
        return "\n".join(formatted_history)
        
    except Exception as e:
        console.error(f"Error formatting chat history: {str(e)}")
        return ""

async def process_canvas_command(prompt):
    prompt_lower = prompt.lower()
    if prompt_lower.startswith("buat file"):
        # Contoh: "Buat file test.md isinya Hello World"
        parts = prompt.split(" ", 3)
        if len(parts) >= 4:
            filename = parts[2]
            content = parts[3].replace("isinya", "").strip()
            file = canvas_manager.create_file(filename, filetype=filename.split(".")[-1], content=content)
            return f"✅ File `{filename}` berhasil dibuat!\n\n{file.get_content()}"
        else:
            return "Format perintah kurang lengkap."
    elif prompt_lower.startswith("tampilkan file"):
        # Contoh: "Tampilkan file test.md"
        parts = prompt.split(" ", 2)
        if len(parts) >= 3:
            filename = parts[2]
            file = canvas_manager.get_file(filename)
            if file:
                return f"📄 Isi file `{filename}`:\n\n{file.get_content()}"
            else:
                return "File tidak ditemukan."
        else:
            return "Format perintah kurang lengkap."
    elif prompt_lower.startswith("edit file"):
        # Contoh: "Edit file test.md jadi ..."
        parts = prompt.split(" ", 3)
        if len(parts) >= 4:
            filename = parts[2]
            new_content = parts[3].replace("jadi", "").strip()
            file = canvas_manager.get_file(filename)
            if file:
                file.update_content(new_content)
                return f"✏️ File `{filename}` berhasil diupdate!\n\n{file.get_content()}"
            else:
                return "File tidak ditemukan."
        else:
            return "Format perintah kurang lengkap."
    elif prompt_lower.startswith("list file"):
        files = canvas_manager.list_files()
        if files:
            return "📂 Daftar file virtual:\n" + "\n".join(f"- {f}" for f in files)
        else:
            return "Belum ada file virtual yang dibuat."
    elif prompt_lower.startswith("export file"):
        # Contoh: "Export file test.md"
        parts = prompt.split(" ", 2)
        if len(parts) >= 3:
            filename = parts[2]
            file = canvas_manager.get_file(filename)
            if file:
                return f"📤 Export file `{filename}`:\n\n{file.export()}"
            else:
                return "File tidak ditemukan."
        else:
            return "Format perintah kurang lengkap."
    return None

async def process_ai_response(client, message, prompt, photo_file_id=None):
    """Process AI response using Replicate API with system prompt, chat history, and user memory"""
    try:
        # Send typing action
        await client.send_chat_action(
            chat_id=message.chat.id,
            action=enums.ChatAction.TYPING
        )
        
        # Get system prompt
        from syncara.modules.system_prompt import system_prompt

        # Dapatkan assistant config berdasarkan username client (jika ada)
        assistant_id = get_assistant_by_username(getattr(client, 'name', 'AERIS')) or 'AERIS'
        assistant_config = get_assistant_config(assistant_id) or {}
        
        # Ambil parameter model dari config, fallback ke default
        temperature = assistant_config.get('temperature', 1)
        presence_penalty = assistant_config.get('presence_penalty', 0)
        frequency_penalty = assistant_config.get('frequency_penalty', 0)

        # Prepare context for system prompt
        context = {
            'bot_name': 'AERIS',
            'bot_username': 'Aeris_sync',
            'user_id': message.from_user.id if message.from_user else 0
        }
        
        # Ambil ingatan user dari database dengan context yang lebih lengkap
        user_context = None
        if message.from_user:
            user_context = await get_user_context(message.from_user.id)
        
        # Tambahkan info user context ke context jika ada
        if user_context:
            context['user_context'] = user_context

        system_prompt_text = system_prompt.get_chat_prompt(context)
        
        # Personalisasi prompt berdasarkan learning patterns
        if message.from_user:
            system_prompt_text = await ai_learning.get_personalized_prompt(
                message.from_user.id, 
                system_prompt_text
            )
        
        # Get chat history for context
        chat_history = await get_chat_history(client, message.chat.id)
        formatted_history = format_chat_history(chat_history)
        
        # Prepare full prompt with context
        full_prompt = prompt
        
        # Add chat history and user context if available
        if formatted_history or user_context:
            full_prompt = ""
            if formatted_history:
                full_prompt += f"📝 **Chat History:**\n{formatted_history}\n"
            if user_context:
                user_info = user_context.get('user_info', {})
                preferences = user_context.get('preferences', {})
                
                full_prompt += f"\n🧠 **User Context:**\n"
                full_prompt += f"Nama: {user_info.get('name', '')} | Username: @{user_info.get('username', '')}\n"
                full_prompt += f"Interaksi ke: {user_info.get('interaction_count', 0)}\n"
                full_prompt += f"Gaya Komunikasi: {preferences.get('communication_style', 'default')}\n"
                full_prompt += f"Panjang Respons: {preferences.get('response_length', 'medium')}\n"
                full_prompt += f"Gunakan Emoji: {preferences.get('emoji_usage', True)}\n"
                
                if user_context.get('personality_notes'):
                    full_prompt += f"Catatan Kepribadian: {user_context['personality_notes']}\n"
                
                # Add recent conversation context
                recent_convos = user_context.get('recent_conversations', [])
                if recent_convos:
                    full_prompt += f"\n📚 **Recent Conversations:**\n"
                    for conv in recent_convos[-2:]:  # Last 2 conversations
                        full_prompt += f"- User: {conv.get('message', '')[:80]}...\n"
                        full_prompt += f"- AI: {conv.get('response', '')[:80]}...\n"
            
            full_prompt += f"\n💬 **Current Message:**\n{prompt}"
        
        # Cek perintah canvas sebelum proses AI
        canvas_result = await process_canvas_command(prompt)
        if canvas_result:
            await client.send_message(chat_id=message.chat.id, text=canvas_result, reply_to_message_id=message.id)
            return
        
        # Generate AI response using Replicate
        console.info(f"Generating AI response for: {prompt[:50]}...")
        
        ai_response = await replicate_api.generate_response(
            prompt=full_prompt,
            system_prompt=system_prompt_text,
            temperature=temperature,
            max_tokens=2048,
            image_file_id=photo_file_id,
            client=client,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty
        )
        
        # Process shortcodes in AI response
        try:
            from syncara.shortcode import registry
            console.info(f"Shortcode registry loaded with {len(registry.shortcodes)} handlers")
            processed_response = await process_shortcodes_in_response(ai_response, client, message)
        except ImportError as e:
            console.error(f"Import error for shortcode registry: {e}")
            processed_response = ai_response
        except Exception as e:
            console.error(f"Error processing shortcodes: {e}")
            processed_response = ai_response
        
        # Send the AI response
        await client.send_message(
            chat_id=message.chat.id,
            text=f"{processed_response}",
            reply_to_message_id=message.id
        )
        
        # Learn from this interaction for future improvements
        if message.from_user:
            await learn_from_interaction(
                message.from_user.id,
                prompt,
                processed_response
            )
        
        console.info("✅ AI response sent successfully")
        
    except Exception as e:
        console.error(f"Error in process_ai_response: {str(e)}")
        # Fallback response
        await client.send_message(
            chat_id=message.chat.id,
            text=f"❌ Maaf, terjadi kesalahan saat memproses permintaan Anda.\n\nError: {str(e)[:100]}...",
            reply_to_message_id=message.id
        )

async def process_shortcodes_in_response(response_text, client, message):
    """Process shortcodes in AI response and execute them"""
    try:
        import re
        from syncara.shortcode import registry
        
        # Pattern to match shortcodes like [CATEGORY:ACTION] or [CATEGORY:ACTION:params]
        shortcode_pattern = r'\[([A-Z]+:[A-Z_]+)(?::([^\]]*))?\]'
        
        # Find all shortcodes first for validation
        all_matches = list(re.finditer(shortcode_pattern, response_text))
        shortcode_names = [match.group(1).strip() for match in all_matches]
        
        # If no shortcodes found, return original response
        if not all_matches:
            return response_text
        
        # Validate shortcode execution order
        validation = registry.validate_shortcode_order(shortcode_names)
        if not validation['valid']:
            console.warning("Shortcode execution order issues detected:")
            for issue in validation['issues']:
                console.warning(f"  - {issue}")
        
        # Collect execution results
        execution_results = []
        successful_executions = []
        failed_executions = []
        created_files = []
        pending_images = []
        pending_responses = []
        
        async def execute_shortcode_silent(match):
            """Execute shortcode without sending files immediately"""
            full_shortcode = match.group(0)  # Full match like [USER:PROMOTE:7691971162] or [CHANNEL:START]
            shortcode_name = match.group(1).strip()  # USER:PROMOTE or CHANNEL:START
            params_str = match.group(2)  # 7691971162 or None
            
            # Handle None params (for shortcodes without parameters)
            if params_str is None:
                params_str = ""
            else:
                params_str = params_str.strip()
            
            console.info(f"Processing shortcode: {shortcode_name} with params: '{params_str}'")
            
            # Execute shortcode with params as string
            try:
                result = await registry.execute_shortcode(shortcode_name, client, message, params_str)
                
                execution_result = {
                    'shortcode': shortcode_name,
                    'params': params_str,
                    'success': result,
                    'full_match': full_shortcode
                }
                
                execution_results.append(execution_result)
                
                if result:
                    console.info(f"Shortcode {shortcode_name} executed successfully")
                    successful_executions.append(shortcode_name)
                    
                    # Track results based on shortcode type
                    if shortcode_name == 'CANVAS:CREATE':
                        filename = params_str.split(':')[0] if ':' in params_str else params_str
                        created_files.append(filename)
                        console.info(f"File {filename} added to pending send list")
                    elif shortcode_name == 'IMAGE:GEN':
                        if isinstance(result, str):
                            pending_images.append(result)
                            console.info(f"Image {result} added to pending send list")
                    elif shortcode_name.startswith(('USERBOT:', 'GROUP:', 'USER:')):
                        if isinstance(result, str):
                            pending_responses.append(result)
                            console.info(f"Response {result} added to pending send list")
                    elif shortcode_name.startswith(('PYTHON:', 'CODE:', 'CALC:')):
                        if isinstance(result, str):
                            pending_responses.append(result)
                            console.info(f"Python result {result} added to pending send list")
                    elif shortcode_name.startswith(('SEARCH:', 'FILE:', 'FIND:', 'CHAT:')):
                        if isinstance(result, str):
                            pending_responses.append(result)
                            console.info(f"Search result {result} added to pending send list")
                    elif shortcode_name.startswith(('TODO:')):
                        if isinstance(result, str):
                            pending_responses.append(result)
                            console.info(f"TODO result {result} added to pending send list")
                    
                    return ""  # Remove shortcode from text without replacement
                else:
                    console.error(f"Shortcode {shortcode_name} failed")
                    failed_executions.append(shortcode_name)
                    return ""  # Remove shortcode from text without replacement
                    
            except Exception as e:
                console.error(f"Error executing shortcode {shortcode_name}: {str(e)}")
                failed_executions.append(shortcode_name)
                execution_results.append({
                    'shortcode': shortcode_name,
                    'params': params_str,
                    'success': False,
                    'error': str(e),
                    'full_match': full_shortcode
                })
                return ""  # Remove shortcode from text without replacement
        
        # Process shortcodes one by one since re.sub doesn't support async
        processed_response = response_text
        matches = list(re.finditer(shortcode_pattern, response_text))
        
        # Process in reverse order to avoid index issues
        for match in reversed(matches):
            replacement = await execute_shortcode_silent(match)
            start, end = match.span()
            processed_response = processed_response[:start] + replacement + processed_response[end:]
        
        # Clean up extra whitespace and newlines
        processed_response = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_response)
        processed_response = processed_response.strip()
        
        # Schedule delayed sending for all types of results
        if created_files or pending_images or pending_responses:
            # Schedule file sending after AI response is sent
            asyncio.create_task(send_all_delayed_results(
                created_files, pending_images, pending_responses, client, message
            ))
            console.info(f"Scheduled delayed sending - Files: {created_files}, Images: {pending_images}, Responses: {pending_responses}")
        
        # Return clean response without files sent yet
        return processed_response
        
    except Exception as e:
        console.error(f"Error processing shortcodes: {str(e)}")
        return response_text

async def send_all_delayed_results(created_files, pending_images, pending_responses, client, message):
    """Send all delayed results after AI response"""
    try:
        # Wait for AI response to be sent first
        await asyncio.sleep(1.0)  # Small delay to ensure AI response is sent
        
        console.info(f"Now sending delayed results - Files: {created_files}, Images: {pending_images}, Responses: {pending_responses}")
        
        # Send canvas files
        if created_files:
            await send_created_files_delayed(created_files, client, message)
        
        # Send images
        if pending_images:
            await send_pending_images_delayed(pending_images, client, message)
        
        # Send responses
        if pending_responses:
            await send_pending_responses_delayed(pending_responses, client, message)
            
    except Exception as e:
        console.error(f"Error in send_all_delayed_results: {str(e)}")

async def send_pending_images_delayed(pending_images, client, message):
    """Send pending images with delay"""
    try:
        # Import the image shortcode instance directly
        from syncara.shortcode.image_generation import image_shortcode
        
        if image_shortcode and hasattr(image_shortcode, 'send_pending_images'):
            await image_shortcode.send_pending_images(client, pending_images)
            console.info(f"Sent {len(pending_images)} pending images")
        else:
            console.error("Image shortcode handler not found")
            
    except ImportError as e:
        console.error(f"Error importing image shortcode: {str(e)}")
    except Exception as e:
        console.error(f"Error in send_pending_images_delayed: {str(e)}")

async def send_pending_responses_delayed(pending_responses, client, message):
    """Send pending responses with delay"""
    try:
        # Import shortcode instances directly
        shortcode_instances = []
        
        try:
            from syncara.shortcode.todo_management import todo_shortcode
            if hasattr(todo_shortcode, 'send_pending_results'):
                shortcode_instances.append(('todo_shortcode', todo_shortcode))
        except ImportError:
            pass
            
        try:
            from syncara.shortcode.python_execution import python_shortcode
            if hasattr(python_shortcode, 'send_pending_results'):
                shortcode_instances.append(('python_shortcode', python_shortcode))
        except ImportError:
            pass
            
        try:
            from syncara.shortcode.userbot_management import userbot_shortcode
            if hasattr(userbot_shortcode, 'send_pending_responses'):
                shortcode_instances.append(('userbot_shortcode', userbot_shortcode))
        except ImportError:
            pass
        
        # Send responses from all shortcode instances
        for handler_name, handler in shortcode_instances:
            try:
                if hasattr(handler, 'send_pending_responses'):
                    await handler.send_pending_responses(client, pending_responses)
                elif hasattr(handler, 'send_pending_results'):
                    await handler.send_pending_results(client, pending_responses)
                console.info(f"Sent responses from {handler_name}")
            except Exception as e:
                console.error(f"Error sending responses from {handler_name}: {str(e)}")
                
    except Exception as e:
        console.error(f"Error in send_pending_responses_delayed: {str(e)}")

# Keep the original function for backward compatibility
async def send_created_files_delayed(created_files, client, message):
    """Send created files with a delay after AI response"""
    try:
        console.info(f"Sending delayed canvas files: {created_files}")
        
        from syncara.modules.canvas_manager import canvas_manager
        from io import BytesIO
        
        for filename in created_files:
            try:
                console.info(f"Sending delayed file: {filename}")
                
                file_obj = canvas_manager.get_file(filename)
                if file_obj:
                    file_content = file_obj.export()
                    file_bytes = BytesIO(file_content.encode('utf-8'))
                    file_bytes.name = filename
                    
                    # Send file as separate message with clean caption
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=file_bytes,
                        caption=f"📄 **{filename}**\n\nFile siap untuk didownload! ✅",
                        reply_to_message_id=message.id
                    )
                    
                    console.info(f"Successfully sent delayed file: {filename}")
                else:
                    console.error(f"File {filename} not found in canvas for delayed sending")
                    
            except Exception as e:
                console.error(f"Error sending delayed file {filename}: {str(e)}")
                
    except Exception as e:
        console.error(f"Error in send_created_files_delayed: {str(e)}")

async def initialize_ai_handler():
    """Initialize AI handler components"""
    try:
        console.info("🚀 Initializing AI handler with multiple assistants...")
        
        # Setup handlers untuk semua assistant
        await setup_assistant_handlers()
        
        # Check bot manager handlers dengan error handling
        try:
            if hasattr(bot, 'dispatcher') and hasattr(bot.dispatcher, 'groups'):
                handler_count = len(bot.dispatcher.groups)
                console.info(f"Bot manager handlers registered: {handler_count}")
            else:
                console.warning("Bot manager dispatcher not fully initialized yet")
                # Count handlers manually from bot instance
                handler_count = len(bot.handlers) if hasattr(bot, 'handlers') else 0
                console.info(f"Bot manager handlers registered: {handler_count}")
        except Exception as e:
            console.error(f"Error checking bot manager handlers: {str(e)}")
            console.info("Bot manager handlers registered: Unable to determine")
        
        # Get active assistants info
        active_assistants = assistant_manager.get_active_assistants()
        console.info(f"✅ AI handler initialized with {len(active_assistants)} assistants: {', '.join(active_assistants)}")
        
        # Show assistant status
        for assistant_id in active_assistants:
            config = assistant_manager.get_assistant_config(assistant_id)
            if config:
                console.info(f"   {config['emoji']} {config['name']} (@{config['username']}) - {config['personality']}")
        
    except Exception as e:
        console.error(f"Error initializing AI handler: {str(e)}")

# Export important functions and variables for other modules
__all__ = [
    'process_ai_response',
    'initialize_ai_handler',
    'get_chat_history',
    'format_chat_history',
    'cache_userbot_info',
    'USERBOT_INFO_CACHE',
    'USERBOT_PROMPT_MAPPING',
    'CHAT_HISTORY_CONFIG'
]

# Hapus semua command terkait music player dan voice chat
def remove_music_commands():
    pass  # Placeholder agar tidak error import

@bot.on_message(filters.command("autonomous") & filters.user(OWNER_ID))
async def autonomous_control(client, message):
    """Control autonomous AI features"""
    try:
        # 🚀 TRIGGER: Save user data for autonomous command
        await _trigger_user_save_for_command(client, message)
        
        command_parts = message.text.split()
        
        if len(command_parts) == 1:
            # Show main status
            stats = await autonomous_ai.get_autonomous_stats()
            
            status_text = "🤖 **Autonomous AI Control Panel**\n\n"
            status_text += f"📊 **Status**: {'🟢 Active' if stats.get('active', False) else '🔴 Inactive'}\n"
            status_text += f"⏱️ **Uptime**: {stats.get('uptime', '0 minutes')}\n"
            status_text += f"👤 **Active Users**: {stats.get('active_users', 0)}\n"
            status_text += f"📈 **Tasks Completed**: {stats.get('completed_tasks', 0)}\n"
            status_text += f"🔄 **Pattern Analysis**: {stats.get('pattern_analysis_count', 0)}\n\n"
            
            status_text += "🎯 **Available Commands**:\n"
            status_text += "• `/autonomous status` - Detailed status\n"
            status_text += "• `/autonomous tasks` - Recent tasks\n"
            status_text += "• `/autonomous patterns` - User patterns\n"
            status_text += "• `/autonomous test` - Test functionality\n"
            status_text += "• `/autonomous restart` - Restart autonomous AI\n"
            
            await message.reply(status_text)
            
        elif command_parts[1] == "status":
            # Detailed status
            health_check = await autonomous_ai.run_health_check()
            stats = await autonomous_ai.get_autonomous_stats()
            
            status_text = "🔍 **Autonomous AI Detailed Status**\n\n"
            
            # System health
            status_text += "🏥 **System Health**:\n"
            for check_name, result in health_check.get('checks', {}).items():
                emoji = "✅" if result else "❌"
                status_text += f"• {emoji} {check_name.replace('_', ' ').title()}\n"
            
            # Recent activity
            status_text += f"\n📊 **Recent Activity** (24h):\n"
            status_text += f"• Proactive Messages: {stats.get('proactive_messages_24h', 0)}\n"
            status_text += f"• Pattern Updates: {stats.get('pattern_updates_24h', 0)}\n"
            status_text += f"• Health Checks: {stats.get('health_checks_24h', 0)}\n"
            
            await message.reply(status_text)
            
        elif command_parts[1] == "tasks":
            # Recent tasks
            recent_tasks = await autonomous_ai.get_recent_tasks(limit=10)
            
            if recent_tasks:
                status_text = "📋 **Recent Autonomous Tasks**\n\n"
                for task in recent_tasks:
                    task_emoji = {"completed": "✅", "failed": "❌", "running": "🔄"}.get(task.get('status', 'unknown'), "❓")
                    status_text += f"{task_emoji} **{task.get('type', 'Unknown')}**\n"
                    status_text += f"   Target: User {task.get('user_id', 'Unknown')}\n"
                    status_text += f"   Time: {task.get('timestamp', 'Unknown')}\n"
                    if task.get('result'):
                        status_text += f"   Result: {task['result'][:50]}...\n"
                    status_text += "\n"
            else:
                status_text = "📋 **Recent Autonomous Tasks**\n\nNo recent tasks found."
            
            await message.reply(status_text)
            
        elif command_parts[1] == "patterns":
            # User patterns analysis
            pattern_stats = await autonomous_ai.get_pattern_stats()
            
            status_text = "🧠 **User Pattern Analysis**\n\n"
            status_text += f"👥 **Users Analyzed**: {pattern_stats.get('total_users', 0)}\n"
            status_text += f"📊 **Active Patterns**: {pattern_stats.get('active_patterns', 0)}\n"
            status_text += f"🎯 **Successful Predictions**: {pattern_stats.get('successful_predictions', 0)}\n"
            status_text += f"📈 **Accuracy Rate**: {pattern_stats.get('accuracy_rate', 0)}%\n\n"
            
            # Top patterns
            top_patterns = pattern_stats.get('top_patterns', [])
            if top_patterns:
                status_text += "🔝 **Top Patterns**:\n"
                for pattern in top_patterns[:5]:
                    status_text += f"• {pattern.get('name', 'Unknown')}: {pattern.get('frequency', 0)} times\n"
            
            await message.reply(status_text)
            
        elif command_parts[1] == "test":
            # Test autonomous functionality
            await message.reply("🧪 Testing autonomous AI functionality...")
            
            test_results = await autonomous_ai.run_test_suite()
            
            status_text = "🧪 **Autonomous AI Test Results**\n\n"
            
            for test_name, result in test_results.items():
                emoji = "✅" if result.get('passed', False) else "❌"
                status_text += f"{emoji} **{test_name}**\n"
                if not result.get('passed', False):
                    status_text += f"   Error: {result.get('error', 'Unknown error')}\n"
                status_text += f"   Time: {result.get('execution_time', 0):.2f}s\n\n"
            
            overall_status = "✅ All tests passed" if all(r.get('passed', False) for r in test_results.values()) else "❌ Some tests failed"
            status_text += f"**Overall**: {overall_status}"
            
            await message.reply(status_text)
            
        elif command_parts[1] == "restart":
            # Restart autonomous AI
            await message.reply("🔄 Restarting autonomous AI...")
            
            restart_result = await autonomous_ai.restart()
            
            if restart_result.get('success', False):
                await message.reply("✅ Autonomous AI restarted successfully!")
            else:
                await message.reply(f"❌ Failed to restart autonomous AI: {restart_result.get('error', 'Unknown error')}")
        
        else:
            await message.reply("❌ Unknown autonomous command. Use `/autonomous` for help.")
    
    except Exception as e:
        console.error(f"Error in autonomous control: {str(e)}")
        await message.reply(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("canvas") & filters.user(OWNER_ID))
async def canvas_debug_command(client, message):
    """Debug canvas files and shortcode system"""
    try:
        from syncara.modules.canvas_manager import canvas_manager
        from syncara.shortcode import registry
        
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            # Show canvas status
            files = canvas_manager.list_files()
            response = f"🎨 **Canvas Debug Info**\n\n"
            response += f"**Files in Canvas:** {len(files)}\n"
            if files:
                response += f"**Available Files:**\n"
                for file in files:
                    response += f"• {file}\n"
            else:
                response += "• No files available\n"
            
            response += f"\n**Shortcode Status:**\n"
            response += f"• Total handlers: {len(registry.shortcodes)}\n"
            response += f"• Canvas handlers: {len([s for s in registry.shortcodes if s.startswith('CANVAS:')])}\n"
            
            await message.reply(response)
            return
        
        command = args[0].lower()
        
        if command == "list":
            files = canvas_manager.list_files()
            if files:
                response = "📂 **Canvas Files:**\n"
                for file_name in files:
                    file_obj = canvas_manager.get_file(file_name)
                    if file_obj:
                        content_preview = file_obj.get_content()[:100] + "..." if len(file_obj.get_content()) > 100 else file_obj.get_content()
                        response += f"• **{file_name}** ({file_obj.filetype})\n"
                        response += f"  Preview: {content_preview}\n\n"
                await message.reply(response)
            else:
                await message.reply("📂 No files in canvas")
        
        elif command == "clear":
            canvas_manager.clear_files()
            await message.reply("✅ Canvas cleared")
        
        elif command == "test":
            # Test shortcode execution order
            test_shortcodes = ["CANVAS:EXPORT:test.txt", "CANVAS:CREATE:test.txt"]
            validation = registry.validate_shortcode_order(test_shortcodes)
            
            response = f"🧪 **Shortcode Order Test:**\n\n"
            response += f"**Test Shortcodes:** {test_shortcodes}\n"
            response += f"**Valid:** {'✅' if validation['valid'] else '❌'}\n"
            
            if validation['issues']:
                response += f"**Issues:**\n"
                for issue in validation['issues']:
                    response += f"• {issue}\n"
            
            await message.reply(response)
        
        elif command == "create_test":
            # Create test file manually
            test_content = "Test file content\nLine 2\nLine 3"
            file = canvas_manager.create_file("test.txt", "txt", test_content)
            
            if file:
                await message.reply(f"✅ Test file created successfully\nContent: {file.get_content()}")
            else:
                await message.reply("❌ Failed to create test file")
        
        elif command == "export_test":
            # Try to export test file
            from syncara.shortcode import registry
            result = await registry.execute_shortcode("CANVAS:EXPORT", client, message, "test.txt")
            
            if result:
                await message.reply("✅ Test export successful")
            else:
                await message.reply("❌ Test export failed")
        
        elif command == "debug_ai":
            # Debug AI shortcode processing
            test_ai_response = "Saya akan membuat file artikel untuk Anda:\n\n[CANVAS:CREATE:artikel.txt:txt:Ini adalah konten artikel]\n\nLalu saya export:\n\n[CANVAS:EXPORT:artikel.txt]"
            
            response = f"🧪 **AI Response Debug:**\n\n"
            response += f"**Test Response:**\n{test_ai_response}\n\n"
            
            # Check shortcode validation
            import re
            shortcode_pattern = r'\[([A-Z]+:[A-Z_]+):([^\]]*)\]'
            matches = list(re.finditer(shortcode_pattern, test_ai_response))
            shortcode_names = [match.group(1).strip() for match in matches]
            
            validation = registry.validate_shortcode_order(shortcode_names)
            
            response += f"**Shortcodes found:** {shortcode_names}\n"
            response += f"**Valid order:** {'✅' if validation['valid'] else '❌'}\n"
            
            if validation['issues']:
                response += f"**Issues:**\n"
                for issue in validation['issues']:
                    response += f"• {issue}\n"
            
            await message.reply(response)
        
        elif command == "test_flow":
            # Test full canvas flow: create -> export
            await message.reply("🧪 Testing full canvas flow...")
            
            # Step 1: Create file
            await message.reply("Step 1: Creating file...")
            from syncara.shortcode import registry
            
            create_result = await registry.execute_shortcode("CANVAS:CREATE", client, message, "test_flow.txt:txt:Hello World\\nThis is line 2\\nThis is line 3")
            
            if create_result:
                await message.reply("✅ Step 1 passed: File created")
            else:
                await message.reply("❌ Step 1 failed: File creation failed")
                return
            
            # Step 2: Verify file exists
            await message.reply("Step 2: Verifying file exists...")
            files = canvas_manager.list_files()
            if "test_flow.txt" in files:
                await message.reply("✅ Step 2 passed: File exists in canvas")
            else:
                await message.reply(f"❌ Step 2 failed: File not found. Available: {files}")
                return
            
            # Step 3: Export file
            await message.reply("Step 3: Exporting file...")
            import asyncio
            await asyncio.sleep(0.2)  # Small delay
            
            export_result = await registry.execute_shortcode("CANVAS:EXPORT", client, message, "test_flow.txt")
            
            if export_result:
                await message.reply("✅ Step 3 passed: File exported successfully")
                await message.reply("🎉 Full flow test completed successfully!")
            else:
                await message.reply("❌ Step 3 failed: Export failed")
                
        elif command == "test_ai_flow":
            # Test AI shortcode processing with realistic scenario
            await message.reply("🧪 Testing AI shortcode processing flow...")
            
            # Simulate AI response with shortcodes
            test_ai_response = """Oke, aku akan buatkan file artikel tentang AI untuk kamu! 😊

[CANVAS:CREATE:artikel_ai.txt:txt:Artificial Intelligence di Tahun 2025\\n\\nAI telah berkembang pesat dan mengubah cara kita bekerja.\\n\\nFitur-fitur terbaru:\\n1. Natural Language Processing\\n2. Computer Vision\\n3. Machine Learning\\n\\nKesimpulan:\\nAI akan terus berkembang dan membantu manusia.]

Sekarang aku export file-nya untuk kamu ya! 

[CANVAS:EXPORT:artikel_ai.txt]

File artikel sudah siap! 🚀✨"""

            await message.reply(f"**Original AI Response:**\n{test_ai_response}")
            
            # Process the shortcodes
            processed_response = await process_shortcodes_in_response(test_ai_response, client, message)
            
            await message.reply(f"**Processed Response:**\n{processed_response}")
            
            # Check final canvas status
            files = canvas_manager.list_files()
            await message.reply(f"**Canvas Status:**\nFiles: {files}")
        
        elif command == "test_new_flow":
            # Test the new improved flow
            await message.reply("🧪 Testing new improved AI flow...")
            
            # Simulate AI response with shortcodes (like real scenario)
            test_ai_response = """Oke, siap! Aku akan bantu bikinkan artikel tentang Teknologi dan mengirimkannya dalam bentuk .txt. Yuk, kita mulai! 🚀✨

[CANVAS:CREATE:teknologi_2025.txt:txt:Perkembangan Teknologi di Tahun 2025\\n\\nTeknologi telah berkembang pesat dalam beberapa tahun terakhir. Berikut adalah tren utama:\\n\\n1. Artificial Intelligence (AI)\\n- Machine Learning semakin canggih\\n- Natural Language Processing berkembang pesat\\n\\n2. Internet of Things (IoT)\\n- Smart home semakin populer\\n- Industrial IoT untuk efisiensi\\n\\n3. Blockchain Technology\\n- Cryptocurrency semakin diterima\\n- Smart contracts untuk otomasi\\n\\nKesimpulan:\\nTeknologi akan terus berkembang dan mengubah cara kita hidup dan bekerja.]

File artikel sudah siap dan akan langsung terkirim ke kamu! 😊📂"""

            await message.reply("**Step 1: Original AI Response**")
            await message.reply(test_ai_response)
            
            await message.reply("**Step 2: Processing shortcodes...**")
            
            # Process the shortcodes
            processed_response = await process_shortcodes_in_response(test_ai_response, client, message)
            
            await message.reply("**Step 3: Final processed response**")
            await message.reply(processed_response)
            
            # Check canvas status
            files = canvas_manager.list_files()
            await message.reply(f"**Step 4: Canvas Status**\nFiles: {files}")
        
        elif command == "test_final_flow":
            # Test the final fixed flow
            await message.reply("🧪 Testing FINAL corrected AI flow...")
            
            # Clear canvas first
            canvas_manager.clear_files()
            
            # Simulate real AI response
            await message.reply("**Step 1: Simulating AI response with shortcode**")
            
            test_response = """Oke, siap! Aku akan bikinkan artikel tentang teknologi di tahun 2025 dan mengirimkannya dalam bentuk .txt. Yuk, kita mulai! 🚀✨

[CANVAS:CREATE:artikel_teknologi_2025.txt:txt:Teknologi di Tahun 2025\\n\\nPerkembangan teknologi semakin pesat:\\n\\n1. Artificial Intelligence\\n   - AI lebih pintar dan efisien\\n   - Automasi industri meningkat\\n\\n2. Virtual Reality & Metaverse\\n   - Pengalaman immersive semakin nyata\\n   - Remote work jadi lebih interaktif\\n\\n3. Sustainable Technology\\n   - Energy harvesting technology\\n   - Carbon capture solutions\\n\\nKesimpulan:\\nTeknologi 2025 akan fokus pada sustainability dan human-centric design.]

File artikel sudah siap dan akan langsung terkirim ke kamu! 😊📂"""

            # Step 2: Process shortcodes (should not send file immediately)
            await message.reply("**Step 2: Processing shortcodes (background)**")
            processed = await process_shortcodes_in_response(test_response, client, message)
            
            # Step 3: Send processed response
            await message.reply("**Step 3: Processed AI response (should be clean)**")
            await message.reply(processed)
            
            # Step 4: Check if file will be sent with delay
            await message.reply("**Step 4: Waiting for delayed file sending...**")
            await asyncio.sleep(2)  # Wait for delayed sending
            
            await message.reply("**Step 5: Flow test completed!**")
            
            # Check canvas status
            files = canvas_manager.list_files()
            await message.reply(f"**Canvas Status:** {files}")
        
        elif command == "help":
            help_text = """
🎨 **Canvas Debug Commands:**

• `/canvas` - Show canvas status
• `/canvas list` - List all files with preview
• `/canvas clear` - Clear all files
• `/canvas test` - Test shortcode order validation
• `/canvas create_test` - Create test file manually
• `/canvas export_test` - Export test file
• `/canvas debug_ai` - Debug AI shortcode processing
• `/canvas test_flow` - Test full create→export flow
• `/canvas test_ai_flow` - Test AI response with shortcode processing
• `/canvas test_new_flow` - Test new improved AI flow
• `/canvas test_final_flow` - Test final corrected AI flow
• `/canvas help` - Show this help

🧪 **Shortcode Testing:**
• `/shortcode_test SHORTCODE:ACTION params` - Test individual shortcode
            """
            await message.reply(help_text)
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("shortcode_test") & filters.user(OWNER_ID))
async def shortcode_test_command(client, message):
    """Test shortcode execution manually"""
    try:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if len(args) < 2:
            await message.reply("Usage: `/shortcode_test SHORTCODE:ACTION params`")
            return
        
        shortcode_name = args[0]
        params = ' '.join(args[1:])
        
        from syncara.shortcode import registry
        
        console.info(f"Manual shortcode test: {shortcode_name} with params: {params}")
        
        result = await registry.execute_shortcode(shortcode_name, client, message, params)
        
        if result:
            await message.reply(f"✅ Shortcode {shortcode_name} executed successfully")
        else:
            await message.reply(f"❌ Shortcode {shortcode_name} failed")
            
    except Exception as e:
        await message.reply(f"❌ Error testing shortcode: {str(e)}")
        console.error(f"Error in shortcode test: {str(e)}")

@bot.on_message(filters.command("test_delayed") & filters.user(OWNER_ID))
async def test_delayed_command(client, message):
    """Test delayed processing for all shortcode types"""
    try:
        # Test responses
        test_responses = [
            "Testing IMAGE:GEN delayed: [IMAGE:GEN:cute cat in space]",
            "Testing USERBOT:STATUS delayed: [USERBOT:STATUS:]",
            "Testing GROUP:PIN_MESSAGE delayed: [GROUP:PIN_MESSAGE:123]", 
            "Testing USER:WARN delayed: [USER:WARN:testuser:test warning]",
            "Testing CANVAS:CREATE delayed: [CANVAS:CREATE:test.txt:Hello world content]"
        ]
        
        await message.reply_text("🧪 **Testing Delayed Processing**\n\nTesting all shortcode types with delayed processing...")
        
        for i, test_response in enumerate(test_responses, 1):
            await message.reply_text(f"**Test {i}:**\n{test_response}")
            processed_response = await process_shortcodes_in_response(test_response, client, message)
            await message.reply_text(f"**Result {i}:**\n{processed_response}")
            await asyncio.sleep(2)  # Small delay between tests
            
    except Exception as e:
        console.error(f"Error in test_delayed_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("test_all_flow") & filters.user(OWNER_ID))
async def test_all_flow_command(client, message):
    """Test complete flow with all shortcode types"""
    try:
        # Test combined shortcodes
        test_message = """🧪 **Testing Complete Flow**

AI akan membuat gambar, file, dan manajemen grup sekaligus!

[IMAGE:GEN:cute robot assistant]
[CANVAS:CREATE:test_combined.txt:This is a test file created with delayed processing]
[USERBOT:STATUS:]

Semua hasil akan muncul setelah response AI ini terkirim! 🚀"""
        
        await message.reply_text("🧪 **Testing Complete Flow**\n\nProcessing combined shortcodes...")
        
        # Process the test message
        processed = await process_shortcodes_in_response(test_message, client, message)
        await message.reply_text(processed)
        
    except Exception as e:
        console.error(f"Error in test_all_flow_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("shortcode_status") & filters.user(OWNER_ID))
async def shortcode_status_command(client, message):
    """Show shortcode status and delayed processing info"""
    try:
        from syncara.shortcode import registry
        
        response = "🔧 **Shortcode Status & Delayed Processing**\n\n"
        
        # Registry info
        response += f"**Registry Info:**\n"
        response += f"• Handlers: {len(registry.shortcodes)}\n"
        response += f"• Descriptions: {len(registry.descriptions)}\n\n"
        
        # Check delayed processing support
        response += "**Delayed Processing Support:**\n"
        
        delayed_support = {}
        for shortcode_name, handler in registry.shortcodes.items():
            handler_class = handler.__class__.__name__
            
            # Check for delayed processing methods
            has_delayed = False
            if hasattr(handler, 'send_pending_images'):
                has_delayed = True
                delayed_support[handler_class] = "Images"
            elif hasattr(handler, 'send_pending_responses'):
                has_delayed = True
                delayed_support[handler_class] = "Responses"
            elif hasattr(handler, 'pending_responses'):
                has_delayed = True
                delayed_support[handler_class] = "Responses"
            
            if has_delayed:
                response += f"• ✅ {handler_class} - {delayed_support[handler_class]}\n"
        
        response += "\n**Available Shortcodes:**\n"
        for shortcode, desc in registry.descriptions.items():
            response += f"• `{shortcode}` - {desc}\n"
        
        response += "\n**Test Commands:**\n"
        response += "• `/test_delayed` - Test all shortcode types\n"
        response += "• `/test_all_flow` - Test combined flow\n"
        response += "• `/test_group_fix` - Test GROUP shortcode fixes\n"
        response += "• `/test_python` - Test Python execution\n"
        response += "• `/test_search` - Test file/chat search\n"
        response += "• `/test_todo` - Test TODO management\n"
        response += "• `/test_new_features` - Test all new features\n"
        response += "• `/features_help` - Help for new features\n"
        response += "• `/shortcode_status` - This command\n"
        
        await message.reply_text(response)
        
    except Exception as e:
        console.error(f"Error in shortcode_status_command: {str(e)}")
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("test_group_fix") & filters.user(OWNER_ID))
async def test_group_fix_command(client, message):
    """Test improved GROUP shortcode handling"""
    try:
        # Test responses with invalid and valid parameters
        test_responses = [
            "Testing invalid ID: [GROUP:DELETE_MESSAGE:current_message_id]",
            "Testing valid keyword: [GROUP:PIN_MESSAGE:current_message_id]",
            "Testing invalid format: [GROUP:DELETE_MESSAGE:not_a_number]",
            "Testing reply message: [GROUP:PIN_MESSAGE:reply_message]"
        ]
        
        await message.reply_text("🧪 **Testing Improved GROUP Shortcodes**\n\nTesting parameter validation and special keywords...")
        
        for i, test_response in enumerate(test_responses, 1):
            await message.reply_text(f"**Test {i}:**\n{test_response}")
            processed_response = await process_shortcodes_in_response(test_response, client, message)
            await message.reply_text(f"**Result {i}:**\n{processed_response}")
            await asyncio.sleep(2)  # Small delay between tests
            
    except Exception as e:
        console.error(f"Error in test_group_fix_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("test_python") & filters.user(OWNER_ID))
async def test_python_command(client, message):
    """Test Python execution shortcode"""
    try:
        # Test different Python code examples
        test_codes = [
            "Simple calculation: [PYTHON:EXEC:2 + 2 * 3]",
            "Math operations: [CODE:PYTHON:import math; math.sqrt(16) + math.pi]",
            "String manipulation: [CALC:PYTHON:\"Hello World\".upper().replace(\"WORLD\", \"Python\")]",
            "List operations: [PYTHON:EXEC:list(range(5))]",
            "Security test (should fail): [PYTHON:EXEC:import os; os.listdir()]"
        ]
        
        await message.reply_text("🐍 **Testing Python Execution**\n\nTesting various Python code examples...")
        
        for i, test_code in enumerate(test_codes, 1):
            await message.reply_text(f"**Test {i}:**\n{test_code}")
            processed_response = await process_shortcodes_in_response(test_code, client, message)
            await message.reply_text(f"**Result {i}:**\n{processed_response}")
            await asyncio.sleep(3)  # Longer delay for Python execution
            
    except Exception as e:
        console.error(f"Error in test_python_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("test_search") & filters.user(OWNER_ID))
async def test_search_command(client, message):
    """Test file and chat search shortcodes"""
    try:
        # Test different search examples
        test_searches = [
            "Search Python files: [SEARCH:FILE:*.py]",
            "Find config files: [FILE:SEARCH:config]",
            "Search for modules: [FIND:FILE:modules]",
            "Search chat history: [SEARCH:CHAT:shortcode]",
            "Find specific messages: [CHAT:SEARCH:Python]"
        ]
        
        await message.reply_text("🔍 **Testing Search Functions**\n\nTesting file and chat search capabilities...")
        
        for i, test_search in enumerate(test_searches, 1):
            await message.reply_text(f"**Test {i}:**\n{test_search}")
            processed_response = await process_shortcodes_in_response(test_search, client, message)
            await message.reply_text(f"**Result {i}:**\n{processed_response}")
            await asyncio.sleep(2)  # Delay for search operations
            
    except Exception as e:
        console.error(f"Error in test_search_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("test_new_features") & filters.user(OWNER_ID))
async def test_new_features_command(client, message):
    """Test all new features together"""
    try:
        # Combined test
        combined_test = """🧪 **Testing All New Features**

AI akan menjalankan kode Python, mencari file, mencari chat, dan mengelola TODO sekaligus!

[PYTHON:EXEC:print("Hello from Python!"); result = 5 * 8; print(f"5 x 8 = {result}")]
[SEARCH:FILE:shortcode]
[CHAT:SEARCH:test]
[TODO:CREATE:Test todo dari AI]
[TODO:LIST:]

Semua hasil akan muncul setelah response AI ini! 🚀"""
        
        await message.reply_text("🧪 **Testing All New Features**\n\nProcessing combined Python, search, and TODO operations...")
        
        # Process the test message
        processed = await process_shortcodes_in_response(combined_test, client, message)
        await message.reply_text(processed)
        
    except Exception as e:
        console.error(f"Error in test_new_features_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("test_todo") & filters.user(OWNER_ID))
async def test_todo_command(client, message):
    """Test TODO management shortcode"""
    try:
        # Test different TODO operations
        test_todos = [
            "Create new todo: [TODO:CREATE:Belajar Python programming]",
            "Create another todo: [TODO:ADD:Setup development environment]",
            "List all todos: [TODO:LIST:]",
            "Complete first todo: [TODO:COMPLETE:1]",
            "Create third todo: [TODO:NEW:Deploy aplikasi ke server]",
            "Show todo stats: [TODO:STATS:]",
            "List pending todos: [TODO:SHOW:pending]",
            "Update todo: [TODO:UPDATE:2:Setup Docker environment]",
            "List completed todos: [TODO:VIEW:completed]"
        ]
        
        await message.reply_text("📝 **Testing TODO Management**\n\nTesting various TODO operations...")
        
        for i, test_todo in enumerate(test_todos, 1):
            await message.reply_text(f"**Test {i}:**\n{test_todo}")
            processed_response = await process_shortcodes_in_response(test_todo, client, message)
            await message.reply_text(f"**Result {i}:**\n{processed_response}")
            await asyncio.sleep(2)  # Delay between tests
            
    except Exception as e:
        console.error(f"Error in test_todo_command: {str(e)}")
        await message.reply_text(f"❌ Test error: {str(e)}")

@bot.on_message(filters.command("features_help") & filters.user(OWNER_ID))
async def features_help_command(client, message):
    """Show help for new features"""
    try:
        help_text = """🚀 **New Features Help**

**🐍 Python Execution:**
• `[PYTHON:EXEC:code]` - Execute Python code
• `[CODE:PYTHON:code]` - Alternative syntax  
• `[CALC:PYTHON:code]` - For calculations

**📁 File Search:**
• `[SEARCH:FILE:keyword]` - Search files
• `[FILE:FIND:keyword]` - Alternative syntax

**💬 Chat Search:**
• `[CHAT:SEARCH:keyword]` - Search chats
• `[SEARCH:CHAT:keyword] - Alternative syntax

**📝 TODO Management:**
• `[TODO:CREATE:task]` - Create new todo
• `[TODO:LIST:]` - List all todos
• `[TODO:COMPLETE:id]` - Complete todo

Gunakan fitur ini dalam pesan AI untuk eksekusi otomatis! 🤖✨"""

        await message.reply_text(help_text)
        
    except Exception as e:
        console.error(f"Error in features_help_command: {str(e)}")
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.text & filters.command("dbstatus"))
async def database_status_command(client, message):
    """Show database status and health check"""
    try:
        # 🚀 TRIGGER: Save user data for dbstatus command
        await _trigger_user_save_for_command(client, message)
        
        if message.from_user.id not in OWNER_ID:
            await message.reply("❌ Only owner can access database status.")
            return
        
        await message.reply("🔍 Running database health check...")
        
        from syncara.database import run_database_health_check, get_database_status, database_manager
        
        # Get comprehensive status
        health_report = await run_database_health_check()
        db_status = await get_database_status()
        stats = await database_manager.get_database_stats()
        
        # Format response
        status_text = f"📊 **Database Status Report**\n\n"
        
        # Overall health
        status_emoji = "✅" if health_report.get("overall_status") == "healthy" else "⚠️"
        status_text += f"{status_emoji} **Overall Status**: {health_report.get('overall_status', 'unknown').title()}\n\n"
        
        # Connection info
        if db_status.get("connection_healthy"):
            status_text += "🔗 **Connection**: Healthy\n"
            server_info = db_status.get("server_info", {})
            status_text += f"📦 **MongoDB Version**: {server_info.get('version', 'unknown')}\n"
        else:
            status_text += "❌ **Connection**: Failed\n"
        
        # Database stats
        db_info = stats.get("database_info", {})
        status_text += f"\n📈 **Database Statistics**:\n"
        status_text += f"• Collections: {db_info.get('collections', 0)}\n"
        status_text += f"• Total Objects: {db_info.get('objects', 0):,}\n"
        status_text += f"• Data Size: {db_info.get('data_size', 0) / 1024 / 1024:.1f} MB\n"
        status_text += f"• Storage Size: {db_info.get('storage_size', 0) / 1024 / 1024:.1f} MB\n"
        
        # Collection counts
        status_text += f"\n📋 **Collection Counts**:\n"
        collections_data = [
            ("👤 Users", stats.get("users_count", 0)),
            ("👥 Groups", stats.get("groups_count", 0)),
            ("🎨 Canvas Files", stats.get("canvas_files_count", 0)),
            ("🖼️ Image Generations", stats.get("image_generations_count", 0)),
            ("🤖 Autonomous Tasks", stats.get("autonomous_tasks_count", 0)),
            ("📝 System Logs", stats.get("system_logs_count", 0))
        ]
        
        for name, count in collections_data:
            status_text += f"• {name}: {count:,}\n"
        
        # Recent activity
        activity = stats.get("recent_activity", {})
        status_text += f"\n🔥 **Recent Activity**:\n"
        status_text += f"• Active Users (7 days): {activity.get('recent_users', 0)}\n"
        status_text += f"• Today's Interactions: {activity.get('today_interactions', 0)}\n"
        status_text += f"• Running Workflows: {activity.get('active_workflows', 0)}\n"
        
        # Performance check
        perf_check = health_report.get("checks", {}).get("query_performance", {})
        if perf_check:
            status_text += f"\n⚡ **Performance**:\n"
            status_text += f"• Query Time: {perf_check.get('query_time_ms', 0):.1f}ms\n"
            perf_status = "Good" if perf_check.get('acceptable', True) else "Slow"
            status_text += f"• Performance: {perf_status}\n"
        
        # Failed checks
        if health_report.get("failed_checks"):
            status_text += f"\n⚠️ **Issues Found**:\n"
            for check in health_report["failed_checks"]:
                status_text += f"• {check.replace('_', ' ').title()}\n"
        
        status_text += f"\n🕐 **Last Updated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        await message.reply(status_text)
        
    except Exception as e:
        console.error(f"Error in database status command: {e}")
        await message.reply(f"❌ Error getting database status: {str(e)}")

@bot.on_message(filters.text & filters.command("dbcleanup"))
async def database_cleanup_command(client, message):
    """Run database cleanup"""
    try:
        # 🚀 TRIGGER: Save user data for dbcleanup command
        await _trigger_user_save_for_command(client, message)
        
        if message.from_user.id not in OWNER_ID:
            await message.reply("❌ Only owner can run database cleanup.")
            return
        
        await message.reply("🧹 Starting database cleanup...")
        
        from syncara.database import database_manager
        
        # Run cleanup
        cleanup_results = await database_manager.cleanup_old_data(days_old=30)
        
        if cleanup_results:
            cleanup_text = "✅ **Database Cleanup Completed**\n\n"
            cleanup_text += "📊 **Items Removed**:\n"
            
            for collection, count in cleanup_results.items():
                if count > 0:
                    cleanup_text += f"• {collection.replace('_', ' ').title()}: {count:,}\n"
            
            total_removed = sum(cleanup_results.values())
            cleanup_text += f"\n🗑️ **Total Items Removed**: {total_removed:,}"
        else:
            cleanup_text = "✅ Database cleanup completed (no items to remove)"
        
        await message.reply(cleanup_text)
        
    except Exception as e:
        console.error(f"Error in database cleanup command: {e}")
        await message.reply(f"❌ Error running cleanup: {str(e)}")

@bot.on_message(filters.text & filters.command("dbbackup"))
async def database_backup_command(client, message):
    """Create database backup"""
    try:
        # 🚀 TRIGGER: Save user data for dbbackup command
        await _trigger_user_save_for_command(client, message)
        
        if message.from_user.id not in OWNER_ID:
            await message.reply("❌ Only owner can create database backups.")
            return
        
        # Extract collection name from command
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.reply("❌ Usage: `/dbbackup <collection_name>`\nExample: `/dbbackup users`")
            return
        
        collection_name = command_parts[1]
        
        await message.reply(f"💾 Creating backup of {collection_name} collection...")
        
        from syncara.database import database_manager
        import os
        
        # Create backup filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{collection_name}_{timestamp}.json"
        backup_path = os.path.join("backups", backup_filename)
        
        # Ensure backup directory exists
        os.makedirs("backups", exist_ok=True)
        
        # Create backup
        document_count = await database_manager.backup_collection(collection_name, backup_path)
        
        if document_count > 0:
            file_size = os.path.getsize(backup_path) / 1024 / 1024  # MB
            backup_text = f"✅ **Backup Created Successfully**\n\n"
            backup_text += f"📁 **File**: {backup_filename}\n"
            backup_text += f"📊 **Documents**: {document_count:,}\n"
            backup_text += f"📏 **Size**: {file_size:.2f} MB\n"
            backup_text += f"📍 **Location**: ./backups/"
        else:
            backup_text = f"❌ Failed to create backup for {collection_name}"
        
        await message.reply(backup_text)
        
    except Exception as e:
        console.error(f"Error in database backup command: {e}")
        await message.reply(f"❌ Error creating backup: {str(e)}")

@bot.on_message(filters.command("features"))
async def features_help_command(client, message):
    """Tampilkan bantuan fitur-fitur bot dengan shortcode examples"""
    try:
        # 🚀 TRIGGER: Save user data for features command  
        await _trigger_user_save_for_command(client, message)
        
        help_text = """
🚀 **SyncaraBot Features & Shortcodes**

**🎨 Canvas Management:**
• `[CANVAS:CREATE:filename.py]` - Create new file
• `[CANVAS:LIST:]` - List all files  
• `[CANVAS:READ:filename.py]` - Read file content
• `[CANVAS:UPDATE:filename.py,new content]` - Update file
• `[CANVAS:EXPORT:filename.py]` - Export as document

**🖼️ Image Generation:**
• `[IMAGE:GEN:a beautiful sunset]` - Generate image
• `[IMAGE:HISTORY:]` - View generation history
• `[IMAGE:STATS:]` - View generation statistics

**🐍 Python Execution:**
• `[PYTHON:EXEC:print("Hello World")]` - Execute Python code
• `[PYTHON:EVAL:2+2]` - Evaluate Python expression

**👥 User Management:**
• `[USER:BAN:username]` - Ban user from group
• `[USER:MUTE:username:60]` - Mute user for 60 minutes
• `[USER:WARN:username:reason]` - Warn user
• `[USER:INFO:username]` - Get user information

**📂 File Search:**
• `[SEARCH:FILE:keyword]` - Search files by keyword
• `[FILE:FIND:keyword]` - Alternative syntax

**💬 Chat Search:**
• `[CHAT:SEARCH:keyword]` - Search chats
• `[SEARCH:CHAT:keyword] - Alternative syntax

**📝 TODO Management:**
• `[TODO:CREATE:task]` - Create new task
• `[TODO:LIST:]` - List all tasks
• `[TODO:COMPLETE:id]` - Complete task

**🤖 Userbot Management:**
• `[USERBOT:STATUS:]` - Get userbot status
• `[USERBOT:INFO:]` - Get userbot information

**🔧 Advanced Pyrogram:**
• `[PYROGRAM:method_name:params]` - Call Pyrogram methods
• `[BOUND:method:params]` - Bound method calls
• `[INLINE:method:params]` - Inline method calls

**📋 Multi-step Processing:**
• `[WORKFLOW:CREATE:name]` - Create workflow
• `[WORKFLOW:EXECUTE:id]` - Execute workflow
• `[WORKFLOW:STATUS:id]` - Check workflow status

📚 **How to use:**
1. Type any shortcode in square brackets
2. AI will process and execute the command
3. Results will be shown automatically

💡 **Pro Tips:**
• Combine multiple shortcodes in one message
• Use descriptive filenames for canvas files
• Check status before running complex workflows

Need help with specific features? Just ask! 😊
"""
        
        await message.reply_text(help_text)
        
    except Exception as e:
        console.error(f"Error in features_help_command: {str(e)}")
        await message.reply_text(f"❌ Error: {str(e)}")