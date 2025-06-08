"""
Query Optimization Module
Optimizes user queries for better search results
"""
import json
from typing import List, Dict
from openai import OpenAI
from models import ConversationState, QueryOptimizationResult
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, PRODUCTS_FILE_PATH

class QueryOptimizer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.product_names = self._load_product_names()
        self.common_mistakes = {
            # Common user mistakes → correct product names
            "bio s": "Pro Bio S",
            "np pro": "-NP Pro",
            "amino mix": "AF Amino Mix",
            "ca+": "Ca plus",
            "ca +": "Ca plus",
            "nitraphos": "AF NitraPhos Minus",
            "component abc": ["Component A", "Component B", "Component C"],
            # Polish translations
            "wapń": "calcium",
            "azotany": "nitrates", 
            "fosforany": "phosphates",
            "glony": "algae",
            "koralowce": "corals",
            "brązowieją": "brown turning brown",
            "brązowe": "brown",
        }
        
    def _load_product_names(self) -> List[str]:
        """Load product names from JSON file"""
        try:
            with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data  # Now it's a simple array of strings
        except Exception as e:
            print(f"Error loading products: {e}")
            return []
    
    def _create_optimization_prompt(self, query: str, language: str) -> str:
        return f"""
You are a query optimizer for Aquaforest aquarium products search system.

User query: "{query}"
Detected language: {language}

AVAILABLE PRODUCT NAMES (DO NOT TRANSLATE THESE):
{', '.join(self.product_names[:50])}  # Show first 50 as example

TASK:
1. Create 2-3 optimized search queries in simple English
2. Extract key problems/symptoms (nitrates, phosphates, algae, coral color, etc.)
3. Preserve exact product names if mentioned
4. Translate non-English parts to English
5. Expand abbreviations and fix common mistakes
6. Add related search terms

RULES:
- Keep queries concise (2-6 words)
- Focus on problems AND solutions
- Never translate product names
- Include both symptoms and solutions

Return JSON:
{{
    "original_query": "{query}",
    "optimized_queries": ["query1", "query2", "query3"],
    "detected_products": ["product names found in query"],
    "detected_problems": ["problems/symptoms mentioned"]
}}
"""

    def optimize(self, state: ConversationState) -> ConversationState:
        """Optimize query for better search results"""
        query = state["user_query"]
        
        # First, fix common mistakes
        fixed_query = query.lower()
        for mistake, correction in self.common_mistakes.items():
            if mistake in fixed_query:
                if isinstance(correction, list):
                    fixed_query = fixed_query.replace(mistake, ' '.join(correction))
                else:
                    fixed_query = fixed_query.replace(mistake, correction)
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {
                        "role": "system", 
                        "content": self._create_optimization_prompt(fixed_query, state["detected_language"])
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Update state
            state["original_query"] = query
            state["optimized_queries"] = result.get("optimized_queries", [fixed_query])
            
            # Add the original query if not in English
            if state["detected_language"] != "en":
                state["optimized_queries"].append(query)
                
        except Exception as e:
            print(f"Query optimization error: {e}")
            # Fallback
            state["original_query"] = query
            state["optimized_queries"] = [fixed_query, query]
            
        return state

def optimize_product_query(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)