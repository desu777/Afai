"""
Session Management Endpoints
Session-related endpoints extracted from server.py
"""
from fastapi import HTTPException, Request

def setup_session_endpoints(app, tier2_rate_limit):
    """Setup session endpoints on FastAPI app"""
    
    @app.get("/session/new")
    @tier2_rate_limit()
    async def create_new_session(request: Request):
        """Create a new session and return session ID"""
        from session_manager import get_session_manager
        
        session_manager = get_session_manager()
        session_id = session_manager.generate_session_id()
        
        return {
            "session_id": session_id,
            "status": "created",
            "ttl_minutes": session_manager.ttl_minutes
        }

    @app.get("/session/{session_id}/stats")
    @tier2_rate_limit()
    async def get_session_stats(session_id: str, request: Request):
        """Get session statistics and cache info"""
        from session_manager import get_session_manager
        
        session_manager = get_session_manager()
        extended_cache = session_manager.get_session_cache(session_id)
        
        if not extended_cache:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        return {
            "session_id": session_id,
            "cache_sections": len(extended_cache),
            "metadata_count": len(extended_cache.get("metadata", [])),
            "responses_count": len(extended_cache.get("model_responses", [])),
            "context_fields": len(extended_cache.get("conversation_context", {})),
            "timestamp": extended_cache.get("timestamp")
        }

    @app.delete("/session/{session_id}")
    @tier2_rate_limit()
    async def clear_session(session_id: str, request: Request):
        """Clear specific session cache"""
        from session_manager import get_session_manager
        
        session_manager = get_session_manager()
        success = session_manager.clear_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"session_id": session_id, "status": "cleared"}

    @app.get("/sessions/stats")
    @tier2_rate_limit()
    async def get_all_sessions_stats(request: Request):
        """Get global session manager statistics"""
        from session_manager import get_session_manager
        
        session_manager = get_session_manager()
        stats = session_manager.get_session_stats()
        
        return stats