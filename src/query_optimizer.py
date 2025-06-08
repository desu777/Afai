"""
Query Optimization Module - Wersja 2.1
Optimizes user queries for better search results with conversation context
"""
import json
from typing import List, Dict
from openai import OpenAI
from models import ConversationState, QueryOptimizationResult
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, PRODUCTS_FILE_PATH, TEST_ENV

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
            print(f"Error loading products: {e}")
            return []
    
    def _create_optimization_prompt(self, query: str, language: str, chat_history: List[Dict]) -> str:
        # Format recent conversation for context
        recent_context = ""
        if chat_history:
            recent_exchanges = chat_history[-4:]  # Last 2 exchanges
            recent_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_exchanges])
        
        return f"""
You are an expert query analysis system for the Aquaforest search engine. Your task is to extract key information from the user's query and generate a set of highly effective, English-only search queries.

{'--- CONVERSATION CONTEXT ---' if recent_context else ''}
{recent_context}
{'---' if recent_context else ''}

USER'S CURRENT QUERY: "{query}"
DETECTED LANGUAGE: {language}
LIST OF AVAILABLE AQUAFOREST PRODUCT NAMES:
---
{', '.join(self.product_names)}
---

YOUR TASK (follow these steps precisely):

1.  **Analyze Context**: If the query contains references like "such", "that", "those", check the conversation history to understand what the user is referring to.

2.  **Identify Domain Context**: From the conversation, determine if discussing:
    - Freshwater aquarium → add "freshwater" to queries
    - Marine/saltwater aquarium → add "marine" or "saltwater" to queries
    - General aquarium → no domain modifier needed

3.  **Detect and Correct Product Name:**
    - Scan the original query for any mention of a product name.
    - Use the provided list of product names to find the EXACT, CORRECT product name.
    - If no product name is mentioned, this is fine.

4.  **Generate Optimized Search Queries (English ONLY):**
    - Generate 3-5 highly targeted queries based on context
    - Include domain modifiers when context is clear
    - For references like "such aquarium", expand based on conversation history
    
    Examples:
    - If user discussed freshwater and asks about "supplements for such aquarium"
      → ["freshwater aquarium supplements", "freshwater tank additives", "supplements for freshwater fish", "freshwater aquarium water conditioners"]
    - If user asks about specific problem in context
      → Include both general and context-specific queries

5.  **Output Format:**
    - Return ONLY a single, valid JSON object:
    {{
        "optimized_queries": ["query1", "query2", "query3", "query4"]
    }}
"""

    def optimize(self, state: ConversationState) -> ConversationState:
        """Optimize query for better search results"""
        query = state["user_query"]
        chat_history = state.get("chat_history", [])
        
        if TEST_ENV:
            print(f"\n🕵️ [DEBUG QueryOptimizer] Oryginalne zapytanie: '{query}'")
            if chat_history:
                print(f"📚 [DEBUG QueryOptimizer] Kontekst: ostatnie {len(chat_history[-4:])} wiadomości")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {
                        "role": "system", 
                        "content": self._create_optimization_prompt(query, state["detected_language"], chat_history)
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            state["original_query"] = query
            state["optimized_queries"] = result.get("optimized_queries", [query])
            
            if TEST_ENV:
                print(f"✅ [DEBUG QueryOptimizer] Zoptymalizowane zapytania do Pinecone: {state['optimized_queries']}")
                
        except Exception as e:
            print(f"Query optimization error: {e}")
            state["original_query"] = query
            state["optimized_queries"] = [query]
            if TEST_ENV:
                print(f"⚠️ [DEBUG QueryOptimizer] Błąd optymalizacji, użyto oryginalnego zapytania: {[query]}")
            
        return state

def optimize_product_query(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)