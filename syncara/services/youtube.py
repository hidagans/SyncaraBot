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
    
    async def search_music(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for music on YouTube"""
        try:
            search_opts = self.ydl_opts.copy()
            search_opts.update({
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch' + str(limit) + ':',
            })
            
            def _search():
                with yt_dlp.YoutubeDL(search_opts) as ydl:
                    return ydl.extract_info(query, download=False)
            
            # Run in thread to avoid blocking
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _search)
            
            results = []
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        # Get detailed info for each video
                        detailed_info = await self.get_video_info(entry['id'])
                        if detailed_info:
                            results.append({
                                'id': entry['id'],
                                'title': entry.get('title', 'Unknown Title'),
                                'url': f"https://www.youtube.com/watch?v={entry['id']}",
                                'thumbnail': detailed_info.get('thumbnail'),
                                'duration': detailed_info.get('duration', 0),
                                'channel': detailed_info.get('uploader', 'Unknown Channel'),
                                'view_count': detailed_info.get('view_count', 0),
                                'upload_date': detailed_info.get('upload_date', ''),
                            })
            
            return results
            
        except Exception as e:
            console.error(f"Error searching YouTube: {e}")
            return []
    
    async def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get detailed info for a specific video"""
        try:
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
            
            # Check if file exists and return path
            if os.path.exists(filename):
                return filename
            
            # Try with different extensions
            base_name = os.path.splitext(filename)[0]
            for ext in ['.m4a', '.mp3', '.webm', '.ogg']:
                test_file = base_name + ext
                if os.path.exists(test_file):
                    return test_file
            
            return None
            
        except Exception as e:
            console.error(f"Error downloading audio: {e}")
            return None
    
    def format_duration(self, seconds: int) -> str:
        """Format duration from seconds to MM:SS or HH:MM:SS"""
        if seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    def format_views(self, views: int) -> str:
        """Format view count to readable format"""
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M views"
        elif views >= 1_000:
            return f"{views / 1_000:.1f}K views"
        else:
            return f"{views} views"