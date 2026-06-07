import os
from dotenv import load_dotenv

load_dotenv()

# Admin Chat ID lar — /chatid buyrug'i orqali oling
# Bir nechta admin bo'lishi mumkin
_raw = os.getenv("ADMIN_CHAT_IDS", "")
ADMIN_CHAT_IDS = [int(x.strip()) for x in _raw.split(",") if x.strip().isdigit()]

# CRM ma'lumotlar bazasi joyi
DB_PATH = os.getenv("DB_PATH", "../crm_project/db.sqlite3")
