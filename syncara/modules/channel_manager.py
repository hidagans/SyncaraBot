"""
Channel Manager untuk Syncara Insights
Auto-posting content 24/7 dengan berbagai jenis konten
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

from syncara.console import console
from syncara.services import ReplicateAPI
import re

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for MarkdownV2"""
    # Characters that need to be escaped in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    # Escape each character
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

@dataclass
class ContentPost:
    """Data class untuk content post"""
    id: str
    type: str  # daily_tips, weekly_updates, user_stories, ai_trends, qna, polls, fun_facts
    title: str
    content: str
    media_url: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    engagement_metrics: Optional[Dict] = None
    hashtags: List[str] = None

class ChannelContentGenerator:
    """Generator untuk berbagai jenis konten channel"""
    
    def __init__(self):
        self.replicate_api = ReplicateAPI()
        self._db_initialized = False
    
    async def _ensure_db_connection(self):
        """Ensure database connection"""
        if not self._db_initialized:
            try:
                from syncara.database import (
                    db, log_system_event, log_error,
                    users, conversation_history, system_logs
                )
                self.db = db
                self.log_system_event = log_system_event
                self.log_error = log_error
                self.users = users
                self.conversation_history = conversation_history
                self.system_logs = system_logs
                self.channel_posts = db.channel_posts
                self.channel_analytics = db.channel_analytics
                self._db_initialized = True
            except ImportError:
                console.error("Database not available for channel management")

    async def generate_daily_tips(self) -> ContentPost:
        """Generate daily tips content"""
        try:
            tips_prompts = [
                "Berikan 1 tips praktis penggunaan AI assistant untuk produktivitas harian",
                "Bagikan trik mengoptimalkan prompt AI untuk hasil yang lebih baik", 
                "Tips keamanan data saat menggunakan AI assistant",
                "Cara menggunakan AI untuk automation task sehari-hari",
                "Tips mengintegrasikan AI assistant dengan workflow kerja",
                "Strategi prompt engineering untuk pemula",
                "Tips troubleshooting common AI assistant issues"
            ]
            
            prompt = random.choice(tips_prompts)
            
            system_prompt = """Kamu adalah AERIS, AI assistant dari Syncara. 
            Buat content tips yang:
            - Praktis dan actionable
            - Mudah dipahami
            - Include emoji yang relevan
            - Format yang engaging untuk channel Telegram
            - Panjang 2-3 paragraf
            - Berikan contoh konkret
            """
            
            content = await self.replicate_api.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=500
            )
            
            hashtags = ["#DailyTips", "#SyncaraAI", "#AITips", "#Productivity", "#AI"]
            
            post = ContentPost(
                id=f"daily_tips_{datetime.now().strftime('%Y%m%d')}",
                type="daily_tips",
                title="💡 Daily Tips - Syncara AI",
                content=f"💡 *Daily Tips \\- Syncara AI*\n\n{escape_markdown_v2(content)}\n\n{' '.join(hashtags)}",
                hashtags=hashtags
            )
            
            await self._save_content_to_db(post)
            return post
            
        except Exception as e:
            console.error(f"Error generating daily tips: {str(e)}")
            await self._log_error("channel_manager", f"Error generating daily tips: {str(e)}")
            return None

    async def generate_weekly_updates(self) -> ContentPost:
        """Generate weekly updates content"""
        try:
            # Get system logs dari minggu terakhir
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            await self._ensure_db_connection()
            recent_logs = await self.system_logs.find({
                "timestamp": {"$gte": week_ago},
                "level": "info"
            }).limit(10).to_list(length=None)
            
            # Generate summary dari logs
            log_summary = []
            for log in recent_logs:
                if "user" in log.get("message", "").lower():
                    log_summary.append(f"- {log.get('message', '')}")
            
            prompt = f"""Berdasarkan aktivitas sistem minggu ini:
            {chr(10).join(log_summary[:5])}
            
            Buat weekly update yang engaging untuk channel Syncara Insights.
            Include: improvement, bug fixes, new features, user growth.
            """
            
            system_prompt = """Kamu adalah AERIS, AI assistant dari Syncara.
            Buat weekly update yang:
            - Professional tapi friendly
            - Highlight achievement minggu ini
            - Include emoji yang relevan
            - Format yang menarik untuk channel
            - Mention user appreciation
            """
            
            content = await self.replicate_api.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=600
            )
            
            hashtags = ["#WeeklyUpdate", "#SyncaraNews", "#AIProgress", "#Community"]
            
            post = ContentPost(
                id=f"weekly_update_{datetime.now().strftime('%Y%W')}",
                type="weekly_updates", 
                title="📊 Weekly Updates - Syncara AI",
                content=f"📊 *Weekly Updates \\- Syncara AI*\n\n{escape_markdown_v2(content)}\n\n{' '.join(hashtags)}",
                hashtags=hashtags
            )
            
            await self._save_content_to_db(post)
            return post
            
        except Exception as e:
            console.error(f"Error generating weekly updates: {str(e)}")
            await self._log_error("channel_manager", f"Error generating weekly updates: {str(e)}")
            return None

    async def generate_user_stories(self) -> ContentPost:
        """Generate user stories & testimonials"""
        try:
            await self._ensure_db_connection()
            
            # Get conversation data untuk inspirasi user stories
            recent_convos = await self.conversation_history.find({}).limit(5).to_list(length=None)
            
            prompt = """Buat user story testimonial yang inspiratif tentang penggunaan Syncara AI.
            Ceritakan bagaimana AI assistant membantu user dalam:
            - Meningkatkan produktivitas
            - Menyelesaikan masalah
            - Belajar hal baru
            - Automation task
            
            Format sebagai testimonial yang engaging.
            """
            
            system_prompt = """Kamu adalah AERIS, AI assistant dari Syncara.
            Buat user story yang:
            - Inspiratif dan relatable
            - Showcase real benefits dari AI assistant
            - Include specific use case
            - Emotional connection
            - Professional testimonial format
            """
            
            content = await self.replicate_api.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=500
            )
            
            hashtags = ["#UserStory", "#Testimonial", "#SyncaraSuccess", "#AIImpact"]
            
            post = ContentPost(
                id=f"user_story_{datetime.now().strftime('%Y%m%d_%H')}",
                type="user_stories",
                title="🌟 User Success Story",
                content=f"🌟 *User Success Story*\n\n{escape_markdown_v2(content)}\n\n{' '.join(hashtags)}",
                hashtags=hashtags
            )
            
            await self._save_content_to_db(post)
            return post
            
        except Exception as e:
            console.error(f"Error generating user stories: {str(e)}")
            await self._log_error("channel_manager", f"Error generating user stories: {str(e)}")
            return None

    async def generate_ai_trends(self) -> ContentPost:
        """Generate AI trends content"""
        try:
            trends_topics = [
                "Large Language Models development terbaru",
                "AI automation dalam industri kreatif", 
                "Ethical AI dan responsible development",
                "AI democratization dan accessibility",
                "Future of AI assistant technology",
                "AI dalam education dan learning",
                "Multimodal AI capabilities"
            ]
            
            topic = random.choice(trends_topics)
            
            prompt = f"Analisis trend AI terbaru tentang: {topic}. Berikan insight mendalam dan relevansi untuk pengguna AI assistant."
            
            system_prompt = """Kamu adalah AERIS, AI expert dari Syncara.
            Buat AI trends analysis yang:
            - Insightful dan educational
            - Up-to-date dengan perkembangan terbaru
            - Relevant untuk AI assistant users
            - Include implications untuk future
            - Professional yet accessible
            """
            
            content = await self.replicate_api.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=700
            )
            
            hashtags = ["#AITrends", "#TechInsights", "#FutureAI", "#Innovation"]
            
            post = ContentPost(
                id=f"ai_trends_{datetime.now().strftime('%Y%m')}",
                type="ai_trends",
                title="🚀 AI Trends Analysis",
                content=f"🚀 *AI Trends Analysis*\n\n{escape_markdown_v2(content)}\n\n{' '.join(hashtags)}",
                hashtags=hashtags
            )
            
            await self._save_content_to_db(post)
            return post
            
        except Exception as e:
            console.error(f"Error generating AI trends: {str(e)}")
            await self._log_error("channel_manager", f"Error generating AI trends: {str(e)}")
            return None

    async def generate_qna_content(self) -> ContentPost:
        """Generate Q&A content"""
        try:
            common_questions = [
                "Bagaimana cara mengoptimalkan prompt untuk AI assistant?",
                "Apa perbedaan antara AI assistant dan chatbot biasa?",
                "Bagaimana AI assistant melindungi privasi data pengguna?", 
                "Tips menggunakan AI assistant untuk productive workflow?",
                "Bagaimana cara mengintegrasikan AI assistant dengan tools lain?",
                "Apa saja limitation dari AI assistant saat ini?",
                "Bagaimana future development AI assistant?"
            ]
            
            question = random.choice(common_questions)
            
            prompt = f"Jawab pertanyaan ini secara komprehensif: {question}"
            
            system_prompt = """Kamu adalah AERIS, AI assistant expert dari Syncara.
            Berikan jawaban yang:
            - Comprehensive dan accurate
            - Easy to understand
            - Include practical examples
            - Actionable advice
            - Professional expertise
            """
            
            answer = await self.replicate_api.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=600
            )
            
            content = f"❓ *Q&A Session*\n\n*Q:* {escape_markdown_v2(question)}\n\n*A:* {escape_markdown_v2(answer)}"
            hashtags = ["#QnA", "#AIHelp", "#SyncaraSupport", "#AIEducation"]
            
            post = ContentPost(
                id=f"qna_{datetime.now().strftime('%Y%m%d_%H')}",
                type="qna",
                title="❓ Q&A Session",
                content=f"{content}\n\n{' '.join(hashtags)}",
                hashtags=hashtags
            )
            
            await self._save_content_to_db(post)
            return post
            
        except Exception as e:
            console.error(f"Error generating Q&A content: {str(e)}")
            await self._log_error("channel_manager", f"Error generating Q&A content: {str(e)}")
            return None

    async def generate_fun_facts(self) -> ContentPost:
        """Generate fun facts about AI"""
        try:
            fun_facts_prompts = [
                "Fakta menarik tentang sejarah AI development",
                "Fun facts tentang machine learning algorithms",
                "Interesting facts tentang natural language processing",
                "Amazing facts tentang neural networks", 
                "Cool facts tentang AI dalam kehidupan sehari-hari",
                "Surprising facts tentang AI capabilities",
                "Mind-blowing facts tentang future AI"
            ]
            
            prompt = random.choice(fun_facts_prompts)
            
            system_prompt = """Kamu adalah AERIS, AI educator dari Syncara.
            Buat fun facts yang:
            - Menarik dan surprising
            - Educational value tinggi
            - Easy to remember
            - Include emoji yang fun
            - Engaging untuk social media
            """
            
            content = await self.replicate_api.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=400
            )
            
            hashtags = ["#FunFacts", "#AIFacts", "#DidYouKnow", "#TechTrivia"]
            
            post = ContentPost(
                id=f"fun_facts_{datetime.now().strftime('%Y%m%d')}",
                type="fun_facts",
                title="🎯 AI Fun Facts",
                content=f"🎯 *AI Fun Facts*\n\n{escape_markdown_v2(content)}\n\n{' '.join(hashtags)}",
                hashtags=hashtags
            )
            
            await self._save_content_to_db(post)
            return post
            
        except Exception as e:
            console.error(f"Error generating fun facts: {str(e)}")
            await self._log_error("channel_manager", f"Error generating fun facts: {str(e)}")
            return None

    async def generate_interactive_poll(self) -> ContentPost:
        """Generate interactive poll content"""
        try:
            poll_topics = [
                {
                    "question": "Fitur AI assistant mana yang paling sering kamu gunakan?",
                    "options": ["Text Generation", "Code Assistance", "Data Analysis", "Creative Writing", "Problem Solving"]
                },
                {
                    "question": "Dalam bidang apa AI assistant paling membantu kamu?",
                    "options": ["Work/Business", "Education", "Creative Projects", "Personal Tasks", "Research"]
                },
                {
                    "question": "Seberapa sering kamu menggunakan AI assistant?",
                    "options": ["Setiap hari", "Beberapa kali seminggu", "Seminggu sekali", "Sesekali", "Pertama kali"]
                },
                {
                    "question": "Fitur apa yang ingin kamu lihat di AI assistant masa depan?",
                    "options": ["Voice Interface", "Image Processing", "Video Analysis", "Real-time Collaboration", "IoT Integration"]
                }
            ]
            
            poll_data = random.choice(poll_topics)
            
            content = f"📊 *Interactive Poll*\n\n{escape_markdown_v2(poll_data['question'])}\n\n"
            for i, option in enumerate(poll_data['options'], 1):
                content += f"{i}\\. {escape_markdown_v2(option)}\n"
            
            content += f"\n💬 {escape_markdown_v2('Vote di comments atau emoji react!')}\n"
            content += f"📈 {escape_markdown_v2('Hasil akan dibagikan minggu depan!')}"
            
            hashtags = ["#Poll", "#Community", "#Feedback", "#Engagement"]
            
            post = ContentPost(
                id=f"poll_{datetime.now().strftime('%Y%m%d')}",
                type="polls",
                title="📊 Interactive Poll",
                content=f"{content}\n\n{' '.join(hashtags)}",
                hashtags=hashtags
            )
            
            await self._save_content_to_db(post)
            return post
            
        except Exception as e:
            console.error(f"Error generating poll: {str(e)}")
            await self._log_error("channel_manager", f"Error generating poll: {str(e)}")
            return None

    async def _save_content_to_db(self, post: ContentPost):
        """Save generated content to database"""
        try:
            await self._ensure_db_connection()
            
            post_doc = {
                "post_id": post.id,
                "type": post.type,
                "title": post.title,
                "content": post.content,
                "media_url": post.media_url,
                "hashtags": post.hashtags or [],
                "created_at": datetime.utcnow(),
                "scheduled_time": post.scheduled_time,
                "posted_time": post.posted_time,
                "status": "generated",
                "engagement_metrics": {
                    "views": 0,
                    "reactions": 0,
                    "comments": 0,
                    "shares": 0
                }
            }
            
            await self.channel_posts.insert_one(post_doc)
            await self.log_system_event("info", "channel_manager", f"Generated content: {post.type}")
            
        except Exception as e:
            console.error(f"Error saving content to database: {str(e)}")

    async def _log_error(self, module: str, error: str):
        """Log error to database"""
        try:
            await self.log_error(module, error)
        except:
            pass

