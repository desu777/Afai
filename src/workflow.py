"""
LangGraph Workflow Definition - VERSION 3.1 with Improved Follow-up
Enhanced follow-up routing, better cache utilization
"""
from langgraph.graph import StateGraph, END
from models import ConversationState, Intent
from openai import OpenAI
from intent_detector import detect_intent_and_language
from query_optimizer import optimize_product_query
from pinecone_client import search_products_k20
from results_filter import intelligent_results_filter
from confidence_scorer import evaluate_confidence, route_based_on_confidence
from response_formatter import format_final_response, escalate_to_human, handle_follow_up
import json
from config import PRODUCTS_FILE_PATH, OPENAI_API_KEY, OPENAI_MODEL, TEST_ENV, debug_print, ENHANCED_K_VALUE

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

def business_reasoner(state: ConversationState) -> ConversationState:
    """Business Logic Reasoner with competitor detection and product validation"""
    debug_print(f"🧠 [BusinessReasoner] Analyzing query: '{state['user_query']}'", "🧠")
    
    try:
        # Load business knowledge
        with open("data/products_turbo.json", 'r', encoding='utf-8') as f:
            products_knowledge = json.load(f)
        
        debug_print(f"📚 [BusinessReasoner] Loaded {len(products_knowledge)} products with business context")
        
        # 🆕 COMPETITOR LIST
        COMPETITORS = ["Red Sea", "Seachem", "Tropic Marin", "Brightwell", "Two Little Fishies", 
                      "Salifert", "Continuum", "Korallen-Zucht", "ESV", "Kent Marine"]
        
        # Check for competitors
        is_competitor_query = any(comp.lower() in state["user_query"].lower() for comp in COMPETITORS)
        if is_competitor_query:
            debug_print(f"🏢 [BusinessReasoner] Competitor detected in query")
            state["intent"] = Intent.COMPETITOR
        
        # Create relevant business context
        business_context = _create_business_context(state["user_query"], products_knowledge)
        context_lines = business_context.split('\n')
        debug_print(f"🎯 [BusinessReasoner] Created business context with {len(context_lines)} relevant items")
        
        # GPT reasoning with business knowledge
        business_analysis = _analyze_with_business_context(state, business_context)
        
        # Apply business intelligence to state
        if business_analysis:
            state["business_analysis"] = business_analysis
            
            # 🆕 Validate product names
            if business_analysis.get("product_name_corrections"):
                corrected_name = business_analysis["product_name_corrections"]
                if corrected_name != "None" and _validate_product_exists(corrected_name, state.get("product_names", [])):
                    debug_print(f"✅ [BusinessReasoner] Product name validated: {corrected_name}")
                else:
                    debug_print(f"⚠️ [BusinessReasoner] Product name not found in catalog: {corrected_name}")
            
            # Apply intent correction if suggested
            if business_analysis.get("intent_correction") and business_analysis["intent_correction"] != "same":
                old_intent = state["intent"]
                state["intent"] = business_analysis["intent_correction"]
                debug_print(f"✅ [BusinessReasoner] Intent corrected: {old_intent} → {state['intent']}")
            
            # Add domain hint
            if business_analysis.get("domain_hint") and business_analysis["domain_hint"] != "unknown":
                state["domain_filter"] = business_analysis["domain_hint"]
                debug_print(f"🎯 [BusinessReasoner] Domain detected: {business_analysis['domain_hint']}")
            
            # Add search enhancement context
            if business_analysis.get("search_enhancement"):
                state["search_context"] = business_analysis["search_enhancement"]
                debug_print(f"🔍 [BusinessReasoner] Search enhancement: {business_analysis['search_enhancement'][:100]}...")
            
            # 🆕 Store product for purchase inquiry
            if state["intent"] == Intent.PURCHASE_INQUIRY and business_analysis.get("product_name_corrections"):
                state["purchase_product"] = business_analysis["product_name_corrections"]
                debug_print(f"🛒 [BusinessReasoner] Purchase product identified: {state['purchase_product']}")
            
            debug_print(f"💡 [BusinessReasoner] Business interpretation: {business_analysis.get('business_interpretation', 'N/A')[:100]}...")
        
    except Exception as e:
        debug_print(f"❌ [BusinessReasoner] Error: {e}")
        # Fallback - continue without business analysis
        pass
    
    return state

