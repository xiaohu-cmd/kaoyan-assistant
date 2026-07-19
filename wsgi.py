import sys, os
sys.path.insert(0, '/home/xiaohu/kaoyan-assistant')
sys.path.insert(0, '/home/xiaohu/kaoyan-assistant/backend')

# Pre-load seed data
os.chdir('/home/xiaohu/kaoyan-assistant')

from backend.database import init_db, DATABASE_DIR
os.makedirs(DATABASE_DIR, exist_ok=True)
init_db()

from backend.main import app as application
