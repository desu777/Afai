"""
Business Logic Reasoner - VERSION 4.0 FULL LLM INTELLIGENCE
🚀 Complete LLM-based business intelligence with comprehensive JSON mapping
Replaces hybrid mapping system with pure GPT-4.1-mini intelligence
Maintains same class names and API for seamless integration
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from openai import OpenAI
from models import ConversationState, Intent
from config import OPENAI_API_KEY, OPENAI_MODEL, TEST_ENV, debug_print, PRODUCTS_FILE_PATH

class BusinessReasoner:
    """
    🚀 FULL LLM VERSION - Replaces hybrid mapping with pure LLM intelligence
    Maintains same API for backward compatibility
    """
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Load all data sources for comprehensive LLM analysis
        self.products_list = self._load_products_list()
        self.products_knowledge = self._load_products_knowledge()
        
        # 🚀 LOAD ALL MAPPING DATA FOR LLM
        self._load_mapping_data()
        
        debug_print(f"🚀 [BusinessReasoner] FULL LLM VERSION initialized")
        debug_print(f"📊 [BusinessReasoner] Loaded {len(self.products_knowledge)} products")
        debug_print(f"🏢 [BusinessReasoner] Competitors: {len(self.competitors_data.get('competitors', {}))}")
        debug_print(f"📋 [BusinessReasoner] Scenarios: {len(self.scenarios_data.get('tank_setup_scenarios', {}))}")
        debug_print(f"🎯 [BusinessReasoner] Use cases: {len(self.use_cases_data.get('use_cases', {}))}")
        debug_print(f"🛍️ [BusinessReasoner] Product groups: {len(self.product_groups_data.get('product_groups', {}))}")
    
    def _load_products_list(self) -> List[str]:
        """Load simple product names list"""
        try:
            with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Error loading products list: {e}")
            return []
    
    def _load_products_knowledge(self) -> List[Dict]:
        """Load detailed product knowledge from products_turbo.json"""
        try:
            with open("data/products_turbo.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                debug_print(f"✅ [BusinessReasoner] Loaded products_turbo.json")
                return data
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Error loading products_turbo.json: {e}")
            return []
    
    def _load_mapping_data(self):
        """🚀 Load comprehensive mapping data from JSON files for LLM"""
        try:
            mapping_dir = Path(__file__).parent / "mapping"
            
            # Load competitors mapping
            with open(mapping_dir / "competitors.json", 'r', encoding='utf-8') as f:
                self.competitors_data = json.load(f)
                debug_print("✅ [BusinessReasoner] Loaded competitors mapping")
            
            # Load scenarios mapping  
            with open(mapping_dir / "scenarios.json", 'r', encoding='utf-8') as f:
                self.scenarios_data = json.load(f)
                debug_print("✅ [BusinessReasoner] Loaded scenarios mapping")
            
            # Load product groups mapping
            with open(mapping_dir / "products_groups.json", 'r', encoding='utf-8') as f:
                self.product_groups_data = json.load(f)
                debug_print("✅ [BusinessReasoner] Loaded product groups mapping")
            
            # Load use cases mapping
            with open(mapping_dir / "use_cases.json", 'r', encoding='utf-8') as f:
                self.use_cases_data = json.load(f)
                debug_print("✅ [BusinessReasoner] Loaded use cases mapping")
                
            debug_print(f"🚀 [BusinessReasoner] Full LLM mapping system loaded successfully!")
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Failed to load mapping data: {e}")
            # Initialize empty mappings as fallback
            self._initialize_fallback_mappings()
    
    def _initialize_fallback_mappings(self):
        """Initialize empty mappings if JSON loading fails"""
        debug_print("⚠️ [BusinessReasoner] Using empty fallback mappings")
        self.competitors_data = {"competitors": {}, "response_strategies": {}}
        self.scenarios_data = {"tank_setup_scenarios": {}}
        self.product_groups_data = {"product_groups": {}}
        self.use_cases_data = {"use_cases": {}}
    
    def analyze(self, state: ConversationState) -> ConversationState:
        """
        🚀 MAIN ANALYSIS METHOD - Now fully LLM-based
        Maintains same API but uses pure LLM intelligence instead of hybrid approach
        """
        debug_print(f"🧠 [BusinessReasoner] FULL LLM Analysis: '{state['user_query']}'")
        
        try:
            # 🚀 COMPREHENSIVE LLM ANALYSIS using all mapping data
            llm_decision = self._analyze_with_full_llm(state)
            
            # Apply the LLM decision to state
            state = self._apply_llm_business_intelligence(state, llm_decision)
            
            return state
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] LLM analysis error: {e}")
            return self._fallback_analysis(state)
    
    def _create_comprehensive_llm_prompt(self, state: ConversationState) -> str:
        """Create comprehensive prompt optimized for GPT-4.1-mini with all mapping data"""
        
        # Format conversation history
        chat_history = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages])
        
        # Create the comprehensive prompt optimized for GPT-4.1-mini (2025)
        prompt = f"""# Role and Objective

