import yt_dlp
import asyncio
import os
import tempfile
from typing import List, Dict, Optional
from syncara import console

class YouTubeService:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
    
    async def search_music(self, query: str, limit: int = 5, retries: int = 3) -> List[Dict]:
        """Search for music on YouTube - with detailed logging and retry"""
        for attempt in range(1, retries+1):
            try:
                console.info(f"[YOUTUBE] Search attempt {attempt} for: {query}")
                search_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'default_search': f'ytsearch{limit}:',
                    'ignoreerrors': True,
                }
                def _search():
                    with yt_dlp.YoutubeDL(search_opts) as ydl:
                        return ydl.extract_info(query, download=False)
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(None, _search)
                console.info(f"[YOUTUBE] Search completed. Info type: {type(info)}")
                results = []
                if info and 'entries' in info:
                    console.info(f"[YOUTUBE] Found {len(info['entries'])} entries for query: {query}")
                    for i, entry in enumerate(info['entries']):
                        if entry and not entry.get('_type') == 'url':
                            try:
                                video_id = entry.get('id', '')
                                title = entry.get('title', 'Unknown Title')
                                uploader = entry.get('uploader', entry.get('channel', 'Unknown Channel'))
                                duration = entry.get('duration', 0)
                                view_count = entry.get('view_count', 0)
                                thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                                result = {
                                    'id': video_id,
                                    'title': title,
                                    'url': f"https://www.youtube.com/watch?v={video_id}",
                                    'thumbnail': thumbnail,
                                    'duration': duration or 0,
                                    'channel': uploader,
                                    'view_count': view_count or 0,
                                    'upload_date': entry.get('upload_date', ''),
                                }
                                results.append(result)
                                console.info(f"[YOUTUBE] Added result {i+1}: {title[:50]}...")
                            except Exception as e:
                                console.error(f"[YOUTUBE] Error processing entry {i}: {e}")
                                continue
                else:
                    console.warning(f"[YOUTUBE] No entries found in search results for query: {query}")
                console.info(f"[YOUTUBE] Returning {len(results)} results for query: {query}")
                return results
            except Exception as e:
                console.error(f"[YOUTUBE] Search error (attempt {attempt}) for query '{query}': {e}")
                import traceback
                console.error(f"[YOUTUBE] Traceback: {traceback.format_exc()}")
                if attempt < retries:
                    console.info(f"[YOUTUBE] Retrying search for '{query}' after delay...")
                    await asyncio.sleep(1)
                else:
                    console.error(f"[YOUTUBE] All retries failed for query: {query}")
                    return []
    
    async def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get detailed info for a specific video"""
        try:
            console.info(f"Getting video info for: {video_id}")
            def _get_info():
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _get_info)
            return info
        except Exception as e:
            console.error(f"Error getting video info: {e}")
            return None
    
    async def download_audio(self, video_id: str, output_dir: str = None) -> Optional[str]:
        """Download audio from YouTube video"""
        try:
            console.info(f"Downloading audio for video: {video_id}")
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            download_opts = self.ydl_opts.copy()
            download_opts.update({
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
            })
            def _download():
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}")
                    return ydl.prepare_filename(info)
            loop = asyncio.get_event_loop()
            filename = await loop.run_in_executor(None, _download)
            if os.path.exists(filename):
                console.info(f"Audio downloaded successfully: {filename}")
                return filename
            base_name = os.path.splitext(filename)[0]
            for ext in ['.m4a', '.mp3', '.webm', '.ogg']:
                test_file = base_name + ext
                if os.path.exists(test_file):
                    console.info(f"Audio found with extension {ext}: {test_file}")
                    return test_file
            console.error(f"Downloaded file not found: {filename}")
            return None
        except Exception as e:
            console.error(f"Error downloading audio: {e}")
            import traceback
            console.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def format_duration(self, seconds: int) -> str:
        """Format duration from seconds to MM:SS or HH:MM:SS"""
        if not seconds or seconds <= 0:
            return "0:00"
        if seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    def format_views(self, views: int) -> str:
        """Format view count to readable format"""
        if not views or views <= 0:
            return "0 views"
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M views"
        elif views >= 1_000:
            return f"{views / 1_000:.1f}K views"
        else:
            return f"{views} views"