def _validate_product_exists(product_name: str, product_list: list[str]) -> bool:
    """🆕 Validate if product exists in catalog"""
    return any(product_name.lower() in p.lower() for p in product_list)

def _create_business_context(query: str, products: list) -> str:
    """Create relevant business context from structured data"""
    query_words = set(query.lower().split())
    relevant_products = []
    
    for product in products:
        # Check if product might be relevant (loose semantic check)
        product_text = " ".join([
            product.get("product_name", ""),
            " ".join(product.get("keywords", [])),
            " ".join(product.get("solves_problems", [])),
            product.get("use_case", "")
        ]).lower()
        
        # If any query word appears in product context
        if any(word in product_text for word in query_words if len(word) > 2):
            relevant_products.append(product)
        
        # Stop at reasonable limit
        if len(relevant_products) >= 15:
            break
    
    # Format for GPT context
    context_lines = []
    for p in relevant_products[:10]:  # Top 10 most relevant
        context_lines.append(
            f"- {p['product_name']}: {p.get('use_case', 'N/A')[:80]}... "
            f"Solves: {', '.join(p.get('solves_problems', [])[:3])}"
        )
    
    return "\\n".join(context_lines) if context_lines else "No directly relevant products found."

def _analyze_with_business_context(state: ConversationState, business_context: str) -> dict:
    """GPT reasoning with business knowledge"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    chat_history_context = ""
    if state.get("chat_history"):
        recent_messages = state["chat_history"][-4:]  # Last 2 exchanges
        chat_history_context = "\\nRECENT CONVERSATION:\\n" + "\\n".join([
            f"{msg['role']}: {msg['content'][:100]}..." for msg in recent_messages
        ])
    
    prompt = f"""You are an expert aquarium business analyst with deep product knowledge.

USER QUERY: "{state['user_query']}"
DETECTED INTENT: {state['intent']}
DETECTED LANGUAGE: {state.get('detected_language', 'unknown')}
{chat_history_context}

RELEVANT BUSINESS KNOWLEDGE:
{business_context}

BUSINESS LOGIC ANALYSIS:
Analyze this query with aquarium business intelligence:

1. PRODUCT NAME CORRECTIONS: Are there typos or common names?
   - "nitraphos" → "AF NitraPhos Minus"
   - "bio s" → "Pro Bio S"  
   - "amino mixa" → "AF Amino Mix"

2. BUSINESS INTERPRETATION: What does user REALLY want?
   - "kupić aiptasię" → wants Aiptasia TREATMENT (Aiptasia Shot), not aiptasia itself
   - "potrzebuję czegoś na żelazo" → needs iron supplements/products for aquarium
   - "na żelazo", "iron", "Fe" → looking for iron-related products  
   - "te produkty" → refers to previous context
   - "nitraphos" → likely means "AF NitraPhos Minus"

3. DOMAIN DETECTION: Freshwater, marine, or universal?
   - Look for clues: "słodkowodne", "SPS", "korale", "rafy", etc.

4. INTENT VERIFICATION: Is the detected intent correct?
   - "potrzebuję czegoś na żelazo" should be PRODUCT_QUERY, not purchase_inquiry
   - Questions about specific products without "kupić/buy" keywords should be PRODUCT_QUERY  
   - Only direct purchase requests ("gdzie kupić", "jak zamówić") should be purchase_inquiry

Respond ONLY with valid JSON:
{{
  "business_interpretation": "clear explanation of what user wants",
  "product_name_corrections": "any typos or alternative names identified",
  "intent_correction": "product_query|purchase_inquiry|same",
  "domain_hint": "freshwater|seawater|universal|unknown",
  "search_enhancement": "specific terms and context to enhance search"
}}"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            messages=[{"role": "system", "content": prompt}]
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        debug_print(f"🤖 [BusinessReasoner] GPT analysis completed")
        return result
        
    except json.JSONDecodeError as e:
        debug_print(f"❌ [BusinessReasoner] JSON parsing error: {e}")
        return {}
    except Exception as e:
        debug_print(f"❌ [BusinessReasoner] GPT analysis error: {e}")
        return {}

