"""
Aquaforest RAG System - FastAPI Server with SQLite Integration and CSV Export
FastAPI server for serving the RAG agent to frontend applications with analytics
Port: 2103
"""
import asyncio
import time
import sqlite3
import json
import csv
import io
import threading
import queue
from datetime import datetime
from typing import Dict, List, Optional, Any, Generator
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import our existing modules using the same variable names as config.py
from config import debug_print, TEST_ENV, CORS_ORIGINS
from models import ConversationState
from main import AquaforestAssistant
import messenger_server

# Import security middleware
from security_middleware import (
    setup_security_middleware, 
    tier1_rate_limit, tier2_rate_limit, tier3_rate_limit,
    vision_rate_limit, csv_export_rate_limit, global_rate_limit,
    security_headers_middleware, get_rate_limit_status
)

# Database configuration
DB_PATH = "aquaforest_analytics.db"

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict[str, str]] = []
    debug: bool = False
    image_url: Optional[str] = None  # 🆕 URL do zdjęcia dla analizy vision
    session_id: Optional[str] = None  # 🆕 Session ID for cache management

class ChatResponse(BaseModel):
    response: str
    success: bool = True
    error: Optional[str] = None
    execution_time: Optional[float] = None
    session_id: Optional[str] = None  # 🆕 Session ID returned to frontend

class FeedbackRequest(BaseModel):
    message_id: Optional[int] = None
    rating: Optional[int] = None  # 1-5 stars
    comment: str  # Required - this is what user actually sends
    user_type: str = "test"  # "test" or "admin"

class AnalyticsQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 100

