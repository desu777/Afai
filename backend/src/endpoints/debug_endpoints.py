"""
Debug Endpoints Module
Debug and health check endpoints extracted from server.py
"""
import os
import time
from fastapi import HTTPException, Request, Query
from config import TEST_ENV, debug_print
from database import get_db, load_messenger_chat_history, save_messenger_message
from main import AquaforestAssistant
import messenger_server

def setup_debug_endpoints(app, tier3_rate_limit, global_rate_limit, vision_rate_limit, ChatRequest):
    """Setup debug endpoints on FastAPI app"""
    
    @app.get("/")
    @tier3_rate_limit()
    async def root(request: Request):
        """Health check endpoint"""
        return {
            "message": "🐠 Aquaforest RAG API is running",
            "version": "2.2.0",
            "status": "healthy",
            "analytics_enabled": True
        }

    @app.get("/health")
    @tier3_rate_limit()
    async def health_check(request: Request):
        """Detailed health check"""
        return {
            "status": "healthy",
            "debug_mode": TEST_ENV,
            "timestamp": time.time(),
            "database_status": "connected"
        }

    @app.get("/debug/toggle")
    @global_rate_limit()
    async def toggle_debug(request: Request):
        """Toggle debug mode for testing purposes"""
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
    async def get_messenger_history_debug(user_id: str, request: Request, limit: int = 10):
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

    # Facebook Messenger Webhook Endpoints
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
        assistant = AquaforestAssistant(analytics_instance=None)
        return await messenger_server.webhook_handler(
            request, assistant, 
            load_history_func=load_messenger_chat_history,
            save_message_func=save_messenger_message
        )

    # Vision Analysis Test Endpoint
    @app.post("/debug/test-vision")
    @vision_rate_limit()
    async def test_vision_analysis(chat_request: ChatRequest, request: Request):
        """Test endpoint for vision analysis functionality"""
        
        if not chat_request.image_url:
            raise HTTPException(status_code=400, detail="image_url is required for vision testing")
        
        try:
            debug_print(f"📸 [VisionTest] Testing vision analysis with: {chat_request.image_url[:100]}...", "🧪")
            
            # Create test conversation state
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
                "image_url": chat_request.image_url,
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
                "original_query": chat_request.message,
                "enhanced_query": result_state.get("user_query", ""),
                "image_analysis": result_state.get("image_analysis", ""),
                "detected_intent": result_state.get("intent", ""),
                "detected_language": result_state.get("detected_language", ""),
                "image_url": chat_request.image_url
            }
            
        except Exception as e:
            debug_print(f"❌ [VisionTest] Error: {e}", "🚨")
            raise HTTPException(status_code=500, detail=f"Vision analysis error: {str(e)}")

    # Vision Analysis Examples Endpoint
    @app.get("/debug/vision-examples")
    @global_rate_limit()
    async def get_vision_examples(request: Request):
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