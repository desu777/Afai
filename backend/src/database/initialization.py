"""
Database Initialization
Table creation and setup extracted from server.py
"""
from .connection import get_db
from config import debug_print

def init_database():
    """Initialize SQLite database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                comment TEXT NOT NULL,
                user_type TEXT DEFAULT 'test',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create analyze table for workflow analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyze (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_query TEXT NOT NULL,
                detected_language TEXT,
                intent_detector_decision TEXT,
                intent_confidence REAL,
                business_reasoner_decision TEXT,
                business_corrections TEXT,
                query_optimizer_queries TEXT,
                pinecone_results_count INTEGER,
                pinecone_top_results TEXT,
                filter_decision TEXT,
                filtered_results_count INTEGER,
                final_response TEXT,
                total_execution_time REAL,
                node_timings TEXT,
                escalated BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create messenger_history table for Facebook Messenger conversations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messenger_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message_role TEXT NOT NULL CHECK (message_role IN ('user', 'assistant')),
                message_content TEXT NOT NULL,
                message_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messenger_history_user_time 
            ON messenger_history(user_id, created_at DESC)
        """)
        
        conn.commit()
        debug_print("✅ Database initialized successfully")
        debug_print("🗄️ 📅 [Messenger] Chat history database initialized")