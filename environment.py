from dotenv import load_dotenv
import os

load_dotenv()

ENTRY = "https://discordapp.com/api/v9"
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"]
CAP_API_KEY = os.environ["CAP_API_KEY"]
TEXT_API_KEY = os.environ["TEXT_API_KEY"]
CATCHALL = os.environ["CATCHALL"]
# PROXY_KEY = os.environ["WEBSCRAPINGAPI_KEY"]