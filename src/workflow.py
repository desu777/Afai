"""
LangGraph Workflow Definition
Defines the complete RAG workflow using LangGraph
"""
from langgraph.graph import StateGraph, END
from models import ConversationState, Intent
from intent_detector import detect_intent_and_language
from query_optimizer import optimize_product_query
from pinecone_client import search_products_k15, enhanced_search_k20
from confidence_scorer import evaluate_confidence, route_based_on_confidence
from response_formatter import (
    format_final_response, 
    add_llm_knowledge, 
    escalate_to_human
)
import json
from config import PRODUCTS_FILE_PATH

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
    
    if intent == Intent.GREETING:
        return "format_response"
    elif intent == Intent.BUSINESS:
        return "format_response"
    elif intent == Intent.COMPETITOR:
        return "format_response"
    elif intent == Intent.CENSORED:
        return "format_response"
    elif intent == Intent.CALCULATOR:
        return "escalate_support"  # Calculator needs special handling
    elif intent == Intent.PRODUCT_QUERY:
        return "optimize_query"
    else:
        return "escalate_support"

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
    
    # Define edges
    workflow.add_edge("detect_intent", "load_products")
    workflow.add_conditional_edges(
        "load_products",
        route_intent,
        {
            "format_response": "format_response",
            "escalate_support": "escalate_support",
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
    
    # Set entry point
    workflow.set_entry_point("detect_intent")
    
    return workflow.compile()

# Create the compiled workflow
app = create_workflow()