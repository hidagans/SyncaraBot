from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        
        # Collections
        self.users = self.db.users
        self.groups = self.db.groups
        self.settings = self.db.settings
    
    # User operations
    async def add_user(self, user_id, username=None, first_name=None):
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "joined_at": datetime.now()
        }
        
        return self.users.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True
        )
    
    # Group operations
    async def add_group(self, chat_id, title=None):
        group_data = {
            "chat_id": chat_id,
            "title": title,
            "added_at": datetime.now()
        }
        
        return self.groups.update_one(
            {"chat_id": chat_id},
            {"$set": group_data},
            upsert=True
        )
    
    # Tambahkan method lain sesuai kebutuhan
