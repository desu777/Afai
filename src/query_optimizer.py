"""
Query Optimization Module - VERSION 4.0 REVOLUTIONARY LLM INTELLIGENCE
🚀 CONCEPT-BASED SEARCH: From "find AF Build" to "find calcium supplements for coral calcification"
Complete evolution from name-based to concept-based intelligent discovery
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
        self.products_knowledge = self._load_products_knowledge()
        
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
    
    def _load_products_knowledge(self) -> List[Dict]:
        """🆕 Load detailed product knowledge for concept-based search"""
        try:
            with open("data/products_turbo.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                debug_print(f"✅ [QueryOptimizer] Loaded {len(data)} products knowledge for concept analysis")
                return data
        except Exception as e:
            debug_print(f"❌ [QueryOptimizer] Error loading products knowledge: {e}")
            return []

    def _create_revolutionary_prompt(self, state: ConversationState) -> str:
        """🚀 REVOLUTIONARY: Create LLM prompt for concept-based search"""
        
        query = state["user_query"]
        language = state["detected_language"]
        
        # Get priority products from Business Reasoner
        priority_products = state.get("af_alternatives_to_search", [])
        
        # Chat history for context
        chat_history = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages])
        
        # Business context
        business_context = ""
        if state.get("business_analysis"):
            ba = state["business_analysis"]
            business_context = f"""
Business Analysis:
- Interpretation: {ba.get('business_interpretation', 'N/A')}
- Detected Scenario: {ba.get('detected_scenario', 'None')}
- Use Case: {ba.get('detected_use_case', 'None')}
- Domain: {ba.get('domain_hint', 'unknown')}
"""

        # 🚀 FILTER products_knowledge for priority products
        priority_products_data = []
        if priority_products:
            for priority_product in priority_products:
                for product_data in self.products_knowledge:
                    if product_data.get("product_name") == priority_product:
                        priority_products_data.append(product_data)
                        break

        priority_products_json = json.dumps(priority_products_data, indent=1, ensure_ascii=False)

        prompt = f"""# REVOLUTIONARY QUERY OPTIMIZER - CONCEPT-BASED SEARCH

You are transforming search from "name-based" to "concept-based" discovery. Your mission is to understand WHAT problems the priority products solve, and generate search queries that find related concepts, knowledge, and complementary products.

## CORE PRINCIPLE: FROM NAMES TO CONCEPTS

❌ OLD WAY (name-based): User asks about "AF Build" → search for "AF Build"
✅ NEW WAY (concept-based): User asks about "AF Build" → understand it's for "coral calcification" → search for:
- "coral calcification supplements"
- "improving SPS skeletal growth"  
- "calcium carbonate absorption"
- "hard coral growth enhancement"

## WHY THIS REVOLUTION MATTERS:
1. **Knowledge Discovery**: Find articles about "coral calcification" that don't mention "AF Build" by name
2. **Complementary Products**: Discover products that solve related problems or enhance the main product
3. **Educational Context**: Surface guides, tips, and knowledge that provide deeper understanding
4. **Intelligent Connections**: Connect user problems to broader aquarium concepts

## USER CONTEXT

**USER QUERY:** "{query}"
**LANGUAGE:** {language}
**PRIORITY PRODUCTS (from Business Reasoner):** {priority_products}

**CONVERSATION HISTORY:**
{chat_history if chat_history else "No previous conversation"}

{business_context}

## PRIORITY PRODUCTS DETAILED KNOWLEDGE

These are the products Business Reasoner identified as most relevant. Your job is to understand their CONCEPTS and PURPOSES:

{priority_products_json}

## YOUR MISSION: CONCEPT EXTRACTION & INTELLIGENT SEARCH

🧠 **STEP 1: CONCEPT ANALYSIS**
For each priority product, analyze:
- What PROBLEMS does it solve? (from solves_problems field)
- What are its KEY FUNCTIONS? (from use_case field)  
- What KEYWORDS represent its purpose? (from keywords field)
- What CATEGORY does it belong to? (from category field)

🎯 **STEP 2: CONCEPT-BASED QUERY GENERATION**
Generate 8-12 search queries that will find:

**PRIMARY CONCEPTS (40%)** - Core problems/functions:
- Instead of "AF Build", search for "coral calcification enhancement", "SPS growth supplements"
- Instead of "Ca Plus", search for "calcium supplementation reef", "marine calcium deficiency"
- Instead of "Pro Bio S", search for "beneficial bacteria aquarium", "biological filtration enhancement"

**KNOWLEDGE & EDUCATION (30%)** - Related articles and guides:
- "how to improve coral calcification"
- "reef tank calcium management guide"
- "SPS coral care techniques"
- "biological filtration principles"

**COMPLEMENTARY CONCEPTS (20%)** - Related products and systems:
- Products that work WITH the priority products
- Supporting equipment or supplements
- Testing and monitoring related to the concepts

