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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import our existing modules using the same variable names as config.py
from config import debug_print, TEST_ENV, CORS_ORIGINS
from models import ConversationState
from main import AquaforestAssistant

# Database configuration
DB_PATH = "aquaforest_analytics.db"

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict[str, str]] = []
    debug: bool = False

class ChatResponse(BaseModel):
    response: str
    success: bool = True
    error: Optional[str] = None
    execution_time: Optional[float] = None

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
                confidence_score REAL,
                confidence_reasoning TEXT,
                final_response TEXT,
                total_execution_time REAL,
                node_timings TEXT,
                escalated BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Database initialized successfully")

# Initialize database on startup
init_database()

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
        """Get user-friendly message for each node"""
        messages = {
            "detect_intent_and_language": "🔍 Understanding your question...",
            "load_product_names": "📋 Loading product database...", 
            "business_reasoner": "🧠 Analyzing your needs...",
            "optimize_product_query": "🔎 Optimizing search...",
            "search_products_k20": "🗃️ Searching product catalog...",
            "evaluate_confidence": "✅ Validating results...",
            "format_final_response": "📝 Preparing response...",
            "handle_follow_up": "🔄 Processing follow-up...",
            "escalate_to_human": "🆘 Escalating to support...",
            "follow_up_router": "🤔 Analyzing context...",
            # Legacy names for compatibility
            "detect_intent": "🔍 Understanding your question...",
            "load_products": "📋 Loading product database...",
            "optimize_query": "🔎 Optimizing search...",
            "search_pinecone": "🗃️ Searching product catalog...",
            "format_response": "📝 Preparing response...",
            "escalate_support": "🆘 Escalating to support..."
        }
        return messages.get(node_name, f"Processing {node_name}...")
    
    def capture_state_data(self, state: ConversationState):
        """Extract analytics data from workflow state"""
        self.data["user_query"] = state.get("user_query", "")
        self.data["detected_language"] = state.get("detected_language", "")
        
        # Intent detection
        self.data["intent_detector_decision"] = str(state.get("intent", ""))
        
        # Extract intent confidence from business analysis or set default
        business_analysis = state.get("business_analysis", {})
        self.data["intent_confidence"] = 0.8  # Default value, as it's not explicitly stored
        
        # Business reasoner
        self.data["business_reasoner_decision"] = business_analysis.get("business_interpretation", "")
        self.data["business_corrections"] = business_analysis.get("product_name_corrections", "")
        
        # Query optimization
        self.data["query_optimizer_queries"] = json.dumps(state.get("optimized_queries", []))
        
        # Pinecone results
        search_results = state.get("search_results", [])
        self.data["pinecone_results_count"] = len(search_results)
        top_results = []
        for result in search_results[:3]:
            meta = result.get("metadata", {})
            top_results.append({
                "product": meta.get("product_name", ""),
                "score": result.get("score", 0)
            })
        self.data["pinecone_top_results"] = json.dumps(top_results)
        
        # Filtering
        self.data["filter_decision"] = state.get("filter_reasoning", "")
        self.data["filtered_results_count"] = len(search_results)  # After filtering
        
        # Confidence
        self.data["confidence_score"] = state.get("confidence", 0.0)
        self.data["confidence_reasoning"] = state.get("evaluation_reasoning", "")
        
        # Response
        self.data["final_response"] = state.get("final_response", "")
        self.data["escalated"] = state.get("escalate", False)
        
        # Total time
        self.data["total_execution_time"] = time.time() - self.start_time

# Global analytics instance
analytics = WorkflowAnalytics()

# Initialize the assistant
assistant = None  # Will be initialized after analytics is created

# Initialize the assistant with analytics support
assistant = AquaforestAssistant(analytics_instance=analytics)

