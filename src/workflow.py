"""
LangGraph Workflow Definition - VERSION 4.1 with Analytics Integration
Enhanced with node timing capture for analytics
"""
import time
from functools import wraps
from langgraph.graph import StateGraph, END
from models import ConversationState, Intent
from openai import OpenAI
from intent_detector import detect_intent_and_language
from business_reasoner import business_reasoner
from query_optimizer import optimize_product_query
from pinecone_client import search_products_k20
# 🗑️ REMOVED: from results_filter import intelligent_results_filter - Business Reasoner does smart filtering
from response_formatter import format_final_response
import json
from config import PRODUCTS_FILE_PATH, TEST_ENV, debug_print, ENHANCED_K_VALUE
from llm_client_factory import LLMClientFactory

def timing_wrapper(func):
    """Decorator to measure execution time of workflow nodes with analytics and streaming"""
    @wraps(func)
    def wrapper(state: ConversationState) -> ConversationState:
        # 🆕 Get analytics instance from state instead of global variable
        session_analytics = state.get("analytics_instance")
        
        # 🔍 DEBUG: Check if analytics is set
        if TEST_ENV:
            print(f"🔍 [DEBUG timing_wrapper] session_analytics is: {session_analytics}")
        
        # Capture node start for streaming
        if session_analytics:
            session_analytics.capture_node_start(func.__name__)
            if TEST_ENV:
                print(f"📡 [DEBUG timing_wrapper] Sent node_start for: {func.__name__}")
        else:
            if TEST_ENV:
                print(f"⚠️ [DEBUG timing_wrapper] session_analytics is None - no streaming")
        
        start_time = time.time()
        result = func(state)
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Capture timing for analytics
        if session_analytics:
            session_analytics.capture_node_timing(func.__name__, execution_time)
            session_analytics.capture_node_complete(func.__name__)
            if TEST_ENV:
                print(f"📡 [DEBUG timing_wrapper] Sent node_complete for: {func.__name__}")
        
        if TEST_ENV:
            print(f"⏱️  [{func.__name__}] Node execution time: {execution_time:.3f}s")
        
        # Store timing in state for analytics
        if "node_timings" not in result:
            result["node_timings"] = {}
        result["node_timings"][func.__name__] = execution_time
        
        return result
    return wrapper

@timing_wrapper
def load_product_names(state: ConversationState) -> ConversationState:
    """Load product names into state"""
    try:
        with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
            state["product_names"] = json.load(f)
            debug_print(f"📋 [LoadProducts] Loaded {len(state['product_names'])} product names")
    except Exception as e:
        if TEST_ENV:
            print(f"❌ [DEBUG LoadProducts] Error loading products: {e}")
        debug_print(f"❌ [LoadProducts] Error loading products: {e}")
        state["product_names"] = []
    return state

def route_intent(state: ConversationState) -> str:
    """Route based on detected intent"""
    intent = state.get("intent", Intent.OTHER)
    
    debug_print(f"🚦 [Router] Routing for intent='{intent}'")
    
    # Store routing decision for analytics
    if "routing_decisions" not in state:
        state["routing_decisions"] = []
    state["routing_decisions"].append({
        "router": "route_intent",
        "decision": intent,
        "next_node": ""
    })
    
    if intent in [Intent.GREETING, Intent.BUSINESS, Intent.COMPETITOR, 
                  Intent.CENSORED, Intent.PURCHASE_INQUIRY, Intent.SUPPORT, Intent.OTHER]:
        debug_print(f"➡️ [Router] Routing to: format_response (special intent)")
        state["routing_decisions"][-1]["next_node"] = "format_response"
        return "format_response"
    elif intent in [Intent.PRODUCT_QUERY, Intent.ANALYZE_ICP]:
        debug_print(f"➡️ [Router] Routing to: business_reasoner (product query/ICP analysis)")
        state["routing_decisions"][-1]["next_node"] = "business_reasoner"
        return "optimize_query"
    elif intent == Intent.FOLLOW_UP:
        debug_print(f"➡️ [Router] Routing to: enhanced_follow_up_router (follow-up question)")
        state["routing_decisions"][-1]["next_node"] = "enhanced_follow_up_router"
        return "enhanced_follow_up_router"
    else:
        debug_print(f"➡️ [Router] Routing to: format_response (unknown intent)")
        state["routing_decisions"][-1]["next_node"] = "format_response"
        return "format_response"

