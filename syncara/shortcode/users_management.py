# syncara/shortcode/users_management.py
from syncara import console
from pyrogram.types import ChatPermissions, ChatPrivileges  # Tambahkan ChatPrivileges
from datetime import datetime, timedelta

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
                # If username doesn't work, try to find in chat members
                try:
                    async for member in client.get_chat_members(message.chat.id):
                        if (member.user.username and member.user.username.lower() == user_identifier.lower()) or \
                           (member.user.first_name and member.user.first_name.lower() == user_identifier.lower()):
                            return member.user.id
                except Exception:
                    pass
                
                # Last resort: try to parse as int
                return int(user_identifier)
                
        except Exception as e:
            console.error(f"Error resolving user ID for '{user_identifier}': {e}")
            return None
    
    async def ban_user(self, client, message, params):
        """Ban a user from the group"""
        try:
            user_id = await self.resolve_user_id(client, message, params)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {params}")
                return False
                
            await client.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
            console.info(f"Banned user {user_id} ({params}) from chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error banning user: {e}")
            return False
    
    async def unban_user(self, client, message, params):
        """Unban a user from the group"""
        try:
            user_id = await self.resolve_user_id(client, message, params)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {params}")
                return False
                
            await client.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
            console.info(f"Unbanned user {user_id} ({params}) from chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error unbanning user: {e}")
            return False
    
    async def kick_user(self, client, message, params):
        """Kick a user from the group"""
        try:
            user_id = await self.resolve_user_id(client, message, params)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {params}")
                return False
                
            await client.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
            await client.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
            console.info(f"Kicked user {user_id} ({params}) from chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error kicking user: {e}")
            return False
    
    async def mute_user(self, client, message, params):
        """Mute a user in the group"""
        try:
            parts = params.split(':')
            user_id = await self.resolve_user_id(client, message, parts[0])
            if user_id is None:
                console.error(f"Could not resolve user ID for: {parts[0]}")
                return False
            
            # Calculate until_date if duration is provided
            until_date = None
            if len(parts) > 1 and parts[1].isdigit():
                duration_minutes = int(parts[1])
                until_date = datetime.now() + timedelta(minutes=duration_minutes)
            
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
            
            duration_text = f" for {parts[1]} minutes" if len(parts) > 1 else ""
            console.info(f"Muted user {user_id} ({parts[0]}) in chat {message.chat.id}{duration_text}")
            return True
        except Exception as e:
            console.error(f"Error muting user: {e}")
            return False
    
    async def unmute_user(self, client, message, params):
        """Unmute a user in the group"""
        try:
            user_id = await self.resolve_user_id(client, message, params)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {params}")
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
            
            console.info(f"Unmuted user {user_id} ({params}) in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error unmuting user: {e}")
            return False
    
    async def warn_user(self, client, message, params):
        """Warn a user (placeholder - you can implement warning system)"""
        try:
            parts = params.split(':', 1)
            user_id = await self.resolve_user_id(client, message, parts[0])
            if user_id is None:
                console.error(f"Could not resolve user ID for: {parts[0]}")
                return False
                
            reason = parts[1] if len(parts) > 1 else "No reason provided"
            
            # Here you can implement warning system with database
            # For now, just log the warning
            console.info(f"Warning issued to user {user_id} ({parts[0]}) in chat {message.chat.id}: {reason}")
            return True
        except Exception as e:
            console.error(f"Error warning user: {e}")
            return False
    
    async def promote_user(self, client, message, params):
        """Promote a user to admin"""
        try:
            parts = params.split(':', 1)
            user_id = await self.resolve_user_id(client, message, parts[0])
            if user_id is None:
                console.error(f"Could not resolve user ID for: {parts[0]}")
                return False
                
            title = parts[1] if len(parts) > 1 else "Admin"
            
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
            if title != "Admin":
                await client.set_administrator_title(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    title=title
                )
            
            console.info(f"Promoted user {user_id} ({parts[0]}) to admin in chat {message.chat.id} with title: {title}")
            return True
        except Exception as e:
            console.error(f"Error promoting user: {e}")
            return False
    
    async def demote_user(self, client, message, params):
        """Demote a user from admin"""
        try:
            user_id = await self.resolve_user_id(client, message, params)
            if user_id is None:
                console.error(f"Could not resolve user ID for: {params}")
                return False
            
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
            
            console.info(f"Demoted user {user_id} ({params}) from admin in chat {message.chat.id}")
            return True
        except Exception as e:
            console.error(f"Error demoting user: {e}")
            return False