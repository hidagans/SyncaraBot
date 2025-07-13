from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, Optional, List

from config.config import MONGO_URI

# MongoDB connection
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.SyncaraBot

# ==================== CORE COLLECTIONS ====================
# User and Group Management
users = db.users
groups = db.groups

# ==================== FEATURE COLLECTIONS ====================
# AI Learning and Memory
ai_learning = db.ai_learning
assistant_memory = db.assistant_memory
conversation_history = db.conversation_history

# Canvas Management
canvas_files = db.canvas_files
canvas_history = db.canvas_history

# Todo Management (sudah ada implementasi di todo_management.py)
# Koleksi todos dibuat dinamis per chat: todos_{chat_id}

# Multi-step Processing
workflow_definitions = db.workflow_definitions
workflow_executions = db.workflow_executions
workflow_templates = db.workflow_templates

# Image Generation
image_generations = db.image_generations
image_history = db.image_history

# User/Group Management
user_permissions = db.user_permissions
group_settings = db.group_settings
user_warnings = db.user_warnings
ban_records = db.ban_records
mute_records = db.mute_records

# Pyrogram Integration
pyrogram_sessions = db.pyrogram_sessions
pyrogram_cache = db.pyrogram_cache

# Autonomous AI
autonomous_tasks = db.autonomous_tasks
user_patterns = db.user_patterns
scheduled_actions = db.scheduled_actions

# Channel Management
channel_posts = db.channel_posts
channel_analytics = db.channel_analytics
channel_schedule = db.channel_schedule
channel_content_queue = db.channel_content_queue

# System Monitoring
system_logs = db.system_logs
performance_metrics = db.performance_metrics
error_logs = db.error_logs

# ==================== DATABASE UTILITIES ====================
class DatabaseManager:
    """Database manager untuk operasi database yang umum"""
    
    def __init__(self):
        self.client = mongo_client
        self.db = db
    
    async def ensure_indexes(self):
        """Buat indexes untuk performa yang lebih baik"""
        try:
            # Users collection indexes
            await users.create_index("user_id", unique=True)
            await users.create_index("username")
            await users.create_index("last_interaction")
            
            # Groups collection indexes
            await groups.create_index("chat_id", unique=True)
            await groups.create_index("group_type")
            
            # Canvas files indexes
            await canvas_files.create_index([("chat_id", 1), ("filename", 1)], unique=True)
            await canvas_files.create_index("created_at")
            
            # Workflow executions indexes
            await workflow_executions.create_index("execution_id", unique=True)
            await workflow_executions.create_index([("user_id", 1), ("status", 1)])
            await workflow_executions.create_index("created_at")
            
            # Image generations indexes
            await image_generations.create_index("user_id")
            await image_generations.create_index("created_at")
            
            # User permissions indexes
            await user_permissions.create_index([("user_id", 1), ("chat_id", 1)], unique=True)
            
            # Channel management indexes
            await channel_posts.create_index("post_id", unique=True)
            await channel_posts.create_index("type")
            await channel_posts.create_index("created_at")
            await channel_posts.create_index("posted_time")
            await channel_posts.create_index("status")
            
            await channel_analytics.create_index("timestamp")
            await channel_analytics.create_index("channel_username")
            
            await channel_schedule.create_index("content_type")
            await channel_schedule.create_index("scheduled_time")
            
            # System logs indexes
            await system_logs.create_index("timestamp")
            await system_logs.create_index("level")
            await system_logs.create_index("module")
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Bersihkan data lama untuk menghemat storage"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Cleanup old logs
            await system_logs.delete_many({"timestamp": {"$lt": cutoff_date}})
            await error_logs.delete_many({"timestamp": {"$lt": cutoff_date}})
            
            # Cleanup old canvas history
            await canvas_history.delete_many({"created_at": {"$lt": cutoff_date}})
            
            # Cleanup old workflow executions
            await workflow_executions.delete_many({
                "created_at": {"$lt": cutoff_date},
                "status": {"$in": ["completed", "failed", "cancelled"]}
            })
            
            # Cleanup old cache
            await pyrogram_cache.delete_many({"expires_at": {"$lt": datetime.utcnow()}})
            
            # Cleanup old channel analytics (keep 3 months)
            analytics_cutoff = datetime.utcnow() - timedelta(days=90)
            await channel_analytics.delete_many({"timestamp": {"$lt": analytics_cutoff}})
            
            print(f"✅ Cleaned up data older than {days_old} days")
            
        except Exception as e:
            print(f"❌ Error cleaning up old data: {e}")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Dapatkan statistik database"""
        try:
            stats = {}
            
            # Collection counts
            collections = [
                "users", "groups", "canvas_files", "workflow_executions",
                "image_generations", "user_permissions", "system_logs",
                "channel_posts", "channel_analytics"
            ]
            
            for collection_name in collections:
                collection = getattr(db, collection_name)
                count = await collection.count_documents({})
                stats[collection_name] = count
            
            # Database size info
            db_stats = await db.command("dbstats")
            stats["database_size"] = db_stats.get("dataSize", 0)
            stats["storage_size"] = db_stats.get("storageSize", 0)
            stats["index_size"] = db_stats.get("indexSize", 0)
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}
    
    async def backup_collection(self, collection_name: str, backup_path: str):
        """Backup koleksi tertentu"""
        try:
            collection = getattr(db, collection_name)
            documents = await collection.find({}).to_list(length=None)
            
            import json
            with open(backup_path, 'w') as f:
                json.dump(documents, f, default=str, indent=2)
            
            print(f"✅ Collection {collection_name} backed up to {backup_path}")
            
        except Exception as e:
            print(f"❌ Error backing up {collection_name}: {e}")

# Create database manager instance
database_manager = DatabaseManager()

# ==================== INITIALIZATION ====================
async def initialize_database():
    """Inisialisasi database dengan indexes dan data awal"""
    try:
        await database_manager.ensure_indexes()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

# ==================== HELPER FUNCTIONS ====================
async def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Dapatkan data user lengkap"""
    return await users.find_one({"user_id": user_id})

