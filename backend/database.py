import sqlite3
import os
from pydantic import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trust_vault.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # User Credentials for the Advocate to use
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (
        service_name TEXT PRIMARY KEY,
        username TEXT,
        password TEXT
    )''')
    
    # Pre-approved limits
    c.execute('''CREATE TABLE IF NOT EXISTS limits (
        service_name TEXT PRIMARY KEY,
        amount_limit REAL
    )''')
    
    # Pending Bills for Steward Review
    c.execute('''CREATE TABLE IF NOT EXISTS pending_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT,
        amount REAL,
        status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
        reasoning TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Seed data if empty
    c.execute('SELECT count(*) FROM credentials')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO credentials VALUES ('utility_portal', 'senior_citizen', 'password123')")
        c.execute("INSERT INTO limits VALUES ('utility_portal', 100.00)")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
