"""
Business Logic Reasoner - VERSION 4.1 REFACTORED
🚀 Complete LLM-based business intelligence with clean architecture
Separated web scraping and prompt template for better organization
Maintains same class names and API for seamless integration
"""
import json
import os
import re  # 🆕 For ICP URL parsing  
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from openai import OpenAI
from models import ConversationState, Intent
from config import OPENAI_API_KEY, OPENAI_MODEL, TEST_ENV, debug_print, PRODUCTS_FILE_PATH, DISABLE_BUSINESS_MAPPINGS, ENABLE_COMPETITORS_ONLY
from icp_scraper import ICPScraper  # 🆕 Separated web scraping
from prompts import load_prompt_template  # 🆕 External prompt template

class BusinessReasoner:
    """
    🚀 FULL LLM VERSION - Replaces hybrid mapping with pure LLM intelligence
    Maintains same API for backward compatibility
    """
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.icp_scraper = ICPScraper()  # 🆕 Separated ICP scraping
        
        # Load all data sources for comprehensive LLM analysis
        self.products_list = self._load_products_list()
        self.products_knowledge = self._load_products_knowledge()
        
        # 🚀 LOAD MAPPING DATA (with different modes)
        if ENABLE_COMPETITORS_ONLY:
            self._load_competitors_only()
            debug_print(f"🚀 [BusinessReasoner] VERSION 4.1 COMPETITORS-ONLY initialized")
            debug_print(f"📊 [BusinessReasoner] Loaded {len(self.products_knowledge)} products")
            debug_print(f"🏢 [BusinessReasoner] Competitors: {len(self.competitors_data.get('competitors', {}))}")
            debug_print("⚠️ [BusinessReasoner] Other mappings disabled - using LLM intelligence only")
        elif not DISABLE_BUSINESS_MAPPINGS:
            self._load_mapping_data()
            debug_print(f"🚀 [BusinessReasoner] VERSION 4.1 REFACTORED initialized")
            debug_print(f"📊 [BusinessReasoner] Loaded {len(self.products_knowledge)} products")
            debug_print(f"🏢 [BusinessReasoner] Competitors: {len(self.competitors_data.get('competitors', {}))}")
            debug_print(f"📋 [BusinessReasoner] Scenarios: {len(self.scenarios_data.get('tank_setup_scenarios', {}))}")
            debug_print(f"🎯 [BusinessReasoner] Use cases: {len(self.use_cases_data.get('use_cases', {}))}")
            debug_print(f"🛍️ [BusinessReasoner] Product groups: {len(self.product_groups_data.get('product_groups', {}))}")
        else:
            debug_print("⚠️ [BusinessReasoner] MAPPINGS DISABLED - Running without mapping data")
            self._initialize_fallback_mappings()
            debug_print(f"🚀 [BusinessReasoner] VERSION 4.1 LITE initialized (no mappings)")
            debug_print(f"📊 [BusinessReasoner] Loaded {len(self.products_knowledge)} products")
    
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
    
    def _load_competitors_only(self):
        """🆕 Load only competitors mapping, initialize others as empty"""
        try:
            mapping_dir = Path(__file__).parent / "mapping"
            
            # Load only competitors mapping
            with open(mapping_dir / "competitors.json", 'r', encoding='utf-8') as f:
                self.competitors_data = json.load(f)
                debug_print("✅ [BusinessReasoner] Loaded competitors mapping (ONLY)")
            
            # Initialize other mappings as empty
            self.scenarios_data = {"tank_setup_scenarios": {}}
            self.product_groups_data = {"product_groups": {}}
            self.use_cases_data = {"use_cases": {}}
            
            debug_print(f"🎯 [BusinessReasoner] Competitors-only mode: {len(self.competitors_data.get('competitors', {}))} competitor categories loaded")
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Failed to load competitors mapping: {e}")
            # Fallback to empty mappings
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
            # 🆕 ICP URL EXTRACTION - Handle before LLM analysis
            if state.get("intent") == Intent.ANALYZE_ICP:
                # Look for ICP URL in the query
                icp_url_match = re.search(r'(https?://)?aquaforestlab\.com/(?:pl|en)/results/\w+', state['user_query'])
                if icp_url_match:
                    icp_url = icp_url_match.group(0)
                    if not icp_url.startswith('http'):
                        icp_url = 'https://' + icp_url
                    
                    # Extract ICP data and add to state using separated scraper
                    icp_data = self.icp_scraper.extract_icp_data_from_url(icp_url)
                    state["icp_analysis"] = icp_data
                    debug_print(f"🔬 [BusinessReasoner] ICP data extracted for URL: {icp_url}")
                    
                    # 📋 ADD ICP RESULTS TO USER QUERY for LLM analysis
                    if icp_data.get("parameters"):
                        icp_summary = self.icp_scraper.format_icp_data_for_llm(icp_data["parameters"], icp_data.get("metadata", {}))
                        enhanced_query = f"{state['user_query']}\n\n📊 ICP TEST RESULTS:\n{icp_summary}"
                        
                        # 🆕 ADD LAB DOSING RECOMMENDATIONS from ICP page
                        if icp_data.get("raw_data"):
                            icp_recommendations = self.icp_scraper.extract_icp_recommendations_text(icp_data["raw_data"])
                            if icp_recommendations:
                                recs_text = "\n".join(icp_recommendations)
                                enhanced_query += f"\n\n🔬 LAB DOSING RECOMMENDATIONS:\n{recs_text}"
                                debug_print(f"📋 [BusinessReasoner] Added {len(icp_recommendations)} lab dosing recommendations")
                        
                        state["user_query"] = enhanced_query
                        debug_print(f"📋 [BusinessReasoner] Enhanced query with ICP data + lab recommendations")
                        
                        # 🔍 DEBUG: Print full ICP results for debugging
                        debug_print(f"📊 [BusinessReasoner] COMPLETE ICP ANALYSIS:")
                        debug_print(f"{enhanced_query}")
                else:
                    debug_print(f"⚠️ [BusinessReasoner] ANALYZE_ICP intent but no URL found in query")
            
            # 🚀 COMPREHENSIVE LLM ANALYSIS using all mapping data
            llm_decision = self._analyze_with_full_llm(state)
            
            # Apply the LLM decision to state
            state = self._apply_llm_business_intelligence(state, llm_decision)
            
            return state
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] LLM analysis error: {e}")
            return self._fallback_analysis(state)
    
    def _create_comprehensive_llm_prompt(self, state: ConversationState) -> str:
        """Create comprehensive prompt using external template"""
        
        # Format conversation history
        chat_history = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages])
        
        # Try to load prompt from external template
        prompt = load_prompt_template(
            "business_reasoning",
            user_query=state['user_query'],
            detected_language=state.get('detected_language', 'en'),
            intent=state.get('intent', 'unknown'),
            chat_history=chat_history if chat_history else "No previous conversation context",
            icp_parameter_mapping=json.dumps(self.product_groups_data.get("icp_corrections", {}).get("parameter_map", {}), indent=1, ensure_ascii=False),
            products_knowledge=json.dumps(self.products_knowledge, indent=1, ensure_ascii=False),
            competitors_data=json.dumps(self.competitors_data, indent=1, ensure_ascii=False),
            scenarios_data=json.dumps(self.scenarios_data, indent=1, ensure_ascii=False),
            use_cases_data=json.dumps(self.use_cases_data, indent=1, ensure_ascii=False),
            product_groups_data=json.dumps(self.product_groups_data, indent=1, ensure_ascii=False)
        )
        
        # Fallback if template loading fails
        if not prompt:
            debug_print("⚠️ [BusinessReasoner] Using fallback hardcoded prompt")
            prompt = f"""
You are an Aquaforest business intelligence specialist.
Analyze this query: "{state['user_query']}"
Return JSON with product recommendations and business analysis.
"""

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
                
                reasoning = decision_data.get('reasoning_steps', {})
                print(f"   - Stage 1 products (direct): {reasoning.get('stage_1_products', 'N/A')[:50]}...")
                print(f"   - Stage 2 products (mapping): {reasoning.get('stage_2_products', 'N/A')[:50]}...")
                
                print(f"   - Total priority products: {len(decision_data.get('priority_products', []))}")
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
        product_recommendations = decision.get("product_recommendations", {})
        
        # 🆕 INTELLIGENT CATEGORIZATION: Extract all products from categories
        all_products = []
        for category, products in product_recommendations.items():
            if isinstance(products, list):
                all_products.extend(products)
        
        # Backward compatibility: also check legacy priority_products field
        legacy_products = decision.get("priority_products", [])
        if legacy_products:
            all_products.extend(legacy_products)
        
        if all_products:
            state["af_alternatives_to_search"] = all_products
            debug_print(f"🧠 [BusinessReasoner] LLM selected {len(all_products)} products via intelligent categorization")
        
            # Store categorized structure for Response Formatter
            state["product_recommendations"] = product_recommendations
            debug_print(f"📊 [BusinessReasoner] Categorized into {len(product_recommendations)} categories: {list(product_recommendations.keys())}")
        
            # Set first product as main correction for backward compatibility
            if all_products:
                state["business_analysis"]["product_name_corrections"] = all_products[0]
        else:
            debug_print(f"⚠️ [BusinessReasoner] No products found by LLM analysis")
        
        # 🚀 COMPREHENSIVE BUSINESS RECOMMENDATIONS
        recommendations = []
        
        # Categorized products recommendation
        if product_recommendations:
            recommendations.append({
                "type": "categorized_products",
                "categories": product_recommendations,
                "reasoning": decision.get("reasoning_steps", {}).get("categorization_logic", "LLM-organized into logical categories based on comprehensive analysis")
            })
        
        # 🚨 Alternative products (ONLY for competitor situations)
        alternative_products = decision.get("alternative_products", [])
        if alternative_products and competitors:  # Only if competitors detected
            recommendations.append({
                "type": "alternative_products", 
                "products": alternative_products,
                "note": "Alternative options for competitor products"
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
        
        # 🚨 CRITICAL FIX: FOLLOW_UP can only exist with chat history - ONLY this correction is allowed
        current_intent = state.get("intent", "")
        chat_history = state.get("chat_history", [])
        
        if current_intent == Intent.FOLLOW_UP and (not chat_history or len(chat_history) == 0):
            debug_print(f"🚨 [BusinessReasoner] CRITICAL FIX: Preventing FOLLOW_UP intent without chat history")
            debug_print(f"📋 [BusinessReasoner] Chat history length: {len(chat_history) if chat_history else 0}")
            state["intent"] = Intent.PRODUCT_QUERY  # Default to product_query for first messages
            debug_print(f"✅ [BusinessReasoner] Corrected intent from follow_up to product_query")
        
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