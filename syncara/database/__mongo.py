from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, Optional, List
import logging

from config.config import MONGO_URI
from syncara.console import console

# Validate MongoDB URI
if not MONGO_URI:
    console.error("❌ MONGO_URI not found in environment variables!")
    raise ValueError("MONGO_URI is required for database connection")

# MongoDB connection with error handling
try:
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client.SyncaraBot
    console.info("✅ MongoDB client initialized successfully")
except Exception as e:
    console.error(f"❌ Failed to initialize MongoDB client: {e}")
    raise

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

# ==================== CONNECTION HEALTH CHECK ====================
async def check_database_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        # Ping database
        await mongo_client.admin.command('ping')
        console.info("🔄 Database connection is healthy")
        return True
    except Exception as e:
        console.error(f"❌ Database connection failed: {e}")
        return False

async def get_database_status() -> Dict[str, Any]:
    """Get comprehensive database status"""
    try:
        status = {
            "connection_healthy": await check_database_connection(),
            "client_info": {
                "host": mongo_client.HOST,
                "port": mongo_client.PORT,
                "database_name": "SyncaraBot"
            },
            "timestamp": datetime.utcnow()
        }
        
        if status["connection_healthy"]:
            # Get server info
            server_info = await mongo_client.server_info()
            status["server_info"] = {
                "version": server_info.get("version", "unknown"),
                "uptime": server_info.get("uptime", 0)
            }
            
            # Get database stats
            db_stats = await db.command("dbstats")
            status["database_stats"] = {
                "collections": db_stats.get("collections", 0),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0),
                "index_size": db_stats.get("indexSize", 0),
                "objects": db_stats.get("objects", 0)
            }
        
        return status
    except Exception as e:
        console.error(f"Error getting database status: {e}")
        return {"connection_healthy": False, "error": str(e)}

