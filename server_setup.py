"""Run on server to seed all data."""
import sys, os
sys.path.insert(0, '/opt/kaoyan-assistant')
sys.path.insert(0, '/opt/kaoyan-assistant/backend')

import sqlite3
db = sqlite3.connect('/opt/kaoyan-assistant/data/kaoyan.db')
db.row_factory = sqlite3.Row

# Show counts
for table in ['vocab_words', 'school_info', 'writing_essays', 'flashcards', 'tasks', 'notes_and_errors']:
    c = db.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()['c']
    print(f'{table}: {c}')

db.close()
print('Server data check complete')
