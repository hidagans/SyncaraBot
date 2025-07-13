# syncara/shortcode/users_management.py
from syncara.console import console
from pyrogram.types import ChatPermissions, ChatPrivileges  # Tambahkan ChatPrivileges
from datetime import datetime, timedelta
import asyncio

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
        }
        
        self.descriptions = {
            'USER:BAN': 'Ban a user from the group. Usage: [USER:BAN:user_id_or_username]',
            'USER:UNBAN': 'Unban a user from the group. Usage: [USER:UNBAN:user_id_or_username]',
            'USER:KICK': 'Kick a user from the group. Usage: [USER:KICK:user_id_or_username]',
            'USER:MUTE': 'Mute a user in the group. Usage: [USER:MUTE:user_id_or_username:duration_minutes]',
            'USER:UNMUTE': 'Unmute a user in the group. Usage: [USER:UNMUTE:user_id_or_username]',
            'USER:WARN': 'Warn a user. Usage: [USER:WARN:user_id_or_username:reason]',
            'USER:PROMOTE': 'Promote a user to admin. Usage: [USER:PROMOTE:user_id_or_username:title]',
            'USER:DEMOTE': 'Demote a user from admin. Usage: [USER:DEMOTE:user_id_or_username]'
        }
        
        self.pending_responses = {}

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
                console.info(f"Found user {user_identifier} with ID: {user.id}")
                return user.id
            except Exception as e:
                console.error(f"Error getting user by username '{user_identifier}': {e}")
                
                # If username doesn't work, try to find in chat members
                try:
                    async for member in client.get_chat_members(message.chat.id):
                        if member.user.username and member.user.username.lower() == user_identifier.lower():
                            console.info(f"Found user {user_identifier} in chat members with ID: {member.user.id}")
                            return member.user.id
                        elif member.user.first_name and member.user.first_name.lower() == user_identifier.lower():
                            console.info(f"Found user {user_identifier} by first name with ID: {member.user.id}")
                            return member.user.id
                except Exception as e:
                    console.error(f"Error searching chat members for '{user_identifier}': {e}")
                
                # Try to get user by mention format
                try:
                    if user_identifier.startswith('user'):
                        # Handle mention format like "user123456789"
                        user_id = user_identifier.replace('user', '')
                        if user_id.isdigit():
                            return int(user_id)
                except:
                    pass
                
                console.error(f"Could not resolve user ID for '{user_identifier}'")
                return None
                
        except Exception as e:
            console.error(f"Error resolving user ID for '{user_identifier}': {e}")
            return None
    
    async def ban_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Ban a user from the group"""
        try:
            user_identifier = params.strip()
            console.info(f"Attempting to ban user: {user_identifier}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
                
            await client.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
            
            # Store for delayed sending
            response_id = f"user_ban_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil ban user: {user_identifier}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:BAN] Banned user {user_id} ({user_identifier}): {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:BAN] Error: {e}")
            return False
    
    async def unban_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Unban a user from the group"""
        try:
            user_identifier = params.strip()
            console.info(f"Attempting to unban user: {user_identifier}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
                
            await client.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
            
            # Store for delayed sending
            response_id = f"user_unban_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil unban user: {user_identifier}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:UNBAN] Unbanned user {user_id} ({user_identifier}): {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:UNBAN] Error: {e}")
            return False
    
    async def kick_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Kick a user from the group"""
        try:
            user_identifier = params.strip()
            console.info(f"Attempting to kick user: {user_identifier}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
                
            await client.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
            await client.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
            
            # Store for delayed sending
            response_id = f"user_kick_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil kick user: {user_identifier}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:KICK] Kicked user {user_id} ({user_identifier}): {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:KICK] Error: {e}")
            return False
    
    async def mute_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Mute a user in the group"""
        try:
            parts = params.split(':')
            user_identifier = parts[0].strip()
            console.info(f"Attempting to mute user: {user_identifier}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
            
            # Calculate until_date if duration is provided
            until_date = None
            duration_text = ""
            if len(parts) > 1 and parts[1].isdigit():
                duration_minutes = int(parts[1])
                until_date = datetime.now() + timedelta(minutes=duration_minutes)
                duration_text = f" selama {duration_minutes} menit"
            
            # Restrict user permissions
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
            
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=permissions,
                until_date=until_date
            )
            
            # Store for delayed sending
            response_id = f"user_mute_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil mute user: {user_identifier}{duration_text}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:MUTE] Muted user {user_id} ({user_identifier}){duration_text}: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:MUTE] Error: {e}")
            return False
    
    async def unmute_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Unmute a user in the group"""
        try:
            user_identifier = params.strip()
            console.info(f"Attempting to unmute user: {user_identifier}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
            
            # Restore default permissions
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
            
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=permissions
            )
            
            # Store for delayed sending
            response_id = f"user_unmute_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil unmute user: {user_identifier}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:UNMUTE] Unmuted user {user_id} ({user_identifier}): {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:UNMUTE] Error: {e}")
            return False
    
    async def warn_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Warn a user (placeholder - you can implement warning system)"""
        try:
            parts = params.split(':', 1)
            user_identifier = parts[0].strip()
            reason = parts[1] if len(parts) > 1 else "Tidak ada alasan"
            
            console.info(f"Attempting to warn user: {user_identifier}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
            
            # Store for delayed sending
            response_id = f"user_warn_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"⚠️ **PERINGATAN** untuk {user_identifier}\n\n**Alasan:** {reason}\n\nIni adalah peringatan resmi dari admin.",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:WARN] Warning issued to user {user_id} ({user_identifier}): {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:WARN] Error: {e}")
            return False
    
    async def promote_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Promote a user to admin"""
        try:
            parts = params.split(':', 1)
            user_identifier = parts[0].strip()
            title = parts[1] if len(parts) > 1 else "Admin"
            
            console.info(f"Attempting to promote user: {user_identifier} with title: {title}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
            
            console.info(f"Resolved user ID {user_id} for {user_identifier}")
            
            # Check if user is already admin
            try:
                chat_member = await client.get_chat_member(message.chat.id, user_id)
                if chat_member.status in ["administrator", "creator"]:
                    # Store for delayed sending
                    response_id = f"user_promote_already_{message.id}"
                    self.pending_responses[response_id] = {
                        'text': f"ℹ️ User {user_identifier} sudah menjadi admin",
                        'chat_id': message.chat.id,
                        'reply_to_message_id': message.id
                    }
                    return response_id
            except Exception as e:
                console.error(f"Error checking user status: {e}")
            
            # Promote user
            await client.promote_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=False,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
            )
            
            # Set custom title if provided
            if title and title != "Admin":
                try:
                    await client.set_administrator_title(
                        chat_id=message.chat.id,
                        user_id=user_id,
                        title=title
                    )
                except Exception as e:
                    console.error(f"Error setting title: {e}")
            
            # Store for delayed sending
            response_id = f"user_promote_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil promote user: {user_identifier} dengan title: {title}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:PROMOTE] Promoted user {user_id} ({user_identifier}) with title {title}: {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:PROMOTE] Error: {e}")
            return False
    
    async def demote_user(self, client, message, params):
        if not await is_admin_or_owner(client, message):
            return False
            
        """Demote a user from admin"""
        try:
            user_identifier = params.strip()
            console.info(f"Attempting to demote user: {user_identifier}")
            
            user_id = await self.resolve_user_id(client, message, user_identifier)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {user_identifier}")
                return False
            
            # Check if user is admin
            try:
                chat_member = await client.get_chat_member(message.chat.id, user_id)
                if chat_member.status not in ["administrator"]:
                    # Store for delayed sending
                    response_id = f"user_demote_not_admin_{message.id}"
                    self.pending_responses[response_id] = {
                        'text': f"ℹ️ User {user_identifier} bukan admin",
                        'chat_id': message.chat.id,
                        'reply_to_message_id': message.id
                    }
                    return response_id
            except Exception as e:
                console.error(f"Error checking user status: {e}")
            
            # Demote user
            await client.promote_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                privileges=ChatPrivileges(
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            
            # Store for delayed sending
            response_id = f"user_demote_{message.id}"
            self.pending_responses[response_id] = {
                'text': f"✅ Berhasil demote user: {user_identifier}",
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[USER:DEMOTE] Demoted user {user_id} ({user_identifier}): {response_id}")
            return response_id
            
        except Exception as e:
            console.error(f"[USER:DEMOTE] Error: {e}")
            return False
    
    async def send_pending_responses(self, client, response_ids):
        """Send pending responses"""
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