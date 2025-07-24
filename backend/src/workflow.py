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
# [REMOVED] from results_filter import intelligent_results_filter - Business Reasoner does smart filtering
from response_formatter import format_final_response
import json
from config import PRODUCTS_FILE_PATH, TEST_ENV, debug_print, ENHANCED_K_VALUE
from llm_client_factory import LLMClientFactory
from utils.logger import logger

def timing_wrapper(func):
    """Decorator to measure execution time of workflow nodes with analytics and streaming"""
    @wraps(func)
    def wrapper(state: ConversationState) -> ConversationState:
        # [NEW] Get analytics instance from state instead of global variable
        session_analytics = state.get("analytics_instance")
        
        # [DEBUG] Check if analytics is set
        logger.debug(f"session_analytics is: {session_analytics}", "DETAIL")
        
        # Capture node start for streaming
        if session_analytics:
            session_analytics.capture_node_start(func.__name__)
            logger.debug(f"Sent node_start for: {func.__name__}", "DETAIL")
        else:
            logger.debug("session_analytics is None - no streaming", "DETAIL")
        
        start_time = time.time()
        result = func(state)
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Capture timing for analytics
        if session_analytics:
            session_analytics.capture_node_timing(func.__name__, execution_time)
            session_analytics.capture_node_complete(func.__name__)
            logger.debug(f"Sent node_complete for: {func.__name__}", "DETAIL")
        
        logger.performance(f"Node execution time: {func.__name__}", execution_time, "SUB")
        
        # Store timing in state for analytics
        if "node_timings" not in result:
            result["node_timings"] = {}
        result["node_timings"][func.__name__] = execution_time
        
        return result
    return wrapper

def load_product_names(state: ConversationState) -> ConversationState:
    """Load product names into state"""
    try:
        with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
            state["product_names"] = json.load(f)
            logger.database(f"Loaded {len(state['product_names'])} product names", "SUB")
    except Exception as e:
        logger.error(f"Error loading products: {e}", "SUB")
        state["product_names"] = []
    return state

def route_intent(state: ConversationState) -> str:
    """Route based on detected intent"""
    intent = state.get("intent", Intent.OTHER)
    
    logger.workflow(f"Routing for intent='{intent}'", "SUB")
    
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
        logger.workflow("Routing to: format_response (special intent)", "DETAIL")
        state["routing_decisions"][-1]["next_node"] = "format_response"
        return "format_response"
    elif intent in [Intent.PRODUCT_QUERY, Intent.ANALYZE_ICP]:
        logger.workflow("Routing to: business_reasoner (product query/ICP analysis)", "DETAIL")
        state["routing_decisions"][-1]["next_node"] = "business_reasoner"
        return "optimize_query"
    elif intent == Intent.FOLLOW_UP:
        logger.workflow("Routing to: enhanced_follow_up_router (follow-up question)", "DETAIL")
        state["routing_decisions"][-1]["next_node"] = "enhanced_follow_up_router"
        return "enhanced_follow_up_router"
    else:
        logger.workflow("Routing to: format_response (unknown intent)", "DETAIL")
        state["routing_decisions"][-1]["next_node"] = "format_response"
        return "format_response"

def enhanced_follow_up_router(state: ConversationState) -> ConversationState:
    """Enhanced follow-up router with session-based cache and Flash 2.0 evaluation
    [FIXED] Removed double timing_wrapper to eliminate state synchronization issues
    """
    from session_manager import get_session_manager
    from follow_up_evaluator import evaluate_follow_up_cache
    
    logger.workflow("Evaluating session cache for follow-up", "SUB")
    
    session_id = state.get("session_id")
    if not session_id:
        logger.workflow("No session ID - routing to business_reasoner", "DETAIL")
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
        logger.workflow(f"No cache for session {session_id} - routing to business_reasoner", "DETAIL")
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
        logger.workflow(f"Cache sufficient (confidence: {evaluation['confidence']}) - routing to format_response", "DETAIL")
    else:
        # Cache insufficient - prepare smart prompt for business reasoner
        state["smart_business_prompt"] = evaluation["business_prompt"]
        logger.workflow("Cache insufficient - routing to business_reasoner with smart prompt", "DETAIL")
    
    # Store evaluation for analytics
    state["follow_up_evaluation"] = evaluation
    
    return state

