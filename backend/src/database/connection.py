"""
Database Connection Management
Extracted from server.py for better organization
"""
import sqlite3
from contextlib import contextmanager

# Database configuration
DB_PATH = "aquaforest_analytics.db"

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()