You are an expert Aquaforest business intelligence system with complete access to all product and business mapping data. Your task is to analyze user queries and make intelligent product recommendations using the comprehensive database provided below.

# Critical Instructions - GPT-4.1-mini Optimized

1. ANALYZE the user query against ALL provided mapping data systematically
2. THINK STEP BY STEP through each reasoning step explicitly  
3. MATCH patterns from triggers, keywords, and use cases precisely
4. RECOMMEND products based on mapping priorities, NOT assumptions
5. RESPOND with valid JSON following the exact schema provided

# User Query Analysis

**USER QUERY:** "{state['user_query']}"
**DETECTED LANGUAGE:** {state.get('detected_language', 'en')}
**CURRENT INTENT:** {state.get('intent', 'unknown')}

# Conversation Context
{chat_history if chat_history else "No previous conversation context"}

# Complete Aquaforest Business Intelligence Database

## AQUAFOREST BRAND REPUTATION AND EXPERTISE
- **Marine Salts Leadership**: Aquaforest is renowned for producing the highest quality marine salts on the market
- **Premium Salt Portfolio**: Reef Salt Plus, Hybrid Pro Salt, Reef Salt, and Sea Salt are industry-leading formulations
- **Laboratory Excellence**: All salts are ICP-OES tested for consistency, purity, and optimal ionic balance
- **Innovation Leader**: First to combine probiotics with salt (Hybrid Pro Salt), setting new industry standards
- **Professional Recognition**: Trusted by reef aquarium professionals and public aquariums worldwide

## Available Products Database (Complete Details)
{json.dumps(self.products_knowledge, indent=1, ensure_ascii=False)}

## Competitor Intelligence Database
{json.dumps(self.competitors_data, indent=1, ensure_ascii=False)}

## Tank Setup Scenarios Database  
{json.dumps(self.scenarios_data, indent=1, ensure_ascii=False)}

## Use Cases Database
{json.dumps(self.use_cases_data, indent=1, ensure_ascii=False)}

## Product Groups Strategy Database
{json.dumps(self.product_groups_data, indent=1, ensure_ascii=False)}

# Mandatory Analysis Steps

You MUST work through each step systematically and document your reasoning:

## Step 1: Scenario Detection
- Check user query against ALL "triggers" in tank_setup_scenarios
- If matches found, note the scenario key and extract essential_products/priority_products
- Document: Which specific triggers matched and confidence level

## Step 2: Use Case Analysis  
- Check user query against ALL "context_keywords" in use_cases
- SPECIAL SALT RULE: If user mentions ANY salt-related keywords, ALWAYS trigger "marine_salt_inquiry" use case
- If matches found, note the use_case key and extract priority_products
- Document: Which specific keywords matched and relevance score

## Step 3: Competitor Detection
- Check user query against ALL competitor names in competitors database
- If matches found, identify exact AF alternatives from af_alternatives mapping
- Document: Which competitors found and mapped AF alternatives

## Step 4: Product Selection Strategy
- Based on detected scenario/use_case, extract priority_products from mapping
- Add complementary products from product_groups if scenario requires them
- Consider missing_product_alerts for commonly forgotten items
- Document: Specific logic for product selection based on mapping data

