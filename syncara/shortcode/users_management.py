# syncara/shortcode/users_management.py
from syncara.console import console
from pyrogram.types import ChatPermissions, ChatPrivileges  # Tambahkan ChatPrivileges
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, Optional

async def is_admin_or_owner(client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")

class UserManagementShortcode:
    def __init__(self):
        self.handlers = {
            'USER:BAN': self.ban_user,
            'USER:UNBAN': self.unban_user,
            'USER:KICK': self.kick_user,
            'USER:MUTE': self.mute_user,
            'USER:UNMUTE': self.unmute_user,
            'USER:WARN': self.warn_user,
            'USER:PROMOTE': self.promote_user,
            'USER:DEMOTE': self.demote_user,
            'USER:WARNINGS': self.show_warnings,
            'USER:INFO': self.show_user_info,
            'USER:HISTORY': self.show_user_history,
        }
        
        self.descriptions = {
            'USER:BAN': 'Ban a user from the group. Usage: [USER:BAN:user_id_or_username]',
            'USER:UNBAN': 'Unban a user from the group. Usage: [USER:UNBAN:user_id_or_username]',
            'USER:KICK': 'Kick a user from the group. Usage: [USER:KICK:user_id_or_username]',
            'USER:MUTE': 'Mute a user in the group. Usage: [USER:MUTE:user_id_or_username:duration_minutes]',
            'USER:UNMUTE': 'Unmute a user in the group. Usage: [USER:UNMUTE:user_id_or_username]',
            'USER:WARN': 'Warn a user. Usage: [USER:WARN:user_id_or_username:reason]',
            'USER:PROMOTE': 'Promote a user to admin. Usage: [USER:PROMOTE:user_id_or_username:title]',
            'USER:DEMOTE': 'Demote a user from admin. Usage: [USER:DEMOTE:user_id_or_username]',
            'USER:WARNINGS': 'Show user warnings. Usage: [USER:WARNINGS:user_id_or_username]',
            'USER:INFO': 'Show user information. Usage: [USER:INFO:user_id_or_username]',
            'USER:HISTORY': 'Show user action history. Usage: [USER:HISTORY:user_id_or_username]',
        }
        
        self.pending_responses = {}
        self._db_initialized = False

    async def _ensure_db_connection(self):
        """Ensure database connection is available"""
        if not self._db_initialized:
            try:
                from syncara.database import (
                    user_warnings, ban_records, mute_records, 
                    user_permissions, log_system_event, log_error
                )
                self.user_warnings = user_warnings
                self.ban_records = ban_records
                self.mute_records = mute_records
                self.user_permissions = user_permissions
                self.log_system_event = log_system_event
                self.log_error = log_error
                self._db_initialized = True
            except ImportError:
                console.error("Database not available for user management persistence")

    async def resolve_user_id(self, client, message, user_identifier):
        """
        Resolve user identifier (username, user_id, or mention) to user_id
        """
        try:
            # If it's already a number, return it
            if user_identifier.isdigit():
                return int(user_identifier)
            
            # Remove @ if present
            if user_identifier.startswith('@'):
                user_identifier = user_identifier[1:]
            
            # Try to get user info by username
            try:
                user = await client.get_users(user_identifier)
                return user.id
            except Exception:
                # If username doesn't work, try as user_id string
                try:
                    return int(user_identifier)
                except ValueError:
                    return None
        except Exception as e:
            console.error(f"Error resolving user ID: {str(e)}")
            return None

    async def ban_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:BAN:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Ban user
            await client.ban_chat_member(message.chat.id, user_id)
            
            # Record ban in database
            await self._record_ban(
                user_id=user_id,
                chat_id=message.chat.id,
                banned_by=message.from_user.id,
                reason=f"Banned by admin",
                duration=None  # Permanent ban
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"🚫 User {user_identifier} telah di-ban dari group",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error banning user: {str(e)}")
            await self._log_error("user_management", f"Error banning user: {str(e)}")
            return False

    async def unban_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:UNBAN:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Unban user
            await client.unban_chat_member(message.chat.id, user_id)
            
            # Update ban record in database
            await self._update_ban_record(
                user_id=user_id,
                chat_id=message.chat.id,
                unbanned_by=message.from_user.id
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"✅ User {user_identifier} telah di-unban",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error unbanning user: {str(e)}")
            await self._log_error("user_management", f"Error unbanning user: {str(e)}")
            return False

    async def kick_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:KICK:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Kick user (ban then unban)
            await client.ban_chat_member(message.chat.id, user_id)
            await client.unban_chat_member(message.chat.id, user_id)
            
            # Record kick action
            await self._record_action(
                user_id=user_id,
                chat_id=message.chat.id,
                action="kick",
                performed_by=message.from_user.id,
                reason="Kicked by admin"
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"👋 User {user_identifier} telah di-kick dari group",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error kicking user: {str(e)}")
            await self._log_error("user_management", f"Error kicking user: {str(e)}")
            return False

    async def mute_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            parts = params.split(':', 1)
            if len(parts) < 1:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:MUTE:user_id_or_username:duration_minutes]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_identifier = parts[0].strip()
            duration_minutes = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 60
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Mute user
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
            
            # Calculate unmute time
            unmute_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
            
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=permissions,
                until_date=unmute_time
            )
            
            # Record mute in database
            await self._record_mute(
                user_id=user_id,
                chat_id=message.chat.id,
                muted_by=message.from_user.id,
                duration_minutes=duration_minutes,
                reason=f"Muted for {duration_minutes} minutes"
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"🔇 User {user_identifier} telah di-mute selama {duration_minutes} menit",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error muting user: {str(e)}")
            await self._log_error("user_management", f"Error muting user: {str(e)}")
            return False

    async def unmute_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:UNMUTE:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Unmute user - restore normal permissions
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=permissions
            )
            
            # Update mute record
            await self._update_mute_record(
                user_id=user_id,
                chat_id=message.chat.id,
                unmuted_by=message.from_user.id
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"🔊 User {user_identifier} telah di-unmute",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error unmuting user: {str(e)}")
            await self._log_error("user_management", f"Error unmuting user: {str(e)}")
            return False

    async def warn_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            parts = params.split(':', 1)
            if len(parts) < 1:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:WARN:user_id_or_username:reason]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_identifier = parts[0].strip()
            reason = parts[1].strip() if len(parts) > 1 else "No reason provided"
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Record warning
            warning_count = await self._record_warning(
                user_id=user_id,
                chat_id=message.chat.id,
                warned_by=message.from_user.id,
                reason=reason
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"⚠️ User {user_identifier} telah di-warn\n📝 Reason: {reason}\n📊 Total warnings: {warning_count}",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error warning user: {str(e)}")
            await self._log_error("user_management", f"Error warning user: {str(e)}")
            return False

    async def promote_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            parts = params.split(':', 1)
            if len(parts) < 1:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:PROMOTE:user_id_or_username:title]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_identifier = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else "Admin"
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Promote user
            privileges = ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                is_anonymous=False
            )
            
            await client.promote_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                privileges=privileges
            )
            
            # Set custom title if provided
            if title != "Admin":
                await client.set_administrator_title(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    title=title
                )
            
            # Record promotion
            await self._record_permission_change(
                user_id=user_id,
                chat_id=message.chat.id,
                changed_by=message.from_user.id,
                action="promote",
                title=title
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"👑 User {user_identifier} telah di-promote menjadi {title}",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error promoting user: {str(e)}")
            await self._log_error("user_management", f"Error promoting user: {str(e)}")
            return False

    async def demote_user(self, client, message, params):
        # Validasi tipe chat
        if getattr(message.chat, 'type', None) not in ["group", "supergroup"]:
            return False
            
        if not await is_admin_or_owner(client, message):
            return False
            
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:DEMOTE:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Demote user (remove all admin privileges)
            privileges = ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                is_anonymous=False
            )
            
            await client.promote_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                privileges=privileges
            )
            
            # Record demotion
            await self._record_permission_change(
                user_id=user_id,
                chat_id=message.chat.id,
                changed_by=message.from_user.id,
                action="demote"
            )
            
            await client.send_message(
                chat_id=message.chat.id,
                text=f"📉 User {user_identifier} telah di-demote",
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error demoting user: {str(e)}")
            await self._log_error("user_management", f"Error demoting user: {str(e)}")
            return False

    async def show_warnings(self, client, message, params):
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:WARNINGS:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Get user warnings
            warnings = await self._get_user_warnings(user_id, message.chat.id)
            
            if not warnings:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"✅ User {user_identifier} tidak memiliki warning",
                    reply_to_message_id=message.id
                )
                return True
            
            # Format warnings
            response = f"⚠️ **Warnings untuk {user_identifier}:**\n\n"
            for i, warning in enumerate(warnings[-5:], 1):  # Show last 5 warnings
                timestamp = warning.get('created_at', datetime.utcnow()).strftime('%d/%m %H:%M')
                reason = warning.get('reason', 'No reason')
                response += f"**{i}.** {timestamp}\n📝 {reason}\n\n"
            
            if len(warnings) > 5:
                response += f"... dan {len(warnings) - 5} warning lainnya"
            
            response += f"\n📊 **Total warnings:** {len(warnings)}"
            
            await client.send_message(
                chat_id=message.chat.id,
                text=response,
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error showing warnings: {str(e)}")
            await self._log_error("user_management", f"Error showing warnings: {str(e)}")
            return False

    async def show_user_info(self, client, message, params):
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:INFO:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Get user info from Telegram
            try:
                user = await client.get_users(user_id)
                member = await client.get_chat_member(message.chat.id, user_id)
            except Exception as e:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Gagal mendapatkan info user: {str(e)}",
                    reply_to_message_id=message.id
                )
                return False
            
            # Get user stats from database
            stats = await self._get_user_stats(user_id, message.chat.id)
            
            # Format user info
            response = f"👤 **User Information:**\n\n"
            response += f"**Name:** {user.first_name or 'N/A'}"
            if user.last_name:
                response += f" {user.last_name}"
            response += f"\n**Username:** @{user.username or 'N/A'}"
            response += f"\n**User ID:** `{user.id}`"
            response += f"\n**Status:** {member.status}"
            
            if stats:
                response += f"\n\n📊 **Statistics:**"
                response += f"\n⚠️ **Warnings:** {stats.get('warnings', 0)}"
                response += f"\n🚫 **Bans:** {stats.get('bans', 0)}"
                response += f"\n🔇 **Mutes:** {stats.get('mutes', 0)}"
                response += f"\n👑 **Promotions:** {stats.get('promotions', 0)}"
            
            await client.send_message(
                chat_id=message.chat.id,
                text=response,
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error showing user info: {str(e)}")
            await self._log_error("user_management", f"Error showing user info: {str(e)}")
            return False

    async def show_user_history(self, client, message, params):
        try:
            user_identifier = params.strip()
            if not user_identifier:
                await client.send_message(
                    chat_id=message.chat.id,
                    text="❌ Format: [USER:HISTORY:user_id_or_username]",
                    reply_to_message_id=message.id
                )
                return False
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if not user_id:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ User '{user_identifier}' tidak ditemukan",
                    reply_to_message_id=message.id
                )
                return False
            
            # Get user action history
            history = await self._get_user_history(user_id, message.chat.id, limit=10)
            
            if not history:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"📜 User {user_identifier} tidak memiliki history action",
                    reply_to_message_id=message.id
                )
                return True
            
            # Format history
            response = f"📜 **Action History untuk {user_identifier}:**\n\n"
            for i, action in enumerate(history, 1):
                timestamp = action.get('timestamp', datetime.utcnow()).strftime('%d/%m %H:%M')
                action_type = action.get('action', 'unknown')
                reason = action.get('reason', 'No reason')
                
                action_emoji = {
                    'warn': '⚠️',
                    'ban': '🚫',
                    'unban': '✅',
                    'mute': '🔇',
                    'unmute': '🔊',
                    'kick': '👋',
                    'promote': '👑',
                    'demote': '📉'
                }.get(action_type, '📝')
                
                response += f"**{i}.** {action_emoji} {action_type.title()} - {timestamp}\n"
                response += f"📝 {reason}\n\n"
            
            await client.send_message(
                chat_id=message.chat.id,
                text=response,
                reply_to_message_id=message.id
            )
            
            return True
            
        except Exception as e:
            console.error(f"Error showing user history: {str(e)}")
            await self._log_error("user_management", f"Error showing user history: {str(e)}")
            return False

    # ==================== DATABASE OPERATIONS ====================
    
    async def _record_warning(self, user_id: int, chat_id: int, warned_by: int, reason: str) -> int:
        """Record user warning and return total warning count"""
        try:
            await self._ensure_db_connection()
            
            warning_doc = {
                'user_id': user_id,
                'chat_id': chat_id,
                'warned_by': warned_by,
                'reason': reason,
                'created_at': datetime.utcnow()
            }
            
            await self.user_warnings.insert_one(warning_doc)
            
            # Get total warning count
            count = await self.user_warnings.count_documents({
                'user_id': user_id,
                'chat_id': chat_id
            })
            
            await self.log_system_event("info", "user_management", f"User {user_id} warned in chat {chat_id}")
            
            return count
            
        except Exception as e:
            console.error(f"Error recording warning: {str(e)}")
            return 0

    async def _record_ban(self, user_id: int, chat_id: int, banned_by: int, reason: str, duration: Optional[int] = None):
        """Record user ban"""
        try:
            await self._ensure_db_connection()
            
            ban_doc = {
                'user_id': user_id,
                'chat_id': chat_id,
                'banned_by': banned_by,
                'reason': reason,
                'duration_minutes': duration,
                'created_at': datetime.utcnow(),
                'is_active': True,
                'unbanned_at': None,
                'unbanned_by': None
            }
            
            await self.ban_records.insert_one(ban_doc)
            await self.log_system_event("info", "user_management", f"User {user_id} banned in chat {chat_id}")
            
        except Exception as e:
            console.error(f"Error recording ban: {str(e)}")

    async def _update_ban_record(self, user_id: int, chat_id: int, unbanned_by: int):
        """Update ban record when user is unbanned"""
        try:
            await self._ensure_db_connection()
            
            await self.ban_records.update_one(
                {
                    'user_id': user_id,
                    'chat_id': chat_id,
                    'is_active': True
                },
                {
                    '$set': {
                        'is_active': False,
                        'unbanned_at': datetime.utcnow(),
                        'unbanned_by': unbanned_by
                    }
                }
            )
            
            await self.log_system_event("info", "user_management", f"User {user_id} unbanned in chat {chat_id}")
            
        except Exception as e:
            console.error(f"Error updating ban record: {str(e)}")

    async def _record_mute(self, user_id: int, chat_id: int, muted_by: int, duration_minutes: int, reason: str):
        """Record user mute"""
        try:
            await self._ensure_db_connection()
            
            mute_doc = {
                'user_id': user_id,
                'chat_id': chat_id,
                'muted_by': muted_by,
                'reason': reason,
                'duration_minutes': duration_minutes,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(minutes=duration_minutes),
                'is_active': True,
                'unmuted_at': None,
                'unmuted_by': None
            }
            
            await self.mute_records.insert_one(mute_doc)
            await self.log_system_event("info", "user_management", f"User {user_id} muted in chat {chat_id}")
            
        except Exception as e:
            console.error(f"Error recording mute: {str(e)}")

    async def _update_mute_record(self, user_id: int, chat_id: int, unmuted_by: int):
        """Update mute record when user is unmuted"""
        try:
            await self._ensure_db_connection()
            
            await self.mute_records.update_one(
                {
                    'user_id': user_id,
                    'chat_id': chat_id,
                    'is_active': True
                },
                {
                    '$set': {
                        'is_active': False,
                        'unmuted_at': datetime.utcnow(),
                        'unmuted_by': unmuted_by
                    }
                }
            )
            
            await self.log_system_event("info", "user_management", f"User {user_id} unmuted in chat {chat_id}")
            
        except Exception as e:
            console.error(f"Error updating mute record: {str(e)}")

    async def _record_permission_change(self, user_id: int, chat_id: int, changed_by: int, action: str, title: str = None):
        """Record permission change (promote/demote)"""
        try:
            await self._ensure_db_connection()
            
            permission_doc = {
                'user_id': user_id,
                'chat_id': chat_id,
                'changed_by': changed_by,
                'action': action,
                'title': title,
                'created_at': datetime.utcnow()
            }
            
            await self.user_permissions.insert_one(permission_doc)
            await self.log_system_event("info", "user_management", f"User {user_id} {action} in chat {chat_id}")
            
        except Exception as e:
            console.error(f"Error recording permission change: {str(e)}")

    async def _record_action(self, user_id: int, chat_id: int, action: str, performed_by: int, reason: str):
        """Record general user action"""
        try:
            await self._ensure_db_connection()
            
            action_doc = {
                'user_id': user_id,
                'chat_id': chat_id,
                'action': action,
                'performed_by': performed_by,
                'reason': reason,
                'timestamp': datetime.utcnow()
            }
            
            # We can use any of the existing collections or create a general actions collection
            # For now, let's use user_permissions as it's the most general
            await self.user_permissions.insert_one(action_doc)
            await self.log_system_event("info", "user_management", f"Action {action} performed on user {user_id}")
            
        except Exception as e:
            console.error(f"Error recording action: {str(e)}")

    async def _get_user_warnings(self, user_id: int, chat_id: int) -> list:
        """Get user warnings from database"""
        try:
            await self._ensure_db_connection()
            
            warnings = await self.user_warnings.find({
                'user_id': user_id,
                'chat_id': chat_id
            }).sort('created_at', -1).to_list(length=None)
            
            return warnings
            
        except Exception as e:
            console.error(f"Error getting user warnings: {str(e)}")
            return []

    async def _get_user_stats(self, user_id: int, chat_id: int) -> Dict[str, int]:
        """Get user statistics from database"""
        try:
            await self._ensure_db_connection()
            
            stats = {}
            
            # Count warnings
            stats['warnings'] = await self.user_warnings.count_documents({
                'user_id': user_id,
                'chat_id': chat_id
            })
            
            # Count bans
            stats['bans'] = await self.ban_records.count_documents({
                'user_id': user_id,
                'chat_id': chat_id
            })
            
            # Count mutes
            stats['mutes'] = await self.mute_records.count_documents({
                'user_id': user_id,
                'chat_id': chat_id
            })
            
            # Count promotions
            stats['promotions'] = await self.user_permissions.count_documents({
                'user_id': user_id,
                'chat_id': chat_id,
                'action': 'promote'
            })
            
            return stats
            
        except Exception as e:
            console.error(f"Error getting user stats: {str(e)}")
            return {}

    async def _get_user_history(self, user_id: int, chat_id: int, limit: int = 10) -> list:
        """Get user action history from database"""
        try:
            await self._ensure_db_connection()
            
            history = []
            
            # Get warnings
            warnings = await self.user_warnings.find({
                'user_id': user_id,
                'chat_id': chat_id
            }).to_list(length=None)
            
            for warning in warnings:
                history.append({
                    'timestamp': warning.get('created_at'),
                    'action': 'warn',
                    'reason': warning.get('reason')
                })
            
            # Get bans
            bans = await self.ban_records.find({
                'user_id': user_id,
                'chat_id': chat_id
            }).to_list(length=None)
            
            for ban in bans:
                history.append({
                    'timestamp': ban.get('created_at'),
                    'action': 'ban',
                    'reason': ban.get('reason')
                })
            
            # Get mutes
            mutes = await self.mute_records.find({
                'user_id': user_id,
                'chat_id': chat_id
            }).to_list(length=None)
            
            for mute in mutes:
                history.append({
                    'timestamp': mute.get('created_at'),
                    'action': 'mute',
                    'reason': mute.get('reason')
                })
            
            # Get permission changes
            permissions = await self.user_permissions.find({
                'user_id': user_id,
                'chat_id': chat_id
            }).to_list(length=None)
            
            for perm in permissions:
                history.append({
                    'timestamp': perm.get('created_at', perm.get('timestamp')),
                    'action': perm.get('action'),
                    'reason': perm.get('reason', f"Permission {perm.get('action')}")
                })
            
            # Sort by timestamp and limit
            history.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            return history[:limit]
            
        except Exception as e:
            console.error(f"Error getting user history: {str(e)}")
            return []

    async def _log_error(self, module: str, error: str):
        """Log error to database"""
        try:
            await self.log_error(module, error)
        except:
            pass

    async def send_pending_responses(self, client, response_ids):
        """Send pending responses with delay"""
        if not response_ids:
            return
            
        sent_responses = []
        
        for response_id in response_ids:
            if response_id in self.pending_responses:
                response_data = self.pending_responses[response_id]
                
                try:
                    await client.send_message(
                        chat_id=response_data['chat_id'],
                        text=response_data['text'],
                        reply_to_message_id=response_data['reply_to_message_id']
                    )
                    sent_responses.append(response_id)
                    console.info(f"[USER] Sent response: {response_id}")
                    
                except Exception as e:
                    console.error(f"[USER] Error sending response {response_id}: {e}")
                    
                # Clean up
                del self.pending_responses[response_id]
                
        return sent_responses

# Create instance untuk diimpor oleh __init__.py
users_shortcode = UserManagementShortcode()