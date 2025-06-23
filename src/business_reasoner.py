"""
Business Logic Reasoner - VERSION 4.0 FULL LLM INTELLIGENCE
🚀 Complete LLM-based business intelligence with comprehensive JSON mapping
Replaces hybrid mapping system with pure GPT-4.1-mini intelligence
Maintains same class names and API for seamless integration
"""
import json
import os
import re  # 🆕 For ICP URL parsing  
import requests  # 🆕 For web scraping ICP data
from bs4 import BeautifulSoup  # 🆕 For HTML parsing
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
            # 🆕 ICP URL EXTRACTION - Handle before LLM analysis
            if state.get("intent") == Intent.ANALYZE_ICP:
                # Look for ICP URL in the query
                icp_url_match = re.search(r'(https?://)?aquaforestlab\.com/(?:pl|en)/results/\w+', state['user_query'])
                if icp_url_match:
                    icp_url = icp_url_match.group(0)
                    if not icp_url.startswith('http'):
                        icp_url = 'https://' + icp_url
                    
                    # Extract ICP data and add to state
                    icp_data = self._extract_icp_data_from_url(icp_url)
                    state["icp_analysis"] = icp_data
                    debug_print(f"🔬 [BusinessReasoner] ICP data extracted for URL: {icp_url}")
                    
                    # 📋 ADD ICP RESULTS TO USER QUERY for LLM analysis
                    if icp_data.get("parameters"):
                        icp_summary = self._format_icp_data_for_llm(icp_data["parameters"], icp_data.get("metadata", {}))
                        enhanced_query = f"{state['user_query']}\n\n📊 ICP TEST RESULTS:\n{icp_summary}"
                        state["user_query"] = enhanced_query
                        debug_print(f"📋 [BusinessReasoner] Enhanced query with ICP data")
                        
                        # 🔍 DEBUG: Print full ICP results for debugging
                        debug_print(f"📊 [BusinessReasoner] ICP TEST RESULTS:")
                        debug_print(f"{icp_summary}")
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
        """Create comprehensive prompt optimized for GPT-4.1-mini with all mapping data"""
        
        # Format conversation history
        chat_history = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages])
        
        # Create the comprehensive prompt optimized for GPT-4.1-mini (2025)
        prompt = f"""# Role and Objective

You are an expert Aquaforest product advisor with complete access to all product databases and business mapping data. Your task is to intelligently recommend products using a systematic two-stage analysis process.

# 🧠 CRITICAL INSTRUCTION - Two-Stage Product Discovery Process

You MUST follow this exact process for EVERY query:

## STAGE 1: Direct Product Analysis (products_turbo.json)
- Search through ALL products in the complete product database
- Check: product_name, category, keywords, solves_problems, use_case fields
- Find products that DIRECTLY match the user's query
- Examples:
  - "Fish food" → find products with category="foods_and_supplementation" + fish keywords
  - "Salts" → find products with "salt" in product_name or marine salt category
  - "Algae control" → find products where solves_problems contains "algae"
  - "Low magnesium" → find products with keywords containing "magnesium"

## STAGE 2: Mapping & Category Analysis  
- Search through product_groups, use_cases, scenarios mappings
- Find relevant categories/groups that match the query
- Extract ALL products from matching categories
- For ICP parameters: use icp_corrections parameter_map
- Examples:
  - "Fish food" → also check fish_nutrition group for additional products
  - "ICP low Mg" → use Mg.too_low mapping for complete product list

## STAGE 3: Intelligent Aggregation
- Combine products from Stage 1 + Stage 2
- Remove duplicates automatically
- Include ALL unique products in priority_products
- NO LIMITS on quantity - if 15 products match, include all 15

🚨 UNIVERSAL RULE FOR ALL SCENARIOS:
- NOT just ICP analysis - apply this for ALL user queries
- Fish food queries → ALL fish foods
- Salt queries → ALL salts  
- Problem solving → ALL relevant products
- Category requests → ALL products in category

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

## ICP PARAMETER MAPPING - MANDATORY USAGE FOR WATER ANALYSIS
🚨 When you identify ANY parameter problem (too_high/too_low), you MUST:
1. Find the parameter in the mapping below
2. Take ALL products for that status  
3. Add them to priority_products
4. Example: "Ca too_low" → take ALL products from Ca.too_low mapping

PARAMETER MAPPING:
{json.dumps(self.product_groups_data.get("icp_corrections", {}).get("parameter_map", {}), indent=1, ensure_ascii=False)}

## Available Products Database (Complete Details) - STAGE 1 SOURCE
{json.dumps(self.products_knowledge, indent=1, ensure_ascii=False)}

## Competitor Intelligence Database - STAGE 2 SOURCE
{json.dumps(self.competitors_data, indent=1, ensure_ascii=False)}

## Tank Setup Scenarios Database - STAGE 2 SOURCE
{json.dumps(self.scenarios_data, indent=1, ensure_ascii=False)}

## Use Cases Database - STAGE 2 SOURCE
{json.dumps(self.use_cases_data, indent=1, ensure_ascii=False)}

## Product Groups Strategy Database - STAGE 2 SOURCE
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

## Step 4: Two-Stage Product Discovery & Selection
- STAGE 1: Search products_turbo.json for direct matches to user query
- STAGE 2: Search mapping databases for category/group matches
- STAGE 3: Combine ALL products from both stages
- 🚨 NO LIMITS: If 15 products match across both stages, include all 15
- Document: Specific products found in each stage and reasoning

## Step 5: Intelligent Product Categorization
After identifying all relevant products, organize them into logical categories:

**DYNAMIC CATEGORIZATION RULES:**
🚨 CRITICAL: Create categories ONLY based on user's actual query - DO NOT use all 6 categories for every query!

**AVAILABLE CATEGORY OPTIONS:**
- **startup_essentials**: Core foundation products (salts, live rock, basic supplements)
- **water_chemistry**: All water parameter products (Ca, Mg, KH, trace elements, ICP corrections)
- **biological_system**: Bacterial products, bio media, filtration aids, biological supplements
- **feeding_nutrition**: All foods, feeding supplements, nutrition enhancers
- **maintenance_control**: Test kits, carbon, problem solvers, maintenance products
- **advanced_optimization**: Lab series, specialized/high-concentration products

**SMART DYNAMIC LOGIC:**
- ANALYZE user query to determine which categories are actually relevant
- CREATE only the categories that match the user's specific question
- Examples:
  * "fish food" query → ONLY "feeding_nutrition" category
  * "ICP low calcium" → ONLY "water_chemistry" category  
  * "new tank setup" → "startup_essentials" + "biological_system" + "water_chemistry"
  * "algae problem" → "maintenance_control" + maybe "biological_system"
  * "fish recommendations and food" → ONLY "feeding_nutrition" category
  * "salt recommendation" → ONLY "startup_essentials" category
  * "calcium dosing" → ONLY "water_chemistry" category
- Include 2-6 products per relevant category
- NEVER create categories that don't match the user's query

🚨 CRITICAL: Return ONLY relevant categories - if user asks about fish food, don't include salt or rock products!

## Step 6: Strategic Response Planning
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
        "stage_1_products": "Products found directly in products_turbo.json with reasoning",
        "stage_2_products": "Products found in mapping databases with reasoning", 
        "product_selection_logic": "Combined reasoning for all products from both stages",
        "categorization_logic": "Reasoning for how products were organized into categories",
        "response_strategy_logic": "Reasoning for chosen response approach"
    }},
    "business_interpretation": "Clear 1-2 sentence explanation of what user wants",
    "detected_scenario": "exact_scenario_key_from_scenarios_mapping_or_null",
    "detected_use_case": "exact_use_case_key_from_use_cases_mapping_or_null",
    "detected_competitors": ["exact_competitor_names_found_in_query"],
    "product_recommendations": {{
        "category_name_based_on_query": ["relevant_products_only"],
        "another_relevant_category_if_needed": ["more_relevant_products"]
    }},
    "alternative_products": ["backup_AF_products_from_mapping"],  
    "complementary_products": ["products_that_work_together_from_groups_mapping"],
    "competitor_alternatives": {{"competitor_name": "AF_alternative_from_mapping"}},
    "response_strategy": "direct|educational|comparative|troubleshooting",
    "missing_product_alerts": ["products_from_missing_alerts_mapping_if_applicable"],
    "intent_suggestion": "product_query|follow_up|purchase_inquiry|support|greeting|business|competitor|censored|analyze_icp",
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
        
        # 🚀 INTENT CORRECTION based on LLM analysis
        intent_suggestion = decision.get("intent_suggestion", "")
        
        # 🚨 CRITICAL FIX: FOLLOW_UP can only exist with chat history
        chat_history = state.get("chat_history", [])
        if intent_suggestion == "follow_up" and (not chat_history or len(chat_history) == 0):
            debug_print(f"🚨 [BusinessReasoner] CRITICAL FIX: Preventing FOLLOW_UP intent without chat history")
            debug_print(f"📋 [BusinessReasoner] Chat history length: {len(chat_history) if chat_history else 0}")
            intent_suggestion = "product_query"  # Default to product_query for first messages
            debug_print(f"✅ [BusinessReasoner] Corrected intent from follow_up to product_query")
        
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
    
    def _extract_icp_data_from_url(self, url: str) -> Dict:
        """🆕 Extract ICP test data from Aquaforest Lab URL"""
        try:
            debug_print(f"🌐 [BusinessReasoner] Fetching ICP data from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 🔍 LOG: Response details
            debug_print(f"📊 [BusinessReasoner] HTTP Status: {response.status_code}")
            debug_print(f"📊 [BusinessReasoner] Content-Type: {response.headers.get('content-type', 'unknown')}")
            debug_print(f"📊 [BusinessReasoner] Content Length: {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 🔍 LOG: HTML structure analysis
            debug_print(f"📋 [BusinessReasoner] Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Find all tables
            tables = soup.find_all('table')
            debug_print(f"📋 [BusinessReasoner] Found {len(tables)} table(s) on page")
            
            # 🆕 EXTRACT ICP METADATA (test info)
            metadata = self._extract_icp_metadata(soup)
            
            # Structure based on typical ICP test results
            icp_data = {
                "url": url,
                "parameters": {},
                "metadata": metadata,  # 🆕 Add metadata
                "status": "success",
                "debug_info": {
                    "tables_found": len(tables),
                    "page_title": soup.title.string if soup.title else None
                }
            }
            
            # 🎯 EXTRACT ALL ICP DATA - Dynamic table parsing
            results_table = soup.find('table', class_='table-results') or soup.find('table')
            
            if results_table:
                debug_print(f"📋 [BusinessReasoner] Found results table")
                
                # Find all test result rows (skip header)
                test_rows = results_table.find_all('tr')[1:]  # Skip header
                debug_print(f"📋 [BusinessReasoner] Processing {len(test_rows)} parameter rows")
                
                for i, row in enumerate(test_rows):
                    # Extract all cells dynamically
                    all_cells = row.find_all('td')
                    if len(all_cells) >= 3:  # Need at least: element, range, result
                        
                        # 📊 COLUMN MAPPING (English workflow)
                        element = all_cells[0].get_text(strip=True)
                        recommended_range = all_cells[1].get_text(strip=True) 
                        user_result = all_cells[2].get_text(strip=True)
                        change = all_cells[3].get_text(strip=True) if len(all_cells) > 3 else ""
                        
                        # Skip empty or header-like rows
                        if not element or element.lower() in ['pierwiastek', 'element']:
                            continue
                        
                        debug_print(f"📊 [BusinessReasoner] ELEMENT: '{element}' | RECOMMENDED: '{recommended_range}' | RESULT: '{user_result}' | CHANGE: '{change}'")
                        
                        # 🧠 SMART ANALYSIS: Check if result is within recommended range
                        status = self._analyze_icp_parameter_status(element, recommended_range, user_result)
                        
                        icp_data["parameters"][element] = {
                            "element": element,
                            "recommended_range": recommended_range, 
                            "user_result": user_result,
                            "change": change,
                            "status": status,
                            "needs_correction": status in ["too_high", "too_low"]
                        }
                    else:
                        # Log incomplete rows
                        if all_cells:
                            cell_contents = [cell.get_text(strip=True) for cell in all_cells]
                            debug_print(f"📊 [BusinessReasoner] Row {i+1} (incomplete): {cell_contents}")
            else:
                debug_print(f"⚠️ [BusinessReasoner] No results table found")
            
            # 🔍 LOG: Final extraction summary
            debug_print(f"✅ [BusinessReasoner] Extracted {len(icp_data['parameters'])} ICP parameters")
            if icp_data["parameters"]:
                param_names = list(icp_data["parameters"].keys())[:5]  # First 5 parameters
                debug_print(f"📋 [BusinessReasoner] Sample parameters: {param_names}")
            
            return icp_data
            
        except requests.RequestException as e:
            debug_print(f"❌ [BusinessReasoner] HTTP error fetching ICP data: {e}")
            return {"url": url, "parameters": {}, "status": "http_error", "error": str(e)}
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Error extracting ICP data: {e}")
            return {"url": url, "parameters": {}, "status": "parse_error", "error": str(e)}
    
    def _analyze_icp_parameter_status(self, element: str, recommended_range: str, user_result: str) -> str:
        """🧠 Analyze if ICP parameter result is within recommended range"""
        try:
            import re
            
            # Extract numeric values from strings
            def extract_number(text):
                # Find first number (including decimals)
                match = re.search(r'(\d+\.?\d*)', text.replace(',', '.'))
                return float(match.group(1)) if match else None
            
            # Parse recommended range (e.g., "33 - 38 ppt", "0 - 0.0300 mg/l")
            range_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', recommended_range.replace(',', '.'))
            if range_match:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
                
                # Extract result value
                result_val = extract_number(user_result)
                
                if result_val is not None:
                    debug_print(f"🧠 [BusinessReasoner] Analysis: {element} = {result_val} (range: {min_val}-{max_val})")
                    
                    if result_val < min_val:
                        return "too_low"
                    elif result_val > max_val:
                        return "too_high"
                    else:
                        return "optimal"
            
            # If can't parse range, check for single value or zero
            if "0 mg/l" in recommended_range or recommended_range.strip() == "0":
                result_val = extract_number(user_result)
                if result_val is not None and result_val > 0:
                    return "too_high"
                elif result_val == 0:
                    return "optimal"
            
            debug_print(f"⚠️ [BusinessReasoner] Could not analyze: {element} - {recommended_range} vs {user_result}")
            return "unknown"
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Error analyzing {element}: {e}")
            return "unknown"
    
    def _extract_icp_metadata(self, soup) -> Dict:
        """🆕 Extract ICP test metadata (test number, aquarium info, date)"""
        metadata = {}
        
        try:
            import re
            
            # 🔍 DEBUG: Print all text content to see structure
            debug_print(f"📋 [BusinessReasoner] Searching for metadata in page content...")
            
            # Look for test number in page title first
            title = soup.title.string if soup.title else ""
            debug_print(f"📋 [BusinessReasoner] Page title: '{title}'")
            if "Test wody" in title or "#" in title:
                test_match = re.search(r'#?(\d+)', title)
                if test_match:
                    metadata["test_number"] = test_match.group(1)
                    debug_print(f"📋 [BusinessReasoner] Found test number in title: {metadata['test_number']}")
            
            # 🎯 IMPROVED: Look for specific patterns in all text elements
            all_text_elements = soup.find_all(['div', 'span', 'strong', 'p'])
            
            for element in all_text_elements:
                text = element.get_text(strip=True)
                
                # Look for "Badanie Woda morska: NUMBER"
                badanie_match = re.search(r'Badanie\s+Woda\s+morska:?\s*(\d+)', text, re.IGNORECASE)
                if badanie_match and not metadata.get("test_number"):
                    metadata["test_number"] = badanie_match.group(1)
                    debug_print(f"📋 [BusinessReasoner] Found test number: {metadata['test_number']} in text: '{text[:50]}...'")
                
                # Look for "Akwarium (SPS): INFO"
                aquarium_match = re.search(r'Akwarium\s*\([^)]+\):?\s*(.+)', text, re.IGNORECASE)
                if aquarium_match and not metadata.get("aquarium_info"):
                    aquarium_info = aquarium_match.group(1).strip()
                    if aquarium_info and aquarium_info != ":":  # Skip empty results
                        metadata["aquarium_info"] = aquarium_info
                        debug_print(f"📋 [BusinessReasoner] Found aquarium info: '{metadata['aquarium_info']}' in text: '{text[:50]}...'")
                
                # Look for "Data: DATE"
                date_match = re.search(r'Data:?\s*([\d-]+)', text, re.IGNORECASE)
                if date_match and not metadata.get("test_date"):
                    test_date = date_match.group(1).strip()
                    if test_date and test_date != "-":  # Skip empty results
                        metadata["test_date"] = test_date
                        debug_print(f"📋 [BusinessReasoner] Found test date: '{metadata['test_date']}' in text: '{text[:50]}...'")
            
            # 🔍 FALLBACK: Look for patterns in the entire page text
            if not metadata.get("test_number") or not metadata.get("aquarium_info") or not metadata.get("test_date"):
                full_text = soup.get_text()
                debug_print(f"📋 [BusinessReasoner] Fallback search in full page text...")
                
                # Extract test number from anywhere
                if not metadata.get("test_number"):
                    test_matches = re.findall(r'(\d{7})', full_text)
                    if test_matches:
                        metadata["test_number"] = test_matches[0]  # Take first 7-digit number
                        debug_print(f"📋 [BusinessReasoner] Fallback found test number: {metadata['test_number']}")
                
                # Extract aquarium info more broadly
                if not metadata.get("aquarium_info"):
                    aquarium_matches = re.findall(r'Domowe\s+\d+\s+LPS', full_text, re.IGNORECASE)
                    if aquarium_matches:
                        metadata["aquarium_info"] = aquarium_matches[0]
                        debug_print(f"📋 [BusinessReasoner] Fallback found aquarium: {metadata['aquarium_info']}")
                
                # Extract date more broadly
                if not metadata.get("test_date"):
                    date_matches = re.findall(r'20\d{2}-\d{2}-\d{2}', full_text)
                    if date_matches:
                        metadata["test_date"] = date_matches[0]
                        debug_print(f"📋 [BusinessReasoner] Fallback found date: {metadata['test_date']}")
            
            debug_print(f"📋 [BusinessReasoner] Final extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Error extracting metadata: {e}")
            return {}
    
    def _format_icp_data_for_llm(self, parameters: Dict, metadata: Dict = None) -> str:
        """📋 Format ICP data for LLM analysis with aquarium info for precise dosing calculations"""
        lines = []
        
        # 🎯 AQUARIUM INFO for dosing calculations
        if metadata:
            aquarium_info = metadata.get("aquarium_info", "")
            test_date = metadata.get("test_date", "")
            
            # Extract volume from aquarium_info (e.g., "Domowe 1150 LPS")
            import re
            volume_match = re.search(r'(\d+)', aquarium_info) if aquarium_info else None
            volume = volume_match.group(1) if volume_match else "unknown"
            
            lines.append(f"AQUARIUM: {volume}L | DATE: {test_date}")
            lines.append("")
        
        lines.append("ELEMENT | RECOMMENDED | RESULT | CHANGE | STATUS")
        lines.append("-" * 60)
        
        for param_name, data in parameters.items():
            element = data.get("element", param_name)
            
            # Format element name: "PO4Fosforany" → "PO4 Fosforany"
            import re
            match = re.match(r'^([A-Za-z0-9]+)([A-Z][a-z]+.*)$', element)
            if match:
                symbol = match.group(1)
                name = match.group(2)
                element_formatted = f"{symbol} {name}"
            else:
                element_formatted = element
            
            recommended = data.get("recommended_range", "")
            user_result = data.get("user_result", "")
            change = data.get("change", "")
            status = data.get("status", "unknown")
            
            status_icon = {
                "too_high": "⬆️ HIGH",
                "too_low": "⬇️ LOW", 
                "optimal": "✅ OK",
                "unknown": "❓"
            }.get(status, status)
            
            line = f"{element_formatted} | {recommended} | {user_result} | {change} | {status_icon}"
            lines.append(line)
        
        return "\n".join(lines)
    
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