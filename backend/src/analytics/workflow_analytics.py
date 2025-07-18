"""
Workflow Analytics Module
Enhanced analytics capture class with streaming support
"""
import json
import time
from typing import Dict, Any, Optional, Callable
from models import ConversationState
from config import TEST_ENV, debug_print
from utils.logger import logger

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
    
    def set_streaming_callback(self, callback: Callable):
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
        logger.debug(f"node_name='{node_name}', message='{message}'", "DETAIL")
        logger.debug(f"streaming_callback={self.streaming_callback}", "DETAIL")
        
        if self.streaming_callback:
            update_data = {
                "node": node_name,
                "status": "processing",
                "message": message,
                "elapsed_time": elapsed_time
            }
            logger.debug(f"Calling streaming_callback with: {update_data}", "DETAIL")
            self.streaming_callback(update_data)
        else:
            logger.debug("streaming_callback is None!", "DETAIL")
    
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