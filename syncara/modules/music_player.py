import asyncio
import os
import tempfile
from typing import Dict, List, Optional
from pyrogram import Client
from pyrogram.types import Message
from syncara import console
from syncara.services.youtube import YouTubeService

class MusicPlayer:
    def __init__(self):
        self.youtube = YouTubeService()
        self.current_sessions = {}  # chat_id -> session_info
        self.search_results = {}    # message_id -> search_results
        self.download_cache = {}    # video_id -> file_path
        
    async def search_and_show_results(self, client: Client, message: Message, query: str):
        """Search for music and show results with preview"""
        try:
            # Send searching message
            search_msg = await message.reply("🔍 Mencari musik di YouTube...")
            
            # Search for music
            results = await self.youtube.search_music(query, limit=5)
            
            if not results:
                await search_msg.edit("❌ Tidak ditemukan hasil untuk pencarian tersebut.")
                return
            
            # Store results for callback handling
            self.search_results[search_msg.id] = {
                'results': results,
                'current_index': 0,
                'chat_id': message.chat.id,
                'user_id': message.from_user.id
            }
            
            # Show first result
            await self.show_music_preview(client, search_msg, results[0], 0, len(results))
            
        except Exception as e:
            console.error(f"Error in search_and_show_results: {e}")
            await message.reply("❌ Terjadi kesalahan saat mencari musik.")
    
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
            
            # Send or edit message with photo
            if music_info['thumbnail']:
                if hasattr(message, 'photo') and message.photo:
                    await message.edit_media(
                        media=f"photo:{music_info['thumbnail']}",
                        caption=caption,
                        reply_markup=reply_markup
                    )
                else:
                    await message.delete()
                    new_msg = await client.send_photo(
                        chat_id=message.chat.id,
                        photo=music_info['thumbnail'],
                        caption=caption,
                        reply_markup=reply_markup
                    )
                    # Update stored message ID
                    if message.id in self.search_results:
                        self.search_results[new_msg.id] = self.search_results.pop(message.id)
            else:
                await message.edit_text(
                    text=caption,
                    reply_markup=reply_markup,
                    disable_web_page_preview=False
                )
                
        except Exception as e:
            console.error(f"Error showing music preview: {e}")
    
    async def handle_callback(self, client: Client, callback_query):
        """Handle music player callbacks"""
        try:
            data = callback_query.data
            message = callback_query.message
            user_id = callback_query.from_user.id
            
            # Check if user has permission (same user who initiated search)
            if message.id in self.search_results:
                if self.search_results[message.id]['user_id'] != user_id:
                    await callback_query.answer("❌ Hanya yang meminta musik yang bisa mengontrol player.", show_alert=True)
                    return
            
            if data.startswith("music_prev_"):
                await self.handle_navigation(client, callback_query, "prev")
            elif data.startswith("music_next_"):
                await self.handle_navigation(client, callback_query, "next")
            elif data.startswith("music_play_"):
                await self.handle_play(client, callback_query)
            elif data.startswith("music_close_"):
                await self.handle_close(client, callback_query)
            elif data.startswith("music_search_again_"):
                await self.handle_search_again(client, callback_query)
            elif data == "music_disabled":
                await callback_query.answer()
                
        except Exception as e:
            console.error(f"Error handling music callback: {e}")
            await callback_query.answer("❌ Terjadi kesalahan.")
    
    async def handle_navigation(self, client: Client, callback_query, direction: str):
        """Handle prev/next navigation"""
        try:
            message_id = callback_query.message.id
            if message_id not in self.search_results:
                await callback_query.answer("❌ Session expired.")
                return
            
            session = self.search_results[message_id]
            results = session['results']
            current_index = session['current_index']
            
            if direction == "prev" and current_index > 0:
                session['current_index'] -= 1
            elif direction == "next" and current_index < len(results) - 1:
                session['current_index'] += 1
            else:
                await callback_query.answer()
                return
            
            new_index = session['current_index']
            await self.show_music_preview(
                client, 
                callback_query.message, 
                results[new_index], 
                new_index, 
                len(results)
            )
            await callback_query.answer()
            
        except Exception as e:
            console.error(f"Error in navigation: {e}")
            await callback_query.answer("❌ Terjadi kesalahan.")
    
    async def handle_play(self, client: Client, callback_query):
        """Handle play button - join voice chat and play music"""
        try:
            data_parts = callback_query.data.split("_")
            video_id = data_parts[-1]
            message_id = int(data_parts[-2])
            
            if message_id not in self.search_results:
                await callback_query.answer("❌ Session expired.")
                return
            
            session = self.search_results[message_id]
            chat_id = session['chat_id']
            
            # Update message to show loading
            await callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⏳ Downloading...", callback_data="music_disabled")
                ]])
            )
            
            await callback_query.answer("🎵 Downloading and preparing music...")
            
            # Download audio
            audio_file = await self.youtube.download_audio(video_id)
            if not audio_file:
                await callback_query.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ Download Failed", callback_data="music_disabled")
                    ]])
                )
                return
            
            # Join voice chat and play
            success = await self.join_and_play(client, chat_id, audio_file, video_id)
            
            if success:
                # Update message to show now playing
                current_music = session['results'][session['current_index']]
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
            else:
                await callback_query.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ Failed to Play", callback_data="music_disabled")
                    ]])
                )
                
        except Exception as e:
            console.error(f"Error in handle_play: {e}")
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
            if message_id in self.search_results:
                del self.search_results[message_id]
            
            await callback_query.message.delete()
            await callback_query.answer("✅ Music player closed.")
            
        except Exception as e:
            console.error(f"Error closing music player: {e}")
            await callback_query.answer("❌ Terjadi kesalahan.")
    
    async def handle_search_again(self, client: Client, callback_query):
        """Handle search again button"""
        try:
            await callback_query.answer("🔍 Ketik perintah musik lagi untuk pencarian baru.")
            await self.handle_close(client, callback_query)
            
        except Exception as e:
            console.error(f"Error in search again: {e}")
            await callback_query.answer("❌ Terjadi kesalahan.")

# Global music player instance
music_player = MusicPlayer()