@timing_wrapper
def enhanced_follow_up_router(state: ConversationState) -> ConversationState:
    """Enhanced follow-up router with session-based cache and Flash 2.0 evaluation"""
    from session_manager import get_session_manager
    from follow_up_evaluator import evaluate_follow_up_cache
    
    debug_print(f"🔄 [Enhanced Follow-up Router] Evaluating session cache for follow-up")
    
    session_id = state.get("session_id")
    if not session_id:
        debug_print(f"❌ [Enhanced Follow-up Router] No session ID - routing to business_reasoner")
        # Set default evaluation for no session scenario
        state["follow_up_evaluation"] = {
            "sufficient": False,
            "confidence": 0.0,
            "reasoning": "No session ID available",
            "business_prompt": f"User asked: {state['user_query']}\nPlease provide comprehensive information about this query."
        }
        return state
    
    # Get session cache
    session_manager = get_session_manager()
    extended_cache = session_manager.get_session_cache(session_id)
    
    if not extended_cache:
        debug_print(f"❌ [Enhanced Follow-up Router] No cache for session {session_id} - routing to business_reasoner")
        # Set default evaluation for no cache scenario
        state["follow_up_evaluation"] = {
            "sufficient": False,
            "confidence": 0.0,
            "reasoning": "No cache available for this session",
            "business_prompt": f"User asked: {state['user_query']}\nPlease provide comprehensive information about this query."
        }
        return state
    
    # Use Flash 2.0 to evaluate cache sufficiency
    evaluation = evaluate_follow_up_cache(state, extended_cache)
    
    if evaluation["sufficient"]:
        # Cache is sufficient - prepare data for response formatter
        state["cache_response_data"] = evaluation["response_data"]
        debug_print(f"✅ [Enhanced Follow-up Router] Cache sufficient (confidence: {evaluation['confidence']}) - routing to format_response")
    else:
        # Cache insufficient - prepare smart prompt for business reasoner
        state["smart_business_prompt"] = evaluation["business_prompt"]
        debug_print(f"❌ [Enhanced Follow-up Router] Cache insufficient - routing to business_reasoner with smart prompt")
    
    # Store evaluation for analytics
    state["follow_up_evaluation"] = evaluation
    
    return state

def route_enhanced_follow_up(state: ConversationState) -> str:
    """Enhanced follow-up router based on Flash 2.0 evaluation"""
    # Store routing decision for analytics
    if "routing_decisions" not in state:
        state["routing_decisions"] = []
    
    # Check if Flash 2.0 evaluation was successful
    evaluation = state.get("follow_up_evaluation")
    
    if not evaluation:
        debug_print(f"❌ [Enhanced Follow-up Router] No evaluation found - routing to business_reasoner")
        state["routing_decisions"].append({
            "router": "route_enhanced_follow_up",
            "decision": "no_evaluation",
            "next_node": "business_reasoner"
        })
        return "business_reasoner"
    
    if evaluation["sufficient"]:
        debug_print(f"✅ [Enhanced Follow-up Router] Cache sufficient - routing to format_response")
        state["routing_decisions"].append({
            "router": "route_enhanced_follow_up", 
            "decision": f"cache_sufficient_confidence_{evaluation['confidence']}",
            "next_node": "format_response"
        })
        return "format_response"
    else:
        debug_print(f"❌ [Enhanced Follow-up Router] Cache insufficient - routing to business_reasoner")
        state["routing_decisions"].append({
            "router": "route_enhanced_follow_up",
            "decision": f"cache_insufficient: {evaluation['reasoning'][:50]}...",
            "next_node": "business_reasoner"
        })
        return "business_reasoner"

def create_workflow() -> StateGraph:
    """Create the enhanced LangGraph workflow with analytics"""
    debug_print("🏗️ [Workflow] Creating enhanced LangGraph workflow with analytics...")
    debug_print(f"🔧 [Workflow] Using ENHANCED_K_VALUE={ENHANCED_K_VALUE}")
    debug_print("🚀 [Workflow] REMOVED intelligent_filter - Business Reasoner provides superior filtering")
    debug_print("🗑️ [Workflow] REMOVED confidence_scorer - Direct routing for better performance")
    debug_print("⚡ [Workflow] Performance improvement: ~18 seconds saved per query + reduced token usage")
        
    workflow = StateGraph(ConversationState)
    
    # Add nodes with timing wrapper
    nodes = [
        ("detect_intent", detect_intent_and_language),
        ("load_products", load_product_names),
        ("business_reasoner", business_reasoner),
        ("optimize_query", optimize_product_query),
        ("search_pinecone", search_products_k20),
        # 🗑️ REMOVED: ("evaluate_confidence", evaluate_confidence) - CONFIDENCE SCORER DELETED
        ("format_response", format_final_response),

        ("enhanced_follow_up_router", enhanced_follow_up_router)
    ]
    
    for node_name, node_func in nodes:
        workflow.add_node(node_name, timing_wrapper(node_func))
        debug_print(f"   ➕ Added node: {node_name}")
    
    # Define edges
    workflow.set_entry_point("detect_intent")
    workflow.add_edge("detect_intent", "load_products")
    # 🚀 OPTIMIZATION: Route directly after load_products to skip business_reasoner for special intents
    workflow.add_conditional_edges(
        "load_products", route_intent,
        {
            "format_response": "format_response", 
            "optimize_query": "business_reasoner",  # Product queries need business analysis
            "enhanced_follow_up_router": "enhanced_follow_up_router"
        }
    )
    # Business reasoner now only handles product queries
    workflow.add_edge("business_reasoner", "optimize_query")
    workflow.add_conditional_edges(
        "enhanced_follow_up_router", route_enhanced_follow_up,
        {
            "format_response": "format_response",
            "business_reasoner": "business_reasoner"
        }
    )
    workflow.add_edge("optimize_query", "search_pinecone")
    # 🚀 DIRECT ROUTING: search_pinecone → format_response (no confidence check)
    workflow.add_edge("search_pinecone", "format_response")
    
    # All paths lead to END
    workflow.add_edge("format_response", END)
    
    debug_print("✅ [Workflow] Enhanced workflow with direct routing created and compiled")
        
    return workflow.compile()

# Create and export the workflow app
app = create_workflow()

# 🗑️ REMOVED: set_workflow_analytics - analytics now passed via state