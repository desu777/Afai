"""
Aquaforest RAG System - Refactored FastAPI Server
FastAPI server for serving the RAG agent to frontend applications with analytics
Port: 2103
"""
from typing import Dict, List, Optional
from fastapi import Request
from pydantic import BaseModel

# Import core modules
from core import create_app, run_server

# Import endpoint modules
from endpoints import (
    setup_chat_endpoints,
    setup_session_endpoints,
    setup_feedback_endpoints,
    setup_analytics_endpoints,
    setup_export_endpoints,
    setup_debug_endpoints,
    setup_security_endpoints
)

# Import security middleware
from security_middleware import (
    tier1_rate_limit, tier2_rate_limit, tier3_rate_limit,
    vision_rate_limit, csv_export_rate_limit, global_rate_limit
)

# Import analytics
from analytics import WorkflowAnalytics

# Import main assistant
from main import AquaforestAssistant

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict[str, str]] = []
    debug: bool = False
    image_url: Optional[str] = None  # URL do zdjęcia dla analizy vision
    session_id: Optional[str] = None  # Session ID for cache management
    access_level: Optional[str] = None  # Access level: "test", "admin", "support"

class ChatResponse(BaseModel):
    response: str
    success: bool = True
    error: Optional[str] = None
    execution_time: Optional[float] = None
    session_id: Optional[str] = None  # Session ID returned to frontend

class FeedbackRequest(BaseModel):
    message_id: Optional[int] = None
    rating: Optional[int] = None  # 1-5 stars
    comment: str  # Required - this is what user actually sends
    user_type: str = "test"  # "test" or "admin"

class AnalyticsQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 100

# Create FastAPI app
app = create_app()

# Global analytics instance for non-streaming requests (fallback)
global_analytics = WorkflowAnalytics()

# Initialize the assistant without analytics (will be set per request)
assistant = AquaforestAssistant(analytics_instance=None)

# Setup all endpoints
setup_chat_endpoints(app, tier1_rate_limit, ChatRequest, ChatResponse)
setup_session_endpoints(app, tier2_rate_limit)
setup_feedback_endpoints(app, tier3_rate_limit, FeedbackRequest)
setup_analytics_endpoints(app, tier2_rate_limit, AnalyticsQuery)
setup_export_endpoints(app, csv_export_rate_limit)
setup_debug_endpoints(app, tier3_rate_limit, global_rate_limit, vision_rate_limit, ChatRequest)
setup_security_endpoints(app, global_rate_limit)

if __name__ == "__main__":
    run_server()