# Initialize FastAPI app
app = FastAPI(
    title="Aquaforest RAG API",
    description="AI Assistant API for Aquaforest products and solutions with analytics",
    version="2.2.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Setup security middleware and rate limiting
setup_security_middleware(app)

# Add security headers middleware
app.middleware("http")(security_headers_middleware)

# Database management
@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

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
        
        # 🆕 Create messenger_history table for Facebook Messenger conversations
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

# Initialize database on startup
init_database()

# 🆕 MESSENGER HISTORY MANAGEMENT FUNCTIONS
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
                debug_print(f"📚 [Messenger] Loaded {len(chat_history)} messages for context for user {user_id}")
                return chat_history
            else:
                debug_print(f"📭 [Messenger] No chat history found for user {user_id}")
                return []
                
    except Exception as e:
        debug_print(f"❌ [Messenger] Error loading chat history for {user_id}: {e}")
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
            debug_print(f"💾 [Messenger] Saved {role} message for user {user_id}")
            
    except Exception as e:
        debug_print(f"❌ [Messenger] Error saving message for {user_id}: {e}")

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
                debug_print(f"🧹 [Messenger] Cleaned up {deleted_count} old messages (older than {days_to_keep} days)")
                
    except Exception as e:
        debug_print(f"❌ [Messenger] Error cleaning up old messages: {e}")

# Enhanced analytics capture class with streaming support
class WorkflowAnalytics:
    def __init__(self):
        self.reset()
        self.streaming_callback = None
    
    def reset(self):
        self.data = {
            "user_query": "",
            "node_timings": {},
            "workflow_data": {}
        }
        self.start_time = time.time()
        self.current_node = None
    
    def set_streaming_callback(self, callback):
        """Set callback for streaming workflow updates"""
        self.streaming_callback = callback
    
    def capture_node_timing(self, node_name: str, duration: float):
        # Zabezpieczenie przed błędem gdy node_timings jest stringiem zamiast słownikiem
        if isinstance(self.data["node_timings"], str):
            try:
                self.data["node_timings"] = json.loads(self.data["node_timings"])
            except:
                self.data["node_timings"] = {}
        elif not isinstance(self.data["node_timings"], dict):
            self.data["node_timings"] = {}
        
        self.data["node_timings"][node_name] = duration
    
    def capture_node_start(self, node_name: str, message: str = ""):
        """Capture when a node starts execution"""
        self.current_node = node_name
        elapsed_time = time.time() - self.start_time
        
        if not message:
            message = self._get_node_message(node_name)
        
        # 🔍 DEBUG: Check streaming callback
        if TEST_ENV:
            debug_print(f"🔍 [DEBUG capture_node_start] node_name='{node_name}', message='{message}'", "🔍")
            debug_print(f"🔍 [DEBUG capture_node_start] self.streaming_callback={self.streaming_callback}", "🔍")
        
        if self.streaming_callback:
            update_data = {
                "node": node_name,
                "status": "processing",
                "message": message,
                "elapsed_time": elapsed_time
            }
            if TEST_ENV:
                debug_print(f"🚀 [DEBUG capture_node_start] Calling streaming_callback with: {update_data}", "🚀")
            self.streaming_callback(update_data)
        else:
            if TEST_ENV:
                debug_print(f"⚠️ [DEBUG capture_node_start] streaming_callback is None!", "⚠️")
    
    def capture_node_complete(self, node_name: str, message: str = ""):
        """Capture when a node completes execution"""
        elapsed_time = time.time() - self.start_time
        
        if not message:
            message = f"✅ {self._get_node_message(node_name)} - Complete"
        
        if self.streaming_callback:
            self.streaming_callback({
                "node": node_name,
                "status": "complete",
                "message": message,
                "elapsed_time": elapsed_time
            })
    
    def capture_workflow_complete(self, final_response: str):
        """Capture when entire workflow completes"""
        elapsed_time = time.time() - self.start_time
        
        if self.streaming_callback:
            self.streaming_callback({
                "node": "complete",
                "status": "complete", 
                "message": final_response,
                "elapsed_time": elapsed_time
            })
    
    def _get_node_message(self, node_name: str) -> str:
        """Get human-readable message for node execution"""
        messages = {
            "detect_intent_and_language": "🔍 Understanding your question...",
            "load_product_names": "📋 Loading product database...",
            "business_reasoner": "🧠 Analyzing your needs...",
            "optimize_product_query": "🔎 Optimizing search...",
            "search_products_k20": "🗃️ Searching product catalog...",
            "format_final_response": "✍️ Generating response...",

            "handle_follow_up": "🔄 Processing follow-up...",
            "follow_up_router": "🔄 Analyzing context..."
        }
        return messages.get(node_name, f"⚙️ Processing {node_name}...")
    
    def capture_state_data(self, state: ConversationState):
        """Capture comprehensive workflow data"""
        # Basic query data
        self.data["user_query"] = state.get("user_query", "")
        self.data["detected_language"] = state.get("detected_language", "")
        
        # Intent detection
        self.data["intent_detector_decision"] = str(state.get("intent", ""))
        
        # Extract intent confidence from business analysis or set default
        business_analysis = state.get("business_analysis", {})
        self.data["intent_confidence"] = 0.8  # Default value, as it's not explicitly stored
        
        # Business reasoning
        if business_analysis:
            self.data["business_reasoner_decision"] = business_analysis.get("business_interpretation", "")
            self.data["business_corrections"] = business_analysis.get("product_name_corrections", "")
        
        # Query optimization
        optimized_queries = state.get("optimized_queries", [])
        self.data["query_optimizer_queries"] = json.dumps(optimized_queries) if optimized_queries else ""
        
        # Pinecone search results
        search_results = state.get("search_results", [])
        self.data["pinecone_results_count"] = len(search_results)
        
        # Top 3 results for analysis
        top_results = []
        for result in search_results[:3]:
            metadata = result.get('metadata', {})
            top_results.append({
                "product_name": metadata.get('product_name', ''),
                "score": result.get('score', 0),
                "domain": metadata.get('domain', '')
            })
        self.data["pinecone_top_results"] = json.dumps(top_results)
        
        # Filter results (if any filtering was done)
        self.data["filter_decision"] = state.get("filter_reasoning", "Direct routing - no filtering")
        self.data["filtered_results_count"] = len(search_results)  # Same as pinecone since no filtering
        
        # Final response
        self.data["final_response"] = state.get("final_response", "")
        
        # Escalation
        self.data["escalated"] = state.get("escalate", False)
        
        # Node timings - merge with existing timings collected during workflow
        state_node_timings = state.get("node_timings", {})
        if isinstance(self.data["node_timings"], dict):
            self.data["node_timings"].update(state_node_timings)
        else:
            self.data["node_timings"] = state_node_timings
        
        # Total execution time
        self.data["total_execution_time"] = time.time() - self.start_time

# Global analytics instance for non-streaming requests (fallback)
global_analytics = WorkflowAnalytics()

# Initialize the assistant without analytics (will be set per request)
assistant = AquaforestAssistant(analytics_instance=None)

# 🚀 NEW: Streaming chat endpoint with Server-Sent Events
@app.post("/chat/stream")
@tier1_rate_limit()
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint that provides real-time workflow updates via Server-Sent Events
    """
    def generate_stream():
        # 🆕 Handle session management using SessionManager
        from session_manager import get_session_manager
        session_manager = get_session_manager()
        
        session_id = request.session_id
        if not session_id:
            # Generate new session for first-time users
            session_id = session_manager.generate_session_id()
            debug_print(f"🆕 [StreamServer] Generated new session: {session_id}")
        else:
            debug_print(f"🔄 [StreamServer] Using existing session: {session_id}")
        
        session_analytics = WorkflowAnalytics()
        session_analytics.reset()
        
        if TEST_ENV:
            debug_print(f"🆔 [StreamServer] Starting session {session_id}: {request.message[:30]}...", "🆔")
        
        # 🚀 Real-time streaming with threading
        update_queue = queue.Queue()
        workflow_finished = threading.Event()
        
        def streaming_callback(update):
            if TEST_ENV:
                debug_print(f"📡 [StreamServer] Adding update to queue: {update}", "🔊")
            # Add to queue for immediate streaming
            update_queue.put(update)
        
        def run_workflow():
            """Run workflow in separate thread"""
            try:
                debug_print(f"📨 [StreamServer] Session {session_id} - Received streaming chat request: {request.message[:50]}...", "🔍")
                
                # Create conversation state with session analytics and session management
                conversation_state = {
                    "user_query": request.message,
                    "detected_language": "en",
                    "intent": "other",
                    "product_names": [],
                    "original_query": "",
                    "optimized_queries": [],
                    "search_results": [],
                    "iteration": 0,
                    "final_response": "",
                    "escalate": False,
                    "domain_filter": None,
                    "chat_history": request.chat_history,
                    "context_cache": [],
                    "session_id": session_id,  # 🆕 Session ID for cache management
                    "extended_cache": None,    # 🆕 Will be populated during workflow
                    "image_url": request.image_url,  # 🆕 Vision analysis
                    "image_analysis": None,  # 🆕 Will be filled by intent detector
                    "node_timings": {},
                    "routing_decisions": [],
                    "total_execution_time": 0.0,
                    "analytics_instance": session_analytics
                }
                
                debug_print(f"🔄 [StreamServer] Processing with streaming workflow (debug={request.debug})", "⚙️")
                
                # 🆕 Create dedicated assistant instance for this session
                session_assistant = AquaforestAssistant(analytics_instance=session_analytics)
                
                # Process with analytics capture and streaming
                result_state = session_assistant.process_query_sync(conversation_state, debug=request.debug)
                
                # 🆕 Save extended cache to session if available
                if result_state.get("extended_cache"):
                    session_manager.update_session_cache(session_id, result_state["extended_cache"])
                    debug_print(f"💾 [StreamServer] Updated session cache for {session_id}")
                
                # Send final completion update
                session_analytics.capture_workflow_complete(result_state.get("final_response", ""))
                
                # Capture analytics from final state
                session_analytics.capture_state_data(result_state)
                
                # Save analytics to database
                save_analytics_to_db(session_analytics)
                
                debug_print(f"✅ [StreamServer] Session {session_id} - Streaming response completed", "⏱️")
                
            except Exception as e:
                error_msg = f"An error occurred while processing your request: {str(e)}"
                debug_print(f"❌ [StreamServer] Error: {error_msg}", "🚨")
                
                # Send error update
                error_response = "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
                error_update = {
                    "node": "error",
                    "status": "error",
                    "message": error_response if not TEST_ENV else f"Debug Error: {error_msg}",
                    "elapsed_time": time.time() - session_analytics.start_time
                }
                update_queue.put(error_update)
            finally:
                # Signal that workflow is finished
                workflow_finished.set()
        
        # Set up streaming callback for this session
        session_analytics.set_streaming_callback(streaming_callback)
        
        # Start workflow in separate thread
        workflow_thread = threading.Thread(target=run_workflow)
        workflow_thread.start()
        
        # Stream updates in real-time
        sent_count = 0
        while True:
            try:
                # Try to get update from queue (with timeout)
                update = update_queue.get(timeout=1.0)
                sent_count += 1
                
                if TEST_ENV:
                    debug_print(f"📤 [StreamServer] Streaming update #{sent_count}: {update['node']}", "📤")
                
                # 🆕 Handle very long messages
                json_data = json.dumps(update)
                if len(json_data) > 8192 and TEST_ENV:
                    debug_print(f"⚠️ [StreamServer] Large final message ({len(json_data)} bytes)", "⚠️")
                
                yield f"data: {json_data}\n\n"
                
            except queue.Empty:
                # Check if workflow is finished
                if workflow_finished.is_set():
                    # Try to get any remaining updates
                    try:
                        while True:
                            update = update_queue.get_nowait()
                            sent_count += 1
                            if TEST_ENV:
                                debug_print(f"📤 [StreamServer] Final update #{sent_count}: {update['node']}", "📤")
                            
                            # 🆕 Handle very long messages
                            json_data = json.dumps(update)
                            if len(json_data) > 8192 and TEST_ENV:
                                debug_print(f"⚠️ [StreamServer] Large final message ({len(json_data)} bytes)", "⚠️")
                            
                            yield f"data: {json_data}\n\n"
                    except queue.Empty:
                        break
                    break
        
        # Wait for workflow thread to complete
        workflow_thread.join()
        
        if TEST_ENV:
            debug_print(f"🏁 [StreamServer] Streaming completed. Total updates sent: {sent_count}", "🏁")
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

# Modified chat endpoint with analytics
@app.post("/chat", response_model=ChatResponse)
@tier1_rate_limit()
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user messages and returns AI responses
    """
    global_analytics.reset()
    start_time = time.time()
    
    try:
        debug_print(f"📨 [Server] Received chat request: {request.message[:50]}...", "🔍")
        
        # 🆕 Handle session management
        from session_manager import get_session_manager
        session_manager = get_session_manager()
        
        session_id = request.session_id
        if not session_id:
            # Generate new session for first-time users
            session_id = session_manager.generate_session_id()
            debug_print(f"🆕 [Server] Generated new session: {session_id}")
        else:
            debug_print(f"🔄 [Server] Using existing session: {session_id}")
        
        # Create conversation state with global analytics and session
        conversation_state = {
            "user_query": request.message,
            "detected_language": "en",
            "intent": "other",
            "product_names": [],
            "original_query": "",
            "optimized_queries": [],
            "search_results": [],
            "iteration": 0,
            "final_response": "",
            "escalate": False,
            "domain_filter": None,
            "chat_history": request.chat_history,
            "context_cache": [],
            "session_id": session_id,  # 🆕 Session ID for cache management
            "extended_cache": None,    # 🆕 Will be populated during workflow
            "image_url": request.image_url,  # 🆕 Vision analysis
            "image_analysis": None,  # 🆕 Will be filled by intent detector
            "node_timings": {},
            "routing_decisions": [],
            "total_execution_time": 0.0,
            "analytics_instance": global_analytics
        }
        
        debug_print(f"🔄 [Server] Processing with workflow (debug={request.debug})", "⚙️")
        
        # Create assistant instance with global analytics for non-streaming requests
        non_streaming_assistant = AquaforestAssistant(analytics_instance=global_analytics)
        
        # Process with analytics capture
        result_state = non_streaming_assistant.process_query_sync(conversation_state, debug=request.debug)
        
        # Capture analytics from final state
        global_analytics.capture_state_data(result_state)
        
        # 🆕 Save extended cache to session if available
        if result_state.get("extended_cache"):
            session_manager.update_session_cache(session_id, result_state["extended_cache"])
            debug_print(f"💾 [Server] Updated session cache for {session_id}")
        
        # Save analytics to database
        save_analytics_to_db(global_analytics)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        debug_print(f"✅ [Server] Response ready in {execution_time:.3f}s", "⏱️")
        
        return ChatResponse(
            response=result_state.get("final_response", "Sorry, I couldn't process your request."),
            success=True,
            execution_time=execution_time,
            session_id=session_id  # 🆕 Return session_id to frontend
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"An error occurred while processing your request: {str(e)}"
        
        debug_print(f"❌ [Server] Error: {error_msg}", "🚨")
        
        if TEST_ENV:
            return ChatResponse(
                response=f"Debug Error: {error_msg}",
                success=False,
                error=str(e),
                execution_time=execution_time,
                session_id=session_id if 'session_id' in locals() else None
            )
        else:
            return ChatResponse(
                response="I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu",
                success=False,
                error="Internal server error",
                execution_time=execution_time,
                session_id=session_id if 'session_id' in locals() else None
            )

def save_analytics_to_db(analytics_instance=None):
    """Save analytics data to SQLite database"""
    # Use provided analytics instance or fallback to global
    analytics_obj = analytics_instance or global_analytics
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analyze (
                    user_query, detected_language, intent_detector_decision,
                    intent_confidence, business_reasoner_decision, business_corrections,
                    query_optimizer_queries, pinecone_results_count, pinecone_top_results,
                    filter_decision, filtered_results_count,
                    final_response, total_execution_time, node_timings, escalated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analytics_obj.data.get("user_query", ""),
                analytics_obj.data.get("detected_language", ""),
                analytics_obj.data.get("intent_detector_decision", ""),
                analytics_obj.data.get("intent_confidence", 0.0),
                analytics_obj.data.get("business_reasoner_decision", ""),
                analytics_obj.data.get("business_corrections", ""),
                analytics_obj.data.get("query_optimizer_queries", ""),
                analytics_obj.data.get("pinecone_results_count", 0),
                analytics_obj.data.get("pinecone_top_results", ""),
                analytics_obj.data.get("filter_decision", ""),
                analytics_obj.data.get("filtered_results_count", 0),
                analytics_obj.data.get("final_response", ""),
                analytics_obj.data.get("total_execution_time", 0.0),
                json.dumps(analytics_obj.data.get("node_timings", {})) if isinstance(analytics_obj.data.get("node_timings"), dict) else analytics_obj.data.get("node_timings", ""),
                analytics_obj.data.get("escalated", False)
            ))
            
            conn.commit()
            debug_print("✅ Analytics saved to database")
            
    except Exception as e:
        debug_print(f"❌ Error saving analytics: {e}")

# Feedback endpoint
# 🆕 SESSION MANAGEMENT ENDPOINTS
@app.get("/session/new")
@tier2_rate_limit()
async def create_new_session():
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
async def get_session_stats(session_id: str):
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
async def clear_session(session_id: str):
    """Clear specific session cache"""
    from session_manager import get_session_manager
    
    session_manager = get_session_manager()
    success = session_manager.clear_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"session_id": session_id, "status": "cleared"}