class ChannelManager:
    """Main channel manager untuk auto-posting"""
    
    def __init__(self, channel_username: str = "@syncara_insight"):
        self.channel_username = channel_username
        self.content_generator = ChannelContentGenerator()
        self.is_running = False
        self._db_initialized = False
        
        # Content schedule
        self.content_schedule = {
            "daily_tips": {"hour": 8, "minute": 0},      # 08:00 setiap hari
            "fun_facts": {"hour": 14, "minute": 0},      # 14:00 setiap hari  
            "qna": {"hour": 20, "minute": 0},            # 20:00 setiap hari
            "user_stories": {"hour": 10, "minute": 30},  # 10:30 setiap 2 hari
            "weekly_updates": {"weekday": 1, "hour": 9}, # Senin 09:00
            "ai_trends": {"day": 1, "hour": 11},         # Tanggal 1 setiap bulan
            "polls": {"hour": 16, "minute": 0}           # 16:00 setiap 3 hari
        }

    async def _ensure_db_connection(self):
        """Ensure database connection"""
        if not self._db_initialized:
            try:
                from syncara.database import db, log_system_event, log_error
                self.db = db
                self.log_system_event = log_system_event
                self.log_error = log_error
                self.channel_posts = db.channel_posts
                self.channel_analytics = db.channel_analytics
                self.channel_schedule = db.channel_schedule
                self._db_initialized = True
            except ImportError:
                console.error("Database not available for channel management")

    async def start_auto_posting(self, client):
        """Start auto-posting scheduler"""
        console.info("🚀 Starting Syncara Insights auto-posting...")
        self.is_running = True
        
        try:
            # Start background tasks with proper error handling
            tasks = []
            
            # Create tasks with exception handling
            daily_task = asyncio.create_task(self._daily_content_scheduler(client))
            weekly_task = asyncio.create_task(self._weekly_content_scheduler(client))
            monthly_task = asyncio.create_task(self._monthly_content_scheduler(client))
            analytics_task = asyncio.create_task(self._analytics_tracker(client))
            
            tasks.extend([daily_task, weekly_task, monthly_task, analytics_task])
            
            console.info(f"✅ Started {len(tasks)} scheduler tasks")
            
            # Wait for all tasks with proper exception handling
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            console.error(f"❌ Error in auto-posting scheduler: {str(e)}")
            self.is_running = False
            await self.log_error("channel_manager", f"Auto-posting scheduler error: {str(e)}")
        
        finally:
            console.info("🔄 Auto-posting scheduler stopped")
            self.is_running = False

    async def stop_auto_posting(self):
        """Stop auto-posting"""
        console.info("⏹️ Stopping Syncara Insights auto-posting...")
        self.is_running = False

    async def _daily_content_scheduler(self, client):
        """Daily content posting scheduler"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Daily Tips - 08:00
                if (current_time.hour == 8 and current_time.minute == 0 and 
                    not await self._is_content_posted_today("daily_tips")):
                    
                    post = await self.content_generator.generate_daily_tips()
                    if post:
                        await self._post_to_channel(client, post)
                
                # Fun Facts - 14:00
                if (current_time.hour == 14 and current_time.minute == 0 and
                    not await self._is_content_posted_today("fun_facts")):
                    
                    post = await self.content_generator.generate_fun_facts()
                    if post:
                        await self._post_to_channel(client, post)
                
                # Q&A - 20:00
                if (current_time.hour == 20 and current_time.minute == 0 and
                    not await self._is_content_posted_today("qna")):
                    
                    post = await self.content_generator.generate_qna_content()
                    if post:
                        await self._post_to_channel(client, post)
                
                # User Stories - setiap 2 hari sekali 10:30
                if (current_time.hour == 10 and current_time.minute == 30 and
                    current_time.day % 2 == 0 and
                    not await self._is_content_posted_today("user_stories")):
                    
                    post = await self.content_generator.generate_user_stories()
                    if post:
                        await self._post_to_channel(client, post)
                
                # Polls - setiap 3 hari sekali 16:00
                if (current_time.hour == 16 and current_time.minute == 0 and
                    current_time.day % 3 == 0 and
                    not await self._is_content_posted_today("polls")):
                    
                    post = await self.content_generator.generate_interactive_poll()
                    if post:
                        await self._post_to_channel(client, post)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                console.error(f"Error in daily scheduler: {str(e)}")
                await self.log_error("channel_manager", f"Daily scheduler error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _weekly_content_scheduler(self, client):
        """Weekly content scheduler"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Weekly Updates - Senin 09:00
                if (current_time.weekday() == 0 and current_time.hour == 9 and 
                    current_time.minute == 0 and
                    not await self._is_content_posted_this_week("weekly_updates")):
                    
                    post = await self.content_generator.generate_weekly_updates()
                    if post:
                        await self._post_to_channel(client, post)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                console.error(f"Error in weekly scheduler: {str(e)}")
                await self.log_error("channel_manager", f"Weekly scheduler error: {str(e)}")
                await asyncio.sleep(3600)

    async def _monthly_content_scheduler(self, client):
        """Monthly content scheduler"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # AI Trends - Tanggal 1 setiap bulan 11:00
                if (current_time.day == 1 and current_time.hour == 11 and 
                    current_time.minute == 0 and
                    not await self._is_content_posted_this_month("ai_trends")):
                    
                    post = await self.content_generator.generate_ai_trends()
                    if post:
                        await self._post_to_channel(client, post)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                console.error(f"Error in monthly scheduler: {str(e)}")
                await self.log_error("channel_manager", f"Monthly scheduler error: {str(e)}")
                await asyncio.sleep(3600)

    async def _analytics_tracker(self, client):
        """Track channel analytics"""
        while self.is_running:
            try:
                await self._update_channel_analytics(client)
                await asyncio.sleep(3600)  # Update analytics every hour
                
            except Exception as e:
                console.error(f"Error in analytics tracker: {str(e)}")
                await asyncio.sleep(3600)

    async def _post_to_channel(self, client, post: ContentPost):
        """Post content to channel"""
        try:
            # Post to channel - using MarkdownV2 parse_mode with proper formatting
            message = await client.send_message(
                chat_id=self.channel_username,
                text=post.content,
                parse_mode='MarkdownV2'
            )
            
            # Update database
            await self._ensure_db_connection()
            await self.channel_posts.update_one(
                {"post_id": post.id},
                {
                    "$set": {
                        "status": "posted",
                        "posted_time": datetime.utcnow(),
                        "message_id": message.id,
                        "channel_username": self.channel_username
                    }
                }
            )
            
            console.info(f"✅ Posted to channel: {post.type} - {post.title}")
            await self.log_system_event("info", "channel_manager", f"Posted content: {post.type}")
            
        except Exception as e:
            console.error(f"Error posting to channel with MarkdownV2: {str(e)}")
            
            # Try with regular Markdown parse mode
            try:
                message = await client.send_message(
                    chat_id=self.channel_username,
                    text=post.content,
                    parse_mode='Markdown'
                )
                
                # Update database
                await self._ensure_db_connection()
                await self.channel_posts.update_one(
                    {"post_id": post.id},
                    {
                        "$set": {
                            "status": "posted",
                            "posted_time": datetime.utcnow(),
                            "message_id": message.id,
                            "channel_username": self.channel_username
                        }
                    }
                )
                
                console.info(f"✅ Posted to channel (Markdown): {post.type} - {post.title}")
                await self.log_system_event("info", "channel_manager", f"Posted content (Markdown): {post.type}")
                
            except Exception as e2:
                console.error(f"Error posting with Markdown: {str(e2)}")
                await self.log_error("channel_manager", f"Error posting with Markdown: {str(e2)}")
                
                # Final fallback - try posting without special formatting
                try:
                    # Strip markdown formatting and try again
                    plain_content = post.content.replace('*', '').replace('_', '').replace('__', '').replace('~', '').replace('||', '').replace('`', '').replace('>', '')
                    message = await client.send_message(
                        chat_id=self.channel_username,
                        text=plain_content,
                        parse_mode=None
                    )
                    
                    # Update database
                    await self._ensure_db_connection()
                    await self.channel_posts.update_one(
                        {"post_id": post.id},
                        {
                            "$set": {
                                "status": "posted",
                                "posted_time": datetime.utcnow(),
                                "message_id": message.id,
                                "channel_username": self.channel_username
                            }
                        }
                    )
                    
                    console.info(f"✅ Posted to channel (plain text): {post.type} - {post.title}")
                    await self.log_system_event("info", "channel_manager", f"Posted content (plain): {post.type}")
                    
                except Exception as e3:
                    console.error(f"Failed to post even with plain text: {str(e3)}")
                    await self.log_error("channel_manager", f"Failed to post plain text: {str(e3)}")

    async def _is_content_posted_today(self, content_type: str) -> bool:
        """Check if content type was posted today"""
        try:
            await self._ensure_db_connection()
            
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            count = await self.channel_posts.count_documents({
                "type": content_type,
                "status": "posted",
                "posted_time": {"$gte": today_start, "$lt": today_end}
            })
            
            return count > 0
            
        except Exception as e:
            console.error(f"Error checking daily posts: {str(e)}")
            return False

    async def _is_content_posted_this_week(self, content_type: str) -> bool:
        """Check if content type was posted this week"""
        try:
            await self._ensure_db_connection()
            
            # Get start of current week (Monday)
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            
            count = await self.channel_posts.count_documents({
                "type": content_type,
                "status": "posted", 
                "posted_time": {"$gte": week_start, "$lt": week_end}
            })
            
            return count > 0
            
        except Exception as e:
            console.error(f"Error checking weekly posts: {str(e)}")
            return False

    async def _is_content_posted_this_month(self, content_type: str) -> bool:
        """Check if content type was posted this month"""
        try:
            await self._ensure_db_connection()
            
            today = datetime.now()
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if today.month == 12:
                month_end = month_start.replace(year=today.year+1, month=1)
            else:
                month_end = month_start.replace(month=today.month+1)
            
            count = await self.channel_posts.count_documents({
                "type": content_type,
                "status": "posted",
                "posted_time": {"$gte": month_start, "$lt": month_end}
            })
            
            return count > 0
            
        except Exception as e:
            console.error(f"Error checking monthly posts: {str(e)}")
            return False

    async def _update_channel_analytics(self, client):
        """Update channel analytics"""
        try:
            await self._ensure_db_connection()
            
            # Get channel info
            try:
                channel_info = await client.get_chat(self.channel_username)
                member_count = getattr(channel_info, 'members_count', 0)
            except:
                member_count = 0
            
            # Save analytics
            analytics_doc = {
                "timestamp": datetime.utcnow(),
                "channel_username": self.channel_username,
                "member_count": member_count,
                "posts_today": await self._get_posts_count_today(),
                "posts_this_week": await self._get_posts_count_this_week(),
                "posts_this_month": await self._get_posts_count_this_month()
            }
            
            await self.channel_analytics.insert_one(analytics_doc)
            
        except Exception as e:
            console.error(f"Error updating analytics: {str(e)}")

    async def _get_posts_count_today(self) -> int:
        """Get posts count today"""
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            count = await self.channel_posts.count_documents({
                "status": "posted",
                "posted_time": {"$gte": today_start, "$lt": today_end}
            })
            return count
        except:
            return 0

    async def _get_posts_count_this_week(self) -> int:
        """Get posts count this week"""
        try:
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            
            count = await self.channel_posts.count_documents({
                "status": "posted",
                "posted_time": {"$gte": week_start, "$lt": week_end}
            })
            return count
        except:
            return 0

    async def _get_posts_count_this_month(self) -> int:
        """Get posts count this month"""
        try:
            today = datetime.now()
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if today.month == 12:
                month_end = month_start.replace(year=today.year+1, month=1)
            else:
                month_end = month_start.replace(month=today.month+1)
            
            count = await self.channel_posts.count_documents({
                "status": "posted",
                "posted_time": {"$gte": month_start, "$lt": month_end}
            })
            return count
        except:
            return 0

    async def get_channel_stats(self) -> Dict[str, Any]:
        """Get comprehensive channel statistics"""
        try:
            await self._ensure_db_connection()
            
            # Get latest analytics
            latest_analytics = await self.channel_analytics.find({}).sort("timestamp", -1).limit(1).to_list(length=1)
            
            # Get content type distribution
            content_types = await self.channel_posts.aggregate([
                {"$match": {"status": "posted"}},
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]).to_list(length=None)
            
            # Get recent posts
            recent_posts = await self.channel_posts.find({
                "status": "posted"
            }).sort("posted_time", -1).limit(10).to_list(length=None)
            
            stats = {
                "channel_username": self.channel_username,
                "member_count": latest_analytics[0].get("member_count", 0) if latest_analytics else 0,
                "total_posts": await self.channel_posts.count_documents({"status": "posted"}),
                "posts_today": await self._get_posts_count_today(),
                "posts_this_week": await self._get_posts_count_this_week(),
                "posts_this_month": await self._get_posts_count_this_month(),
                "content_distribution": {item["_id"]: item["count"] for item in content_types},
                "recent_posts": recent_posts,
                "last_updated": datetime.utcnow()
            }
            
            return stats
            
        except Exception as e:
            console.error(f"Error getting channel stats: {str(e)}")
            return {}

    async def manual_post(self, client, content_type: str) -> bool:
        """Manually trigger a post"""
        try:
            generators = {
                "daily_tips": self.content_generator.generate_daily_tips,
                "weekly_updates": self.content_generator.generate_weekly_updates,
                "user_stories": self.content_generator.generate_user_stories,
                "ai_trends": self.content_generator.generate_ai_trends,
                "qna": self.content_generator.generate_qna_content,
                "fun_facts": self.content_generator.generate_fun_facts,
                "polls": self.content_generator.generate_interactive_poll
            }
            
            if content_type not in generators:
                console.error(f"Unknown content type: {content_type}")
                return False
            
            post = await generators[content_type]()
            if post:
                await self._post_to_channel(client, post)
                return True
            return False
            
        except Exception as e:
            console.error(f"Error in manual post: {str(e)}")
            return False

# Global instance
channel_manager = ChannelManager() 