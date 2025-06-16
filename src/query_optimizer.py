"""
Query Optimization Module - Version 3.0 with Category Support
Enhanced to work with business reasoner's category detection
"""
import json
import re
from typing import List, Dict
from openai import OpenAI
from models import ConversationState, QueryOptimizationResult
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, PRODUCTS_FILE_PATH, TEST_ENV, debug_print
from prompts import load_prompt_template

class QueryOptimizer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.product_names = self._load_product_names()
        self.common_mistakes = {
            "bio s": "Pro Bio S", "np pro": "-NP Pro", "amino mix": "AF Amino Mix",
            "ca+": "Ca plus", "ca +": "Ca plus", "nitraphos": "AF NitraPhos Minus",
            "component abc": ["Component A", "Component B", "Component C"],
            "calcium": "calcium", "nitrates": "nitrates", "phosphates": "phosphates",
            "algae": "algae", "corals": "corals", "browning": "brown turning brown",
            "brown": "brown",
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
        """Detect if query is comparing products"""
        comparison_patterns = [
            r'(.+?)\s+vs\.?\s+(.+)',
            r'(.+?)\s+versus\s+(.+)',
            r'difference between\s+(.+?)\s+and\s+(.+)',
            r'difference between\s+(.+?)\s+and\s+(.+)',
            r'compare\s+(.+?)\s+and\s+(.+)',
            r'compare\s+(.+?)\s+and\s+(.+)',
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
        """Create query optimization prompt using external template"""
        query = state["user_query"]
        language = state["detected_language"]
        chat_history = state.get("chat_history", [])
        
        # Format recent conversation for context
        conversation_context = ""
        if chat_history:
            recent_exchanges = chat_history[-4:]
            recent_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_exchanges])
            conversation_context = f"""--- CONVERSATION CONTEXT ---
{recent_context}
---"""
        
        # Check for comparison
        comparison_products = self._detect_comparison(query)
        
        # Get business intelligence context
        business_context = ""
        category_context = ""
        if state.get("business_analysis"):
            ba = state["business_analysis"]
            
            # Safe handling of products_in_category
            products_in_category = ba.get('products_in_category', [])
            if not isinstance(products_in_category, list):
                products_in_category = []
            
            # Safe handling of solutions_for_problem
            solutions_for_problem = ba.get('solutions_for_problem', [])
            if isinstance(solutions_for_problem, dict):
                # Extract solutions from dict structure
                solutions_list = []
                if 'correction' in solutions_for_problem:
                    solutions_list.extend(solutions_for_problem['correction'])
                if 'maintenance' in solutions_for_problem:
                    solutions_list.extend(solutions_for_problem['maintenance'])
                solutions_for_problem = solutions_list
            elif not isinstance(solutions_for_problem, list):
                solutions_for_problem = []
            
            business_context = f"""--- BUSINESS INTELLIGENCE ---
Business Interpretation: {ba.get('business_interpretation', 'N/A')}
Product Name Corrections: {ba.get('product_name_corrections', 'None')}
Category Requested: {ba.get('category_requested', 'None')}
Products in Category: {', '.join(products_in_category)}
Problem Identified: {ba.get('problem_identified', 'None')}
Solutions: {', '.join(solutions_for_problem)}
Domain Hint: {ba.get('domain_hint', 'unknown')}
Search Enhancement: {ba.get('search_enhancement', 'None')}
---"""
            # Special handling for category requests
            if ba.get('category_requested') and products_in_category:
                category_context = f"""🆕 CATEGORY REQUEST DETECTED: "{ba['category_requested']}"
Products to find: {', '.join(products_in_category)}

SPECIAL INSTRUCTIONS:
1. Create queries that will find ALL products in this category
2. Include the exact product names as separate queries
3. Add category-level queries like "{ba['category_requested']} products"
"""
        
        # ENHANCED PROMPT WITH COMPARISON SUPPORT
        comparison_instructions = ""
        if comparison_products:
            comparison_instructions = f"""🆕 COMPARISON DETECTED: User is comparing "{comparison_products[0]}" with "{comparison_products[1]}"

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
        
        # Try to load prompt from template
        prompt = load_prompt_template(
            "query_optimization",
            conversation_context=conversation_context,
            business_context=business_context,
            user_query=query,
            language=language,
            product_names=', '.join(self.product_names),
            category_context=category_context,
            comparison_instructions=comparison_instructions
        )
        
        # Fallback to simple prompt if template fails
        if not prompt:
            if TEST_ENV:
                print("⚠️ [QueryOptimizer] Using fallback hardcoded prompt")
            prompt = f"""
Generate search queries for: "{query}"
Return JSON: {{"optimized_queries": ["{query}"]}}
"""
        
        return prompt

    def optimize(self, state: ConversationState) -> ConversationState:
        """Optimize query for better search results"""
        query = state["user_query"]
        chat_history = state.get("chat_history", [])
        
        debug_print(f"🕵️ [QueryOptimizer] Original query: '{query}'")
        if chat_history:
            debug_print(f"📚 [QueryOptimizer] Context: last {len(chat_history[-4:])} messages")
        
        # Check for comparison
        comparison_products = self._detect_comparison(query)
        if comparison_products:
            debug_print(f"🔀 [QueryOptimizer] Product comparison detected: {comparison_products}")
        
        # Log business intelligence usage
        if state.get("business_analysis"):
            debug_print(f"🧠 [QueryOptimizer] Using business intelligence from business_reasoner")
            ba = state["business_analysis"]
            if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                debug_print(f"🔧 [QueryOptimizer] Product corrections: {ba['product_name_corrections']}")
            if ba.get("category_requested"):
                debug_print(f"📦 [QueryOptimizer] Category: {ba['category_requested']} with {len(ba.get('products_in_category', []))} products")
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
            
            # Store comparison info if detected
            if comparison_products:
                state["comparison_products"] = comparison_products
            
            debug_print(f"✅ [QueryOptimizer] Optimized queries for Pinecone: {state['optimized_queries']}")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG QueryOptimizer] Query optimization error: {e}")
            state["original_query"] = query
            
            # Fallback strategies
            if state.get("business_analysis", {}).get("products_in_category"):
                # If category detected, use product names as queries
                products_in_category = state["business_analysis"]["products_in_category"]
                if isinstance(products_in_category, list):
                    state["optimized_queries"] = products_in_category + [query]
                else:
                    state["optimized_queries"] = [query]
                debug_print(f"⚠️ [QueryOptimizer] Fallback to category products: {state['optimized_queries']}")
            elif comparison_products:
                # Fallback for comparisons
                state["optimized_queries"] = comparison_products + [query]
                debug_print(f"⚠️ [QueryOptimizer] Fallback for comparison: {state['optimized_queries']}")
            else:
                # Generic fallback
                state["optimized_queries"] = [query]
                debug_print(f"⚠️ [QueryOptimizer] Fallback to original query: {[query]}")
            
        return state

def optimize_product_query(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)