# ==================== DATABASE UTILITIES ====================
class DatabaseManager:
    """Database manager untuk operasi database yang umum"""
    
    def __init__(self):
        self.client = mongo_client
        self.db = db
    
    async def ensure_indexes(self):
        """Buat indexes untuk performa yang lebih baik"""
        try:
            console.info("🔧 Creating database indexes...")
            
            # Users collection indexes
            await users.create_index("user_id", unique=True)
            await users.create_index("username")
            await users.create_index("last_interaction")
            await users.create_index("interaction_count")
            
            # Groups collection indexes
            await groups.create_index("chat_id", unique=True)
            await groups.create_index("group_type")
            
            # Canvas files indexes
            await canvas_files.create_index([("chat_id", 1), ("filename", 1)], unique=True)
            await canvas_files.create_index("created_at")
            await canvas_files.create_index("updated_at")
            
            # Workflow executions indexes
            await workflow_executions.create_index("execution_id", unique=True)
            await workflow_executions.create_index([("user_id", 1), ("status", 1)])
            await workflow_executions.create_index("created_at")
            await workflow_executions.create_index("status")
            
            # Image generations indexes
            await image_generations.create_index("user_id")
            await image_generations.create_index("created_at")
            await image_generations.create_index("success")
            
            # User permissions indexes
            await user_permissions.create_index([("user_id", 1), ("chat_id", 1)], unique=True)
            await user_permissions.create_index("created_at")
            
            # Autonomous AI indexes
            await autonomous_tasks.create_index("task_id", unique=True)
            await autonomous_tasks.create_index("status")
            await autonomous_tasks.create_index("scheduled_at")
            
            await user_patterns.create_index("user_id")
            await user_patterns.create_index("pattern_type")
            await user_patterns.create_index("updated_at")
            
            await scheduled_actions.create_index("action_id", unique=True)
            await scheduled_actions.create_index("scheduled_at")
            await scheduled_actions.create_index("status")
            
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
            
            # Error logs indexes
            await error_logs.create_index("timestamp")
            await error_logs.create_index("module")
            
            # Performance metrics indexes
            await performance_metrics.create_index("timestamp")
            await performance_metrics.create_index("metric_name")
            
            console.info("✅ Database indexes created successfully")
            
        except Exception as e:
            console.error(f"❌ Error creating indexes: {e}")
            raise
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Bersihkan data lama untuk menghemat storage"""
        try:
            console.info(f"🧹 Starting cleanup of data older than {days_old} days...")
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cleanup_results = {}
            
            # Cleanup old logs
            logs_deleted = await system_logs.delete_many({"timestamp": {"$lt": cutoff_date}})
            cleanup_results["system_logs"] = logs_deleted.deleted_count
            
            errors_deleted = await error_logs.delete_many({"timestamp": {"$lt": cutoff_date}})
            cleanup_results["error_logs"] = errors_deleted.deleted_count
            
            # Cleanup old canvas history
            canvas_deleted = await canvas_history.delete_many({"created_at": {"$lt": cutoff_date}})
            cleanup_results["canvas_history"] = canvas_deleted.deleted_count
            
            # Cleanup old workflow executions
            workflow_deleted = await workflow_executions.delete_many({
                "created_at": {"$lt": cutoff_date},
                "status": {"$in": ["completed", "failed", "cancelled"]}
            })
            cleanup_results["workflow_executions"] = workflow_deleted.deleted_count
            
            # Cleanup old cache
            cache_deleted = await pyrogram_cache.delete_many({"expires_at": {"$lt": datetime.utcnow()}})
            cleanup_results["pyrogram_cache"] = cache_deleted.deleted_count
            
            # Cleanup old channel analytics (keep 3 months)
            analytics_cutoff = datetime.utcnow() - timedelta(days=90)
            analytics_deleted = await channel_analytics.delete_many({"timestamp": {"$lt": analytics_cutoff}})
            cleanup_results["channel_analytics"] = analytics_deleted.deleted_count
            
            # Cleanup old autonomous tasks
            autonomous_deleted = await autonomous_tasks.delete_many({
                "created_at": {"$lt": cutoff_date},
                "status": {"$in": ["completed", "failed"]}
            })
            cleanup_results["autonomous_tasks"] = autonomous_deleted.deleted_count
            
            console.info(f"✅ Cleanup completed. Results: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            console.error(f"❌ Error cleaning up old data: {e}")
            return {}
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Dapatkan statistik database"""
        try:
            stats = {}
            
            # Collection counts
            collections = [
                "users", "groups", "canvas_files", "workflow_executions",
                "image_generations", "user_permissions", "system_logs",
                "channel_posts", "channel_analytics", "autonomous_tasks",
                "user_patterns", "scheduled_actions", "error_logs"
            ]
            
            for collection_name in collections:
                collection = getattr(db, collection_name)
                count = await collection.count_documents({})
                stats[f"{collection_name}_count"] = count
            
            # Database size info
            db_stats = await db.command("dbstats")
            stats["database_info"] = {
                "collections": db_stats.get("collections", 0),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0),
                "index_size": db_stats.get("indexSize", 0),
                "objects": db_stats.get("objects", 0),
                "avg_obj_size": db_stats.get("avgObjSize", 0)
            }
            
            # Recent activity
            stats["recent_activity"] = {
                "recent_users": await users.count_documents({
                    "last_interaction": {"$gte": datetime.utcnow() - timedelta(days=7)}
                }),
                "today_interactions": await system_logs.count_documents({
                    "timestamp": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
                }),
                "active_workflows": await workflow_executions.count_documents({
                    "status": "running"
                })
            }
            
            return stats
            
        except Exception as e:
            console.error(f"❌ Error getting database stats: {e}")
            return {}
    
    async def backup_collection(self, collection_name: str, backup_path: str):
        """Backup koleksi tertentu"""
        try:
            console.info(f"💾 Starting backup of collection: {collection_name}")
            collection = getattr(db, collection_name)
            documents = await collection.find({}).to_list(length=None)
            
            import json
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, default=str, indent=2, ensure_ascii=False)
            
            console.info(f"✅ Collection {collection_name} backed up to {backup_path} ({len(documents)} documents)")
            return len(documents)
            
        except Exception as e:
            console.error(f"❌ Error backing up {collection_name}: {e}")
            return 0
    
    async def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity across collections"""
        try:
            console.info("🔍 Validating data integrity...")
            results = {}
            
            # Check for orphaned records
            # Canvas files without valid chat_ids
            canvas_without_chats = await canvas_files.count_documents({
                "chat_id": {"$nin": await groups.distinct("chat_id")}
            })
            results["orphaned_canvas_files"] = canvas_without_chats
            
            # Workflow executions without valid users
            workflow_without_users = await workflow_executions.count_documents({
                "user_id": {"$nin": await users.distinct("user_id")}
            })
            results["orphaned_workflows"] = workflow_without_users
            
            # Check for data consistency
            total_users = await users.count_documents({})
            users_with_patterns = await users.count_documents({"ai_learning_patterns": {"$exists": True}})
            
            results["data_consistency"] = {
                "total_users": total_users,
                "users_with_learning_patterns": users_with_patterns,
                "learning_coverage": f"{(users_with_patterns/total_users*100):.1f}%" if total_users > 0 else "0%"
            }
            
            console.info(f"✅ Data integrity validation completed: {results}")
            return results
            
        except Exception as e:
            console.error(f"❌ Error validating data integrity: {e}")
            return {}

# Create database manager instance
database_manager = DatabaseManager()

# ==================== INITIALIZATION ====================
async def initialize_database():
    """Inisialisasi database dengan indexes dan data awal"""
    try:
        console.info("🚀 Initializing database...")
        
        # Check connection first
        if not await check_database_connection():
            raise ConnectionError("Database connection failed")
        
        # Create indexes
        await database_manager.ensure_indexes()
        
        # Get initial stats
        stats = await database_manager.get_database_stats()
        console.info(f"📊 Database ready with {stats.get('database_info', {}).get('collections', 0)} collections")
        
        console.info("✅ Database initialized successfully")
        
    except Exception as e:
        console.error(f"❌ Error initializing database: {e}")
        raise

# ==================== HELPER FUNCTIONS ====================
async def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Dapatkan data user lengkap dengan error handling"""
    try:
        return await users.find_one({"user_id": user_id})
    except Exception as e:
        console.error(f"Error getting user data for {user_id}: {e}")
        return None