def route_enhanced_follow_up(state: ConversationState) -> str:
    """Enhanced follow-up router based on Flash 2.0 evaluation with confidence threshold
    [ADDED] Confidence threshold 0.7 - use cache if confidence >= 0.7
    """
    # Store routing decision for analytics
    if "routing_decisions" not in state:
        state["routing_decisions"] = []
    
    # Check if Flash 2.0 evaluation was successful
    evaluation = state.get("follow_up_evaluation")
    
    if not evaluation:
        logger.workflow("No evaluation found - routing to business_reasoner", "DETAIL")
        state["routing_decisions"].append({
            "router": "route_enhanced_follow_up",
            "decision": "no_evaluation",
            "next_node": "business_reasoner"
        })
        return "business_reasoner"
    
    # [NEW] Confidence threshold logic - override LLM decision if confidence >= 0.7
    confidence = evaluation.get("confidence", 0.0)
    sufficient = evaluation.get("sufficient", False)
    
    # Use cache if either LLM says sufficient OR confidence >= 0.7
    use_cache = sufficient or confidence >= 0.7
    
    if use_cache:
        # Ensure cache_response_data is prepared for threshold override cases
        if not state.get("cache_response_data") and confidence >= 0.7:
            # Prepare cache data for threshold override
            from session_manager import get_session_manager
            session_manager = get_session_manager()
            session_id = state.get("session_id")
            if session_id:
                extended_cache = session_manager.get_session_cache(session_id)
                if extended_cache:
                    from follow_up_evaluator import follow_up_evaluator
                    response_data = follow_up_evaluator._prepare_response_data(state, extended_cache)
                    state["cache_response_data"] = response_data
        
        decision_reason = "cache_sufficient" if sufficient else f"confidence_threshold_override_{confidence:.2f}"
        logger.workflow(f"Using cache (sufficient={sufficient}, confidence={confidence:.2f}) - routing to format_response", "DETAIL")
        state["routing_decisions"].append({
            "router": "route_enhanced_follow_up", 
            "decision": decision_reason,
            "next_node": "format_response"
        })
        return "format_response"
    else:
        logger.workflow(f"Cache insufficient (sufficient={sufficient}, confidence={confidence:.2f} < 0.7) - routing to business_reasoner", "DETAIL")
        state["routing_decisions"].append({
            "router": "route_enhanced_follow_up",
            "decision": f"confidence_below_threshold_{confidence:.2f}: {evaluation['reasoning'][:50]}...",
            "next_node": "business_reasoner"
        })
        return "business_reasoner"

def create_workflow() -> StateGraph:
    """Create the enhanced LangGraph workflow with analytics"""
    logger.workflow("Creating enhanced LangGraph workflow with analytics...")
    logger.workflow(f"Using ENHANCED_K_VALUE={ENHANCED_K_VALUE}", "SUB")
    logger.workflow("REMOVED intelligent_filter - Business Reasoner provides superior filtering", "SUB")
    logger.workflow("REMOVED confidence_scorer - Direct routing for better performance", "SUB")
    logger.workflow("Performance improvement: ~18 seconds saved per query + reduced token usage", "SUB")
        
    workflow = StateGraph(ConversationState)
    
    # Add nodes with timing wrapper
    nodes = [
        ("detect_intent", timing_wrapper(detect_intent_and_language)),
        ("load_products", timing_wrapper(load_product_names)),
        ("business_reasoner", timing_wrapper(business_reasoner)),
        ("optimize_query", timing_wrapper(optimize_product_query)),
        ("search_pinecone", timing_wrapper(search_products_k20)),
        # [REMOVED] ("evaluate_confidence", evaluate_confidence) - CONFIDENCE SCORER DELETED
        ("format_response", timing_wrapper(format_final_response)),
        # [FIXED] No timing_wrapper to avoid double wrapping
        ("enhanced_follow_up_router", enhanced_follow_up_router)
    ]
    
    for node_name, node_func in nodes:
        workflow.add_node(node_name, node_func)
        logger.workflow(f"Added node: {node_name}", "SUB")
    
    # Define edges
    workflow.set_entry_point("detect_intent")
    workflow.add_edge("detect_intent", "load_products")
    # [OPTIMIZATION] Route directly after load_products to skip business_reasoner for special intents
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
    # [FIXED] Enhanced follow-up router with proper conditional edge function
    workflow.add_conditional_edges(
        "enhanced_follow_up_router", route_enhanced_follow_up,
        {
            "format_response": "format_response",
            "business_reasoner": "business_reasoner"
        }
    )
    workflow.add_edge("optimize_query", "search_pinecone")
    # [DIRECT] search_pinecone → format_response (no confidence check)
    workflow.add_edge("search_pinecone", "format_response")
    
    # All paths lead to END
    workflow.add_edge("format_response", END)
    
    logger.workflow("Enhanced workflow with direct routing created and compiled", "SUB")
        
    return workflow.compile()

# Create and export the workflow app
app = create_workflow()

# [REMOVED] set_workflow_analytics - analytics now passed via state