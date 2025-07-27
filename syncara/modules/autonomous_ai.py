import asyncio
from datetime import datetime, timedelta
import random
from syncara.shortcode import registry
from syncara.services import ReplicateAPI
from syncara.database import db, users, user_patterns, autonomous_tasks, scheduled_actions
from syncara.console import console

class AutonomousAI:
    def __init__(self):
        self.active_tasks = {}
        self.monitoring_chats = set()
        self.user_patterns = {}
        self.scheduled_actions = []
        self.is_running = False
        self.last_activity_check = datetime.now()
    
    async def start_autonomous_mode(self):
        console.info("🤖 Starting Autonomous AI Mode...")
        self.is_running = True
        # Start multiple background tasks
        tasks = [
            asyncio.create_task(self.monitor_user_activity()),
            asyncio.create_task(self.proactive_assistance()),
            asyncio.create_task(self.scheduled_tasks_runner()),
            asyncio.create_task(self.chat_health_monitor()),
            asyncio.create_task(self.learning_optimizer()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            console.error(f"Error in autonomous mode: {e}")
            self.is_running = False
    
    async def monitor_user_activity(self):
        console.info("🔍 Starting user activity monitoring...")
        while self.is_running:
            try:
                active_users = await self.get_active_users()
                console.info(f"📊 Monitoring {len(active_users)} active users")
                
                for user_id in active_users:
                    pattern = await self.analyze_user_pattern(user_id)
                    if pattern and pattern.get('prediction_confidence', 0) > 0.7:
                        await self.execute_proactive_action(user_id, pattern)
                
                # Update last activity check
                self.last_activity_check = datetime.now()
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                console.error(f"Error in monitor_user_activity: {e}")
                await asyncio.sleep(60)
    
    async def proactive_assistance(self):
        console.info("🚀 Starting proactive assistance...")
        from syncara import assistant_manager
        
        while self.is_running:
            try:
                assistants = assistant_manager.get_all_assistants()
                console.info(f"🤖 Running proactive assistance for {len(assistants)} assistants")
                
                for assistant_id, assistant_data in assistants.items():
                    client = assistant_data["client"]
                    opportunities = await self.find_proactive_opportunities(assistant_id)
                    
                    for opportunity in opportunities:
                        await self.execute_proactive_help(client, opportunity)
                        await asyncio.sleep(10)  # Delay between actions
                
                await asyncio.sleep(900)  # Check every 15 minutes
                
            except Exception as e:
                console.error(f"Error in proactive_assistance: {e}")
                await asyncio.sleep(120)
    
    async def execute_proactive_action(self, user_id, pattern):
        """Execute proactive action with error handling"""
        from syncara import assistant_manager
        try:
            action_type = pattern['suggested_action']
            assistant_id = self.select_best_assistant(action_type)
            client = assistant_manager.get_assistant(assistant_id)
            
            if not client:
                console.warning(f"Assistant {assistant_id} not available")
                return
            
            proactive_message = await self.generate_proactive_message(user_id, pattern)
            
            success = await self.safe_send_message(
                client=client, 
                user_id=user_id, 
                text=f"💡 **Proactive Assistant**\n\n{proactive_message}",
                message_type="proactive_action"
            )
            
            if success:
                await self.log_proactive_action(user_id, action_type, proactive_message)
                console.info(f"✅ Sent proactive message to user {user_id}")
            
        except Exception as e:
            console.error(f"Error in execute_proactive_action: {e}")
    
    async def generate_proactive_message(self, user_id, pattern):
        try:
            user_context = await self.get_user_context(user_id)
            
            messages = {
                'help_offer': [
                    "Hai! Aku lihat kamu sering nanya tentang ini. Butuh bantuan lebih detail? 🤔",
                    "Ada yang bisa aku bantu? Aku notice kamu lagi explore fitur ini 😊",
                    "Mau aku kasih tips untuk hal yang kamu lagi cari? 💡"
                ],
                'feature_suggestion': [
                    "Eh, tau gak ada fitur baru yang mungkin kamu suka? Mau aku tunjukin? ✨",
                    "Kamu udah coba fitur shortcode belum? Bisa bikin hidup lebih mudah loh! 🚀",
                    "Ada cara lebih efisien buat yang kamu lagi kerjain nih 🔧"
                ],
                'reminder': [
                    "Ingetin aja, jangan lupa istirahat ya! 😴",
                    "Udah lama gak ngobrol, apa kabar? 👋",
                    "Ada yang tertunda gak? Mau aku bantu track? 📝"
                ]
            }
            
            action_type = pattern.get('suggested_action', 'help_offer')
            possible_messages = messages.get(action_type, messages['help_offer'])
            
            return random.choice(possible_messages)
            
        except Exception as e:
            console.error(f"Error generating proactive message: {e}")
            return "Hai! Ada yang bisa aku bantu? 😊"
    
    # REAL IMPLEMENTATIONS instead of placeholders
    async def get_active_users(self):
        """Get users who have been active in the last 24 hours"""
        try:
            # Get users with recent activity, but exclude unreachable ones
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            active_users_cursor = users.find({
                "last_interaction": {"$gte": cutoff_time},
                "interaction_count": {"$gte": 3},  # At least 3 interactions
                "unreachable": {"$ne": True},  # Not marked as unreachable
                "conversation_history": {"$exists": True, "$ne": []}  # Has conversation history
            }).limit(30)  # Reduce limit to avoid overwhelming
            
            active_users = []
            async for user in active_users_cursor:
                active_users.append(user["user_id"])
            
            return active_users
            
        except Exception as e:
            console.error(f"Error getting active users: {e}")
            return []
    
    async def analyze_user_pattern(self, user_id):
        """Analyze user patterns from database"""
        try:
            # Get user data
            user_data = await users.find_one({"user_id": user_id})
            if not user_data:
                return None
            
            # Get existing patterns
            pattern_data = await user_patterns.find_one({"user_id": user_id})
            
            # Analyze interaction frequency
            interaction_count = user_data.get("interaction_count", 0)
            last_interaction = user_data.get("last_interaction", datetime.now())
            
            # Calculate time since last interaction
            time_since_last = datetime.now() - last_interaction
            
            # Determine suggested action based on patterns
            suggested_action = "help_offer"
            confidence = 0.5
            
            if time_since_last.total_seconds() > 3600:  # 1 hour
                if interaction_count > 10:
                    suggested_action = "reminder"
                    confidence = 0.8
            elif interaction_count > 5:
                suggested_action = "feature_suggestion"
                confidence = 0.7
            
            # Check conversation history for specific patterns
            conv_history = user_data.get("conversation_history", [])
            if len(conv_history) > 0:
                recent_messages = conv_history[-5:]  # Last 5 messages
                # If user asking similar questions, increase confidence
                if len(set(msg.get("type", "") for msg in recent_messages)) <= 2:
                    confidence += 0.2
            
            pattern = {
                'user_id': user_id,
                'last_activity': last_interaction.isoformat(),
                'interaction_count': interaction_count,
                'suggested_action': suggested_action,
                'prediction_confidence': min(confidence, 1.0),
                'common_actions': [msg.get("type", "chat") for msg in conv_history[-10:]],
                'time_since_last': time_since_last.total_seconds()
            }
            
            # Update patterns in database
            await user_patterns.update_one(
                {"user_id": user_id},
                {"$set": {
                    "pattern_data": pattern,
                    "last_updated": datetime.now()
                }},
                upsert=True
            )
            
            return pattern
            
        except Exception as e:
            console.error(f"Error analyzing user pattern for {user_id}: {e}")
            return None
    
    async def find_proactive_opportunities(self, assistant_id):
        """Find opportunities for proactive assistance"""
        try:
            opportunities = []
            
            # Check for users who might need help
            users_needing_help = await users.find({
                "last_interaction": {"$gte": datetime.now() - timedelta(hours=6)},
                "interaction_count": {"$gte": 2}
            }).limit(10).to_list(length=10)
            
            for user_data in users_needing_help:
                user_id = user_data["user_id"]
                
                # Check if user has unresolved issues
                conv_history = user_data.get("conversation_history", [])
                if conv_history:
                    last_msg = conv_history[-1]
                    if "?" in last_msg.get("message", "") and not last_msg.get("resolved", False):
                        opportunities.append({
                            "type": "help_offer",
                            "user_id": user_id,
                            "priority": 0.8,
                            "reason": "unresolved_question"
                        })
            
            # Check for feature suggestions
            feature_opportunities = await users.find({
                "interaction_count": {"$gte": 5},
                "ai_learning_patterns.topics": {"$exists": True}
            }).limit(5).to_list(length=5)
            
            for user_data in feature_opportunities:
                opportunities.append({
                    "type": "feature_suggestion",
                    "user_id": user_data["user_id"],
                    "priority": 0.6,
                    "reason": "active_user"
                })
            
            return opportunities[:5]  # Return top 5 opportunities
            
        except Exception as e:
            console.error(f"Error finding proactive opportunities: {e}")
            return []
    
    async def execute_proactive_help(self, client, opportunity):
        """Execute proactive help action"""
        try:
            user_id = opportunity["user_id"]
            help_type = opportunity["type"]
            
            # Verify user exists and we can message them
            user_data = await users.find_one({"user_id": user_id})
            if not user_data:
                console.warning(f"User {user_id} not found in database")
                return
            
            # Check if user is already marked as unreachable
            if user_data.get("unreachable", False):
                console.info(f"User {user_id} is marked as unreachable, skipping proactive help")
                return
            
            # Check if user has sufficient interaction history
            interaction_count = user_data.get("interaction_count", 0)
            if interaction_count < 2:
                console.info(f"User {user_id} has insufficient interaction history ({interaction_count})")
                return
            
            messages = {
                "help_offer": "👋 Hai! Aku lihat kamu butuh bantuan. Ada yang bisa aku bantu?",
                "feature_suggestion": "✨ Eh, ada fitur keren yang mungkin kamu suka! Mau aku tunjukin?",
                "reminder": "⏰ Jangan lupa istirahat ya! Semangat terus! 💪"
            }
            
            message = messages.get(help_type, messages["help_offer"])
            
            # Try to send message with proper error handling
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=f"🤖 **Proactive Assistant**\n\n{message}"
                )
                
                # Log successful action
                await autonomous_tasks.insert_one({
                    "type": "proactive_help",
                    "user_id": user_id,
                    "help_type": help_type,
                    "timestamp": datetime.now(),
                    "status": "executed"
                })
                
                console.info(f"✅ Executed proactive help for user {user_id}")
                
            except Exception as telegram_error:
                if "PEER_ID_INVALID" in str(telegram_error):
                    console.warning(f"Cannot send proactive help to user {user_id}: Invalid peer (user may have blocked or deleted chat)")
                    
                    # Mark user as unreachable to avoid future attempts
                    await users.update_one(
                        {"user_id": user_id},
                        {"$set": {"unreachable": True, "unreachable_since": datetime.now()}}
                    )
                    
                    # Log failed attempt
                    await autonomous_tasks.insert_one({
                        "type": "proactive_help",
                        "user_id": user_id,
                        "help_type": help_type,
                        "timestamp": datetime.now(),
                        "status": "failed",
                        "error": "PEER_ID_INVALID - User marked as unreachable"
                    })
                    
                else:
                    console.error(f"Telegram error sending proactive help to {user_id}: {telegram_error}")
                    
                    # Log other errors
                    await autonomous_tasks.insert_one({
                        "type": "proactive_help",
                        "user_id": user_id,
                        "help_type": help_type,
                        "timestamp": datetime.now(),
                        "status": "failed",
                        "error": str(telegram_error)
                    })
            
        except Exception as e:
            console.error(f"Error in proactive help execution: {e}")
            # Log system error
            try:
                await autonomous_tasks.insert_one({
                    "type": "proactive_help",
                    "user_id": opportunity.get("user_id", 0),
                    "help_type": opportunity.get("type", "unknown"),
                    "timestamp": datetime.now(),
                    "status": "system_error",
                    "error": str(e)
                })
            except:
                pass  # Don't let logging errors crash the system
    
    def select_best_assistant(self, action_type):
        """Select best assistant for action type"""
        assistant_mapping = {
            'help_offer': 'AERIS',
            'feature_suggestion': 'NOVA',
            'reminder': 'KAIROS',
            'technical_help': 'ZEKE',
            'music_suggestion': 'LYRA'
        }
        return assistant_mapping.get(action_type, 'AERIS')
    
    async def log_proactive_action(self, user_id, action_type, message):
        """Log proactive action to database"""
        try:
            await autonomous_tasks.insert_one({
                "type": "proactive_action",
                "user_id": user_id,
                "action_type": action_type,
                "message": message,
                "timestamp": datetime.now(),
                "status": "completed"
            })
        except Exception as e:
            console.error(f"Error logging proactive action: {e}")
    
    async def get_user_context(self, user_id):
        """Get user context from database"""
        try:
            user_data = await users.find_one({"user_id": user_id})
            if not user_data:
                return {}
            
            return {
                "preferences": user_data.get("ai_learning_patterns", {}),
                "interaction_count": user_data.get("interaction_count", 0),
                "last_topics": [msg.get("type", "") for msg in user_data.get("conversation_history", [])[-5:]]
            }
        except Exception as e:
            console.error(f"Error getting user context: {e}")
            return {}
    
    async def scheduled_tasks_runner(self):
        """Run scheduled tasks"""
        console.info("📅 Starting scheduled tasks runner...")
        
        while self.is_running:
            try:
                # Get pending scheduled tasks
                pending_tasks = await scheduled_actions.find({
                    "execute_at": {"$lte": datetime.now()},
                    "status": "pending"
                }).limit(10).to_list(length=10)
                
                for task in pending_tasks:
                    await self.execute_scheduled_task(task)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                console.error(f"Error in scheduled tasks runner: {e}")
                await asyncio.sleep(60)
    
    async def execute_scheduled_task(self, task):
        """Execute a scheduled task"""
        try:
            task_id = task["_id"]
            task_type = task.get("type", "message")
            
            # Mark as executing
            await scheduled_actions.update_one(
                {"_id": task_id},
                {"$set": {"status": "executing", "started_at": datetime.now()}}
            )
            
            if task_type == "reminder":
                await self.send_reminder(task)
            elif task_type == "suggestion":
                await self.send_suggestion(task)
            
            # Mark as completed
            await scheduled_actions.update_one(
                {"_id": task_id},
                {"$set": {"status": "completed", "completed_at": datetime.now()}}
            )
            
            console.info(f"✅ Executed scheduled task: {task_type}")
            
        except Exception as e:
            console.error(f"Error executing scheduled task: {e}")
            await scheduled_actions.update_one(
                {"_id": task["_id"]},
                {"$set": {"status": "failed", "error": str(e)}}
            )
    
    async def safe_send_message(self, client, user_id, text, message_type="autonomous"):
        """Safely send message with PEER_ID_INVALID error handling and context validation"""
        try:
            # Check if user is marked as unreachable
            user_data = await users.find_one({"user_id": user_id})
            if not user_data:
                console.warning(f"User {user_id} not found in database")
                return False
                
            if user_data.get("unreachable", False):
                console.info(f"User {user_id} is marked as unreachable, skipping message")
                return False
            
            # Check interaction context for proactive messages
            if message_type in ["proactive_action", "proactive_help", "reminder", "suggestion"]:
                contexts = user_data.get('interaction_contexts', {})
                has_private_chat = contexts.get('has_private_chat', False)
                
                if not has_private_chat:
                    console.info(f"User {user_id} never had private chat, skipping {message_type} message")
                    # Don't mark as unreachable, just skip proactive private messages
                    await autonomous_tasks.insert_one({
                        "type": message_type,
                        "user_id": user_id,
                        "timestamp": datetime.now(),
                        "status": "skipped",
                        "reason": "no_private_chat_history"
                    })
                    return False
                
                # Additional validation for user interaction level
                interaction_count = user_data.get("interaction_count", 0)
                if interaction_count < 3:
                    console.info(f"User {user_id} has insufficient interaction count ({interaction_count}) for {message_type}")
                    return False
            
            await client.send_message(chat_id=user_id, text=text)
            return True
            
        except Exception as e:
            if "PEER_ID_INVALID" in str(e):
                console.warning(f"Cannot send {message_type} message to user {user_id}: Invalid peer (blocked or no private chat)")
                
                # Mark user as unreachable for private messages only
                await users.update_one(
                    {"user_id": user_id},
                    {"$set": {"unreachable": True, "unreachable_since": datetime.now()}}
                )
                
                # Log failed attempt
                await autonomous_tasks.insert_one({
                    "type": message_type,
                    "user_id": user_id,
                    "timestamp": datetime.now(),
                    "status": "failed",
                    "error": "PEER_ID_INVALID - User marked as unreachable"
                })
                
            else:
                console.error(f"Error sending {message_type} message to {user_id}: {e}")
                
            return False

    async def send_reminder(self, task):
        """Send reminder message with error handling"""
        from syncara import assistant_manager
        
        user_id = task.get("user_id")
        message = task.get("message", "⏰ Reminder dari assistant kamu!")
        assistant_id = task.get("assistant_id", "AERIS")
        
        client = assistant_manager.get_assistant(assistant_id)
        if client:
            success = await self.safe_send_message(client, user_id, message, "reminder")
            if success:
                console.info(f"✅ Sent reminder to user {user_id}")
    
    async def send_suggestion(self, task):
        """Send suggestion message with error handling"""
        from syncara import assistant_manager
        
        user_id = task.get("user_id")
        suggestion = task.get("suggestion", "💡 Ada saran nih dari assistant kamu!")
        assistant_id = task.get("assistant_id", "NOVA")
        
        client = assistant_manager.get_assistant(assistant_id)
        if client:
            success = await self.safe_send_message(client, user_id, suggestion, "suggestion")
            if success:
                console.info(f"✅ Sent suggestion to user {user_id}")
    
    async def chat_health_monitor(self):
        """Monitor chat health and engagement"""
        console.info("💬 Starting chat health monitor...")
        
        while self.is_running:
            try:
                # Monitor inactive users (with better filtering)
                inactive_threshold = datetime.now() - timedelta(days=7)
                
                # Only target users who:
                # 1. Have recent interactions (not too old)
                # 2. Are not marked as unreachable
                # 3. Have sufficient conversation history
                inactive_chats = await users.find({
                    "last_interaction": {"$lt": inactive_threshold, "$gte": datetime.now() - timedelta(days=30)},  # Not older than 30 days
                    "interaction_count": {"$gte": 5},  # At least 5 interactions
                    "unreachable": {"$ne": True},  # Not marked as unreachable
                    "conversation_history": {"$exists": True, "$ne": []}  # Has conversation history
                }).limit(10).to_list(length=10)  # Reduce to 10 to avoid spam
                
                console.info(f"💬 Found {len(inactive_chats)} inactive users to re-engage")
                
                for chat in inactive_chats:
                    await self.send_reengagement_message(chat["user_id"])
                    await asyncio.sleep(5)  # 5 second delay between messages to avoid rate limits
                
                await asyncio.sleep(21600)  # Check every 6 hours instead of 1 hour
                
            except Exception as e:
                console.error(f"Error in chat health monitor: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def send_reengagement_message(self, user_id):
        """Send re-engagement message to inactive users"""
        from syncara import assistant_manager
        
        try:
            # Verify user exists and we can message them
            user_data = await users.find_one({"user_id": user_id})
            if not user_data:
                console.warning(f"User {user_id} not found in database")
                return
            
            # Check if user has enough interaction history (at least 3 interactions)
            interaction_count = user_data.get("interaction_count", 0)
            if interaction_count < 3:
                console.info(f"User {user_id} has insufficient interaction history ({interaction_count})")
                return
            
            # Check if user has recent conversations (not just database entry)
            conv_history = user_data.get("conversation_history", [])
            if not conv_history or len(conv_history) < 2:
                console.info(f"User {user_id} has no conversation history")
                return
            
            messages = [
                "👋 Hai! Lama gak ketemu nih. Apa kabar? Ada yang bisa aku bantu?",
                "😊 Kangen ngobrol sama kamu! Ada update menarik nih, mau tau?",
                "✨ Udah lama gak chat! Ada fitur baru yang keren loh, mau coba?"
            ]
            
            client = assistant_manager.get_assistant("AERIS")
            if client:
                message = random.choice(messages)
                
                # Try to send message with error handling
                try:
                    await client.send_message(
                        chat_id=user_id,
                        text=f"💝 **Re-engagement**\n\n{message}"
                    )
                    
                    # Log successful re-engagement
                    await autonomous_tasks.insert_one({
                        "type": "re_engagement",
                        "user_id": user_id,
                        "message": message,
                        "timestamp": datetime.now(),
                        "status": "sent"
                    })
                    
                    console.info(f"📤 Sent re-engagement message to {user_id}")
                    
                except Exception as telegram_error:
                    if "PEER_ID_INVALID" in str(telegram_error):
                        console.warning(f"Cannot send to user {user_id}: Invalid peer (user may have blocked or deleted chat)")
                        
                        # Mark user as unreachable to avoid future attempts
                        await users.update_one(
                            {"user_id": user_id},
                            {"$set": {"unreachable": True, "unreachable_since": datetime.now()}}
                        )
                    else:
                        console.error(f"Telegram error sending to {user_id}: {telegram_error}")
                        
                    # Log failed attempt
                    await autonomous_tasks.insert_one({
                        "type": "re_engagement",
                        "user_id": user_id,
                        "message": message,
                        "timestamp": datetime.now(),
                        "status": "failed",
                        "error": str(telegram_error)
                    })
        
        except Exception as e:
            console.error(f"Error sending re-engagement message: {e}")
    
    async def learning_optimizer(self):
        """Optimize AI learning based on patterns"""
        console.info("🧠 Starting learning optimizer...")
        
        while self.is_running:
            try:
                # Analyze learning patterns and optimize
                await self.optimize_response_patterns()
                await self.update_user_preferences()
                await self.cleanup_old_data()
                
                await asyncio.sleep(7200)  # Run every 2 hours
                
            except Exception as e:
                console.error(f"Error in learning optimizer: {e}")
                await asyncio.sleep(1800)
    
    async def optimize_response_patterns(self):
        """Optimize response patterns based on user feedback"""
        try:
            # Get users with feedback data
            users_with_feedback = await users.find({
                "ai_learning_quality": {"$exists": True, "$ne": []}
            }).limit(50).to_list(length=50)
            
            for user_data in users_with_feedback:
                user_id = user_data["user_id"]
                quality_data = user_data.get("ai_learning_quality", [])
                
                if len(quality_data) >= 5:
                    # Analyze patterns and update preferences
                    await self.update_learning_preferences(user_id, quality_data)
            
            console.info("🎯 Optimized response patterns")
            
        except Exception as e:
            console.error(f"Error optimizing response patterns: {e}")
    
    async def update_learning_preferences(self, user_id, quality_data):
        """Update user learning preferences"""
        try:
            # Analyze preferred response length
            avg_length = sum(data.get("response_length", 0) for data in quality_data) / len(quality_data)
            
            # Analyze emoji usage preference
            emoji_usage = sum(1 for data in quality_data if data.get("has_emoji", False)) / len(quality_data)
            
            preferences = {
                "preferred_response_length": avg_length,
                "emoji_preference": emoji_usage,
                "last_optimized": datetime.now()
            }
            
            await users.update_one(
                {"user_id": user_id},
                {"$set": {"learning_preferences": preferences}}
            )
            
        except Exception as e:
            console.error(f"Error updating learning preferences: {e}")
    
    async def update_user_preferences(self):
        """Update user preferences based on interaction patterns"""
        try:
            # Update user interaction patterns
            await users.update_many(
                {"last_interaction": {"$exists": True}},
                {"$set": {"preferences_updated": datetime.now()}}
            )
            
            console.info("📊 Updated user preferences")
            
        except Exception as e:
            console.error(f"Error updating user preferences: {e}")
    
    async def cleanup_old_data(self):
        """Cleanup old autonomous tasks and patterns"""
        try:
            # Remove tasks older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            result = await autonomous_tasks.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            if result.deleted_count > 0:
                console.info(f"🗑️ Cleaned up {result.deleted_count} old autonomous tasks")
            
        except Exception as e:
            console.error(f"Error cleaning up old data: {e}")

class SmartShortcodeExecutor:
    def __init__(self):
        self.execution_history = {}
        self.success_patterns = {}
    
    async def auto_execute_shortcodes(self, context):
        try:
            relevant_shortcodes = await self.analyze_context_for_shortcodes(context)
            for shortcode_data in relevant_shortcodes:
                if shortcode_data['confidence'] > 0.7:
                    await self.execute_smart_shortcode(shortcode_data)
        except Exception as e:
            console.error(f"Error in auto_execute_shortcodes: {e}")
    
    async def execute_smart_shortcode(self, shortcode_data):
        try:
            shortcode = shortcode_data['shortcode']
            params = shortcode_data['inferred_params']
            client = shortcode_data['client']
            context = shortcode_data['context']
            mock_message = self.create_mock_message(context)
            result = await registry.execute_shortcode(
                shortcode=shortcode,
                client=client,
                message=mock_message,
                params=params
            )
            if result:
                console.info(f"✅ Auto-executed shortcode: {shortcode}")
                await self.log_shortcode_success(shortcode, params, result)
            else:
                console.warning(f"❌ Failed to execute shortcode: {shortcode}")
            return result
        except Exception as e:
            console.error(f"Error executing smart shortcode: {e}")
            return False
    async def analyze_context_for_shortcodes(self, context):
        relevant_shortcodes = []
        available_shortcodes = registry.shortcodes.keys()
        for shortcode in available_shortcodes:
            confidence = await self.calculate_shortcode_relevance(shortcode, context)
            if confidence > 0.5:
                params = await self.infer_shortcode_params(shortcode, context)
                relevant_shortcodes.append({
                    'shortcode': shortcode,
                    'confidence': confidence,
                    'inferred_params': params,
                    'client': context.get('client'),
                    'context': context
                })
        relevant_shortcodes.sort(key=lambda x: x['confidence'], reverse=True)
        return relevant_shortcodes[:3]
    async def calculate_shortcode_relevance(self, shortcode, context):
        return random.uniform(0, 1)
    async def infer_shortcode_params(self, shortcode, context):
        return {}
    def create_mock_message(self, context):
        return None
    async def log_shortcode_success(self, shortcode, params, result):
        pass

class ProactiveChatMonitor:
    def __init__(self):
        self.monitored_chats = {}
        self.alert_thresholds = {
            'inactivity': 3600,
            'spam_detection': 5,
            'conflict_keywords': ['toxic', 'spam', 'scam']
        }
    async def start_monitoring(self):
        while True:
            try:
                await self.check_chat_health()
                await self.detect_opportunities()
                await self.auto_moderate()
                await asyncio.sleep(180)
            except Exception as e:
                console.error(f"Error in chat monitoring: {e}")
                await asyncio.sleep(60)
    async def check_chat_health(self):
        from syncara import assistant_manager
        for chat_id, chat_data in self.monitored_chats.items():
            try:
                if await self.is_chat_inactive(chat_id):
                    await self.send_engagement_message(chat_id)
                if await self.detect_problematic_behavior(chat_id):
                    await self.auto_moderate_chat(chat_id)
                if await self.detect_help_opportunity(chat_id):
                    await self.offer_proactive_help(chat_id)
            except Exception as e:
                console.error(f"Error checking chat {chat_id}: {e}")
    async def send_engagement_message(self, chat_id):
        """Send engagement message to chat with error handling"""
        from syncara import assistant_manager
        try:
            assistant_id = await self.select_chat_assistant(chat_id)
            client = assistant_manager.get_assistant(assistant_id)
            if not client:
                return
            
            engagement_msg = await self.generate_engagement_message(chat_id)
            
            try:
                await client.send_message(
                    chat_id=chat_id,
                    text=f"💬 {engagement_msg}"
                )
                console.info(f"✅ Sent engagement message to chat {chat_id}")
                
            except Exception as telegram_error:
                if "PEER_ID_INVALID" in str(telegram_error):
                    console.warning(f"Cannot send engagement message to chat {chat_id}: Invalid peer")
                    
                    # Mark chat as problematic in groups collection
                    await groups.update_one(
                        {"chat_id": chat_id},
                        {"$set": {"unreachable": True, "unreachable_since": datetime.now()}}
                    )
                    
                elif "CHAT_WRITE_FORBIDDEN" in str(telegram_error):
                    console.warning(f"Cannot send to chat {chat_id}: No write permission")
                    
                else:
                    console.error(f"Telegram error sending to chat {chat_id}: {telegram_error}")
                    
        except Exception as e:
            console.error(f"Error in engagement message system: {e}")
    async def auto_moderate_chat(self, chat_id):
        try:
            moderation_actions = [
                "GROUP:WARN:spam_detected",
                "GROUP:MUTE:temporary",
                "USER:INFO:suspicious_activity"
            ]
            for action in moderation_actions:
                await self.execute_moderation_shortcode(chat_id, action)
        except Exception as e:
            console.error(f"Error in auto moderation: {e}")
    async def is_chat_inactive(self, chat_id):
        return False
    async def detect_problematic_behavior(self, chat_id):
        return False
    async def detect_help_opportunity(self, chat_id):
        return False
    async def offer_proactive_help(self, chat_id):
        pass
    async def execute_moderation_shortcode(self, chat_id, action):
        pass
    async def select_chat_assistant(self, chat_id):
        return 'AERIS'
    async def generate_engagement_message(self, chat_id):
        return "Ayo aktifkan kembali obrolan ini!"

class ScheduledAITasks:
    def __init__(self):
        self.scheduled_tasks = []
        self.recurring_tasks = {}
    async def add_scheduled_task(self, task_data):
        task = {
            'id': len(self.scheduled_tasks) + 1,
            'type': task_data['type'],
            'execute_at': task_data['execute_at'],
            'shortcode': task_data.get('shortcode'),
            'params': task_data.get('params', {}),
            'target_chat': task_data.get('target_chat'),
            'assistant_id': task_data.get('assistant_id', 'AERIS'),
            'status': 'pending'
        }
        self.scheduled_tasks.append(task)
        console.info(f"Scheduled task added: {task['type']} at {task['execute_at']}")
    async def run_scheduler(self):
        from syncara import assistant_manager
        while True:
            try:
                current_time = datetime.now()
                for task in self.scheduled_tasks:
                    if (task['status'] == 'pending' and 
                        current_time >= task['execute_at']):
                        await self.execute_scheduled_task(task)
                self.scheduled_tasks = [
                    t for t in self.scheduled_tasks 
                    if t['status'] != 'completed'
                ]
                await asyncio.sleep(60)
            except Exception as e:
                console.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)
    async def execute_scheduled_task(self, task):
        from syncara import assistant_manager
        try:
            task['status'] = 'executing'
            client = assistant_manager.get_assistant(task['assistant_id'])
            if not client:
                task['status'] = 'failed'
                return
            if task['type'] == 'shortcode':
                mock_message = self.create_mock_message(task)
                result = await registry.execute_shortcode(
                    shortcode=task['shortcode'],
                    client=client,
                    message=mock_message,
                    params=task['params']
                )
                task['status'] = 'completed' if result else 'failed'
            elif task['type'] == 'message':
                try:
                    await client.send_message(
                        chat_id=task['target_chat'],
                        text=task['params']['message']
                    )
                    task['status'] = 'completed'
                    console.info(f"✅ Sent scheduled message to {task['target_chat']}")
                    
                except Exception as send_error:
                    if "PEER_ID_INVALID" in str(send_error):
                        console.warning(f"Cannot send scheduled message to {task['target_chat']}: Invalid peer")
                        task['status'] = 'failed'
                        task['error'] = 'PEER_ID_INVALID'
                    elif "CHAT_WRITE_FORBIDDEN" in str(send_error):
                        console.warning(f"Cannot send to {task['target_chat']}: No write permission")
                        task['status'] = 'failed'
                        task['error'] = 'CHAT_WRITE_FORBIDDEN'
                    else:
                        console.error(f"Error sending scheduled message to {task['target_chat']}: {send_error}")
                        task['status'] = 'failed'
                        task['error'] = str(send_error)
            elif task['type'] == 'ai_analysis':
                await self.run_ai_analysis_task(task, client)
                task['status'] = 'completed'
            console.info(f"Executed scheduled task: {task['type']}")
        except Exception as e:
            console.error(f"Error executing scheduled task: {e}")
            task['status'] = 'failed'
    def create_mock_message(self, task):
        return None
    async def run_ai_analysis_task(self, task, client):
        pass 