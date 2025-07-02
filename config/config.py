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
        "api_id": 21445722,
        "api_hash": "710f18f90849255dd85837d00d5fe85f",
        "session_string": "BQFHPFoAoAqzuRBOGZOnI-4Dt5nyBY2FZyZGn4MDxyOAXdec0AF93QsetfmBPeM8lOPveH_GAXIhXI-OeIfCi0Df5YY3ldDpaxzfgjf81bd_PUhbHZ7JJaCZs3T8k-sWAYEQyT4K9MPSO3ScNw22fKRao6YWkWhhb27ZUGBmuNqV1HkY9xqc_FSK9uKSwj9Yhkw882OGPhN7kuMiWXpYUorB6y9ofcEBTM52ZO6i3EtDQ7-opmwOx8WtRF8YsL3sB84LErEOWbCR8fDSe20icc-WkgDd4JMU_I-5sbbBlyFqOtm0SKUvdJ05rTfeg4-KHUco5pFvnHEEP_4FAumdML3QMDqp2wAAAAGc3e6SAA"
    }
]

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "syncara_bot")
