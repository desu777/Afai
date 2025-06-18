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
        
        # 🆕 ENHANCED: Include guaranteed products info
        guaranteed_products = state.get("guaranteed_products", [])
        guaranteed_products_text = ', '.join(guaranteed_products) if guaranteed_products else "None"
        
        # Try to load prompt from template
        prompt = load_prompt_template(
            "query_optimization",
            conversation_context=conversation_context,
            business_context=business_context,
            user_query=query,
            language=language,
            product_names=', '.join(self.product_names),
            guaranteed_products=guaranteed_products_text,
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
        """Optimize query for better search results with enhanced intelligence"""
        query = state["user_query"]
        chat_history = state.get("chat_history", [])
        
        debug_print(f"🕵️ [QueryOptimizer] Original query: '{query}'")
        if chat_history:
            debug_print(f"📚 [QueryOptimizer] Context: last {len(chat_history[-4:])} messages")
        
        # 🆕 ENHANCED: Extract mentioned products from user query
        mentioned_products = self._extract_mentioned_products(query)
        if mentioned_products:
            debug_print(f"🎯 [QueryOptimizer] User mentioned products: {mentioned_products}")
        
        # Check for comparison
        comparison_products = self._detect_comparison(query)
        if comparison_products:
            debug_print(f"🔀 [QueryOptimizer] Product comparison detected: {comparison_products}")
        
        # 🆕 ENHANCED: Collect all critical queries BEFORE LLM call
        critical_queries = []
        guaranteed_products = set()  # Track products we'll find via guaranteed search
        
        # Add mentioned products as high-priority queries
        critical_queries.extend(mentioned_products)
        guaranteed_products.update(mentioned_products)
        
        # 🚀 ENHANCED: Add AF alternatives from competitor detection
        if state.get("af_alternatives_to_search"):
            af_alternatives = state["af_alternatives_to_search"]
            debug_print(f"🎯 [QueryOptimizer] Adding AF alternatives: {af_alternatives}")
            critical_queries.extend(af_alternatives)
            guaranteed_products.update(af_alternatives)
        
        # Log business intelligence usage and extract solutions
        if state.get("business_analysis"):
            debug_print(f"🧠 [QueryOptimizer] Using business intelligence from business_reasoner")
            ba = state["business_analysis"]
            
            if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                debug_print(f"🔧 [QueryOptimizer] Product corrections: {ba['product_name_corrections']}")
                critical_queries.append(ba["product_name_corrections"])
                guaranteed_products.add(ba["product_name_corrections"])
            
            if ba.get("category_requested"):
                debug_print(f"📦 [QueryOptimizer] Category: {ba['category_requested']} with {len(ba.get('products_in_category', []))} products")
                # Add all category products as critical queries
                products_in_category = ba.get('products_in_category', [])
                if isinstance(products_in_category, list):
                    critical_queries.extend(products_in_category)
                    guaranteed_products.update(products_in_category)
            
            # 🆕 ENHANCED: Add solution products as critical queries
            solutions_for_problem = ba.get('solutions_for_problem', [])
            if isinstance(solutions_for_problem, dict):
                # Extract solutions from dict structure
                if 'correction' in solutions_for_problem:
                    critical_queries.extend(solutions_for_problem['correction'])
                    guaranteed_products.update(solutions_for_problem['correction'])
                if 'maintenance' in solutions_for_problem:
                    critical_queries.extend(solutions_for_problem['maintenance'])
                    guaranteed_products.update(solutions_for_problem['maintenance'])
            elif isinstance(solutions_for_problem, list):
                critical_queries.extend(solutions_for_problem)
                guaranteed_products.update(solutions_for_problem)
            
            # 🆕 ENHANCED: Add problem-specific queries (NOT product-specific)
            if ba.get("problem_identified"):
                domain = ba.get("domain_hint", "unknown")
                problem_queries = self._create_problem_queries(ba["problem_identified"], domain)
                critical_queries.extend(problem_queries)
                debug_print(f"🔧 [QueryOptimizer] Added {len(problem_queries)} problem-specific queries for: {ba['problem_identified']}")
            
            if ba.get("domain_hint") and ba["domain_hint"] != "unknown":
                debug_print(f"🎯 [QueryOptimizer] Domain hint: {ba['domain_hint']}")
        
        # Remove duplicates from critical queries
        critical_queries = list(dict.fromkeys(critical_queries))  # Preserves order
        
        try:
            # 🆕 SMART PROMPT: Tell LLM about guaranteed products to avoid redundancy
            enhanced_state = state.copy()
            enhanced_state["guaranteed_products"] = list(guaranteed_products)
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {
                        "role": "system", 
                        "content": self._create_optimization_prompt(enhanced_state)
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            llm_queries = result.get("optimized_queries", [query])
            
            # 🆕 ENHANCED: Combine critical queries with LLM queries
            # Critical queries go first (higher priority in search)
            final_queries = critical_queries + [q for q in llm_queries if q not in critical_queries]
            
            state["original_query"] = query
            state["optimized_queries"] = final_queries
            
            # Store comparison info if detected
            if comparison_products:
                state["comparison_products"] = comparison_products
            
            debug_print(f"✅ [QueryOptimizer] Final queries ({len(critical_queries)} critical + {len(llm_queries)} LLM): {state['optimized_queries']}")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG QueryOptimizer] Query optimization error: {e}")
            state["original_query"] = query
            
            # 🆕 ENHANCED: Smart fallback using critical queries + intelligent backup
            if critical_queries:
                smart_fallback = self._create_smart_fallback(state, critical_queries)
                state["optimized_queries"] = smart_fallback
                debug_print(f"⚠️ [QueryOptimizer] Smart fallback with {len(smart_fallback)} queries: {state['optimized_queries']}")
            elif state.get("business_analysis", {}).get("products_in_category"):
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

    def _extract_mentioned_products(self, query: str) -> List[str]:
        """Extract product names mentioned by user in the query"""
        mentioned_products = []
        query_lower = query.lower()
        
        # Check for exact product name matches (case insensitive)
        for product in self.product_names:
            product_lower = product.lower()
            
            # Check for exact match
            if product_lower in query_lower:
                mentioned_products.append(product)
                continue
            
            # Check for partial matches (for products with common abbreviations)
            # Handle common product name variations
            if product == "AF NitraPhos Minus" and any(term in query_lower for term in ["nitraphos", "nitrafosfat", "nitraphos minus"]):
                mentioned_products.append(product)
            elif product == "Pro Bio S" and any(term in query_lower for term in ["bio s", "probio s"]):
                mentioned_products.append(product)
            elif product == "-NP Pro" and any(term in query_lower for term in ["np pro", "-np pro"]):
                mentioned_products.append(product)
            elif product == "Ca Plus" and any(term in query_lower for term in ["ca plus", "ca+"]):
                mentioned_products.append(product)
            elif product == "Ca plus" and any(term in query_lower for term in ["ca plus", "ca+"]):
                mentioned_products.append(product)
            elif product == "Zeo Mix" and any(term in query_lower for term in ["zeo mix", "zeomix"]):
                mentioned_products.append(product)
            elif product == "Phosphate Minus" and any(term in query_lower for term in ["phosphate minus", "po4 minus"]):
                mentioned_products.append(product)
        
        return list(set(mentioned_products))  # Remove duplicates
    
    def _create_problem_queries(self, problem: str, domain: str = "unknown") -> List[str]:
        """Create problem-specific search queries"""
        problem_queries = []
        
        if problem == "high_nitrates":
            problem_queries.extend([
                "nitrate reduction aquarium",
                "high nitrates solution",
                "NO3 reduction reef tank",
                "nitrate removal products"
            ])
            if domain == "seawater":
                problem_queries.append("marine aquarium nitrate control")
        
        elif problem == "low_calcium":
            problem_queries.extend([
                "calcium supplement aquarium",
                "raise calcium reef tank",
                "low calcium solution",
                "calcium deficiency marine"
            ])
        
        elif problem == "low_magnesium":
            problem_queries.extend([
                "magnesium supplement aquarium",
                "raise magnesium reef tank",
                "low magnesium solution",
                "Mg deficiency marine"
            ])
        
        elif problem == "ph_dropping":
            problem_queries.extend([
                "pH buffer aquarium",
                "raise pH reef tank",
                "alkalinity buffer",
                "KH buffer marine"
            ])
        
        elif problem == "ph_rising":
            problem_queries.extend([
                "lower pH aquarium",
                "pH minus reef tank",
                "reduce alkalinity"
            ])
        
        elif problem == "algae":
            problem_queries.extend([
                "algae control aquarium",
                "algae removal products",
                "phosphate reduction",
                "nutrient control reef"
            ])
        
        elif problem == "corals_browning":
            problem_queries.extend([
                "coral browning solution",
                "coral color enhancement",
                "amino acids corals",
                "coral nutrition"
            ])
        
        return problem_queries

    def _create_smart_fallback(self, state: ConversationState, critical_queries: List[str]) -> List[str]:
        """Create intelligent fallback queries when LLM fails"""
        query = state["user_query"].lower()
        fallback_queries = critical_queries.copy()
        
        # Add domain-specific queries
        if "reef" in query or "marine" in query or "coral" in query:
            fallback_queries.extend([
                "marine aquarium products",
                "reef tank supplements",
                "coral care products"
            ])
        elif "freshwater" in query or "tropical" in query:
            fallback_queries.extend([
                "freshwater aquarium products",
                "tropical fish care"
            ])
        
        # Add action-based queries
        if any(word in query for word in ["raise", "increase", "boost", "podnieść"]):
            fallback_queries.extend([
                "aquarium supplements",
                "parameter correction products"
            ])
        elif any(word in query for word in ["reduce", "lower", "decrease", "obniżyć"]):
            fallback_queries.extend([
                "reduction products",
                "control supplements"
            ])
        
        # Add problem-specific queries based on keywords
        if any(word in query for word in ["nitrate", "no3", "azotany"]):
            fallback_queries.extend([
                "nitrate reduction",
                "NO3 control products"
            ])
        elif any(word in query for word in ["phosphate", "po4", "fosforany"]):
            fallback_queries.extend([
                "phosphate reduction",
                "PO4 control products"
            ])
        elif any(word in query for word in ["calcium", "wapń", "ca"]):
            fallback_queries.extend([
                "calcium supplements",
                "Ca products"
            ])
        elif any(word in query for word in ["magnesium", "magnez", "mg"]):
            fallback_queries.extend([
                "magnesium supplements",
                "Mg products"
            ])
        
        # Add the original query as last resort
        fallback_queries.append(state["user_query"])
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(fallback_queries))

def optimize_product_query(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)