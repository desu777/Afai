"""
Messenger History Management
Database operations for Facebook Messenger conversations
"""
from typing import List, Dict
from .connection import get_db
from config import debug_print

def load_messenger_chat_history(user_id: str) -> List[Dict[str, str]]:
    """Load last exchange (user question + assistant response) for context"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get last 2 messages (1 exchange) for lightweight context
            cursor.execute("""
                SELECT message_role, message_content 
                FROM messenger_history 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 2
            """, (user_id,))
            
            messages = cursor.fetchall()
            
            # Reverse to get chronological order (older first)
            chat_history = []
            for row in reversed(messages):
                chat_history.append({
                    "role": row["message_role"], 
                    "content": row["message_content"]
                })
            
            if chat_history:
                debug_print(f"[INFO] [Messenger] Loaded {len(chat_history)} messages for context for user {user_id}")
                return chat_history
            else:
                debug_print(f"[INFO] [Messenger] No chat history found for user {user_id}")
                return []
                
    except Exception as e:
        debug_print(f"[ERROR] [Messenger] Error loading chat history for {user_id}: {e}")
        return []

def save_messenger_message(user_id: str, role: str, content: str, message_id: str = None):
    """Save a message to messenger history"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO messenger_history (user_id, message_role, message_content, message_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, role, content, message_id))
            
            conn.commit()
            debug_print(f"[CACHE] [Messenger] Saved {role} message for user {user_id}")
            
    except Exception as e:
        debug_print(f"[ERROR] [Messenger] Error saving message for {user_id}: {e}")

def cleanup_old_messenger_history(days_to_keep: int = 30):
    """Clean up old messages to prevent database bloat"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM messenger_history 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days_to_keep))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                debug_print(f"[CLEANUP] [Messenger] Cleaned up {deleted_count} old messages (older than {days_to_keep} days)")
                
    except Exception as e:
        debug_print(f"[ERROR] [Messenger] Error cleaning up old messages: {e}")