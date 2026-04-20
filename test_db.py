import sys
import os
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
from db_manager import DBManager

load_dotenv()

# Database details
db = DBManager(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "1234")
)

# Check panra logic
if db.connect():
    print("✅ Database Connect Aayiduchu!")
    db.init_db()  # Table create panna
    print("✅ Table ready aayiduchu!")
else:
    print("❌ Connection failed! Password illa port-ah check pannunga.")
