import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
OWNER_ID = [
    6696975845
]

# Userbot Configuration
USERBOTS = [
    {
        "name": "userbot1",
        "api_id": 12345,
        "api_hash": "your_api_hash",
        "session_string": "your_session_string_1"
    },
    {
        "name": "userbot2",
        "api_id": 12345,
        "api_hash": "your_api_hash",
        "session_string": "your_session_string_2"
    },
    {
        "name": "userbot3",
        "api_id": 12345,
        "api_hash": "your_api_hash",
        "session_string": "your_session_string_3"
    },
    {
        "name": "userbot4",
        "api_id": 12345,
        "api_hash": "your_api_hash",
        "session_string": "your_session_string_4"
    },
    {
        "name": "userbot5",
        "api_id": 12345,
        "api_hash": "your_api_hash",
        "session_string": "your_session_string_5"
    }
]

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "syncara_bot")
