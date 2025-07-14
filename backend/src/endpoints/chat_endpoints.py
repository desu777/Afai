"""
Chat Endpoints Module
Main chat and streaming endpoints extracted from server.py
"""
import json
import time
import threading
import queue
from typing import Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from config import debug_print, TEST_ENV
from analytics import WorkflowAnalytics
from database import save_analytics_to_db
from main import AquaforestAssistant

def setup_chat_endpoints(app, tier1_rate_limit, ChatRequest, ChatResponse):
    """Setup chat endpoints on FastAPI app"""
    
    @app.post("/chat/stream")
    @tier1_rate_limit()
    async def chat_stream_endpoint(chat_request: ChatRequest, request: Request):
        """
        Streaming chat endpoint that provides real-time workflow updates via Server-Sent Events
        """
        def generate_stream():
            # Handle session management using SessionManager
            from session_manager import get_session_manager
            session_manager = get_session_manager()
            
            session_id = chat_request.session_id
            if not session_id:
                # Generate new session for first-time users
                session_id = session_manager.generate_session_id()
                debug_print(f"🆕 [StreamServer] Generated new session: {session_id}")
            else:
                debug_print(f"🔄 [StreamServer] Using existing session: {session_id}")
            
            session_analytics = WorkflowAnalytics()
            session_analytics.reset()
            
            if TEST_ENV:
                debug_print(f"🆔 [StreamServer] Starting session {session_id}: {chat_request.message[:30]}...", "🆔")
            
            # Real-time streaming with threading
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
                    debug_print(f"📨 [StreamServer] Session {session_id} - Received streaming chat request: {chat_request.message[:50]}...", "🔍")
                    
                    # Create conversation state with session analytics and session management
                    conversation_state = {
                        "user_query": chat_request.message,
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
                        "chat_history": chat_request.chat_history,
                        "context_cache": [],
                        "session_id": session_id,  # Session ID for cache management
                        "extended_cache": None,    # Will be populated during workflow
                        "image_url": chat_request.image_url,  # Vision analysis
                        "image_analysis": None,  # Will be filled by intent detector
                        "node_timings": {},
                        "routing_decisions": [],
                        "total_execution_time": 0.0,
                        "analytics_instance": session_analytics
                    }
                    
                    debug_print(f"🔄 [StreamServer] Processing with streaming workflow (debug={chat_request.debug})", "⚙️")
                    
                    # Create dedicated assistant instance for this session
                    session_assistant = AquaforestAssistant(analytics_instance=session_analytics)
                    
                    # Process with analytics capture and streaming
                    result_state = session_assistant.process_query_sync(conversation_state, debug=chat_request.debug)
                    
                    # Save extended cache to session if available
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
                    
                    # Handle very long messages
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
                                
                                # Handle very long messages
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

    @app.post("/chat", response_model=ChatResponse)
    @tier1_rate_limit()
    async def chat_endpoint(chat_request: ChatRequest, request: Request):
        """
        Main chat endpoint that processes user messages and returns AI responses
        """
        global_analytics = WorkflowAnalytics()
        global_analytics.reset()
        start_time = time.time()
        
        try:
            debug_print(f"📨 [Server] Received chat request: {chat_request.message[:50]}...", "🔍")
            
            # Handle session management
            from session_manager import get_session_manager
            session_manager = get_session_manager()
            
            session_id = chat_request.session_id
            if not session_id:
                # Generate new session for first-time users
                session_id = session_manager.generate_session_id()
                debug_print(f"🆕 [Server] Generated new session: {session_id}")
            else:
                debug_print(f"🔄 [Server] Using existing session: {session_id}")
            
            # Create conversation state with global analytics and session
            conversation_state = {
                "user_query": chat_request.message,
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
                "chat_history": chat_request.chat_history,
                "context_cache": [],
                "session_id": session_id,  # Session ID for cache management
                "extended_cache": None,    # Will be populated during workflow
                "image_url": chat_request.image_url,  # Vision analysis
                "image_analysis": None,  # Will be filled by intent detector
                "node_timings": {},
                "routing_decisions": [],
                "total_execution_time": 0.0,
                "analytics_instance": global_analytics
            }
            
            debug_print(f"🔄 [Server] Processing with workflow (debug={chat_request.debug})", "⚙️")
            
            # Create assistant instance with global analytics for non-streaming requests
            non_streaming_assistant = AquaforestAssistant(analytics_instance=global_analytics)
            
            # Process with analytics capture
            result_state = non_streaming_assistant.process_query_sync(conversation_state, debug=chat_request.debug)
            
            # Capture analytics from final state
            global_analytics.capture_state_data(result_state)
            
            # Save extended cache to session if available
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
                session_id=session_id  # Return session_id to frontend
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