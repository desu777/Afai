"""
Query Optimization Module - Version 2.2 with Comparison Support
Optimizes user queries for better search results with conversation context and product comparisons
"""
import json
import re
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
    
    def _detect_comparison(self, query: str) -> List[str]:
        """🆕 Detect if query is comparing products"""
        comparison_patterns = [
            r'(.+?)\s+vs\.?\s+(.+)',  # product1 vs product2
            r'(.+?)\s+versus\s+(.+)',  # product1 versus product2
            r'różnica między\s+(.+?)\s+a\s+(.+)',  # różnica między X a Y
            r'difference between\s+(.+?)\s+and\s+(.+)',  # difference between X and Y
            r'porównaj\s+(.+?)\s+i\s+(.+)',  # porównaj X i Y
            r'compare\s+(.+?)\s+and\s+(.+)',  # compare X and Y
        ]
        
        for pattern in comparison_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                product1 = match.group(1).strip()
                product2 = match.group(2).strip()
                if TEST_ENV:
                    print(f"🔍 [QueryOptimizer] Detected comparison: '{product1}' vs '{product2}'")
                return [product1, product2]
        return []
    
    def _create_optimization_prompt(self, state: ConversationState) -> str:
        query = state["user_query"]
        language = state["detected_language"]
        chat_history = state.get("chat_history", [])
        
        # Format recent conversation for context
        recent_context = ""
        if chat_history:
            recent_exchanges = chat_history[-4:]
            recent_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_exchanges])
        
        # 🆕 Check for comparison
        comparison_products = self._detect_comparison(query)
        
        # Get business intelligence context
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
        
        # 🆕 ENHANCED PROMPT WITH COMPARISON SUPPORT
        comparison_instructions = ""
        if comparison_products:
            comparison_instructions = f"""
🆕 COMPARISON DETECTED: User is comparing "{comparison_products[0]}" with "{comparison_products[1]}"

SPECIAL INSTRUCTIONS FOR COMPARISONS:
1. Create SEPARATE search queries for EACH product being compared
2. Find the exact product names from the list
3. Include queries that will help find both products' features
4. Add general comparison queries

Example: For "lava soil vs lava soil black":
- "AF Lava Soil"
- "AF Lava Soil Black"
- "lava soil substrate properties"
- "black lava soil aquarium benefits"
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

{comparison_instructions}

YOUR TASK (follow these steps precisely):

1. **Use Business Intelligence**: If business intelligence is provided above, incorporate those insights
2. **Analyze Context**: If the query contains references like "such", "that", "those", check conversation history
3. **Identify Domain Context**: Determine if discussing freshwater/marine/general aquarium
4. **Detect and Correct Product Names**: Use business intelligence corrections first
5. **Handle Comparisons**: If comparing products, create separate queries for each

6. **Generate Optimized Search Queries (English ONLY)**:
   - Generate 3-6 highly targeted queries
   - For comparisons: include separate queries for each product
   - Include domain modifiers when context is clear
   - Prioritize business intelligence suggestions
   
   Examples:
   - Product comparison: ["AF Lava Soil", "AF Lava Soil Black", "lava soil substrate comparison", "black vs brown lava soil"]
   - Business correction: ["AF NitraPhos Minus", "nitrate phosphate reduction", "NO3 PO4 removal"]
   - Domain specific: ["marine aquarium pH problems", "reef tank pH solutions", "saltwater pH control"]

7. **Output Format**:
   - Return ONLY a single, valid JSON object:
   {{
       "optimized_queries": ["query1", "query2", "query3", "query4", "query5"]
   }}
"""

    def optimize(self, state: ConversationState) -> ConversationState:
        """Optimize query for better search results"""
        query = state["user_query"]
        chat_history = state.get("chat_history", [])
        
        debug_print(f"🕵️ [QueryOptimizer] Original query: '{query}'")
        if chat_history:
            debug_print(f"📚 [QueryOptimizer] Context: last {len(chat_history[-4:])} messages")
        
        # 🆕 Check for comparison
        comparison_products = self._detect_comparison(query)
        if comparison_products:
            debug_print(f"🔀 [QueryOptimizer] Product comparison detected: {comparison_products}")
        
        # Log business intelligence usage
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
                        "content": self._create_optimization_prompt(state)
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            state["original_query"] = query
            state["optimized_queries"] = result.get("optimized_queries", [query])
            
            # 🆕 Store comparison info if detected
            if comparison_products:
                state["comparison_products"] = comparison_products
            
            debug_print(f"✅ [QueryOptimizer] Optimized queries for Pinecone: {state['optimized_queries']}")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG QueryOptimizer] Query optimization error: {e}")
            state["original_query"] = query
            
            # 🆕 Fallback for comparisons
            if comparison_products:
                state["optimized_queries"] = comparison_products + [query]
                debug_print(f"⚠️ [QueryOptimizer] Fallback for comparison: {state['optimized_queries']}")
            else:
                state["optimized_queries"] = [query]
                debug_print(f"⚠️ [QueryOptimizer] Fallback to original query: {[query]}")
            
        return state

def optimize_product_query(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)