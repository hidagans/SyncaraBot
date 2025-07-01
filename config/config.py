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
        "session_string": "BQFHPFoASBpAM264M_qZNLbKwTlIpWBy7zLZymCG5qj_G5X0O_8dUhhyskwucAZ-o--_ChHY-Nm7c3ckczZQGQpye_6i49vjWq6y7cTOZK1Czr4hwUnc7k41fmpvEpqizOxGCsJpcLUsD2Rxa27MJRfhrndKx-7GTdoBBi2FbyELu20iieoA15w9Sb6CH5oq8aREYeuziB37f-Eid2Vfu464J2Q_-7qsluhvzSynrFB0aTvOeC0Tm482E_V2D4uneDRHrWkDMb1rhwCugsSO53hHVKtFXYg25nDeUfTYxrEBy5Z0Ft-ZmSuDvPupEXITos3MqcPh06IkJG0u7Ex6wr4rvafT0QAAAAGc3e6SAA"
    }
]

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "syncara_bot")