async def get_group_data(chat_id: int) -> Optional[Dict[str, Any]]:
    """Dapatkan data group lengkap"""
    return await groups.find_one({"chat_id": chat_id})

async def log_system_event(level: str, module: str, message: str, metadata: Dict[str, Any] = None):
    """Log system event ke database"""
    try:
        await system_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "level": level,
            "module": module,
            "message": message,
            "metadata": metadata or {}
        })
    except Exception as e:
        print(f"Error logging system event: {e}")

async def log_error(module: str, error: str, traceback: str = None, user_id: int = None, chat_id: int = None):
    """Log error ke database"""
    try:
        await error_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "module": module,
            "error": error,
            "traceback": traceback,
            "user_id": user_id,
            "chat_id": chat_id
        })
    except Exception as e:
        print(f"Error logging error: {e}")

async def record_performance_metric(metric_name: str, value: float, unit: str = "ms", metadata: Dict[str, Any] = None):
    """Record performance metric"""
    try:
        await performance_metrics.insert_one({
            "timestamp": datetime.utcnow(),
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "metadata": metadata or {}
        })
    except Exception as e:
        print(f"Error recording performance metric: {e}")

# ==================== CHANNEL MANAGEMENT HELPERS ====================
async def log_channel_post(post_id: str, content_type: str, title: str, status: str = "generated"):
    """Log channel post to database"""
    try:
        await channel_posts.insert_one({
            "post_id": post_id,
            "type": content_type,
            "title": title,
            "status": status,
            "created_at": datetime.utcnow()
        })
    except Exception as e:
        print(f"Error logging channel post: {e}")

async def update_channel_post_status(post_id: str, status: str, posted_time: datetime = None):
    """Update channel post status"""
    try:
        update_data = {"status": status}
        if posted_time:
            update_data["posted_time"] = posted_time
        
        await channel_posts.update_one(
            {"post_id": post_id},
            {"$set": update_data}
        )
    except Exception as e:
        print(f"Error updating channel post status: {e}")

async def get_channel_analytics_summary() -> Dict[str, Any]:
    """Get channel analytics summary"""
    try:
        # Get latest analytics
        latest = await channel_analytics.find({}).sort("timestamp", -1).limit(1).to_list(length=1)
        
        # Get posts count
        total_posts = await channel_posts.count_documents({"status": "posted"})
        
        # Get today's posts
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts = await channel_posts.count_documents({
            "status": "posted",
            "posted_time": {"$gte": today_start}
        })
        
        return {
            "latest_analytics": latest[0] if latest else {},
            "total_posts": total_posts,
            "today_posts": today_posts,
            "last_updated": datetime.utcnow()
        }
    except Exception as e:
        print(f"Error getting channel analytics: {e}")
        return {}

# ==================== STARTUP ====================
# Initialize database saat import
asyncio.create_task(initialize_database())