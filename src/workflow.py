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
from response_formatter import format_final_response, escalate_to_human, handle_follow_up
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
                  Intent.CENSORED, Intent.PURCHASE_INQUIRY, Intent.SUPPORT]:
        debug_print(f"➡️ [Router] Routing to: format_response (special intent)")
        state["routing_decisions"][-1]["next_node"] = "format_response"
        return "format_response"
    elif intent in [Intent.PRODUCT_QUERY, Intent.ANALYZE_ICP]:
        debug_print(f"➡️ [Router] Routing to: optimize_query (product query/ICP analysis)")
        state["routing_decisions"][-1]["next_node"] = "optimize_query"
        return "optimize_query"
    elif intent == Intent.FOLLOW_UP:
        debug_print(f"➡️ [Router] Routing to: follow_up_router (follow-up question)")
        state["routing_decisions"][-1]["next_node"] = "follow_up_router"
        return "follow_up_router"
    else:
        debug_print(f"➡️ [Router] Routing to: escalate_support (unknown intent)")
        state["routing_decisions"][-1]["next_node"] = "escalate_support"
        return "escalate_support"

@timing_wrapper
def follow_up_router(state: ConversationState) -> ConversationState:
    """Just a pass-through node for routing decision"""
    debug_print(f"🔄 [Follow-up Router] Checking if can handle follow-up with cache")
    return state

