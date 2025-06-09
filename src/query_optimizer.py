"""
Query Optimization Module - Wersja 2.1
Optimizes user queries for better search results with conversation context
"""
import json
from typing import List, Dict
from openai import OpenAI
from models import ConversationState, QueryOptimizationResult
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, PRODUCTS_FILE_PATH, TEST_ENV, debug_print

class QueryOptimizer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.product_names = self._load_product_names()
        self.common_mistakes = {
            "bio s": "Pro Bio S", "np pro": "-NP Pro", "amino mix": "AF Amino Mix",
            "ca+": "Ca plus", "ca +": "Ca plus", "nitraphos": "AF NitraPhos Minus",
            "component abc": ["Component A", "Component B", "Component C"],
            "wapń": "calcium", "azotany": "nitrates", "fosforany": "phosphates",
            "glony": "algae", "koralowce": "corals", "brązowieją": "brown turning brown",
            "brązowe": "brown",
        }
        
    def _load_product_names(self) -> List[str]:
        """Load product names from JSON file"""
        try:
            with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG QueryOptimizer] Error loading products: {e}")
            return []
    
    def _create_optimization_prompt(self, state: ConversationState) -> str:
        query = state["user_query"]
        language = state["detected_language"]
        chat_history = state.get("chat_history", [])
        
        # Format recent conversation for context
        recent_context = ""
        if chat_history:
            recent_exchanges = chat_history[-4:]  # Last 2 exchanges
            recent_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_exchanges])
        
        # 🆕 NEW: Get business intelligence context
        business_context = ""
        if state.get("business_analysis"):
            ba = state["business_analysis"]
            business_context = f"""
--- BUSINESS INTELLIGENCE ---
Business Interpretation: {ba.get('business_interpretation', 'N/A')}
Product Name Corrections: {ba.get('product_name_corrections', 'None')}
Domain Hint: {ba.get('domain_hint', 'unknown')}
Search Enhancement: {ba.get('search_enhancement', 'None')}
---
"""
        
        return f"""
You are an expert query analysis system for the Aquaforest search engine. Your task is to extract key information from the user's query and generate a set of highly effective, English-only search queries.

{'--- CONVERSATION CONTEXT ---' if recent_context else ''}
{recent_context}
{'---' if recent_context else ''}

{business_context}

USER'S CURRENT QUERY: "{query}"
DETECTED LANGUAGE: {language}
LIST OF AVAILABLE AQUAFOREST PRODUCT NAMES:
---
{', '.join(self.product_names)}
---

YOUR TASK (follow these steps precisely):

1.  **Use Business Intelligence**: If business intelligence is provided above, incorporate those insights:
    - Use corrected product names
    - Apply domain hints (freshwater/marine/seawater)
    - Include search enhancement suggestions
    - Follow business interpretation guidance

2.  **Analyze Context**: If the query contains references like "such", "that", "those", check the conversation history to understand what the user is referring to.

3.  **Identify Domain Context**: From business hints or conversation, determine if discussing:
    - Freshwater aquarium → add "freshwater" to queries
    - Marine/saltwater aquarium → add "marine" or "saltwater" to queries
    - General aquarium → no domain modifier needed

4.  **Detect and Correct Product Name:**
    - Use business intelligence corrections first
    - Scan the original query for any mention of a product name
    - Use the provided list of product names to find the EXACT, CORRECT product name
    - If no product name is mentioned, this is fine

5.  **Generate Optimized Search Queries (English ONLY):**
    - Generate 3-5 highly targeted queries based on context and business intelligence
    - Include domain modifiers when context is clear
    - For references like "such aquarium", expand based on conversation history
    - Prioritize business intelligence suggestions
    
    Examples:
    - If business intelligence suggests "AF NitraPhos Minus" for "nitraphos"
      → ["AF NitraPhos Minus", "nitrate phosphate reduction", "NO3 PO4 removal"]
    - If domain hint is "seawater" and query about pH
      → ["marine aquarium pH problems", "reef tank pH solutions", "saltwater pH control"]

6.  **Output Format:**
    - Return ONLY a single, valid JSON object:
    {{
        "optimized_queries": ["query1", "query2", "query3", "query4"]
    }}
"""

    def optimize(self, state: ConversationState) -> ConversationState:
        """Optimize query for better search results"""
        query = state["user_query"]
        chat_history = state.get("chat_history", [])
        
        debug_print(f"🕵️ [QueryOptimizer] Oryginalne zapytanie: '{query}'")
        if chat_history:
            debug_print(f"📚 [QueryOptimizer] Kontekst: ostatnie {len(chat_history[-4:])} wiadomości")
        
        # 🆕 NEW: Log business intelligence usage
        if state.get("business_analysis"):
            debug_print(f"🧠 [QueryOptimizer] Using business intelligence from business_reasoner")
            ba = state["business_analysis"]
            if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                debug_print(f"🔧 [QueryOptimizer] Product corrections: {ba['product_name_corrections']}")
            if ba.get("domain_hint") and ba["domain_hint"] != "unknown":
                debug_print(f"🎯 [QueryOptimizer] Domain hint: {ba['domain_hint']}")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {
                        "role": "system", 
                        "content": self._create_optimization_prompt(state)  # 🆕 Pass full state
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            state["original_query"] = query
            state["optimized_queries"] = result.get("optimized_queries", [query])
            
            debug_print(f"✅ [QueryOptimizer] Zoptymalizowane zapytania do Pinecone: {state['optimized_queries']}")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG QueryOptimizer] Query optimization error: {e}")
            state["original_query"] = query
            state["optimized_queries"] = [query]
            debug_print(f"⚠️ [QueryOptimizer] Błąd optymalizacji, użyto oryginalnego zapytania: {[query]}")
            
        return state

def optimize_product_query(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)