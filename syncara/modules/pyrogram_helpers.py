# syncara/modules/pyrogram_helpers.py
"""
Helper utilities dan cache system untuk Pyrogram methods.
"""

import asyncio
import time
import json
import os
import hashlib
import pickle
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from syncara.console import console
from pyrogram import types, enums
import aiofiles
from functools import wraps
from collections import defaultdict
import threading

class CacheManager:
    """
    Manager untuk caching data dengan TTL (Time To Live).
    """
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        return time.time() > cache_entry.get('expires_at', 0)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache entry"""
        with self.lock:
            expires_at = time.time() + (ttl or self.default_ttl)
            self.cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache entry"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if self._is_expired(entry):
                del self.cache[key]
                return None
            
            return entry['value']
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Cleanup expired entries"""
        with self.lock:
            expired_keys = []
            for key, entry in self.cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_entries = len(self.cache)
            total_size = sum(len(str(entry['value'])) for entry in self.cache.values())
            
            return {
                'total_entries': total_entries,
                'total_size_bytes': total_size,
                'oldest_entry': min(
                    (entry['created_at'] for entry in self.cache.values()),
                    default=None
                ),
                'newest_entry': max(
                    (entry['created_at'] for entry in self.cache.values()),
                    default=None
                )
            }

class RateLimiter:
    """
    Rate limiter untuk mencegah spam requests.
    """
    
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Clean old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            
            # Check if under limit
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True
            
            return False
    
    def get_reset_time(self, key: str) -> float:
        """Get time when rate limit resets"""
        with self.lock:
            if key not in self.requests or not self.requests[key]:
                return 0
            
            oldest_request = min(self.requests[key])
            return oldest_request + self.window_seconds
    
    def reset(self, key: str) -> None:
        """Reset rate limit for key"""
        with self.lock:
            if key in self.requests:
                del self.requests[key]

