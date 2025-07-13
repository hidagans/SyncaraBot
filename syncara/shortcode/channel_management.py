from syncara.modules.channel_manager import channel_manager
from syncara.console import console
from datetime import datetime
import asyncio
import json

class ChannelManagementShortcode:
    def __init__(self):
        self.handlers = {
            'CHANNEL:START': self.start_auto_posting,
            'CHANNEL:STOP': self.stop_auto_posting,
            'CHANNEL:POST': self.manual_post,
            'CHANNEL:STATS': self.channel_stats,
            'CHANNEL:SCHEDULE': self.show_schedule,
            'CHANNEL:STATUS': self.channel_status,
        }
        self.descriptions = {
            'CHANNEL:START': 'Start auto-posting untuk channel. Usage: [CHANNEL:START]',
            'CHANNEL:STOP': 'Stop auto-posting untuk channel. Usage: [CHANNEL:STOP]',
            'CHANNEL:POST': 'Manual post content. Usage: [CHANNEL:POST:content_type]',
            'CHANNEL:STATS': 'Show channel statistics. Usage: [CHANNEL:STATS]',
            'CHANNEL:SCHEDULE': 'Show posting schedule. Usage: [CHANNEL:SCHEDULE]',
            'CHANNEL:STATUS': 'Show channel status. Usage: [CHANNEL:STATUS]',
        }

    async def start_auto_posting(self, client, message, params):
        """Start auto-posting system"""
        try:
            # Validasi admin
            from config.config import OWNER_ID
            if message.from_user.id != OWNER_ID:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Only owner can control channel auto-posting",
                    reply_to_message_id=message.id
                )
                return False

            if channel_manager.is_running:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="ℹ️ **Channel auto-posting sudah berjalan**\n\nStatus: ✅ Active\nChannel: @syncara_insight",
                    reply_to_message_id=message.id
                )
                return True

            # Start auto-posting in background
            asyncio.create_task(channel_manager.start_auto_posting(client))
            
            await client.send_message(
                chat_id=message.chat.id,
                text="🚀 **Channel Auto-Posting Started!**\n\n✅ Status: Active\n📢 Channel: @syncara_insight\n⏰ Schedule: 24/7 automated posting\n\n📊 Content types:\n- Daily Tips (08:00)\n- Fun Facts (14:00)\n- Q&A Session (20:00)\n- User Stories (setiap 2 hari)\n- Weekly Updates (Senin)\n- AI Trends (bulanan)\n- Interactive Polls (setiap 3 hari)",
                reply_to_message_id=message.id
            )
            
            console.info("🚀 Channel auto-posting started via shortcode")
            return True
            
        except Exception as e:
            console.error(f"Error starting auto-posting: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error starting auto-posting: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

    async def stop_auto_posting(self, client, message, params):
        """Stop auto-posting system"""
        try:
            # Validasi admin
            from config.config import OWNER_ID
            if message.from_user.id != OWNER_ID:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Only owner can control channel auto-posting",
                    reply_to_message_id=message.id
                )
                return False

            if not channel_manager.is_running:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="ℹ️ **Channel auto-posting sudah tidak berjalan**\n\nStatus: ⏹️ Stopped",
                    reply_to_message_id=message.id
                )
                return True

            await channel_manager.stop_auto_posting()
            
            await client.send_message(
                chat_id=message.chat.id,
                text="⏹️ **Channel Auto-Posting Stopped**\n\n❌ Status: Inactive\n📢 Channel: @syncara_insight\n\nAuto-posting telah dihentikan. Gunakan [CHANNEL:START] untuk memulai kembali.",
                reply_to_message_id=message.id
            )
            
            console.info("⏹️ Channel auto-posting stopped via shortcode")
            return True
            
        except Exception as e:
            console.error(f"Error stopping auto-posting: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error stopping auto-posting: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

    async def manual_post(self, client, message, params):
        """Manual post content to channel"""
        try:
            # Validasi admin
            from config.config import OWNER_ID
            if message.from_user.id != OWNER_ID:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Only owner can manually post to channel",
                    reply_to_message_id=message.id
                )
                return False

            content_type = params.strip().lower()
            
            valid_types = [
                "daily_tips", "weekly_updates", "user_stories", 
                "ai_trends", "qna", "fun_facts", "polls"
            ]
            
            if not content_type or content_type not in valid_types:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ **Invalid content type**\n\nValid types:\n" + "\n".join([f"- {t}" for t in valid_types]) + f"\n\nUsage: [CHANNEL:POST:content_type]",
                    reply_to_message_id=message.id
                )
                return False

            # Send processing message
            processing_msg = await client.send_message(
                chat_id=message.chat.id,
                text=f"🔄 **Generating and posting {content_type}...**\n\nPlease wait...",
                reply_to_message_id=message.id
            )

            # Generate and post content
            success = await channel_manager.manual_post(client, content_type)
            
            if success:
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=processing_msg.id,
                    text=f"✅ **Manual post successful!**\n\n📝 Content type: {content_type}\n📢 Posted to: @syncara_insight\n⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
                )
            else:
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=processing_msg.id,
                    text=f"❌ **Manual post failed**\n\n📝 Content type: {content_type}\nCheck logs for details."
                )
            
            return success
            
        except Exception as e:
            console.error(f"Error in manual post: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error in manual post: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

    async def channel_stats(self, client, message, params):
        """Show channel statistics"""
        try:
            stats = await channel_manager.get_channel_stats()
            
            if not stats:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Unable to retrieve channel statistics",
                    reply_to_message_id=message.id
                )
                return False

            # Format statistics
            response = f"📊 **Syncara Insights Statistics**\n\n"
            response += f"📢 **Channel:** {stats.get('channel_username', 'N/A')}\n"
            response += f"👥 **Members:** {stats.get('member_count', 0):,}\n"
            response += f"📝 **Total Posts:** {stats.get('total_posts', 0)}\n\n"
            
            response += f"📅 **Recent Activity:**\n"
            response += f"• Today: {stats.get('posts_today', 0)} posts\n"
            response += f"• This Week: {stats.get('posts_this_week', 0)} posts\n"
            response += f"• This Month: {stats.get('posts_this_month', 0)} posts\n\n"
            
            content_dist = stats.get('content_distribution', {})
            if content_dist:
                response += f"📈 **Content Distribution:**\n"
                for content_type, count in content_dist.items():
                    response += f"• {content_type.replace('_', ' ').title()}: {count}\n"
            
            response += f"\n⏰ **Last Updated:** {stats.get('last_updated', datetime.now()).strftime('%d/%m/%Y %H:%M')}"

            await client.send_message(
                chat_id=message.chat.id,
                text=response,
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error getting channel stats: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error getting channel stats: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

    async def show_schedule(self, client, message, params):
        """Show posting schedule"""
        try:
            schedule_info = """📅 **Syncara Insights Posting Schedule**

🌅 **Daily Content:**
• 08:00 - Daily Tips 💡
• 14:00 - Fun Facts 🎯  
• 20:00 - Q&A Session ❓

📆 **Periodic Content:**
• Setiap 2 hari (10:30) - User Stories 🌟
• Setiap 3 hari (16:00) - Interactive Polls 📊

📅 **Weekly Content:**
• Senin (09:00) - Weekly Updates 📊

📅 **Monthly Content:**
• Tanggal 1 (11:00) - AI Trends Analysis 🚀

⏰ **Time Zone:** UTC+7 (WIB)
🤖 **Status:** """ + ("✅ Active" if channel_manager.is_running else "❌ Inactive") + """

📝 **Content Types:**
- daily_tips: Tips praktis AI
- fun_facts: Fakta menarik AI
- qna: Tanya jawab AI
- user_stories: Kisah sukses user
- polls: Polling interaktif
- weekly_updates: Update mingguan
- ai_trends: Analisis tren AI"""

            await client.send_message(
                chat_id=message.chat.id,
                text=schedule_info,
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error showing schedule: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error showing schedule: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

    async def channel_status(self, client, message, params):
        """Show current channel status"""
        try:
            # Get latest stats
            stats = await channel_manager.get_channel_stats()
            
            status_response = f"📊 **Channel Status - Syncara Insights**\n\n"
            status_response += f"🔄 **Auto-posting:** {'✅ Active' if channel_manager.is_running else '❌ Inactive'}\n"
            status_response += f"📢 **Channel:** @syncara_insight\n"
            status_response += f"👥 **Members:** {stats.get('member_count', 0):,}\n"
            status_response += f"📝 **Total Posts:** {stats.get('total_posts', 0)}\n\n"
            
            status_response += f"📅 **Today's Activity:**\n"
            status_response += f"• Posts Today: {stats.get('posts_today', 0)}\n"
            status_response += f"• Posts This Week: {stats.get('posts_this_week', 0)}\n\n"
            
            # Recent posts
            recent_posts = stats.get('recent_posts', [])
            if recent_posts:
                status_response += f"📝 **Recent Posts:**\n"
                for post in recent_posts[:3]:
                    post_time = post.get('posted_time', datetime.now())
                    if isinstance(post_time, str):
                        post_time = datetime.fromisoformat(post_time.replace('Z', '+00:00'))
                    status_response += f"• {post.get('type', 'unknown').replace('_', ' ').title()} - {post_time.strftime('%d/%m %H:%M')}\n"
            
            status_response += f"\n⏰ **Current Time:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            if channel_manager.is_running:
                status_response += f"\n\n🎯 **Next scheduled posts will be generated automatically according to schedule**"
            else:
                status_response += f"\n\n⚠️ **Auto-posting is currently stopped. Use [CHANNEL:START] to activate.**"

            await client.send_message(
                chat_id=message.chat.id,
                text=status_response,
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error getting channel status: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error getting channel status: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

# Create instance untuk diimpor oleh __init__.py
channel_shortcode = ChannelManagementShortcode() 