import sqlite3
import os
from pydantic import BaseModel

# Support environment variable for database path
DB_PATH = os.getenv(
    "DATABASE_URL",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trust_vault.db")
).replace("sqlite:///", "")

def get_db_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize legacy database tables.
    
    NOTE: For production, use Alembic migrations instead:
        alembic upgrade head
    
    This function creates legacy tables for backward compatibility.
    New tables should be added via Alembic migrations.
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
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
    
    # Pending Bills for Steward Review (Legacy)
    # NOTE: New pending approvals use the pending_approvals table via Alembic
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
    print(f"✅ Database initialized at: {DB_PATH}")
    print("💡 For production, use: alembic upgrade head")
