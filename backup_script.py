import sqlite3
import os
from datetime import datetime

def backup_db(db_path, backup_path):
    conn = sqlite3.connect(db_path)
    backup_conn = sqlite3.connect(backup_path)
    with backup_conn:
        conn.backup(backup_conn)
    backup_conn.close()
    conn.close()

if __name__ == '__main__':
    db_path = 'db.sqlite3'
    backup_path = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    backup_db(db_path, backup_path)
    print(f'Database backup successful: {backup_path}')
