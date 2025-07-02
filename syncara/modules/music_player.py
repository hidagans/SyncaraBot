import asyncio
import os
import tempfile
from typing import Dict, List, Optional
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from syncara import console
from syncara.services.youtube import YouTubeService

class MusicPlayer:
    def __init__(self):
        self.youtube = YouTubeService()
        self.current_sessions = {}  # chat_id -> session_info
        self.search_results = {}    # message_id -> search_results
        self.download_cache = {}    # video_id -> file_path
        
    async def search_and_show_results(self, client: Client, original_message: Message, query: str):
        """Search for music and show results with preview via bot manager"""
        try:
            console.info(f"Music search requested: '{query}' by user {original_message.from_user.id}")
            
            # Search for music
            results = await self.youtube.search_music(query, limit=5)
            
            console.info(f"Search completed. Found {len(results)} results")
            
            if not results:
                await client.send_message(
                    chat_id=original_message.chat.id,
                    text="❌ Tidak ditemukan hasil untuk pencarian tersebut.\n\n💡 Tips:\n• Coba kata kunci yang lebih spesifik\n• Sertakan nama artis\n• Periksa ejaan"
                )
                return
            
            # Send results via bot manager with buttons
            search_msg = await client.send_photo(
                chat_id=original_message.chat.id,
                photo=results[0]['thumbnail'],
                caption=self.format_music_info(results[0], 0, len(results)),
                reply_markup=self.create_music_keyboard(results[0], 0, len(results))
            )
            
            # Store results for callback handling
            self.search_results[search_msg.id] = {
                'results': results,
                'current_index': 0,
                'chat_id': original_message.chat.id,
                'user_id': original_message.from_user.id
            }
            
            console.info(f"Music results sent via bot manager with message ID: {search_msg.id}")
            
        except Exception as e:
            console.error(f"Error in search_and_show_results: {e}")
            import traceback
            console.error(f"Traceback: {traceback.format_exc()}")
            await client.send_message(
                chat_id=original_message.chat.id,
                text="❌ Terjadi kesalahan saat mencari musik. Silakan coba lagi."
            )

    def format_music_info(self, music_info: Dict, current_index: int, total_results: int) -> str:
        """Format music info for display"""
        title = music_info['title'][:50] + "..." if len(music_info['title']) > 50 else music_info['title']
        channel = music_info['channel'][:30] + "..." if len(music_info['channel']) > 30 else music_info['channel']
        duration = self.youtube.format_duration(music_info['duration'])
        views = self.youtube.format_views(music_info['view_count'])
        
        return f"""🎵 **{title}**

    📺 **Channel:** {channel}
    ⏱️ **Duration:** {duration}
    👁️ **Views:** {views}
    🔗 **URL:** [YouTube]({music_info['url']})

    📍 **Result {current_index + 1} of {total_results}**"""

    def create_music_keyboard(self, music_info: Dict, current_index: int, total_results: int):
        """Create inline keyboard for music controls"""
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = []
        
        # Navigation row
        nav_row = []
        if current_index > 0:
            nav_row.append(InlineKeyboardButton("⏮️", callback_data=f"music_prev_{current_index}"))
        else:
            nav_row.append(InlineKeyboardButton("⏸️", callback_data="music_disabled"))
        
        nav_row.append(InlineKeyboardButton("▶️ PLAY", callback_data=f"music_play_{music_info['id']}"))
        
        if current_index < total_results - 1:
            nav_row.append(InlineKeyboardButton("⏭️", callback_data=f"music_next_{current_index}"))
        else:
            nav_row.append(InlineKeyboardButton("⏸️", callback_data="music_disabled"))
        
        keyboard.append(nav_row)
        
        # Control row
        control_row = [
            InlineKeyboardButton("🔄 Search Again", callback_data="music_search_again"),
            InlineKeyboardButton("❌ Close", callback_data="music_close")
        ]
        keyboard.append(control_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    async def show_music_preview(self, client: Client, message: Message, music_info: Dict, current_index: int, total_results: int):
        """Show music preview with controls"""
        try:
            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            # Format music info
            title = music_info['title'][:50] + "..." if len(music_info['title']) > 50 else music_info['title']
            channel = music_info['channel'][:30] + "..." if len(music_info['channel']) > 30 else music_info['channel']
            duration = self.youtube.format_duration(music_info['duration'])
            views = self.youtube.format_views(music_info['view_count'])
            
            caption = f"""🎵 **{title}**
            
    📺 **Channel:** {channel}
    ⏱️ **Duration:** {duration}
    👁️ **Views:** {views}
    🔗 **URL:** [YouTube]({music_info['url']})

    📍 **Result {current_index + 1} of {total_results}**"""
            
            # Create keyboard
            keyboard = []
            
            # Navigation row
            nav_row = []
            if current_index > 0:
                nav_row.append(InlineKeyboardButton("⏮️", callback_data=f"music_prev_{message.id}"))
            else:
                nav_row.append(InlineKeyboardButton("⏸️", callback_data="music_disabled"))
            
            nav_row.append(InlineKeyboardButton("▶️ PLAY", callback_data=f"music_play_{message.id}_{music_info['id']}"))
            
            if current_index < total_results - 1:
                nav_row.append(InlineKeyboardButton("⏭️", callback_data=f"music_next_{message.id}"))
            else:
                nav_row.append(InlineKeyboardButton("⏸️", callback_data="music_disabled"))
            
            keyboard.append(nav_row)
            
            # Control row
            control_row = [
                InlineKeyboardButton("🔄 Search Again", callback_data=f"music_search_again_{message.id}"),
                InlineKeyboardButton("❌ Close", callback_data=f"music_close_{message.id}")
            ]
            keyboard.append(control_row)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Try to send with photo, fallback to text if fails
            photo_sent = False
            if music_info.get('thumbnail'):
                try:
                    console.info(f"Attempting to send photo with thumbnail: {music_info['thumbnail']}")
                    
                    # Try different thumbnail URLs
                    thumbnail_urls = [
                        music_info['thumbnail'],
                        f"https://img.youtube.com/vi/{music_info['id']}/hqdefault.jpg",
                        f"https://img.youtube.com/vi/{music_info['id']}/mqdefault.jpg",
                        f"https://img.youtube.com/vi/{music_info['id']}/default.jpg"
                    ]
                    
                    for thumb_url in thumbnail_urls:
                        try:
                            if hasattr(message, 'photo') and message.photo:
                                # Edit existing photo message
                                await message.edit_media(
                                    media=f"photo:{thumb_url}",
                                    caption=caption,
                                    reply_markup=reply_markup
                                )
                            else:
                                # Delete old message and send new photo
                                await message.delete()
                                new_msg = await client.send_photo(
                                    chat_id=message.chat.id,
                                    photo=thumb_url,
                                    caption=caption,
                                    reply_markup=reply_markup
                                )
                                # Update stored message ID
                                if message.id in self.search_results:
                                    self.search_results[new_msg.id] = self.search_results.pop(message.id)
                            
                            photo_sent = True
                            console.info(f"Successfully sent photo with thumbnail: {thumb_url}")
                            break
                            
                        except Exception as thumb_error:
                            console.warning(f"Failed to send thumbnail {thumb_url}: {thumb_error}")
                            continue
                            
                except Exception as e:
                    console.error(f"Error sending photo: {e}")
            
            # Fallback to text message if photo failed
            if not photo_sent:
                console.info("Sending text message as fallback")
                try:
                    await message.edit_text(
                        text=caption,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True  # Disable preview to avoid URL fetch issues
                    )
                except Exception as e:
                    # If edit fails, try to send new message
                    console.warning(f"Edit failed, sending new message: {e}")
                    await message.delete()
                    new_msg = await client.send_message(
                        chat_id=message.chat.id,
                        text=caption,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True
                    )
                    # Update stored message ID
                    if message.id in self.search_results:
                        self.search_results[new_msg.id] = self.search_results.pop(message.id)
                    
        except Exception as e:
            console.error(f"Error showing music preview: {e}")
            import traceback
            console.error(f"Traceback: {traceback.format_exc()}")
            
            # Ultimate fallback - simple text message
            try:
                simple_text = f"🎵 **{music_info['title']}**\n\n▶️ Klik tombol di bawah untuk memutar musik"
                simple_keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("▶️ PLAY", callback_data=f"music_play_{message.id}_{music_info['id']}")
                ]])
                
                await message.edit_text(
                    text=simple_text,
                    reply_markup=simple_keyboard,
                    disable_web_page_preview=True
                )
            except Exception as final_error:
                console.error(f"Ultimate fallback failed: {final_error}")
                await message.edit_text("❌ Terjadi kesalahan saat menampilkan preview musik.")
    
    async def handle_callback(self, client: Client, callback_query):
        """Handle music player callbacks"""
        try:
            data = callback_query.data
            message = callback_query.message
            user_id = callback_query.from_user.id
            
            console.info(f"Handling music callback: {data}")
            
            # Check user authorization for existing sessions
            if message.id in self.search_results:
                if self.search_results[message.id]['user_id'] != user_id:
                    await callback_query.answer("❌ Hanya yang meminta musik yang bisa mengontrol player.", show_alert=True)
                    return
            
            # Handle different callback types
            if data.startswith("music_prev_"):
                await self.handle_navigation(client, callback_query, "prev")
            elif data.startswith("music_next_"):
                await self.handle_navigation(client, callback_query, "next")
            elif data.startswith("music_play_"):
                await self.handle_play(client, callback_query)
            elif data == "music_close":
                await self.handle_close(client, callback_query)
            elif data == "music_search_again":
                await self.handle_search_again(client, callback_query)
            elif data == "music_disabled":
                await callback_query.answer()
            else:
                console.warning(f"Unknown callback data: {data}")
                await callback_query.answer()
                
        except Exception as e:
            console.error(f"Error handling music callback: {e}")
            import traceback
            console.error(f"Traceback: {traceback.format_exc()}")
            await callback_query.answer("❌ Terjadi kesalahan.")
    
    async def handle_navigation(self, client: Client, callback_query, direction: str):
        """Handle navigation (prev/next) buttons"""
        try:
            message_id = callback_query.message.id
            
            if message_id not in self.search_results:
                await callback_query.answer("❌ Session expired.")
                return
            
            session = self.search_results[message_id]
            current_index = session['current_index']
            results = session['results']
            
            # Calculate new index
            if direction == "prev" and current_index > 0:
                new_index = current_index - 1
            elif direction == "next" and current_index < len(results) - 1:
                new_index = current_index + 1
            else:
                await callback_query.answer()
                return
            
            # Update session
            session['current_index'] = new_index
            
            # Update message with new result
            new_result = results[new_index]
            caption = self.format_music_info(new_result, new_index, len(results))
            keyboard = self.create_music_keyboard(new_result, new_index, len(results), message_id)
            
            await callback_query.message.edit_media(
                media=f"photo:{new_result['thumbnail']}",
                caption=caption,
                reply_markup=keyboard
            )
            
            await callback_query.answer()
            
        except Exception as e:
            console.error(f"Error in handle_navigation: {e}")
            await callback_query.answer("❌ Terjadi kesalahan.")
    
    async def handle_play(self, client: Client, callback_query):
        """Handle play button - Join voice chat and play music"""
        try:
            # Parse callback data: music_play_{video_id}
            data_parts = callback_query.data.split("_")
            if len(data_parts) < 3:
                console.error(f"Invalid callback data format: {callback_query.data}")
                await callback_query.answer("❌ Invalid callback data")
                return
                
            video_id = "_".join(data_parts[2:])  # Handle video IDs with underscores
            message_id = callback_query.message.id
            
            console.info(f"Playing video: {video_id} from message: {message_id}")
            
            # Check if session exists
            if message_id not in self.search_results:
                await callback_query.answer("❌ Session expired. Please search again.")
                return
            
            session = self.search_results[message_id]
            chat_id = session['chat_id']
            
            # Update button to show downloading state
            await callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⏳ Downloading...", callback_data="music_disabled")
                ]])
            )
            
            await callback_query.answer("⏳ Downloading and preparing music...")
            
            # Download audio
            console.info(f"Downloading audio for video: {video_id}")
            audio_file = await self.youtube.download_audio(video_id)
            
            if not audio_file:
                console.error(f"Failed to download audio for video: {video_id}")
                await callback_query.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ Download Failed", callback_data="music_disabled")
                    ]])
                )
                return
            
            console.info(f"Audio downloaded successfully: {audio_file}")
            
            # Join voice chat and play
            success = await self.join_and_play(client, chat_id, audio_file, video_id)
            
            if success:
                # Get current music info
                current_music = None
                for result in session['results']:
                    if result['id'] == video_id:
                        current_music = result
                        break
                
                if not current_music:
                    current_music = session['results'][session['current_index']]
                
                # Update button to show now playing
                await callback_query.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🎵 Now Playing", callback_data="music_disabled")],
                        [
                            InlineKeyboardButton("⏸️ Pause", callback_data=f"music_pause_{chat_id}"),
                            InlineKeyboardButton("⏹️ Stop", callback_data=f"music_stop_{chat_id}")
                        ]
                    ])
                )
                
                # Store current session
                self.current_sessions[chat_id] = {
                    'video_id': video_id,
                    'audio_file': audio_file,
                    'music_info': current_music,
                    'message_id': message_id
                }
                
                console.info(f"Music started playing in chat: {chat_id}")
                
            else:
                console.error(f"Failed to join voice chat and play music in chat: {chat_id}")
                await callback_query.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ Failed to Play", callback_data="music_disabled")
                    ]])
                )
                
        except Exception as e:
            console.error(f"Error in handle_play: {e}")
            import traceback
            console.error(f"Traceback: {traceback.format_exc()}")
            await callback_query.answer("❌ Terjadi kesalahan saat memutar musik.")
    
    async def join_and_play(self, client: Client, chat_id: int, audio_file: str, video_id: str) -> bool:
        """Join voice chat and play audio"""
        try:
            # Import pytgcalls
            try:
                from pytgcalls import PyTgCalls
                from pytgcalls.types import AudioPiped
            except ImportError:
                console.error("PyTgCalls not installed. Install with: pip install py-tgcalls")
                return False
            
            # Initialize PyTgCalls if not exists
            if not hasattr(client, 'pytgcalls'):
                client.pytgcalls = PyTgCalls(client)
                await client.pytgcalls.start()
            
            # Join voice chat
            await client.pytgcalls.join_group_call(
                chat_id,
                AudioPiped(audio_file)
            )
            
            console.info(f"Successfully joined voice chat and playing: {video_id}")
            return True
            
        except Exception as e:
            console.error(f"Error joining voice chat: {e}")
            return False
    
    async def handle_close(self, client: Client, callback_query):
        """Handle close button"""
        try:
            message_id = callback_query.message.id
            
            # Clean up session
            if message_id in self.search_results:
                del self.search_results[message_id]
            
            # Delete message
            await callback_query.message.delete()
            
        except Exception as e:
            console.error(f"Error in handle_close: {e}")
            await callback_query.answer("❌ Terjadi kesalahan.")
    
    async def handle_search_again(self, client: Client, callback_query):
        """Handle search again button"""
        try:
            await callback_query.message.edit_text(
                "🔍 Silakan kirim nama lagu yang ingin dicari:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ Cancel", callback_data="music_close")
                ]])
            )
            
            await callback_query.answer()
            
        except Exception as e:
            console.error(f"Error in handle_search_again: {e}")
            await callback_query.answer("❌ Terjadi kesalahan.")

    def create_music_keyboard(self, music_info: Dict, current_index: int, total_results: int, message_id: int = None):
        """Create inline keyboard for music controls"""
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = []
        
        # Navigation row
        nav_row = []
        if current_index > 0:
            nav_row.append(InlineKeyboardButton("⏮️", callback_data=f"music_prev_{current_index}"))
        else:
            nav_row.append(InlineKeyboardButton("⏸️", callback_data="music_disabled"))
        
        nav_row.append(InlineKeyboardButton("▶️ PLAY", callback_data=f"music_play_{music_info['id']}"))
        
        if current_index < total_results - 1:
            nav_row.append(InlineKeyboardButton("⏭️", callback_data=f"music_next_{current_index}"))
        else:
            nav_row.append(InlineKeyboardButton("⏸️", callback_data="music_disabled"))
        
        keyboard.append(nav_row)
        
        # Control row
        control_row = [
            InlineKeyboardButton("🔄 Search Again", callback_data="music_search_again"),
            InlineKeyboardButton("❌ Close", callback_data="music_close")
        ]
        keyboard.append(control_row)
        
        return InlineKeyboardMarkup(keyboard)

# Global music player instance
music_player = MusicPlayer()