def route_intent(state: ConversationState) -> str:
    """Route based on detected intent"""
    intent = state.get("intent", Intent.OTHER)
    
    debug_print(f"🚦 [Router] Routing for intent='{intent}'")
    
    if intent in [Intent.GREETING, Intent.BUSINESS, Intent.COMPETITOR, 
                  Intent.CENSORED, Intent.PURCHASE_INQUIRY]:
        debug_print(f"➡️ [Router] Routing to: format_response (special intent)")
        return "format_response"
    elif intent == Intent.PRODUCT_QUERY:
        debug_print(f"➡️ [Router] Routing to: optimize_query (product query)")
        return "optimize_query"
    elif intent == Intent.FOLLOW_UP:
        debug_print(f"➡️ [Router] Routing to: follow_up_router (follow-up question)")
        return "follow_up_router"
    else:
        debug_print(f"➡️ [Router] Routing to: escalate_support (unknown intent)")
        return "escalate_support"

def follow_up_router(state: ConversationState) -> dict:
    debug_print(f"🔄 [Follow-up Router] Checking if can handle follow-up with cache")
    return {}

def route_follow_up(state: ConversationState) -> str:
    """🆕 IMPROVED follow-up router with better cache utilization"""
    if not state.get("context_cache"):
        debug_print(f"❌ [Follow-up Router] No cache, routing to optimize_query")
        return "optimize_query"
    
    # 🆕 Check if query references cached products
    cached_products = []
    for item in state.get("context_cache", []):
        if item.get('product_name'):
            cached_products.append(item['product_name'].lower())
    
    query_lower = state["user_query"].lower()
    
    # Check for product references
    products_referenced = any(product in query_lower for product in cached_products)
    
    # Check for contextual references
    contextual_keywords = ['to', 'ten', 'ta', 'te', 'it', 'this', 'that', 'those', 
                          'jeden', 'który', 'która', 'które', 'which', 'one']
    has_contextual_reference = any(keyword in query_lower for keyword in contextual_keywords)
    
    if products_referenced or has_contextual_reference:
        debug_print(f"✅ [Follow-up Router] Found reference to cached content, using cache")
        return "handle_follow_up"
    
    # If still unsure, use LLM check
    client = OpenAI(api_key=OPENAI_API_KEY)
    chat_history_formatted = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    # Create a more focused prompt
    cached_context_summary = f"Cached products: {', '.join([item.get('product_name', 'Unknown') for item in state.get('context_cache', [])])}"
    
    debug_print(f"🤔 [Follow-up Router] LLM check for cache sufficiency")
    
    prompt = f"""
Is the user's latest message asking about something from the previous response?

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---
{cached_context_summary}
---

The user might be:
1. Asking for more details about a mentioned product
2. Asking to compare mentioned products
3. Asking "which one" from previously shown options
4. Using references like "it", "this", "that"

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
            return "handle_follow_up"
        else:
            debug_print(f"❌ [Follow-up Router] Cache insufficient, routing to optimize_query")
            return "optimize_query"
            
    except Exception as e:
        if TEST_ENV:
            print(f"❌ [DEBUG Follow-up Router] Context check error: {e}")
        debug_print(f"❌ [Follow-up Router] Context check error: {e}")
        return "optimize_query"

def create_workflow() -> StateGraph:
    """Create the enhanced LangGraph workflow"""
    debug_print("🏗️ [Workflow] Creating enhanced LangGraph workflow...")
    debug_print(f"🔧 [Workflow] Using ENHANCED_K_VALUE={ENHANCED_K_VALUE}")
        
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    nodes = [
        ("detect_intent", detect_intent_and_language),
        ("load_products", load_product_names),
        ("business_reasoner", business_reasoner),
        ("optimize_query", optimize_product_query),
        ("search_pinecone", search_products_k20),
        ("intelligent_filter", intelligent_results_filter),
        ("evaluate_confidence", evaluate_confidence),
        ("format_response", format_final_response),
        ("escalate_support", escalate_to_human),
        ("handle_follow_up", handle_follow_up),
        ("follow_up_router", follow_up_router)
    ]
    
    for node_name, node_func in nodes:
        workflow.add_node(node_name, node_func)
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
    workflow.add_edge("search_pinecone", "intelligent_filter")
    workflow.add_edge("intelligent_filter", "evaluate_confidence")
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
    
    debug_print("✅ [Workflow] Enhanced workflow created and compiled")
        
    return workflow.compile()

app = create_workflow()