def route_follow_up(state: ConversationState) -> str:
    """Enhanced follow-up router with better cache utilization"""
    # Store routing decision for analytics
    if "routing_decisions" not in state:
        state["routing_decisions"] = []
    
    # 🆕 Check both context_cache AND chat_history (for Messenger)
    has_context_cache = bool(state.get("context_cache"))
    has_chat_history = bool(state.get("chat_history"))
    
    debug_print(f"🔍 [Follow-up Router] context_cache: {len(state.get('context_cache', []))}, chat_history: {len(state.get('chat_history', []))}")
    
    if not has_context_cache and not has_chat_history:
        debug_print(f"❌ [Follow-up Router] No cache or history, routing to optimize_query")
        state["routing_decisions"].append({
            "router": "route_follow_up",
            "decision": "no_cache_no_history",
            "next_node": "optimize_query"
        })
        return "optimize_query"
    
    # 🆕 Enhanced product reference detection from both cache and chat history
    referenced_products = []
    
    # Get products from context_cache
    for item in state.get("context_cache", []):
        if item.get('product_name'):
            referenced_products.append(item['product_name'].lower())
    
    # 🆕 Extract products mentioned in chat history (from assistant responses)
    for msg in state.get("chat_history", []):
        if msg.get("role") == "assistant":
            content = msg.get("content", "").lower()
            # Simple extraction of product names (Ca Plus, Component 1+2+3+, etc.)
            if "ca plus" in content:
                referenced_products.append("ca plus")
            if "component" in content:
                referenced_products.append("component")
            if "calcium" in content:
                referenced_products.append("calcium")
    
    query_lower = state["user_query"].lower()
    
    # Check for product references
    products_referenced = any(product in query_lower for product in referenced_products)
    
    # 🆕 Enhanced contextual references (multi-language)
    contextual_keywords = [
        'to', 'ten', 'ta', 'te', 'it', 'this', 'that', 'those', 'them',
        'one', 'which', 'który', 'która', 'które', 'first', 'second',
        'what about', 'how to use', 'dosage', 'dawkowanie',
        'more', 'details', 'different', 'other', 'polecisz', 'recommend'
    ]
    has_contextual_reference = any(keyword in query_lower for keyword in contextual_keywords)
    
    # Check if asking about something from previous response
    previous_context_words = ['also', 'still', 'additionally', 'besides', 'też', 'także']
    references_previous = any(word in query_lower for word in previous_context_words)
    
    debug_print(f"🔍 [Follow-up Router] products_referenced: {products_referenced}, contextual: {has_contextual_reference}, previous: {references_previous}")
    
    if products_referenced or has_contextual_reference or references_previous:
        debug_print(f"✅ [Follow-up Router] Found reference to previous content, using follow-up handler")
        state["routing_decisions"].append({
            "router": "route_follow_up",
            "decision": "context_reference_found",
            "next_node": "handle_follow_up"
        })
        return "handle_follow_up"
    
    # 🆕 Enhanced LLM check using both cache and chat history
    # Use intent detector for this simple classification task
    client, model_name = LLMClientFactory.create_client("intent_detector")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    # Create a more focused prompt with both sources
    cached_context_summary = f"Cached products: {', '.join([item.get('product_name', 'Unknown') for item in state.get('context_cache', [])])}"
    referenced_products_summary = f"Referenced products from history: {', '.join(referenced_products)}"
    
    # Check if previous response mentioned a category
    category_mentioned = state.get("requested_category") is not None
    
    debug_print(f"🤔 [Follow-up Router] LLM check for context sufficiency (cache + history)")
    
    prompt = f"""
Is the user's latest message asking about something from the previous conversation?

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---
{cached_context_summary}
{referenced_products_summary}
Category was discussed: {category_mentioned}
---

The user might be:
1. Asking for recommendations ("który polecisz?" = "which do you recommend?")
2. Asking to compare mentioned products  
3. Asking "which one" from previously shown options
4. Using references like "it", "this", "that", "ten", "ta"
5. Asking about usage/dosage of discussed products
6. Asking about a different aspect of the same topic

Respond with only "yes" if the query is about previous conversation content, or "no" if it needs new search.
"""
    
    try:
        response = client.chat.completions.create(
            model=model_name, 
            temperature=0, 
            messages=[{"role": "system", "content": prompt}]
        )
        decision = response.choices[0].message.content.strip().lower()
        
        debug_print(f"🤖 [Follow-up Router] LLM decision: '{decision}'")
        
        if "yes" in decision:
            debug_print(f"✅ [Follow-up Router] Context is sufficient, routing to handle_follow_up")
            state["routing_decisions"].append({
                "router": "route_follow_up",
                "decision": f"llm_context_sufficient: {decision}",
                "next_node": "handle_follow_up"
            })
            return "handle_follow_up"
        else:
            debug_print(f"❌ [Follow-up Router] Context insufficient, routing to optimize_query")
            state["routing_decisions"].append({
                "router": "route_follow_up",
                "decision": f"llm_context_insufficient: {decision}",
                "next_node": "optimize_query"
            })
            return "optimize_query"
            
    except Exception as e:
        if TEST_ENV:
            print(f"❌ [DEBUG Follow-up Router] Context check error: {e}")
        debug_print(f"❌ [Follow-up Router] Context check error: {e}")
        state["routing_decisions"].append({
            "router": "route_follow_up",
            "decision": f"error: {str(e)}",
            "next_node": "optimize_query"
        })
        return "optimize_query"

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
        ("escalate_support", escalate_to_human),
        ("handle_follow_up", handle_follow_up),
        ("follow_up_router", follow_up_router)
    ]
    
    for node_name, node_func in nodes:
        workflow.add_node(node_name, timing_wrapper(node_func))
        debug_print(f"   ➕ Added node: {node_name}")
    
    # Define edges
    workflow.set_entry_point("detect_intent")
    workflow.add_edge("detect_intent", "load_products")
    workflow.add_edge("load_products", "business_reasoner")
    workflow.add_conditional_edges(
        "business_reasoner", route_intent,
        {
            "format_response": "format_response", 
            "escalate_support": "escalate_support",
            "optimize_query": "optimize_query", 
            "follow_up_router": "follow_up_router"
        }
    )
    workflow.add_conditional_edges(
        "follow_up_router", route_follow_up,
        {
            "handle_follow_up": "handle_follow_up", 
            "optimize_query": "optimize_query"
        }
    )
    workflow.add_edge("optimize_query", "search_pinecone")
    # 🚀 DIRECT ROUTING: search_pinecone → format_response (no confidence check)
    workflow.add_edge("search_pinecone", "format_response")
    
    # All paths lead to END
    workflow.add_edge("format_response", END)
    workflow.add_edge("escalate_support", END)
    workflow.add_edge("handle_follow_up", END)
    
    debug_print("✅ [Workflow] Enhanced workflow with direct routing created and compiled")
        
    return workflow.compile()

# Create and export the workflow app
app = create_workflow()

# 🗑️ REMOVED: set_workflow_analytics - analytics now passed via state