async def get_group_data(chat_id: int) -> Optional[Dict[str, Any]]:
    """Dapatkan data group lengkap dengan error handling"""
    try:
        return await groups.find_one({"chat_id": chat_id})
    except Exception as e:
        console.error(f"Error getting group data for {chat_id}: {e}")
        return None

async def log_system_event(level: str, module: str, message: str, metadata: Dict[str, Any] = None):
    """Log system event ke database dengan error handling"""
    try:
        await system_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "level": level,
            "module": module,
            "message": message,
            "metadata": metadata or {}
        })
    except Exception as e:
        console.error(f"Error logging system event: {e}")

async def log_error(module: str, error: str, traceback: str = None, user_id: int = None, chat_id: int = None):
    """Log error ke database dengan error handling"""
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
        console.error(f"Error logging error: {e}")

async def record_performance_metric(metric_name: str, value: float, unit: str = "ms", metadata: Dict[str, Any] = None):
    """Record performance metric dengan error handling"""
    try:
        await performance_metrics.insert_one({
            "timestamp": datetime.utcnow(),
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "metadata": metadata or {}
        })
    except Exception as e:
        console.error(f"Error recording performance metric: {e}")

# ==================== HEALTH CHECK FUNCTIONS ====================
async def run_database_health_check() -> Dict[str, Any]:
    """Run comprehensive database health check"""
    try:
        console.info("🏥 Running database health check...")
        
        health_report = {
            "timestamp": datetime.utcnow(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # Connection check
        health_report["checks"]["connection"] = await check_database_connection()
        
        # Stats check
        stats = await database_manager.get_database_stats()
        health_report["checks"]["stats_available"] = bool(stats)
        
        # Data integrity check
        integrity = await database_manager.validate_data_integrity()
        health_report["checks"]["data_integrity"] = bool(integrity)
        
        # Performance check (simple query timing)
        start_time = datetime.utcnow()
        await users.count_documents({})
        query_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        health_report["checks"]["query_performance"] = {
            "acceptable": query_time < 1000,  # < 1 second
            "query_time_ms": query_time
        }
        
        # Overall status
        failed_checks = [k for k, v in health_report["checks"].items() 
                        if (isinstance(v, bool) and not v) or 
                           (isinstance(v, dict) and not v.get("acceptable", True))]
        
        if failed_checks:
            health_report["overall_status"] = "degraded"
            health_report["failed_checks"] = failed_checks
        
        console.info(f"✅ Health check completed: {health_report['overall_status']}")
        return health_report
        
    except Exception as e:
        console.error(f"❌ Error running health check: {e}")
        return {
            "timestamp": datetime.utcnow(),
            "overall_status": "error",
            "error": str(e)
        }

# ==================== CHANNEL MANAGEMENT HELPERS ====================
async def log_channel_post(post_id: str, content_type: str, title: str, status: str = "generated"):
    """Log channel post to database dengan error handling"""
    try:
        await channel_posts.insert_one({
            "post_id": post_id,
            "type": content_type,
            "title": title,
            "status": status,
            "created_at": datetime.utcnow()
        })
    except Exception as e:
        console.error(f"Error logging channel post: {e}")

async def update_channel_post_status(post_id: str, status: str, posted_time: datetime = None):
    """Update channel post status dengan error handling"""
    try:
        update_data = {"status": status}
        if posted_time:
            update_data["posted_time"] = posted_time
        
        await channel_posts.update_one(
            {"post_id": post_id},
            {"$set": update_data}
        )
    except Exception as e:
        console.error(f"Error updating channel post status: {e}")

async def get_channel_analytics_summary() -> Dict[str, Any]:
    """Get channel analytics summary dengan error handling"""
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
        console.error(f"Error getting channel analytics: {e}")
        return {}

# ==================== STARTUP ====================
# NOTE: Database initialization akan dipanggil dari __main__.py
# Tidak menggunakan asyncio.create_task() di sini untuk menghindari event loop error