@app.get("/sessions/stats")
@tier2_rate_limit()
async def get_all_sessions_stats():
    """Get global session manager statistics"""
    from session_manager import get_session_manager
    
    session_manager = get_session_manager()
    stats = session_manager.get_session_stats()
    
    return stats

@app.post("/feedback")
@tier3_rate_limit()
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (
                    message_id, rating, comment, user_type
                ) VALUES (?, ?, ?, ?)
            """, (
                feedback.message_id,
                feedback.rating,
                feedback.comment,
                feedback.user_type
            ))
            conn.commit()
            feedback_id = cursor.lastrowid
            
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Thank you for your feedback!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.post("/analytics/query")
@tier2_rate_limit()
async def get_analytics(query: AnalyticsQuery):
    """Get analytics data with optional filtering"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            sql = "SELECT * FROM analyze WHERE 1=1"
            params = []
            
            if query.start_date:
                sql += " AND created_at >= ?"
                params.append(query.start_date)
            
            if query.end_date:
                sql += " AND created_at <= ?"
                params.append(query.end_date)
            
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(query.limit)
            
            cursor.execute(sql, params)
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                
                # Parse JSON fields with error handling
                try:
                    result["query_optimizer_queries"] = json.loads(result.get("query_optimizer_queries") or "[]")
                except (json.JSONDecodeError, TypeError):
                    result["query_optimizer_queries"] = []
                    debug_print(f"⚠️ [Analytics] Failed to parse query_optimizer_queries for record {result.get('id')}")
                
                try:
                    result["pinecone_top_results"] = json.loads(result.get("pinecone_top_results") or "[]")
                except (json.JSONDecodeError, TypeError):
                    result["pinecone_top_results"] = []
                    debug_print(f"⚠️ [Analytics] Failed to parse pinecone_top_results for record {result.get('id')}")
                
                try:
                    result["node_timings"] = json.loads(result.get("node_timings") or "{}")
                except (json.JSONDecodeError, TypeError):
                    result["node_timings"] = {}
                    debug_print(f"⚠️ [Analytics] Failed to parse node_timings for record {result.get('id')}")
                
                # Add missing fields required by frontend types
                result["confidence_score"] = result.get("intent_confidence", 0)
                result["confidence_reasoning"] = "Based on intent confidence score"
                
                results.append(result)
            
            return {
                "success": True,
                "count": len(results),
                "data": results
            }
    except Exception as e:
        debug_print(f"❌ [Analytics] Error in get_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/summary")