**PROBLEM VARIATIONS (10%)** - Different ways to express the same issues:
- Alternative terminology for the same problems
- Beginner vs advanced ways of describing issues

## SPECIAL RULES

🚨 **GUARANTEED SEARCH AWARENESS**: 
- The priority products {priority_products} will be found through guaranteed search by exact name
- DO NOT waste vector search on names - focus on CONCEPTS and RELATED CONTENT
- Your queries should discover what guaranteed search CANNOT find

🎯 **LANGUAGE ADAPTATION**:
- Generate queries in {language} when appropriate
- Include both technical and beginner-friendly terminology
- Consider regional product naming conventions

🔍 **DISCOVERY FOCUS**:
- Prioritize queries that will find knowledge articles
- Look for complementary products and systems
- Find educational content that enhances understanding
- Connect to broader aquarium keeping concepts

## OUTPUT FORMAT

Return ONLY valid JSON with this structure:

{{
    "reasoning": "Brief explanation of your concept analysis and why these queries will discover valuable related content",
    "concept_analysis": [
        {{"product": "Product Name", "core_concepts": ["concept1", "concept2"], "related_problems": ["problem1", "problem2"]}}
    ],
    "optimized_queries": [
        "concept-based query 1",
        "concept-based query 2", 
        "educational query 3",
        "complementary system query 4",
        "problem variation query 5",
        "knowledge article query 6",
        "related product query 7",
        "advanced technique query 8"
    ]
}}

## EXAMPLE TRANSFORMATION

**PRIORITY PRODUCT:** "AF Build"
**CONCEPT ANALYSIS:** Calcium/carbonate supplement for coral calcification, pH buffering, hard coral growth
**REVOLUTIONARY QUERIES:**
- "coral calcification enhancement techniques"
- "calcium carbonate absorption in SPS corals"  
- "hard coral skeletal growth supplements"
- "reef tank pH stabilization methods"
- "SPS feeding and calcification guide"
- "complementary calcium dosing systems"
- "coral growth rate improvement"
- "alkalinity and calcium balance"

Notice: NO queries for "AF Build" itself - that's handled by guaranteed search!

