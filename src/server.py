"""
Aquaforest RAG System - FastAPI Server
FastAPI server for serving the RAG agent to frontend applications
Port: 2103
"""
import asyncio
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our existing modules using the same variable names as config.py
from config import debug_print, TEST_ENV, CORS_ORIGINS
from models import ConversationState
from main import AquaforestAssistant

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

# Initialize FastAPI app
app = FastAPI(
    title="Aquaforest RAG API",
    description="AI Assistant API for Aquaforest products and solutions",
    version="2.1.0"
)

# CORS Configuration - Allow React frontend (loaded from .env)
origins = CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize the assistant
assistant = AquaforestAssistant()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "🐠 Aquaforest RAG API is running",
        "version": "2.1.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "debug_mode": TEST_ENV,
        "timestamp": time.time()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user messages and returns AI responses
    """
    start_time = time.time()
    
    try:
        debug_print(f"📨 [Server] Received chat request: {request.message[:50]}...", "🔍")
        
        # Create ConversationState from request
        conversation_state: ConversationState = {
            "user_query": request.message,
            "detected_language": "en",  # Will be detected by workflow
            "intent": "other",  # Will be detected by workflow
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
        
        # Process the query using our existing workflow
        result_state = assistant.process_query_sync(conversation_state, debug=request.debug)
        
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
        
        # Don't expose internal errors to users in production
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

@app.get("/debug/toggle")
async def toggle_debug():
    """Toggle debug mode for testing purposes"""
    import os
    import config
    
    current_debug = TEST_ENV
    new_debug = not current_debug
    
    # Update environment variable
    os.environ["TEST_ENV"] = "true" if new_debug else "false"
    config.TEST_ENV = new_debug
    
    return {
        "debug_mode": new_debug,
        "message": f"Debug mode {'enabled' if new_debug else 'disabled'}"
    }

def run_server():
    """Run the FastAPI server"""
    print("\n" + "="*60)
    print("🐠 Starting Aquaforest RAG API Server")
    print("="*60)
    print(f"📍 Port: 2103")
    print(f"📍 Debug Mode: {'ON' if TEST_ENV else 'OFF'}")
    print(f"📍 CORS Origins: {CORS_ORIGINS}")
    print("="*60 + "\n")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=2103,
        reload=True,
        access_log=TEST_ENV  # Only show access logs in debug mode
    )

if __name__ == "__main__":
    run_server() 