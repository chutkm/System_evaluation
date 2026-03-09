import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL= os.getenv("DATABASE_URL")

SCHEDULE_DB_URL = os.getenv("SCHEDULE_DB_URL")