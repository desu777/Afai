"""
Session Manager for Aquaforest RAG System
Handles session-based extended cache with TTL management
"""
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from models import ConversationState
from config import debug_print, TEST_ENV

class SessionManager:
    """Manages session-based extended cache with TTL"""
    
    def __init__(self, ttl_minutes: int = 10):
        self.ttl_minutes = ttl_minutes
        self.ttl_seconds = ttl_minutes * 60
        self.session_cache: Dict[str, Dict[str, Any]] = {}
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task if event loop is available"""
        try:
            loop = asyncio.get_running_loop()
            if loop and not loop.is_closed():
                if self._cleanup_task is None or self._cleanup_task.done():
                    self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        except RuntimeError:
            # No event loop running, cleanup will be manual
            debug_print("[WARN] [SessionManager] No event loop - cleanup will be manual")
    
    async def _cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions"""
        while True:
            try:
                current_time = time.time()
                expired_sessions = []
                
                for session_id, session_data in self.session_cache.items():
                    if current_time - session_data.get("last_seen", 0) > self.ttl_seconds:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.session_cache[session_id]
                    debug_print(f"[CLEANUP] [SessionManager] Expired session: {session_id}")
                
                if expired_sessions:
                    debug_print(f"[CLEANUP] [SessionManager] Cleaned up {len(expired_sessions)} expired sessions")
                
                # Run cleanup every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                debug_print(f"[ERROR] [SessionManager] Cleanup error: {e}")
                await asyncio.sleep(60)
    
    def generate_session_id(self) -> str:
        """Generate new session ID"""
        session_id = str(uuid.uuid4())
        debug_print(f"[NEW] [SessionManager] Generated new session: {session_id}")
        return session_id
    
    def get_session_cache(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get extended cache for session"""
        if session_id not in self.session_cache:
            return None
        
        session_data = self.session_cache[session_id]
        current_time = time.time()
        
        # Check if session expired
        if current_time - session_data.get("last_seen", 0) > self.ttl_seconds:
            del self.session_cache[session_id]
            debug_print(f"[TIME] [SessionManager] Session expired: {session_id}")
            return None
        
        # Update last seen
        session_data["last_seen"] = current_time
        debug_print(f"[OK] [SessionManager] Retrieved cache for session: {session_id}")
        return session_data.get("extended_cache", {})
    
    def update_session_cache(self, session_id: str, extended_cache: Dict[str, Any]):
        """Update extended cache for session"""
        current_time = time.time()
        
        self.session_cache[session_id] = {
            "extended_cache": extended_cache,
            "last_seen": current_time,
            "created_at": self.session_cache.get(session_id, {}).get("created_at", current_time)
        }
        
        debug_print(f"[CACHE] [SessionManager] Updated cache for session: {session_id}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session manager statistics"""
        current_time = time.time()
        active_sessions = 0
        
        for session_data in self.session_cache.values():
            if current_time - session_data.get("last_seen", 0) <= self.ttl_seconds:
                active_sessions += 1
        
        return {
            "total_sessions": len(self.session_cache),
            "active_sessions": active_sessions,
            "ttl_minutes": self.ttl_minutes
        }
    
    def clear_session(self, session_id: str) -> bool:
        """Clear specific session"""
        if session_id in self.session_cache:
            del self.session_cache[session_id]
            debug_print(f"[CLEANUP] [SessionManager] Cleared session: {session_id}")
            return True
        return False
    
    def clear_all_sessions(self):
        """Clear all sessions"""
        count = len(self.session_cache)
        self.session_cache.clear()
        debug_print(f"[CLEANUP] [SessionManager] Cleared all {count} sessions")
    
    def manual_cleanup(self):
        """Manual cleanup for environments without event loop"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.session_cache.items():
            if current_time - session_data.get("last_seen", 0) > self.ttl_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.session_cache[session_id]
            debug_print(f"[CLEANUP] [SessionManager] Expired session: {session_id}")
        
        if expired_sessions:
            debug_print(f"[CLEANUP] [SessionManager] Manually cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)

# Global session manager instance
session_manager = SessionManager(ttl_minutes=10)

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    return session_manager 