class PerformanceMonitor:
    """
    Monitor untuk performance method calls.
    """
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.records: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def record(self, method_name: str, duration: float, success: bool, **kwargs) -> None:
        """Record method call performance"""
        with self.lock:
            record = {
                'method': method_name,
                'duration': duration,
                'success': success,
                'timestamp': time.time(),
                'metadata': kwargs
            }
            
            self.records.append(record)
            
            # Keep only max_records
            if len(self.records) > self.max_records:
                self.records = self.records[-self.max_records:]
    
    def get_stats(self, method_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            records = self.records
            if method_name:
                records = [r for r in records if r['method'] == method_name]
            
            if not records:
                return {}
            
            durations = [r['duration'] for r in records]
            successes = [r for r in records if r['success']]
            
            return {
                'total_calls': len(records),
                'success_rate': len(successes) / len(records) if records else 0,
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0,
                'recent_calls': records[-10:] if records else []
            }

class FileCache:
    """
    File-based cache untuk persistent storage.
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache entry to file"""
        file_path = self._get_file_path(key)
        
        cache_data = {
            'value': value,
            'expires_at': time.time() + (ttl or 3600),
            'created_at': time.time()
        }
        
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(pickle.dumps(cache_data))
        except Exception as e:
            console.error(f"Error saving cache to file: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cache entry from file"""
        file_path = self._get_file_path(key)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                cache_data = pickle.loads(await f.read())
            
            if time.time() > cache_data.get('expires_at', 0):
                os.remove(file_path)
                return None
            
            return cache_data['value']
        except Exception as e:
            console.error(f"Error loading cache from file: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry file"""
        file_path = self._get_file_path(key)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                console.error(f"Error deleting cache file: {e}")
        
        return False
    
    async def clear(self) -> int:
        """Clear all cache files"""
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
        except Exception as e:
            console.error(f"Error clearing cache: {e}")
        
        return count

class MessageQueue:
    """
    Queue untuk message processing dengan priority dan delay.
    """
    
    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.PriorityQueue(maxsize=max_size)
        self.running = False
        self.workers = []
    
    async def put(self, message: Dict[str, Any], priority: int = 5, delay: float = 0) -> None:
        """Add message to queue"""
        if delay > 0:
            await asyncio.sleep(delay)
        
        queue_item = {
            'priority': priority,
            'message': message,
            'timestamp': time.time()
        }
        
        await self.queue.put((priority, queue_item))
    
    async def get(self) -> Dict[str, Any]:
        """Get message from queue"""
        _, queue_item = await self.queue.get()
        return queue_item['message']
    
    async def worker(self, worker_id: int, handler: Callable):
        """Worker to process messages"""
        while self.running:
            try:
                message = await self.get()
                await handler(message)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                console.error(f"Worker {worker_id} error: {e}")
    
    async def start_workers(self, num_workers: int = 3, handler: Callable = None):
        """Start worker processes"""
        self.running = True
        
        for i in range(num_workers):
            worker = asyncio.create_task(self.worker(i, handler))
            self.workers.append(worker)
    
    async def stop_workers(self):
        """Stop worker processes"""
        self.running = False
        
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

class PyrogramHelpers:
    """
    Helper utilities untuk Pyrogram operations.
    """
    
    def __init__(self):
        self.cache = CacheManager()
        self.rate_limiter = RateLimiter()
        self.performance_monitor = PerformanceMonitor()
        self.file_cache = FileCache()
        self.message_queue = MessageQueue()
        
        # Start cache cleanup task
        asyncio.create_task(self._cleanup_task())
    
    async def _cleanup_task(self):
        """Background task untuk cleanup cache"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 menit
                expired_count = self.cache.cleanup_expired()
                if expired_count > 0:
                    console.info(f"Cleaned up {expired_count} expired cache entries")
            except Exception as e:
                console.error(f"Error in cleanup task: {e}")
    
    def cache_method(self, ttl: int = 3600, use_file_cache: bool = False):
        """
        Decorator untuk caching method results.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create cache key
                cache_key = f"{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
                
                # Try to get from cache
                cache_manager = self.file_cache if use_file_cache else self.cache
                cached_result = await cache_manager.get(cache_key) if use_file_cache else cache_manager.get(cache_key)
                
                if cached_result is not None:
                    return cached_result
                
                # Call actual function
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    
                    # Cache result
                    if use_file_cache:
                        await cache_manager.set(cache_key, result, ttl)
                    else:
                        cache_manager.set(cache_key, result, ttl)
                    
                    # Record performance
                    duration = time.time() - start_time
                    self.performance_monitor.record(func.__name__, duration, True)
                    
                    return result
                except Exception as e:
                    # Record performance
                    duration = time.time() - start_time
                    self.performance_monitor.record(func.__name__, duration, False, error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    def rate_limit(self, max_requests: int = 30, window_seconds: int = 60):
        """
        Decorator untuk rate limiting.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create rate limit key
                rate_key = f"{func.__name__}:{args[0] if args else 'default'}"
                
                if not self.rate_limiter.is_allowed(rate_key):
                    reset_time = self.rate_limiter.get_reset_time(rate_key)
                    wait_time = reset_time - time.time()
                    raise Exception(f"Rate limit exceeded. Try again in {wait_time:.2f} seconds")
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def performance_monitor_decorator(self):
        """
        Decorator untuk monitoring performance.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.performance_monitor.record(func.__name__, duration, True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.performance_monitor.record(func.__name__, duration, False, error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    async def batch_operation(self, operations: List[Callable], batch_size: int = 10, delay: float = 0.1) -> List[Any]:
        """
        Execute operations in batches untuk menghindari rate limiting.
        """
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            
            batch_results = await asyncio.gather(*[op() for op in batch], return_exceptions=True)
            results.extend(batch_results)
            
            # Delay between batches
            if delay > 0 and i + batch_size < len(operations):
                await asyncio.sleep(delay)
        
        return results
    
    def create_progress_callback(self, total_items: int, description: str = "Processing"):
        """
        Create progress callback untuk long-running operations.
        """
        processed = 0
        
        def callback(current: int = None):
            nonlocal processed
            if current is not None:
                processed = current
            else:
                processed += 1
            
            percentage = (processed / total_items) * 100
            console.info(f"{description}: {processed}/{total_items} ({percentage:.1f}%)")
        
        return callback
    
    async def safe_execute(self, operation: Callable, max_retries: int = 3, delay: float = 1.0) -> Any:
        """
        Safely execute operation dengan retry logic.
        """
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                console.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        elif seconds < 86400:
            return f"{seconds/3600:.1f}h"
        else:
            return f"{seconds/86400:.1f}d"
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        return re.findall(r'@(\w+)', text)
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        return re.findall(r'#(\w+)', text)
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations"""
        import re
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        return os.path.splitext(filename)[1].lower()
    
    def is_image_file(self, filename: str) -> bool:
        """Check if file is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
        return self.get_file_extension(filename) in image_extensions
    
    def is_video_file(self, filename: str) -> bool:
        """Check if file is a video"""
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        return self.get_file_extension(filename) in video_extensions
    
    def is_audio_file(self, filename: str) -> bool:
        """Check if file is an audio"""
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']
        return self.get_file_extension(filename) in audio_extensions
    
    async def get_media_info(self, file_path: str) -> Dict[str, Any]:
        """Get media file information"""
        try:
            import ffprobe
            
            info = ffprobe.FFProbe(file_path)
            
            return {
                'duration': info.duration,
                'width': info.width,
                'height': info.height,
                'format': info.format,
                'size': os.path.getsize(file_path),
                'bitrate': info.bitrate
            }
        except Exception as e:
            console.error(f"Error getting media info: {e}")
            return {
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
    
    async def compress_image(self, input_path: str, output_path: str, quality: int = 85) -> bool:
        """Compress image file"""
        try:
            from PIL import Image
            
            with Image.open(input_path) as img:
                img.save(output_path, optimize=True, quality=quality)
            
            return True
        except Exception as e:
            console.error(f"Error compressing image: {e}")
            return False
    
    async def create_thumbnail(self, input_path: str, output_path: str, size: tuple = (200, 200)) -> bool:
        """Create thumbnail from image"""
        try:
            from PIL import Image
            
            with Image.open(input_path) as img:
                img.thumbnail(size)
                img.save(output_path)
            
            return True
        except Exception as e:
            console.error(f"Error creating thumbnail: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'memory_cache': self.cache.get_stats(),
            'performance_stats': self.performance_monitor.get_stats(),
            'rate_limiter_stats': {
                'active_keys': len(self.rate_limiter.requests)
            }
        }
    
    async def cleanup_cache(self) -> Dict[str, int]:
        """Cleanup all caches"""
        memory_cleaned = self.cache.cleanup_expired()
        file_cleaned = await self.file_cache.clear()
        
        return {
            'memory_cache_cleaned': memory_cleaned,
            'file_cache_cleaned': file_cleaned
        }

# Global instance
pyrogram_helpers = PyrogramHelpers() 