@tier2_rate_limit()
async def get_analytics_summary():
    """Get analytics summary statistics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total queries
            cursor.execute("SELECT COUNT(*) as total FROM analyze")
            total_queries = cursor.fetchone()["total"]
            
            # Average execution time
            cursor.execute("SELECT AVG(total_execution_time) as avg_time FROM analyze")
            avg_time = cursor.fetchone()["avg_time"] or 0
            
            # Intent distribution
            cursor.execute("""
                SELECT intent_detector_decision, COUNT(*) as count
                FROM analyze 
                WHERE intent_detector_decision != ''
                GROUP BY intent_detector_decision 
                ORDER BY count DESC
            """)
            intent_dist = {row["intent_detector_decision"]: row["count"] for row in cursor.fetchall()}
            
            # Language distribution
            cursor.execute("""
                SELECT detected_language, COUNT(*) as count
                FROM analyze 
                WHERE detected_language != ''
                GROUP BY detected_language 
                ORDER BY count DESC
            """)
            language_dist = {row["detected_language"]: row["count"] for row in cursor.fetchall()}
            
            # Confidence distribution
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN intent_confidence >= 0.8 THEN 1 ELSE 0 END) as high_confidence,
                    SUM(CASE WHEN intent_confidence >= 0.5 AND intent_confidence < 0.8 THEN 1 ELSE 0 END) as medium_confidence,
                    SUM(CASE WHEN intent_confidence < 0.5 THEN 1 ELSE 0 END) as low_confidence
                FROM analyze
                WHERE intent_confidence IS NOT NULL
            """)
            confidence_stats = cursor.fetchone()
            
            # Escalation rate
            cursor.execute("SELECT SUM(CASE WHEN escalated THEN 1 ELSE 0 END) as escalated FROM analyze")
            escalated_count = cursor.fetchone()["escalated"] or 0
            escalation_rate = (escalated_count / total_queries * 100) if total_queries > 0 else 0
            
            return {
                "success": True,
                "summary": {
                    "total_queries": total_queries,
                    "average_execution_time": round(avg_time, 3),
                    "confidence_distribution": {
                        "high_confidence": confidence_stats["high_confidence"] or 0,
                        "medium_confidence": confidence_stats["medium_confidence"] or 0,
                        "low_confidence": confidence_stats["low_confidence"] or 0
                    },
                    "intent_distribution": intent_dist,
                    "language_distribution": language_dist,
                    "escalation_rate": round(escalation_rate, 1)
                }
            }
    except Exception as e:
        debug_print(f"❌ [Analytics] Error in get_analytics_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/summary")
