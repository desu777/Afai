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
        # Convert common_mistakes to a readable string format for the prompt
        mistakes_examples = "\n".join([f'- "{k}" -> "{v if not isinstance(v, list) else " ".join(v)}"' for k, v in self.common_mistakes.items()])

        return f"""
You are an intelligent query optimizer for the Aquaforest aquarium products search system.
Your goal is to correct, translate, and expand the user's query to improve search accuracy.

USER'S ORIGINAL QUERY: "{query}"
DETECTED LANGUAGE: {language}

Here is the complete list of AVAILABLE AQUAFOREST PRODUCT NAMES:
---
{', '.join(self.product_names)}
---

TASK:
1.  **Analyze the original query:** Understand the user's core problem (e.g., high nitrates, algae, coral health).
2.  **Translate to English:** If the query is not in English, translate the problem description, but NEVER translate the product names.
3.  **Correct and Normalize Product Names:**
    -   If you see a product name mentioned, ensure it EXACTLY matches one from the provided list.
    -   Fix common typos, abbreviations, or mistakes. Here are some examples of corrections:
{mistakes_examples}
4.  **Enrich General Queries:** For broad, non-product-specific questions, add descriptive hints to guide the search. For example:
    - If the user asks "how to set up an aquarium" or "getting started guide", enrich the query with terms like `(guide, tutorial, how to start, setup)`.
    - If the user asks "what aquariums do you offer" or "aquarium models", enrich the query with terms like `(AF OceanGuard Aquarium Set, aquarium models and versions)`.
    - If the user asks about "supplements for corals", enrich with `(supplements, coral care, dosing)`.
5.  **Create Optimized Queries:** Generate 2-3 concise, optimized search queries in English. These queries should focus on the core problem and the corrected product names.
    -   Good queries are 2-6 words long.
    -   Combine problems with solutions (e.g., "nitrate reduction -NP Pro", "boost coral color AF Amino Mix").

OUTPUT FORMAT:
Return a single, valid JSON object with the following structure. Do not add any text before or after the JSON.
{{
    "original_query": "{query}",
    "optimized_queries": ["english_query_1", "english_query_2", "english_query_3"],
    "detected_products": ["list of exact product names found in the query"],
    "detected_problems": ["list of key problems/symptoms identified"]
}}
"""

    def optimize(self, state: ConversationState) -> ConversationState:
        """Optimize query for better search results"""
        query = state["user_query"]
        
        # The string replacement logic is now removed.
        # The LLM will handle corrections based on the improved prompt.
        
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
            
            # Update state
            state["original_query"] = query
            state["optimized_queries"] = result.get("optimized_queries", [query])
            
            # Add the original query if not in English
            if state["detected_language"] != "en":
                state["optimized_queries"].append(query)
                
        except Exception as e:
            print(f"Query optimization error: {e}")
            # Fallback
            state["original_query"] = query
            state["optimized_queries"] = [query]
            
        return state

def optimize_product_query(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)