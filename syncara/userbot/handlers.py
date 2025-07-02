# syncara/userbot/handlers.py
from pyrogram import filters
from . import get_userbot, get_all_userbots
from syncara import bot, console
from syncara.modules.process_shortcode import process_shortcode
from syncara.modules.music_player import music_player
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from syncara.services.youtube import YouTubeService

youtube_service = YouTubeService()

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

@app.on_inline_query()
async def inline_query(client, inline_query):
    """Handle inline queries for music search"""
    try:
        query = inline_query.query
        
        if not query:
            # Show default suggestion if no query
            await inline_query.answer(
                results=[
                    InlineQueryResultArticle(
                        title="🎵 Music Search",
                        description="Type a song name to search...",
                        input_message_content=InputTextMessageContent(
                            "Please type a song name after @SyncaraBot to search for music!"
                        ),
                        thumb_url="https://i.imgur.com/Qx8fYr6.png"  # Music icon
                    )
                ],
                cache_time=1
            )
            return

        # Search for music
        results = await youtube_service.search_music(query, limit=5)
        
        if not results:
            # No results found
            await inline_query.answer(
                results=[
                    InlineQueryResultArticle(
                        title="❌ No Results Found",
                        description=f"No results found for: {query}",
                        input_message_content=InputTextMessageContent(
                            f"❌ No music results found for: {query}"
                        )
                    )
                ],
                cache_time=300
            )
            return

        inline_results = []
        for i, music in enumerate(results):
            # Format duration and views
            duration = youtube_service.format_duration(music['duration'])
            views = youtube_service.format_views(music['view_count'])
            
            # Create result
            inline_results.append(
                InlineQueryResultArticle(
                    title=music['title'],
                    description=f"🎵 {music['channel']} | ⏱️ {duration} | 👁️ {views}",
                    thumb_url=music['thumbnail'],
                    input_message_content=InputTextMessageContent(
                        f"🎵 **{music['title']}**\n\n"
                        f"📺 **Channel:** {music['channel']}\n"
                        f"⏱️ **Duration:** {duration}\n"
                        f"👁️ **Views:** {views}\n"
                        f"🔗 **URL:** [YouTube]({music['url']})"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("▶️ PLAY", callback_data=f"music_play_inline_{music['id']}"),
                            InlineKeyboardButton("🔍 Search Again", switch_inline_query_current_chat="")
                        ]
                    ])
                )
            )

        # Answer inline query with results
        await inline_query.answer(
            results=inline_results,
            cache_time=300
        )

    except Exception as e:
        console.error(f"Error in inline query: {e}")
        # Show error to user
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    title="❌ Error",
                    description="An error occurred while searching",
                    input_message_content=InputTextMessageContent(
                        "❌ Sorry, an error occurred while searching for music. Please try again later."
                    )
                )
            ],
            cache_time=5
        )


@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    """Handle callback queries"""
    try:
        data = callback_query.data
        
        # Handle music player callbacks
        if data.startswith("music_"):
            await music_player.handle_callback(client, callback_query)
        else:
            await callback_query.answer("❌ Unknown callback.")
            
    except Exception as e:
        console.error(f"Error handling callback query: {e}")
        await callback_query.answer("❌ Terjadi kesalahan.")

@app.on_callback_query(filters.regex(r"^music_play_inline_(.+)"))
async def handle_inline_play(client, callback_query):
    """Handle play button from inline results"""
    try:
        # Extract video ID
        video_id = callback_query.data.split("_")[-1]
        
        # Get video info
        video_info = await youtube_service.get_video_info(video_id)
        if not video_info:
            await callback_query.answer("❌ Failed to get video info", show_alert=True)
            return

        # Update message with loading state
        await callback_query.edit_message_text(
            f"⏳ Preparing to play: **{video_info['title']}**\n\n"
            "Please wait while I join voice chat and prepare the music..."
        )

        # Download audio
        audio_file = await youtube_service.download_audio(video_id)
        if not audio_file:
            await callback_query.edit_message_text(
                "❌ Failed to download audio. Please try again."
            )
            return

        # Join voice chat and play
        chat_id = callback_query.message.chat.id
        success = await music_player.join_and_play(client, chat_id, audio_file, video_id)

        if success:
            # Update message with now playing
            await callback_query.edit_message_text(
                f"🎵 Now Playing: **{video_info['title']}**\n\n"
                f"📺 Channel: {video_info.get('uploader', 'Unknown')}\n"
                f"⏱️ Duration: {youtube_service.format_duration(video_info.get('duration', 0))}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("⏸️ Pause", callback_data=f"music_pause_{chat_id}"),
                        InlineKeyboardButton("⏹️ Stop", callback_data=f"music_stop_{chat_id}")
                    ],
                    [
                        InlineKeyboardButton("🔍 Search New Song", switch_inline_query_current_chat="")
                    ]
                ])
            )
        else:
            await callback_query.edit_message_text(
                "❌ Failed to play music. Please make sure I have permission to join voice chat."
            )

    except Exception as e:
        console.error(f"Error in inline play handler: {e}")
        await callback_query.edit_message_text(
            "❌ An error occurred while trying to play the music."
        )