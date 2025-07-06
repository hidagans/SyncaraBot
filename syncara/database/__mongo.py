from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URI

# function database
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.SyncaraBot

# variable mongo
users = db.users
group = db.groups