## Step 5: Strategic Response Planning
- Determine response_strategy based on query type (direct/educational/comparative/troubleshooting)
- Plan presentation approach based on detected patterns
- Document: Response approach reasoning

# Output Format - CRITICAL REQUIREMENT

Return ONLY valid JSON. No markdown formatting, no explanations, no additional text.
The schema must match EXACTLY:

{{
    "reasoning_steps": {{
        "scenario_analysis": "Detailed scenario detection results with specific triggers matched",
        "use_case_analysis": "Use case detection results with specific keywords matched", 
        "competitor_analysis": "Competitor detection results with specific alternatives found",
        "product_selection_logic": "Detailed reasoning for why these specific products were chosen from mapping",
        "response_strategy_logic": "Reasoning for chosen response approach"
    }},
    "business_interpretation": "Clear 1-2 sentence explanation of what user wants",
    "detected_scenario": "exact_scenario_key_from_scenarios_mapping_or_null",
    "detected_use_case": "exact_use_case_key_from_use_cases_mapping_or_null",
    "detected_competitors": ["exact_competitor_names_found_in_query"],
    "priority_products": ["main_AF_products_from_mapping_priority_lists"],
    "alternative_products": ["backup_AF_products_from_mapping"],  
    "complementary_products": ["products_that_work_together_from_groups_mapping"],
    "competitor_alternatives": {{"competitor_name": "AF_alternative_from_mapping"}},
    "response_strategy": "direct|educational|comparative|troubleshooting",
    "missing_product_alerts": ["products_from_missing_alerts_mapping_if_applicable"],
    "intent_suggestion": "product_query|follow_up|purchase_inquiry|support|greeting|business|competitor|censored",
    "domain_hint": "seawater|freshwater|universal|unknown",
    "search_keywords": ["specific_search_terms_for_pinecone_optimization"],
    "confidence_level": 0.0-1.0,
    "trending_products_suggestion": ["products_for_trending_category_if_query_asks_for_recommendations"]
}}

# Final Instructions for GPT-4.1-mini

