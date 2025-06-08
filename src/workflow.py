"""
LangGraph Workflow Definition
Defines the complete RAG workflow using LangGraph
"""
from langgraph.graph import StateGraph, END
from models import ConversationState, Intent
from openai import OpenAI
from intent_detector import detect_intent_and_language
from query_optimizer import optimize_product_query
from pinecone_client import search_products_k15, enhanced_search_k20
from confidence_scorer import evaluate_confidence, route_based_on_confidence
from response_formatter import (
    format_final_response, 
    add_llm_knowledge, 
    escalate_to_human,
    handle_follow_up
)
import json
from config import PRODUCTS_FILE_PATH, OPENAI_API_KEY, OPENAI_MODEL

def load_product_names(state: ConversationState) -> ConversationState:
    """Load product names into state"""
    try:
        with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            state["product_names"] = data  # Now it's a simple array of strings
    except Exception as e:
        print(f"Error loading products: {e}")
        state["product_names"] = []
    return state

def route_intent(state: ConversationState) -> str:
    """Route based on detected intent"""
    intent = state.get("intent", Intent.OTHER)
    
    if intent in [Intent.GREETING, Intent.BUSINESS, Intent.COMPETITOR, Intent.CENSORED, Intent.PURCHASE_INQUIRY]:
        return "format_response"
    elif intent == Intent.CALCULATOR:
        return "escalate_support"
    elif intent == Intent.PRODUCT_QUERY:
        return "optimize_query"
    elif intent == Intent.FOLLOW_UP:
        # Before handling a follow-up, check if the context is sufficient
        return "follow_up_router"
    else:
        return "escalate_support"

def follow_up_router(state: ConversationState) -> dict:
    """A dummy node to anchor the conditional edge for follow-ups."""
    return {}

def route_follow_up(state: ConversationState) -> str:
    """
    An LLM-based router that checks if the cached context is sufficient
    to answer a follow-up question. This is a CONDITIONAL EDGE function.
    """
    if not state.get("context_cache"):
        # If there's no cache, we must treat it as a new query
        return "optimize_query"

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    cached_context_formatted = "\n".join([str(item) for item in state.get("context_cache", [])])

    prompt = f"""
As an expert routing system, your task is to determine if the information in the `CACHED INFORMATION` is sufficient to answer the `LATEST USER MESSAGE`.
The user is asking a follow-up question.

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---
CACHED INFORMATION (from the previous response):
{cached_context_formatted}
---

Is the `CACHED INFORMATION` sufficient to fully answer the `LATEST USER MESSAGE`?
Respond with only "yes" or "no".
"""
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0,
            messages=[{"role": "system", "content": prompt}]
        )
        decision = response.choices[0].message.content.strip().lower()
        if "yes" in decision:
            # The context is sufficient, use the cache
            return "handle_follow_up"
        else:
            # The context is NOT sufficient, treat as a new query
            return "optimize_query"
    except Exception as e:
        print(f"Context check for follow-up failed: {e}")
        # Fallback to treating it as a new query
        return "optimize_query"

def create_workflow() -> StateGraph:
    """Create the LangGraph workflow"""
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("detect_intent", detect_intent_and_language)
    workflow.add_node("load_products", load_product_names)
    workflow.add_node("optimize_query", optimize_product_query)
    workflow.add_node("search_pinecone", search_products_k15)
    workflow.add_node("evaluate_confidence", evaluate_confidence)
    workflow.add_node("reasoning_retry", enhanced_search_k20)
    workflow.add_node("format_response", format_final_response)
    workflow.add_node("add_llm_knowledge", add_llm_knowledge)
    workflow.add_node("escalate_support", escalate_to_human)
    workflow.add_node("handle_follow_up", handle_follow_up)
    workflow.add_node("follow_up_router", follow_up_router)
    
    # Define edges
    workflow.add_edge("detect_intent", "load_products")
    workflow.add_conditional_edges(
        "load_products",
        route_intent,
        {
            "format_response": "format_response",
            "escalate_support": "escalate_support",
            "optimize_query": "optimize_query",
            "follow_up_router": "follow_up_router"
        }
    )

    # New conditional edge for the follow-up router
    workflow.add_conditional_edges(
        "follow_up_router",
        route_follow_up,
        {
            "handle_follow_up": "handle_follow_up",
            "optimize_query": "optimize_query"
        }
    )

    workflow.add_edge("optimize_query", "search_pinecone")
    workflow.add_edge("search_pinecone", "evaluate_confidence")
    
    # Conditional routing based on confidence
    workflow.add_conditional_edges(
        "evaluate_confidence",
        route_based_on_confidence,
        {
            "format_response": "format_response",
            "reasoning_retry": "reasoning_retry",
            "add_llm_knowledge": "add_llm_knowledge",
            "escalate_support": "escalate_support"
        }
    )
    
    # After reasoning retry, re-evaluate
    workflow.add_edge("reasoning_retry", "evaluate_confidence")
    
    # All paths lead to END
    workflow.add_edge("format_response", END)
    workflow.add_edge("add_llm_knowledge", END)
    workflow.add_edge("escalate_support", END)
    workflow.add_edge("handle_follow_up", END)
    
    # Set entry point
    workflow.set_entry_point("detect_intent")
    
    return workflow.compile()

# Create the compiled workflow
app = create_workflow()