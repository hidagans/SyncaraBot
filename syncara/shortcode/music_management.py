import os
from syncara import console
from syncara.modules.music_player import music_player

class MusicManagementShortcode:
    def __init__(self):
        self.handlers = {
            'MUSIC:PLAY': self.play_music,
            'MUSIC:SEARCH': self.search_music,
            'MUSIC:STOP': self.stop_music,
            'MUSIC:PAUSE': self.pause_music,
            'MUSIC:RESUME': self.resume_music,
            'MUSIC:SKIP': self.skip_music,
        }
        
        self.descriptions = {
            'MUSIC:PLAY': 'Search and play music from YouTube. Usage: [MUSIC:PLAY:song_name]',
            'MUSIC:SEARCH': 'Search for music without playing. Usage: [MUSIC:SEARCH:song_name]',
            'MUSIC:STOP': 'Stop current music and leave voice chat. Usage: [MUSIC:STOP]',
            'MUSIC:PAUSE': 'Pause current music. Usage: [MUSIC:PAUSE]',
            'MUSIC:RESUME': 'Resume paused music. Usage: [MUSIC:RESUME]',
            'MUSIC:SKIP': 'Skip current music. Usage: [MUSIC:SKIP]'
        }
    
    async def play_music(self, client, message, params):
        """Search and show music options for playing - Assistant will handle the UI"""
        try:
            if not params.strip():
                await message.reply("❌ Mohon berikan nama lagu yang ingin dicari.\nContoh: [MUSIC:PLAY:Shape of You]")
                return False
            
            # Send search request via assistant (userbot)
            await message.reply(f"🔍 Mencari musik: **{params}**\n\nTunggu sebentar...")
            
            # Let the assistant handle the search and display
            await music_player.search_and_show_results(client, message, params)
            return True
            
        except Exception as e:
            console.error(f"Error in play_music: {e}")
            await message.reply(f"❌ Terjadi kesalahan saat mencari musik: {str(e)}")
            return False
    
    async def search_music(self, client, message, params):
        """Search for music without playing - Assistant will handle the UI"""
        try:
            if not params.strip():
                await message.reply("❌ Mohon berikan nama lagu yang ingin dicari.\nContoh: [MUSIC:SEARCH:Shape of You]")
                return False
            
            # Send search request via assistant (userbot)
            await message.reply(f"🔍 Mencari musik: **{params}**\n\nTunggu sebentar...")
            
            # Let the assistant handle the search and display
            await music_player.search_and_show_results(client, message, params)
            return True
            
        except Exception as e:
            console.error(f"Error in search_music: {e}")
            await message.reply(f"❌ Terjadi kesalahan saat mencari musik: {str(e)}")
            return False
    
    async def stop_music(self, client, message, params):
        """Stop current music"""
        try:
            chat_id = message.chat.id
            
            if chat_id not in music_player.current_sessions:
                await message.reply("❌ Tidak ada musik yang sedang diputar.")
                return False
            
            # Stop and leave voice chat
            if hasattr(client, 'pytgcalls'):
                try:
                    await client.pytgcalls.leave_group_call(chat_id)
                except:
                    pass
            
            # Clean up session
            session = music_player.current_sessions.pop(chat_id, {})
            
            # Clean up audio file
            audio_file = session.get('audio_file')
            if audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except:
                    pass
            
            await message.reply("⏹️ Musik dihentikan dan keluar dari voice chat.")
            return True
            
        except Exception as e:
            console.error(f"Error in stop_music: {e}")
            return False
    
    async def pause_music(self, client, message, params):
        """Pause current music"""
        try:
            chat_id = message.chat.id
            
            if chat_id not in music_player.current_sessions:
                await message.reply("❌ Tidak ada musik yang sedang diputar.")
                return False
            
            if hasattr(client, 'pytgcalls'):
                try:
                    await client.pytgcalls.pause_stream(chat_id)
                    await message.reply("⏸️ Musik dijeda.")
                    return True
                except Exception as e:
                    console.error(f"Error pausing music: {e}")
                    return False
            
            return False
            
        except Exception as e:
            console.error(f"Error in pause_music: {e}")
            return False
    
    async def resume_music(self, client, message, params):
        """Resume paused music"""
        try:
            chat_id = message.chat.id
            
            if chat_id not in music_player.current_sessions:
                await message.reply("❌ Tidak ada musik yang sedang diputar.")
                return False
            
            if hasattr(client, 'pytgcalls'):
                try:
                    await client.pytgcalls.resume_stream(chat_id)
                    await message.reply("▶️ Musik dilanjutkan.")
                    return True
                except Exception as e:
                    console.error(f"Error resuming music: {e}")
                    return False
            
            return False
            
        except Exception as e:
            console.error(f"Error in resume_music: {e}")
            return False
    
    async def skip_music(self, client, message, params):
        """Skip current music"""
        try:
            # For now, skip = stop (you can implement queue later)
            return await self.stop_music(client, message, params)
            
        except Exception as e:
            console.error(f"Error in skip_music: {e}")
            return False