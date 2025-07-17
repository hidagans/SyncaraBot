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
            'CHANNEL:DEBUG': self.debug_channel,
            'CHANNEL:TEST': self.test_channel_access,
            'CHANNEL:RESTART': self.restart_auto_posting,
        }
        self.descriptions = {
            'CHANNEL:START': 'Start auto-posting untuk channel. Usage: [CHANNEL:START]',
            'CHANNEL:STOP': 'Stop auto-posting untuk channel. Usage: [CHANNEL:STOP]',
            'CHANNEL:POST': 'Manual post content. Usage: [CHANNEL:POST:content_type]',
            'CHANNEL:STATS': 'Show channel statistics. Usage: [CHANNEL:STATS]',
            'CHANNEL:SCHEDULE': 'Show posting schedule. Usage: [CHANNEL:SCHEDULE]',
            'CHANNEL:STATUS': 'Show channel status. Usage: [CHANNEL:STATUS]',
            'CHANNEL:DEBUG': 'Debug channel posting issues. Usage: [CHANNEL:DEBUG]',
            'CHANNEL:TEST': 'Test channel access and permissions. Usage: [CHANNEL:TEST]',
            'CHANNEL:RESTART': 'Restart auto-posting system. Usage: [CHANNEL:RESTART]',
        }

    async def start_auto_posting(self, client, message, params):
        """Start auto-posting system"""
        try:
            # Validasi admin
            from config.config import OWNER_ID
            if message.from_user.id not in OWNER_ID:
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
            if message.from_user.id not in OWNER_ID:
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
            if message.from_user.id not in OWNER_ID:
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

    async def debug_channel(self, client, message, params):
        """Debug channel posting issues"""
        try:
            # Validasi admin
            from config.config import OWNER_ID
            if message.from_user.id not in OWNER_ID:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Only owner can debug channel issues",
                    reply_to_message_id=message.id
                )
                return False

            debug_info = f"🔍 **Channel Debug Report**\n\n"
            
            # 1. Check auto-posting status
            debug_info += f"**1. Auto-posting Status:**\n"
            debug_info += f"• Running: {'✅ Yes' if channel_manager.is_running else '❌ No'}\n"
            debug_info += f"• Channel: {channel_manager.channel_username}\n\n"
            
            # 2. Check channel access
            debug_info += f"**2. Channel Access Test:**\n"
            try:
                channel_info = await client.get_chat(channel_manager.channel_username)
                debug_info += f"• Channel Found: ✅ Yes\n"
                debug_info += f"• Title: {channel_info.title}\n"
                debug_info += f"• Type: {channel_info.type}\n"
                debug_info += f"• Members: {getattr(channel_info, 'members_count', 'N/A')}\n"
                
                # Test bot's permission
                try:
                    bot_member = await client.get_chat_member(channel_manager.channel_username, 'me')
                    debug_info += f"• Bot Status: {bot_member.status}\n"
                    debug_info += f"• Can Post: {'✅ Yes' if bot_member.status in ['administrator', 'creator'] else '❌ No'}\n"
                except Exception as perm_error:
                    debug_info += f"• Bot Status: ❌ Error: {str(perm_error)}\n"
                    
            except Exception as channel_error:
                debug_info += f"• Channel Access: ❌ Error: {str(channel_error)}\n"
            
            debug_info += f"\n**3. Recent Posts Check:**\n"
            try:
                # Get recent posts from database
                await channel_manager._ensure_db_connection()
                recent_posts = await channel_manager.channel_posts.find({}).sort("created_at", -1).limit(5).to_list(length=None)
                
                if recent_posts:
                    debug_info += f"• Database Posts: {len(recent_posts)} recent posts found\n"
                    for post in recent_posts:
                        status = post.get('status', 'unknown')
                        created_at = post.get('created_at', 'unknown')
                        debug_info += f"  - {post.get('type', 'unknown')}: {status} ({created_at})\n"
                else:
                    debug_info += f"• Database Posts: ❌ No posts found in database\n"
                    
            except Exception as db_error:
                debug_info += f"• Database: ❌ Error: {str(db_error)}\n"
            
            debug_info += f"\n**4. Scheduler Status:**\n"
            debug_info += f"• Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            debug_info += f"• Next Daily Tips: 08:00 (if not posted today)\n"
            debug_info += f"• Next Fun Facts: 14:00 (if not posted today)\n"
            debug_info += f"• Next Q&A: 20:00 (if not posted today)\n"
            
            # Check if today's content was posted
            debug_info += f"\n**5. Today's Content Status:**\n"
            today_checks = [
                ("daily_tips", "Daily Tips"),
                ("fun_facts", "Fun Facts"),
                ("qna", "Q&A Session")
            ]
            
            for content_type, display_name in today_checks:
                posted_today = await channel_manager._is_content_posted_today(content_type)
                debug_info += f"• {display_name}: {'✅ Posted' if posted_today else '❌ Not posted'}\n"
            
            debug_info += f"\n**💡 Troubleshooting Tips:**\n"
            debug_info += f"1. Pastikan bot adalah admin di channel @syncara_insight\n"
            debug_info += f"2. Cek apakah auto-posting sedang berjalan dengan [CHANNEL:STATUS]\n"
            debug_info += f"3. Test manual posting dengan [CHANNEL:POST:daily_tips]\n"
            debug_info += f"4. Restart auto-posting dengan [CHANNEL:STOP] lalu [CHANNEL:START]\n"
            debug_info += f"5. Periksa log error di console"

            await client.send_message(
                chat_id=message.chat.id,
                text=debug_info,
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error in debug_channel: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error in debug: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

    async def test_channel_access(self, client, message, params):
        """Test channel access and send a test message"""
        try:
            # Validasi admin
            from config.config import OWNER_ID
            if message.from_user.id not in OWNER_ID:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Only owner can test channel access",
                    reply_to_message_id=message.id
                )
                return False

            test_msg = await client.send_message(
                chat_id=message.chat.id,
                text="🧪 **Testing Channel Access...**\n\nSedang mencoba kirim pesan test ke channel...",
                reply_to_message_id=message.id
            )

            try:
                # Test send message to channel
                test_content = f"🧪 **Test Message**\n\n✅ Bot berhasil mengirim pesan ke channel!\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🤖 This is a test message from Syncara Bot"
                
                sent_message = await client.send_message(
                    chat_id=channel_manager.channel_username,
                    text=test_content
                )
                
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=test_msg.id,
                    text=f"✅ **Channel Access Test Successful!**\n\n📢 Test message berhasil dikirim ke {channel_manager.channel_username}\n📨 Message ID: {sent_message.id}\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n💡 Channel posting berfungsi dengan baik!"
                )
                
                return True
                
            except Exception as send_error:
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=test_msg.id,
                    text=f"❌ **Channel Access Test Failed!**\n\n🚫 Error: {str(send_error)}\n\n💡 **Possible Issues:**\n• Bot bukan admin di channel\n• Channel tidak ditemukan\n• Bot tidak punya permission untuk post\n• Channel username salah\n\n🔧 **Fix:**\n1. Pastikan bot adalah admin di @syncara_insight\n2. Berikan permission 'Post Messages' ke bot\n3. Cek apakah channel username benar"
                )
                return False
                
        except Exception as e:
            console.error(f"Error in test_channel_access: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error in channel test: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

    async def restart_auto_posting(self, client, message, params):
        """Restart auto-posting system"""
        try:
            # Validasi admin
            from config.config import OWNER_ID
            if message.from_user.id not in OWNER_ID:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Only owner can restart auto-posting",
                    reply_to_message_id=message.id
                )
                return False

            restart_msg = await client.send_message(
                chat_id=message.chat.id,
                text="🔄 **Restarting Auto-posting System...**\n\nPlease wait...",
                reply_to_message_id=message.id
            )

            try:
                # Stop current auto-posting
                if channel_manager.is_running:
                    await channel_manager.stop_auto_posting()
                    await asyncio.sleep(2)  # Wait a bit for cleanup
                
                # Start auto-posting again
                asyncio.create_task(channel_manager.start_auto_posting(client))
                
                # Wait a bit to ensure it starts properly
                await asyncio.sleep(3)
                
                # Check if it's running
                if channel_manager.is_running:
                    await client.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=restart_msg.id,
                        text="✅ **Auto-posting System Restarted Successfully!**\n\n🚀 Status: Active\n📢 Channel: @syncara_insight\n⏰ Scheduler: Running\n\n💡 Auto-posting telah dimulai ulang dan siap bekerja!"
                    )
                else:
                    await client.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=restart_msg.id,
                        text="⚠️ **Auto-posting Restart Warning**\n\n🔄 System telah di-restart tapi status belum aktif\n\n💡 Coba jalankan [CHANNEL:DEBUG] untuk diagnosa lebih lanjut"
                    )
                
                console.info("🔄 Channel auto-posting restarted via shortcode")
                return True
                
            except Exception as restart_error:
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=restart_msg.id,
                    text=f"❌ **Restart Failed**\n\n🚫 Error: {str(restart_error)}\n\n💡 Try using [CHANNEL:DEBUG] to identify the issue"
                )
                return False
                
        except Exception as e:
            console.error(f"Error in restart_auto_posting: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f"❌ Error in restart: {str(e)}",
                reply_to_message_id=message.id
            )
            return False

# Create instance untuk diimpor oleh __init__.py
channel_shortcode = ChannelManagementShortcode() 