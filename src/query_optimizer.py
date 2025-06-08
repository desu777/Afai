"""
Query Optimization Module - Wersja 2.0
Optimizes user queries for better search results
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
    
    def _create_optimization_prompt(self, query: str, language: str) -> str:
        return f"""
You are an expert query analysis system for the Aquaforest search engine. Your task is to extract key information from the user's query and generate a set of highly effective, English-only search queries.

USER'S ORIGINAL QUERY: "{query}"
DETECTED LANGUAGE: {language}
LIST OF AVAILABLE AQUAFOREST PRODUCT NAMES:
---
{', '.join(self.product_names)}
---

YOUR TASK (follow these steps precisely):

1.  **Analyze the User's Intent:** What is the user's core question or problem? (e.g., "what is the dosage?", "how to solve high nitrates?", "what is this product for?").

2.  **Detect and Correct Product Name:**
    - Scan the original query for any mention of a product name.
    - Use the provided list of product names to find the EXACT, CORRECT product name. Correct any typos, abbreviations, or variations (e.g., "amino mix" -> "AF Amino Mix", "ca +" -> "Ca plus").
    - If no product name is mentioned, this is fine.

3.  **Generate Optimized Search Queries (English ONLY):**
    - Based on your analysis, generate a JSON array of 3-4 concise, effective search queries.
    - **Follow this logic:**
        - **IF a product name WAS DETECTED:**
            - Your FIRST query should be the exact, corrected product name and nothing else.
            - The other queries should combine the product name with the user's intent (e.g., "AF Amino Mix dosage", "AF Amino Mix how to use", "AF Amino Mix coral browning").
        - **IF NO product name was detected:**
            - Generate 3-4 variations of the user's problem in English (e.g., "how to reduce nitrates in reef tank", "nitrate reduction solutions", "best product for high nitrates").

4.  **Output Format:**
    - Return ONLY a single, valid JSON object. Do not add any text before or after the JSON.
    - The JSON object should have a single key "optimized_queries" containing an array of strings.

EXAMPLE 1:
User Query: "Jakie jest dawkowanie dla AF Amino Mix?"
Your Output:
{{
    "optimized_queries": [
        "AF Amino Mix",
        "AF Amino Mix dosage",
        "how to dose AF Amino Mix"
    ]
}}

EXAMPLE 2:
User Query: "Moje korale brązowieją"
Your Output:
{{
    "optimized_queries": [
        "corals turning brown",
        "how to fix brown corals",
        "coral browning problem solution"
    ]
}}
"""

    def optimize(self, state: ConversationState) -> ConversationState:
        """Optimize query for better search results"""
        query = state["user_query"]
        
        if TEST_ENV:
            print(f"\n🕵️ [DEBUG QueryOptimizer] Oryginalne zapytanie: '{query}'")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {
                        "role": "system", 
                        "content": self._create_optimization_prompt(query, state["detected_language"])
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