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
from confidence_scorer import evaluate_confidence, route_based_on_confidence
from response_formatter import format_final_response, escalate_to_human, handle_follow_up
import json
from config import PRODUCTS_FILE_PATH, OPENAI_API_KEY, OPENAI_MODEL, TEST_ENV, debug_print, ENHANCED_K_VALUE

# Global analytics capture (will be set by server)
workflow_analytics = None

def timing_wrapper(func):
    """Decorator to measure execution time of workflow nodes with analytics"""
    @wraps(func)
    def wrapper(state: ConversationState) -> ConversationState:
        start_time = time.time()
        result = func(state)
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Capture timing for analytics
        if workflow_analytics:
            workflow_analytics.capture_node_timing(func.__name__, execution_time)
        
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
    elif intent == Intent.PRODUCT_QUERY:
        debug_print(f"➡️ [Router] Routing to: optimize_query (product query)")
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
    
    if not state.get("context_cache"):
        debug_print(f"❌ [Follow-up Router] No cache, routing to optimize_query")
        state["routing_decisions"].append({
            "router": "route_follow_up",
            "decision": "no_cache",
            "next_node": "optimize_query"
        })
        return "optimize_query"
    
    # Check if query references cached products or categories
    cached_products = []
    for item in state.get("context_cache", []):
        if item.get('product_name'):
            cached_products.append(item['product_name'].lower())
    
    query_lower = state["user_query"].lower()
    
    # Check for product references
    products_referenced = any(product in query_lower for product in cached_products)
    
    # Check for contextual references
    contextual_keywords = [
        'to', 'ten', 'ta', 'te', 'it', 'this', 'that', 'those', 'them',
        'one', 'which', 'one', 'first', 'second',
        'what about', 'how to use', 'dosage',
        'more', 'details', 'details', 'different', 'other'
    ]
    has_contextual_reference = any(keyword in query_lower for keyword in contextual_keywords)
    
    # Check if asking about something from previous response
    previous_context_words = ['also', 'also', 'still', 'additionally', 'besides', 'besides']
    references_previous = any(word in query_lower for word in previous_context_words)
    
    if products_referenced or has_contextual_reference or references_previous:
        debug_print(f"✅ [Follow-up Router] Found reference to cached content, using cache")
        state["routing_decisions"].append({
            "router": "route_follow_up",
            "decision": "cache_reference_found",
            "next_node": "handle_follow_up"
        })
        return "handle_follow_up"
    
    # If still unsure, check with LLM
    client = OpenAI(api_key=OPENAI_API_KEY)
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    # Create a more focused prompt
    cached_context_summary = f"Cached products: {', '.join([item.get('product_name', 'Unknown') for item in state.get('context_cache', [])])}"
    
    # Check if previous response mentioned a category
    category_mentioned = state.get("requested_category") is not None
    
    debug_print(f"🤔 [Follow-up Router] LLM check for cache sufficiency")
    
    prompt = f"""
Is the user's latest message asking about something from the previous response?

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---
{cached_context_summary}
Category was discussed: {category_mentioned}
---

The user might be:
1. Asking for more details about a mentioned product
2. Asking to compare mentioned products  
3. Asking "which one" from previously shown options
4. Using references like "it", "this", "that"
5. Asking about usage/dosage of discussed products
6. Asking about a different aspect of the same topic

Respond with only "yes" if the query is about cached content, or "no" if it needs new search.
"""
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL, 
            temperature=0, 
            messages=[{"role": "system", "content": prompt}]
        )
        decision = response.choices[0].message.content.strip().lower()
        
        debug_print(f"🤖 [Follow-up Router] LLM decision: '{decision}'")
        
        if "yes" in decision:
            debug_print(f"✅ [Follow-up Router] Cache is sufficient, routing to handle_follow_up")
            state["routing_decisions"].append({
                "router": "route_follow_up",
                "decision": f"llm_cache_sufficient: {decision}",
                "next_node": "handle_follow_up"
            })
            return "handle_follow_up"
        else:
            debug_print(f"❌ [Follow-up Router] Cache insufficient, routing to optimize_query")
            state["routing_decisions"].append({
                "router": "route_follow_up",
                "decision": f"llm_cache_insufficient: {decision}",
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
    debug_print("⚡ [Workflow] Performance improvement: ~10 seconds saved per query + reduced token usage")
        
    workflow = StateGraph(ConversationState)
    
    # Add nodes with timing wrapper
    nodes = [
        ("detect_intent", detect_intent_and_language),
        ("load_products", load_product_names),
        ("business_reasoner", business_reasoner),
        ("optimize_query", optimize_product_query),
        ("search_pinecone", search_products_k20),
        # 🗑️ REMOVED: ("intelligent_filter", intelligent_results_filter) - Business Reasoner does smart filtering
        ("evaluate_confidence", evaluate_confidence),
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
    # 🚀 SKIP intelligent_filter - Business Reasoner already does smart filtering
    workflow.add_edge("search_pinecone", "evaluate_confidence")
    workflow.add_conditional_edges(
        "evaluate_confidence", route_based_on_confidence,
        {
            "format_response": "format_response", 
            "escalate_support": "escalate_support"
        }
    )
    
    # All paths lead to END
    workflow.add_edge("format_response", END)
    workflow.add_edge("escalate_support", END)
    workflow.add_edge("handle_follow_up", END)
    
    debug_print("✅ [Workflow] Enhanced workflow with analytics created and compiled")
        
    return workflow.compile()

# Create and export the workflow app
app = create_workflow()

def set_workflow_analytics(analytics_instance):
    """Set the analytics instance for workflow timing capture"""
    global workflow_analytics
    workflow_analytics = analytics_instance