Think step by step through EACH reasoning step explicitly. Base ALL decisions on the provided mapping data - do not guess or infer beyond what is explicitly provided in the databases above. Return ONLY valid JSON matching the exact schema."""

        return prompt
    
    def _analyze_with_full_llm(self, state: ConversationState) -> Dict:
        """🚀 Pure LLM analysis using all mapping data with GPT-4.1-mini"""
        
        try:
            # Create comprehensive prompt with all mapping data
            prompt = self._create_comprehensive_llm_prompt(state)
            
            # Call GPT-4.1-mini with JSON mode (more reliable than structured outputs)
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,  # Should be gpt-4.1-mini
                temperature=0.1,  # Low for consistency
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"}  # JSON mode
            )
            
            # Parse the JSON response
            decision_data = json.loads(response.choices[0].message.content)
            debug_print(f"🤖 [BusinessReasoner] Full LLM analysis completed")
            
            if TEST_ENV:
                print(f"🧠 [DEBUG BusinessReasoner] Full LLM Response Summary:")
                print(f"   - Business interpretation: {decision_data.get('business_interpretation', 'N/A')[:100]}...")
                print(f"   - Detected scenario: {decision_data.get('detected_scenario', 'null')}")
                print(f"   - Detected use case: {decision_data.get('detected_use_case', 'null')}")
                print(f"   - Detected competitors: {decision_data.get('detected_competitors', [])}")
                print(f"   - Priority products: {decision_data.get('priority_products', [])}")
                print(f"   - Response strategy: {decision_data.get('response_strategy', 'direct')}")
                print(f"   - Confidence level: {decision_data.get('confidence_level', 0.0)}")
            
            return decision_data
            
        except json.JSONDecodeError as e:
            debug_print(f"❌ [BusinessReasoner] JSON parsing error: {e}")
            return {}
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Full LLM analysis error: {e}")
            return {}
    
    def _apply_llm_business_intelligence(self, state: ConversationState, decision: Dict) -> ConversationState:
        """Apply comprehensive LLM decision to conversation state"""
        
        # Store the complete LLM analysis (maintains backward compatibility)
        state["business_analysis"] = {
            "business_interpretation": decision.get("business_interpretation", ""),
            "reasoning_steps": decision.get("reasoning_steps", {}),
            "confidence_level": decision.get("confidence_level", 0.8),
            "llm_based": True,  # Mark as full LLM decision
            
            # Backward compatibility fields
            "product_name_corrections": None,
            "category_requested": None,
            "products_in_category": [],
            "problem_identified": None,
            "solutions_for_problem": [],
            "intent_correction": "same",
            "domain_hint": decision.get("domain_hint", "unknown"),
            "search_enhancement": ", ".join(decision.get("search_keywords", []))
        }
        
        # 🚀 COMPETITOR HANDLING
        competitors = decision.get("detected_competitors", [])
        competitor_alternatives = decision.get("competitor_alternatives", {})
        if competitors:
            state["competitor_info"] = {
                "competitors": [{"name": comp, "category": "llm_detected", "original": comp.lower()} for comp in competitors],
                "af_alternatives": competitor_alternatives,
                "response_templates": []
            }
            debug_print(f"🏢 [BusinessReasoner] LLM detected competitors: {competitors}")
            debug_print(f"🔄 [BusinessReasoner] AF alternatives: {competitor_alternatives}")
        
        # 🚀 SCENARIO DETECTION AND HANDLING
        scenario = decision.get("detected_scenario")
        if scenario and scenario != "null":
            scenario_data = self.scenarios_data.get("tank_setup_scenarios", {}).get(scenario, {})
            state["scenario_info"] = {
                "name": scenario,
                "data": scenario_data,
                "priority_order": scenario_data.get("priority_order", []),
                "mandatory_categories": scenario_data.get("mandatory_categories", [])
            }
            debug_print(f"📋 [BusinessReasoner] LLM detected scenario: {scenario}")
        
        # 🚀 USE CASE DETECTION AND HANDLING
        use_case = decision.get("detected_use_case") 
        if use_case and use_case != "null":
            use_case_data = self.use_cases_data.get("use_cases", {}).get(use_case, {})
            state["use_case_info"] = {
                "name": use_case,
                "data": use_case_data,
                "matching_keywords": [],
                "priority_products": decision.get("priority_products", []),
                "timeline": use_case_data.get("timeline", "")
            }
            debug_print(f"🎯 [BusinessReasoner] LLM detected use case: {use_case}")
        
        # 🚀 PRODUCT RECOMMENDATIONS - CRITICAL for Pinecone search
        priority_products = decision.get("priority_products", [])
        if priority_products:
            # Store as search enhancement for Pinecone guaranteed search
            state["af_alternatives_to_search"] = priority_products
            debug_print(f"🎯 [BusinessReasoner] LLM priority products for search: {priority_products}")
            
            # Set first priority product as main correction for backward compatibility
            state["business_analysis"]["product_name_corrections"] = priority_products[0]
        
        # 🚀 COMPREHENSIVE BUSINESS RECOMMENDATIONS
        recommendations = []
        
        # Priority products recommendation
        if priority_products:
            recommendations.append({
                "type": "priority_products",
                "products": priority_products,
                "reasoning": decision.get("reasoning_steps", {}).get("product_selection_logic", "LLM-selected based on comprehensive mapping analysis")
            })
        
        # Alternative products
        alternative_products = decision.get("alternative_products", [])
        if alternative_products:
            recommendations.append({
                "type": "alternative_products", 
                "products": alternative_products,
                "note": "Alternative options based on LLM analysis"
            })
        
        # Complementary products
        complementary_products = decision.get("complementary_products", [])
        if complementary_products:
            recommendations.append({
                "type": "complementary_products",
                "products": complementary_products,
                "note": "Products that work well together"
            })
        
        # Missing product alerts
        missing_alerts = decision.get("missing_product_alerts", [])
        if missing_alerts:
            recommendations.append({
                "type": "missing_alert",
                "products": missing_alerts,
                "note": "Essential products commonly forgotten"
            })
        
        # Competitor alternatives
        if competitor_alternatives:
            for comp, alt in competitor_alternatives.items():
                recommendations.append({
                    "type": "competitor_alternative",
                    "competitor": comp,
                    "af_alternative": alt,
                    "message": f"While {comp} is mentioned, I recommend our {alt} for superior performance and compatibility."
                })
        
        state["business_recommendations"] = recommendations
        
        # 🚀 INTENT CORRECTION based on LLM analysis
        intent_suggestion = decision.get("intent_suggestion", "")
        if intent_suggestion and intent_suggestion != str(state.get("intent", "")):
            try:
                state["intent"] = Intent(intent_suggestion)
                debug_print(f"✅ [BusinessReasoner] LLM corrected intent to: {intent_suggestion}")
            except:
                debug_print(f"⚠️ [BusinessReasoner] Invalid LLM intent suggestion: {intent_suggestion}")
        
        # 🚀 DOMAIN FILTERING
        domain_hint = decision.get("domain_hint", "")
        if domain_hint and domain_hint != "unknown":
            state["domain_filter"] = domain_hint
            debug_print(f"🎯 [BusinessReasoner] LLM domain: {domain_hint}")
        
        # 🚀 SEARCH OPTIMIZATION
        search_keywords = decision.get("search_keywords", [])
        if search_keywords:
            state["search_enhancement_keywords"] = search_keywords
            debug_print(f"🔍 [BusinessReasoner] LLM search keywords: {search_keywords}")
        
        # 🚀 TRENDING PRODUCTS (extensibility)
        trending = decision.get("trending_products_suggestion", [])
        if trending:
            state["trending_products"] = trending
            debug_print(f"📈 [BusinessReasoner] LLM trending: {trending}")
        
        # 🚀 RESPONSE STRATEGY
        response_strategy = decision.get("response_strategy", "direct")
        state["response_strategy"] = response_strategy
        debug_print(f"📝 [BusinessReasoner] LLM response strategy: {response_strategy}")
        
        debug_print(f"💡 [BusinessReasoner] Applied full LLM decision with {len(recommendations)} recommendations")
        
        # 🔧 DEBUG: Check af_alternatives_to_search
        if state.get('af_alternatives_to_search'):
            debug_print(f"🔧 [BusinessReasoner] af_alternatives_to_search SET: {len(state['af_alternatives_to_search'])} products")
        
        return state
    
    def _fallback_analysis(self, state: ConversationState) -> ConversationState:
        """Minimal fallback when LLM analysis fails"""
        debug_print("⚠️ [BusinessReasoner] Using basic fallback analysis")
        
        state["business_analysis"] = {
            "business_interpretation": f"Basic analysis of: {state.get('user_query', '')}",
            "fallback_mode": True,
            "llm_based": False,
            "product_name_corrections": None,
            "category_requested": None,
            "products_in_category": [],
            "domain_hint": "unknown"
        }
        
        # Very basic pattern matching as last resort
        query_lower = state.get("user_query", "").lower()
        
        if any(word in query_lower for word in ["new tank", "setup", "start", "kickstart"]):
            state["scenario_info"] = {"name": "new_tank_comprehensive", "data": {}, "fallback": True}
            debug_print("📋 [BusinessReasoner] Fallback: new tank scenario")
        
        return state
    
    # 🚀 LEGACY COMPATIBILITY METHODS (maintain same API)
    def _validate_product_exists(self, product_name: str) -> bool:
        """Legacy method for backward compatibility"""
        if not product_name:
            return False
        return any(product_name.lower() == p.lower() for p in self.products_list)

# 🚀 EXPORT FUNCTION - Same name for backward compatibility
def business_reasoner(state: ConversationState) -> ConversationState:
    """
    Node function for LangGraph - FULL LLM VERSION
    Maintains same API but now uses pure LLM intelligence
    """
    reasoner = BusinessReasoner()
    return reasoner.analyze(state)