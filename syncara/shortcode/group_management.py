class GroupManagementShortcode:
    def __init__(self):
        self.handlers = {
            'GROUP:DELETE_MESSAGE': self.delete_message,
            'GROUP:PIN_MESSAGE': self.pin_message,
        }
        
        self.descriptions = {
            'GROUP:DELETE_MESSAGE': 'Delete a message by its ID. Usage: [GROUP:DELETE_MESSAGE:message_id]',
            'GROUP:PIN_MESSAGE': 'Pin a message in the chat. Usage: [GROUP:PIN_MESSAGE:message_id]'
        }
    
    async def delete_message(self, client, message_id: int):
        try:
            await client.delete_messages(message.chat.id, message_id)
            return True
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False
    
    async def pin_message(self, client, message_id: int):
        try:
            await client.pin_chat_message(message.chat.id, message_id)
            return True
        except Exception as e:
            print(f"Error pinning message: {e}")
            return False