@tier3_rate_limit()
async def get_feedback_summary():
    """Get feedback summary statistics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total feedback
            cursor.execute("SELECT COUNT(*) as total FROM feedback")
            total_feedback = cursor.fetchone()["total"]
            
            # Average rating
            cursor.execute("SELECT AVG(rating) as avg_rating FROM feedback")
            avg_rating = cursor.fetchone()["avg_rating"] or 0
            
            # Rating distribution
            cursor.execute("""
                SELECT rating, COUNT(*) as count
                FROM feedback
                GROUP BY rating
            """)
            rating_dist = {row["rating"]: row["count"] for row in cursor.fetchall()}
            
            # Recent feedback
            cursor.execute("""
                SELECT * FROM feedback
                ORDER BY created_at DESC
                LIMIT 10
            """)
            recent_feedback = [dict(row) for row in cursor.fetchall()]
            
            return {
                "success": True,
                "summary": {
                    "total_feedback": total_feedback,
                    "average_rating": round(avg_rating, 2),
                    "rating_distribution": rating_dist,
                    "recent_feedback": recent_feedback
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CSV Export endpoints
@app.get("/analytics/export/csv")
@csv_export_rate_limit()
async def export_analytics_csv(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Export analytics data as CSV"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            sql = "SELECT * FROM analyze WHERE 1=1"
            params = []
            
            if start_date:
                sql += " AND created_at >= ?"
                params.append(start_date)
            
            if end_date:
                sql += " AND created_at <= ?"
                params.append(end_date)
            
            sql += " ORDER BY created_at DESC"
            
            cursor.execute(sql, params)
            
            # Create CSV in memory with proper formatting for Excel
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            
            # CSV headers
            headers = [
                "ID", "User Query", "Detected Language", "Intent Decision", "Intent Confidence",
                "Business Decision", "Business Corrections", "Query Optimizer", 
                "Pinecone Results", "Top Results", "Filter Decision", 
                "Filtered Results Count", "Final Response",
                "Total Time", "Node Timings", "Escalated", "Created At"
            ]
            
            def clean_text(text):
                """Clean text for CSV export"""
                if not text:
                    return ""
                # Remove newlines and extra whitespace
                cleaned = str(text).replace('\n', ' ').replace('\r', ' ')
                # Limit length to prevent huge CSV cells
                return cleaned[:500] + "..." if len(cleaned) > 500 else cleaned
            
            # Write data
            for row in cursor.fetchall():
                writer.writerow([
                    row["id"],
                    clean_text(row["user_query"]),
                    row["detected_language"] or "",
                    row["intent_detector_decision"] or "",
                    row["intent_confidence"] or 0,
                    clean_text(row["business_reasoner_decision"]),
                    clean_text(row["business_corrections"]),
                    clean_text(row["query_optimizer_queries"]),
                    row["pinecone_results_count"] or 0,
                    clean_text(row["pinecone_top_results"]),
                    clean_text(row["filter_decision"]),
                    row["filtered_results_count"] or 0,
                    clean_text(row["final_response"]),
                    row["total_execution_time"] or 0,
                    clean_text(row["node_timings"]),
                    "Yes" if row["escalated"] else "No",
                    row["created_at"]
                ])
            
            # Create response
            output.seek(0)
            filename = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),  # UTF-8 with BOM for Excel
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/export/csv")
@csv_export_rate_limit()
async def export_feedback_csv(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Export feedback data as CSV"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            sql = "SELECT * FROM feedback WHERE 1=1"
            params = []
            
            if start_date:
                sql += " AND created_at >= ?"
                params.append(start_date)
            
            if end_date:
                sql += " AND created_at <= ?"
                params.append(end_date)
            
            sql += " ORDER BY created_at DESC"
            
            cursor.execute(sql, params)
            
            # Create CSV in memory with proper formatting for Excel
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            
            # Write headers - complete feedback export
            headers = [
                "Feedback ID", "Message ID", "Rating (1-5)", "Comment", "User Type", "Created At"
            ]
            writer.writerow(headers)
            
            # Helper function to clean text for CSV
            def clean_text(text):
                if not text:
                    return ""
                # Replace problematic characters and normalize newlines
                return str(text).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
            
            # Write data - complete feedback data
            for row in cursor.fetchall():
                writer.writerow([
                    row["id"],
                    row["message_id"] or "",
                    row["rating"] or "",
                    clean_text(row["comment"]),
                    row["user_type"] or "test",
                    row["created_at"] or ""
                ])
            
            # Create response
            output.seek(0)
            filename = f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),  # UTF-8 with BOM for Excel
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Original endpoints remain unchanged
@app.get("/")
@tier3_rate_limit()
async def root():
    """Health check endpoint"""
    return {
        "message": "🐠 Aquaforest RAG API is running",
        "version": "2.2.0",
        "status": "healthy",
        "analytics_enabled": True
    }

@app.get("/health")
@tier3_rate_limit()
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "debug_mode": TEST_ENV,
        "timestamp": time.time(),
        "database_status": "connected"
    }

@app.get("/debug/toggle")
@global_rate_limit()
async def toggle_debug():
    """Toggle debug mode for testing purposes"""
    import os
    import config
    
    current_debug = TEST_ENV
    new_debug = not current_debug
    
    os.environ["TEST_ENV"] = "true" if new_debug else "false"
    config.TEST_ENV = new_debug
    
    return {
        "debug_mode": new_debug,
        "message": f"Debug mode {'enabled' if new_debug else 'disabled'}"
    }

@app.get("/debug/messenger-history/{user_id}")
@global_rate_limit()
async def get_messenger_history_debug(user_id: str, limit: int = 10):
    """Debug endpoint to view messenger chat history"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_role, message_content, created_at 
                FROM messenger_history 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            messages = cursor.fetchall()
            
            history = []
            for row in messages:
                history.append({
                    "role": row["message_role"],
                    "content": row["message_content"],
                    "timestamp": row["created_at"]
                })
            
            return {
                "user_id": user_id,
                "message_count": len(history),
                "messages": history
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@app.post("/debug/test-markdown-conversion")
@global_rate_limit()
async def test_markdown_conversion(request: dict):
    """Test endpoint for Markdown to Messenger text conversion"""
    try:
        from messenger_server import convert_markdown_to_messenger_text
        
        original_text = request.get("text", "")
        if not original_text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        converted_text = convert_markdown_to_messenger_text(original_text)
        
        return {
            "original_length": len(original_text),
            "converted_length": len(converted_text),
            "original_text": original_text,
            "converted_text": converted_text,
            "preview": converted_text[:500] + "..." if len(converted_text) > 500 else converted_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

# 🚀 FACEBOOK MESSENGER WEBHOOK ENDPOINTS

@app.get("/webhook")
async def webhook_verify_endpoint(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"), 
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Webhook verification endpoint for Facebook - delegates to messenger_server"""
    return await messenger_server.webhook_verify(hub_mode, hub_challenge, hub_verify_token)

@app.post("/webhook")
async def webhook_handler_endpoint(request: Request):
    """Main webhook handler for Facebook Messenger - delegates to messenger_server"""
    return await messenger_server.webhook_handler(
        request, assistant, 
        load_history_func=load_messenger_chat_history,
        save_message_func=save_messenger_message
    )

# 🆕 VISION ANALYSIS TEST ENDPOINT
@app.post("/debug/test-vision")
@vision_rate_limit()
async def test_vision_analysis(request: ChatRequest):
    """Test endpoint for vision analysis functionality"""
    
    if not request.image_url:
        raise HTTPException(status_code=400, detail="image_url is required for vision testing")
    
    try:
        debug_print(f"📸 [VisionTest] Testing vision analysis with: {request.image_url[:100]}...", "🧪")
        
        # Create test conversation state
        conversation_state = {
            "user_query": request.message,
            "detected_language": "en",
            "intent": "other",
            "product_names": [],
            "original_query": "",
            "optimized_queries": [],
            "search_results": [],
            "iteration": 0,
            "final_response": "",
            "escalate": False,
            "domain_filter": None,
            "chat_history": request.chat_history,
            "context_cache": [],
            "image_url": request.image_url,
            "image_analysis": None,
            "node_timings": {},
            "routing_decisions": [],
            "total_execution_time": 0.0,
            "analytics_instance": None
        }
        
        # Test just the intent detector with vision
        from intent_detector import IntentDetector
        detector = IntentDetector()
        
        # Analyze with vision
        result_state = detector.detect(conversation_state)
        
        return {
            "success": True,
            "original_query": request.message,
            "enhanced_query": result_state.get("user_query", ""),
            "image_analysis": result_state.get("image_analysis", ""),
            "detected_intent": result_state.get("intent", ""),
            "detected_language": result_state.get("detected_language", ""),
            "image_url": request.image_url
        }
        
    except Exception as e:
        debug_print(f"❌ [VisionTest] Error: {e}", "🚨")
        raise HTTPException(status_code=500, detail=f"Vision analysis error: {str(e)}")

# 🆕 VISION ANALYSIS EXAMPLES ENDPOINT
@app.get("/debug/vision-examples")
@global_rate_limit()
async def get_vision_examples():
    """Get example image URLs for testing vision analysis"""
    
    examples = [
        {
            "name": "Coral with algae problem",
            "url": "https://images.unsplash.com/photo-1583212292454-1fe6229603b7?w=800",
            "description": "Example coral with algae issues",
            "suggested_query": "Co to za problem z moimi koralami?"
        },
        {
            "name": "Aquarium with equipment",
            "url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800", 
            "description": "General aquarium setup",
            "suggested_query": "Jak ustawić mój akwarium?"
        },
        {
            "name": "Fish tank with plants",
            "url": "https://images.unsplash.com/photo-1520637836862-4d197d17c669?w=800",
            "description": "Freshwater aquarium with plants",
            "suggested_query": "Moje rośliny nie rosną dobrze"
        }
    ]
    
    return {
        "examples": examples,
        "instructions": "Use POST /debug/test-vision with image_url and message to test vision analysis"
    }

# 🔒 SECURITY STATUS ENDPOINT
@app.get("/security/status")
@global_rate_limit()
async def get_security_status():
    """Get current security and rate limiting configuration"""
    return get_rate_limit_status()

def run_server():
    """Run the FastAPI server"""
    print("\n" + "="*60)
    print("🐠 Starting Aquaforest RAG API Server with Analytics")
    print("="*60)
    print(f"📍 Port: 2103")
    print(f"📍 Debug Mode: {'ON' if TEST_ENV else 'OFF'}")
    print(f"📍 CORS Origins: {CORS_ORIGINS}")
    print(f"📊 Analytics Database: {DB_PATH}")
    
    # Clean up old messenger history on startup
    cleanup_old_messenger_history()
    
    print("="*60 + "\n")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=2103,
        reload=True,
        access_log=TEST_ENV
    )

if __name__ == "__main__":
    run_server()