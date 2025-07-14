import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

# Legacy session string (untuk backward compatibility)
SESSION_STRING = os.getenv("SESSION_STRING")

OWNER_ID = [
    6696975845,  # First owner
    # Add Kenzo's actual User ID here after running /myid
    # Get User ID by sending /myid to the bot
]

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "syncara_bot")