🚀 **NOW GENERATE YOUR REVOLUTIONARY CONCEPT-BASED QUERIES FOR INTELLIGENT DISCOVERY!**"""

        return prompt

    def optimize(self, state: ConversationState) -> ConversationState:
        """🚀 REVOLUTIONARY: Concept-based optimization with full LLM intelligence"""
        query = state["user_query"]
        priority_products = state.get("af_alternatives_to_search", [])
        
        debug_print(f"🚀 [QueryOptimizer] REVOLUTIONARY MODE: Concept-based search")
        debug_print(f"🎯 [QueryOptimizer] Original query: '{query}'")
        
        if priority_products:
            debug_print(f"🧠 [QueryOptimizer] Priority products for concept analysis: {priority_products}")
        else:
            debug_print(f"⚠️ [QueryOptimizer] No priority products - using query-only analysis")

        try:
            # 🚀 REVOLUTIONARY LLM ANALYSIS
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.3,  # Slightly higher for creative concept discovery
                messages=[
                    {
                        "role": "system", 
                        "content": self._create_revolutionary_prompt(state)
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            concept_queries = result.get("optimized_queries", [])
            concept_analysis = result.get("concept_analysis", [])
            reasoning = result.get("reasoning", "")
            
            # Store results
            state["original_query"] = query
            state["optimized_queries"] = concept_queries
            
            # 🆕 Store concept analysis for Response Formatter
            state["concept_analysis"] = {
                "reasoning": reasoning,
                "product_concepts": concept_analysis,
                "query_strategy": "concept_based_discovery"
            }
            
            debug_print(f"✅ [QueryOptimizer] Generated {len(concept_queries)} concept-based queries")
            debug_print(f"🧠 [QueryOptimizer] Concept analysis: {reasoning[:100]}...")
            
            if TEST_ENV:
                print(f"🚀 [QueryOptimizer] REVOLUTIONARY QUERIES:")
                for i, q in enumerate(concept_queries, 1):
                    print(f"   {i}. {q}")
                    
                if concept_analysis:
                    print(f"🧠 [QueryOptimizer] CONCEPT ANALYSIS:")
                    for analysis in concept_analysis:
                        product = analysis.get("product", "Unknown")
                        concepts = analysis.get("core_concepts", [])
                        print(f"   • {product}: {', '.join(concepts)}")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG QueryOptimizer] Revolutionary analysis error: {e}")
            
            # 🆕 INTELLIGENT FALLBACK: Basic concept extraction
            state["original_query"] = query
            
            if priority_products:
                # Create basic concept queries from priority products
                fallback_queries = []
                for product in priority_products:
                    # Find the product in knowledge base
                    for product_data in self.products_knowledge:
                        if product_data.get("product_name") == product:
                            # Extract basic concepts from keywords and use_case
                            keywords = product_data.get("keywords", [])
                            if keywords:
                                # Create concept queries from keywords
                                fallback_queries.append(f"{' '.join(keywords[:3])}")
                            
                            use_case = product_data.get("use_case", "")
                            if use_case and len(use_case) > 50:
                                # Extract key phrases from use_case
                                words = use_case.split()[:10]
                                fallback_queries.append(" ".join(words))
                            break
                
                # Add original query
                fallback_queries.append(query)
                state["optimized_queries"] = list(set(fallback_queries))  # Remove duplicates
                
                debug_print(f"⚠️ [QueryOptimizer] Intelligent fallback: {len(state['optimized_queries'])} concept queries")
            else:
                # Basic fallback
                state["optimized_queries"] = [query]
                debug_print(f"⚠️ [QueryOptimizer] Basic fallback to original query")
            
        return state

    def optimize(self, state: ConversationState) -> ConversationState:
        """🚀 REVOLUTIONARY: Concept-based optimization with full LLM intelligence"""
        query = state["user_query"]
        priority_products = state.get("af_alternatives_to_search", [])
        
        debug_print(f"🚀 [QueryOptimizer] REVOLUTIONARY MODE: Concept-based search")
        debug_print(f"🎯 [QueryOptimizer] Original query: '{query}'")
        
        if priority_products:
            debug_print(f"🧠 [QueryOptimizer] Priority products for concept analysis: {priority_products}")
        else:
            debug_print(f"⚠️ [QueryOptimizer] No priority products - using query-only analysis")

        try:
            # 🚀 REVOLUTIONARY LLM ANALYSIS
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.3,  # Slightly higher for creative concept discovery
                messages=[
                    {
                        "role": "system", 
                        "content": self._create_revolutionary_prompt(state)
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            concept_queries = result.get("optimized_queries", [])
            concept_analysis = result.get("concept_analysis", [])
            reasoning = result.get("reasoning", "")
            
            # Store results
            state["original_query"] = query
            state["optimized_queries"] = concept_queries
            
            # 🆕 Store concept analysis for Response Formatter
            state["concept_analysis"] = {
                "reasoning": reasoning,
                "product_concepts": concept_analysis,
                "query_strategy": "concept_based_discovery"
            }
            
            debug_print(f"✅ [QueryOptimizer] Generated {len(concept_queries)} concept-based queries")
            debug_print(f"🧠 [QueryOptimizer] Concept analysis: {reasoning[:100]}...")
            
            if TEST_ENV:
                print(f"🚀 [QueryOptimizer] REVOLUTIONARY QUERIES:")
                for i, q in enumerate(concept_queries, 1):
                    print(f"   {i}. {q}")
                    
                if concept_analysis:
                    print(f"🧠 [QueryOptimizer] CONCEPT ANALYSIS:")
                    for analysis in concept_analysis:
                        product = analysis.get("product", "Unknown")
                        concepts = analysis.get("core_concepts", [])
                        print(f"   • {product}: {', '.join(concepts)}")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG QueryOptimizer] Revolutionary analysis error: {e}")
            
            # 🆕 INTELLIGENT FALLBACK: Basic concept extraction
            state["original_query"] = query
            
            if priority_products:
                # Create basic concept queries from priority products
                fallback_queries = []
                for product in priority_products:
                    # Find the product in knowledge base
                    for product_data in self.products_knowledge:
                        if product_data.get("product_name") == product:
                            # Extract basic concepts from keywords and use_case
                            keywords = product_data.get("keywords", [])
                            if keywords:
                                # Create concept queries from keywords
                                fallback_queries.append(f"{' '.join(keywords[:3])}")
                            
                            use_case = product_data.get("use_case", "")
                            if use_case and len(use_case) > 50:
                                # Extract key phrases from use_case
                                words = use_case.split()[:10]
                                fallback_queries.append(" ".join(words))
                            break
                
                # Add original query
                fallback_queries.append(query)
                state["optimized_queries"] = list(set(fallback_queries))  # Remove duplicates
                
                debug_print(f"⚠️ [QueryOptimizer] Intelligent fallback: {len(state['optimized_queries'])} concept queries")
            else:
                # Basic fallback
                state["optimized_queries"] = [query]
                debug_print(f"⚠️ [QueryOptimizer] Basic fallback to original query")
            
        return state

# 🚀 EXPORT FUNCTION - Same name for workflow compatibility
def optimize_product_query(state: ConversationState) -> ConversationState:
    """
    🚀 REVOLUTIONARY: Concept-based query optimization
    Main entry point for LangGraph workflow
    """
    optimizer = QueryOptimizer()
    return optimizer.optimize(state)