# 🚀 NEW: Streaming chat endpoint with Server-Sent Events
@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint that provides real-time workflow updates via Server-Sent Events
    """
    def generate_stream():
        analytics.reset()
        
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
                debug_print(f"📨 [StreamServer] Received streaming chat request: {request.message[:50]}...", "🔍")
                
                # Create ConversationState from request
                conversation_state: ConversationState = {
                    "user_query": request.message,
                    "detected_language": "en",
                    "intent": "other",
                    "product_names": [],
                    "original_query": request.message,
                    "optimized_queries": [],
                    "search_results": [],
                    "confidence": 0.0,
                    "evaluation_reasoning": "",
                    "iteration": 0,
                    "final_response": "",
                    "escalate": False,
                    "domain_filter": None,
                    "chat_history": request.chat_history,
                    "context_cache": []
                }
                
                debug_print(f"🔄 [StreamServer] Processing with streaming workflow (debug={request.debug})", "⚙️")
                
                # Process with analytics capture and streaming
                result_state = assistant.process_query_sync(conversation_state, debug=request.debug)
                
                # Send final completion update
                analytics.capture_workflow_complete(result_state.get("final_response", ""))
                
                # Capture analytics from final state
                analytics.capture_state_data(result_state)
                
                # Save analytics to database
                save_analytics_to_db()
                
                debug_print(f"✅ [StreamServer] Streaming response completed", "⏱️")
                
            except Exception as e:
                error_msg = f"An error occurred while processing your request: {str(e)}"
                debug_print(f"❌ [StreamServer] Error: {error_msg}", "🚨")
                
                # Send error update
                error_response = "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
                error_update = {
                    "node": "error",
                    "status": "error",
                    "message": error_response if not TEST_ENV else f"Debug Error: {error_msg}",
                    "elapsed_time": time.time() - analytics.start_time
                }
                update_queue.put(error_update)
            finally:
                # Signal that workflow is finished
                workflow_finished.set()
        
        # Set up streaming callback
        analytics.set_streaming_callback(streaming_callback)
        
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
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user messages and returns AI responses
    """
    analytics.reset()
    start_time = time.time()
    
    try:
        debug_print(f"📨 [Server] Received chat request: {request.message[:50]}...", "🔍")
        
        # Create ConversationState from request
        conversation_state: ConversationState = {
            "user_query": request.message,
            "detected_language": "en",
            "intent": "other",
            "product_names": [],
            "original_query": request.message,
            "optimized_queries": [],
            "search_results": [],
            "confidence": 0.0,
            "evaluation_reasoning": "",
            "iteration": 0,
            "final_response": "",
            "escalate": False,
            "domain_filter": None,
            "chat_history": request.chat_history,
            "context_cache": []
        }
        
        debug_print(f"🔄 [Server] Processing with workflow (debug={request.debug})", "⚙️")
        
        # Process with analytics capture
        result_state = assistant.process_query_sync(conversation_state, debug=request.debug)
        
        # Capture analytics from final state
        analytics.capture_state_data(result_state)
        
        # Save analytics to database
        save_analytics_to_db()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        debug_print(f"✅ [Server] Response ready in {execution_time:.3f}s", "⏱️")
        
        return ChatResponse(
            response=result_state.get("final_response", "Sorry, I couldn't process your request."),
            success=True,
            execution_time=execution_time
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
                execution_time=execution_time
            )
        else:
            return ChatResponse(
                response="I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu",
                success=False,
                error="Internal server error",
                execution_time=execution_time
            )

