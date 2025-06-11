class UserManagementShortcode:
    def __init__(self):
        self.handlers = {
            'USER:BAN': self.ban_user,
            'USER:MUTE': self.mute_user,
        }
        
        self.descriptions = {
            'USER:BAN': 'Ban a user from the group. Usage: [USER:BAN:user_id:reason]',
            'USER:MUTE': 'Mute a user in the group. Usage: [USER:MUTE:user_id:duration]'
        }
    
    async def ban_user(self, client, user_id: int, reason: str = None):
        try:
            await client.ban_chat_member(message.chat.id, user_id)
            return True
        except Exception as e:
            print(f"Error banning user: {e}")
            return False
    
    async def mute_user(self, client, user_id: int, duration: int = None):
        try:
            await client.restrict_chat_member(
                message.chat.id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=duration
            )
            return True
        except Exception as e:
            print(f"Error muting user: {e}")
            return False