def save_analytics_to_db():
    """Save analytics data to database"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analyze (
                    user_query, detected_language, intent_detector_decision,
                    intent_confidence, business_reasoner_decision, business_corrections,
                    query_optimizer_queries, pinecone_results_count, pinecone_top_results,
                    filter_decision, filtered_results_count, confidence_score,
                    confidence_reasoning, final_response, total_execution_time,
                    node_timings, escalated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analytics.data.get("user_query", ""),
                analytics.data.get("detected_language", ""),
                analytics.data.get("intent_detector_decision", ""),
                analytics.data.get("intent_confidence", 0.0),
                analytics.data.get("business_reasoner_decision", ""),
                analytics.data.get("business_corrections", ""),
                analytics.data.get("query_optimizer_queries", "[]"),
                analytics.data.get("pinecone_results_count", 0),
                analytics.data.get("pinecone_top_results", "[]"),
                analytics.data.get("filter_decision", ""),
                analytics.data.get("filtered_results_count", 0),
                analytics.data.get("confidence_score", 0.0),
                analytics.data.get("confidence_reasoning", ""),
                analytics.data.get("final_response", ""),
                analytics.data.get("total_execution_time", 0.0),
                json.dumps(analytics.data.get("node_timings", {})),
                analytics.data.get("escalated", False)
            ))
            conn.commit()
    except Exception as e:
        debug_print(f"❌ [Analytics] Failed to save analytics: {e}", "🚨")

# Feedback endpoint
@app.post("/feedback")
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
                # Parse JSON fields
                result["query_optimizer_queries"] = json.loads(result.get("query_optimizer_queries", "[]"))
                result["pinecone_top_results"] = json.loads(result.get("pinecone_top_results", "[]"))
                result["node_timings"] = json.loads(result.get("node_timings", "{}"))
                results.append(result)
            
            return {
                "success": True,
                "count": len(results),
                "data": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/summary")
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
            
            # Confidence distribution
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN confidence_score >= 0.8 THEN 1 ELSE 0 END) as high_confidence,
                    SUM(CASE WHEN confidence_score >= 0.5 AND confidence_score < 0.8 THEN 1 ELSE 0 END) as medium_confidence,
                    SUM(CASE WHEN confidence_score < 0.5 THEN 1 ELSE 0 END) as low_confidence
                FROM analyze
            """)
            confidence_dist = dict(cursor.fetchone())
            
            # Intent distribution
            cursor.execute("""
                SELECT intent_detector_decision, COUNT(*) as count
                FROM analyze
                GROUP BY intent_detector_decision
            """)
            intent_dist = {row["intent_detector_decision"]: row["count"] for row in cursor.fetchall()}
            
            # Language distribution
            cursor.execute("""
                SELECT detected_language, COUNT(*) as count
                FROM analyze
                GROUP BY detected_language
            """)
            language_dist = {row["detected_language"]: row["count"] for row in cursor.fetchall()}
            
            # Escalation rate
            cursor.execute("SELECT SUM(CASE WHEN escalated THEN 1 ELSE 0 END) as escalated FROM analyze")
            escalated_count = cursor.fetchone()["escalated"] or 0
            
            return {
                "success": True,
                "summary": {
                    "total_queries": total_queries,
                    "average_execution_time": round(avg_time, 3),
                    "confidence_distribution": confidence_dist,
                    "intent_distribution": intent_dist,
                    "language_distribution": language_dist,
                    "escalation_rate": round(escalated_count / total_queries * 100, 2) if total_queries > 0 else 0
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/summary")
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
            
            # Write headers - complete column set for analytics export
            headers = [
                "ID", "User Query", "Detected Language", "Intent Decision", "Intent Confidence",
                "Business Interpretation", "Business Corrections", "Query Optimizer Queries",
                "Pinecone Results Count", "Pinecone Top Results", "Filter Decision", 
                "Filtered Results Count", "Confidence Score", "Confidence Reasoning",
                "Final Response (Full)", "Total Execution Time (s)", "Node Timings (JSON)",
                "Escalated", "Created At"
            ]
            writer.writerow(headers)
            
            # Helper function to clean text for CSV
            def clean_text(text):
                if not text:
                    return ""
                # Replace problematic characters and normalize newlines
                return str(text).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
            
            # Write data - full data without truncation
            for row in cursor.fetchall():
                writer.writerow([
                    row["id"],
                    clean_text(row["user_query"]),
                    clean_text(row["detected_language"]),
                    clean_text(row["intent_detector_decision"]),
                    row["intent_confidence"] or 0,
                    clean_text(row["business_reasoner_decision"]),
                    clean_text(row["business_corrections"]),
                    clean_text(row["query_optimizer_queries"]),
                    row["pinecone_results_count"] or 0,
                    clean_text(row["pinecone_top_results"]),
                    clean_text(row["filter_decision"]),
                    row["filtered_results_count"] or 0,
                    row["confidence_score"] or 0,
                    clean_text(row["confidence_reasoning"]),
                    clean_text(row["final_response"]),  # Full response, cleaned
                    row["total_execution_time"] or 0,
                    clean_text(row["node_timings"]),
                    "Yes" if row["escalated"] else "No",
                    row["created_at"] or ""
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
async def root():
    """Health check endpoint"""
    return {
        "message": "🐠 Aquaforest RAG API is running",
        "version": "2.2.0",
        "status": "healthy",
        "analytics_enabled": True
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "debug_mode": TEST_ENV,
        "timestamp": time.time(),
        "database_status": "connected"
    }

@app.get("/debug/toggle")
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

def run_server():
    """Run the FastAPI server"""
    print("\n" + "="*60)
    print("🐠 Starting Aquaforest RAG API Server with Analytics")
    print("="*60)
    print(f"📍 Port: 2103")
    print(f"📍 Debug Mode: {'ON' if TEST_ENV else 'OFF'}")
    print(f"📍 CORS Origins: {CORS_ORIGINS}")
    print(f"📊 Analytics Database: {DB_PATH}")
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