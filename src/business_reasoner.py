"""
Business Logic Reasoner - VERSION 3.0 HYBRID ENHANCED with JSON Mapping
Advanced business intelligence with comprehensive mapping system and context awareness
🚀 Enhanced with competitors detection, scenario mapping, and product group intelligence
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from openai import OpenAI
from models import ConversationState, Intent
from config import OPENAI_API_KEY, OPENAI_MODEL, TEST_ENV, debug_print, PRODUCTS_FILE_PATH

class BusinessReasoner:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.products_list = self._load_products_list()
        self.products_knowledge = self._load_products_knowledge()
        
        # 🚀 LOAD ENHANCED MAPPING DATA FROM JSON FILES
        self._load_mapping_data()
        
        # 🆕 ENHANCED PRODUCT CATEGORY MAPPING (legacy fallback)
        self.product_categories = {
            "salts": ["Sea Salt", "Reef Salt", "Reef Salt Plus", "Hybrid Pro Salt"],
            "bacteria": ["Pro Bio S", "Pro Bio F", "Life Source", "Life Essence", "Bio S"],
            "calcium_supplements": ["Ca Plus", "Calcium", "Ca plus"],
            "magnesium_supplements": ["Mg Plus", "Magnesium"],
            "kh_supplements": ["KH Plus", "KH Buffer", "KH Pro"],
            "amino_acids": ["AF Amino Mix", "AF Power Elixir", "AF Vitality"],
            "foods": ["AF Marine Mix S", "AF Marine Mix M", "AF Marine Flakes", "AF Algae Feed", "AF Vege Clip"],
            "test_kits": ["Calcium Test Kit", "Magnesium Test Kit", "Alkanity Test Kit", "Nitrate Test Kit", "Phosphate Test Kit"],
            "filter_media": ["Phosphate Minus", "Carbon", "AF Carbon", "Zeo Mix"],
            "balling_method": ["Component 1+2+3+", "Components Pro", "Components Strong"],
            "substrates": ["AF Lava Soil", "AF Lava Soil Black", "AF Natural Substrate"],
            "probiotics": ["Pro Bio S", "Pro Bio F", "-NP Pro", "AF NitraPhos Minus"],
            "cleaning": ["Aiptasia Shot", "AF Protect Dip"],
            "coral_growth": ["AF Growth Boost", "AF Build", "AF Energy"],
            "coral_coloration": ["AF Amino Mix", "AF Power Elixir", "AF Vitality", "Kalium", "Iron"],
            "ph_control": ["KH Buffer", "KH Plus", "AF Minus pH", "AF Air Scrubber"],
            "trace_elements": ["Iodum", "Strontium", "Kalium", "Fluorum", "Component A", "Component B", "Component C"],
            "marine_water": ["AF Perfect Water", "Sea Salt", "Reef Salt", "Reef Salt Plus", "Hybrid Pro Salt"]
        }
        
        # 🆕 ENHANCED PROBLEM-SOLUTION MAPPING  
        self.problem_solutions = {
            "ph_dropping": {
                "marine": ["KH Buffer", "KH Plus", "AF Air Scrubber", "KalkMedia"],
                "freshwater": ["KH Plus", "AF Remineralizer"],
                "explanation": "pH drops require alkalinity buffers"
            },
            "ph_rising": {
                "marine": ["CO2 system", "reduce aeration"],
                "freshwater": ["AF Minus pH", "CO2 injection"],
                "explanation": "pH rises need acidification"
            },
            "algae": ["Phosphate Minus", "-NP Pro", "Pro Bio S", "AF NitraPhos Minus"],
            "corals_browning": ["AF Amino Mix", "AF Power Elixir", "AF Vitality", "Kalium", "Iron"],
            "aiptasia": ["Aiptasia Shot"],
            "cyanobacteria": ["Pro Bio S", "-NP Pro", "AF NitraPhos Minus"],
            "low_calcium": {
                "correction": ["Ca Plus", "Calcium"],
                "maintenance": ["Component 1+2+3+", "Components Pro", "Components Strong"],
                "note": "Balling products contain multiple elements for stability"
            },
            "low_magnesium": {
                "correction": ["Mg Plus", "Magnesium"],
                "maintenance": ["Component 1+2+3+", "Components Pro", "Components Strong"],
                "note": "Balling products contain multiple elements for stability"
            },
            "low_kh": {
                "correction": ["KH Plus", "KH Buffer"],
                "maintenance": ["Component 1+2+3+", "Components Pro", "Components Strong"],
                "note": "Balling products contain multiple elements for stability"
            },
            "high_nitrates": ["AF NitraPhos Minus", "Pro Bio S", "-NP Pro", "Phosphate Minus"],
            "high_phosphates": ["Phosphate Minus", "AF Anti Phosphate", "AF NitraPhos Minus"]
        }
        
        # 🆕 PRODUCT PURPOSE CLASSIFICATION
        self.product_purposes = {
            "Ca Plus": "correction",
            "Calcium": "correction",
            "Mg Plus": "correction",
            "Magnesium": "correction",
            "KH Plus": "correction",
            "KH Buffer": "correction",
            "Component 1+2+3+": "maintenance",
            "Components Pro": "maintenance",
            "Components Strong": "maintenance"
        }
        

        
        # 🆕 COMPETITORS LIST
        self.competitors = [
            "Red Sea", "Seachem", "Tropic Marin", "Brightwell", "Two Little Fishies",
            "Salifert", "Continuum", "Korallen-Zucht", "ESV", "Kent Marine",
            "Aqua Medic", "Fauna Marin", "Nyos", "ATI", "Giesemann"
        ]
    
    def _load_products_list(self) -> List[str]:
        """Load simple product names list"""
        try:
            with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Error loading products list: {e}")
            return []
    
    def _load_products_knowledge(self) -> List[Dict]:
        """Load detailed product knowledge"""
        try:
            with open("data/products_turbo.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Error loading products knowledge: {e}")
            return []
    
    def _load_mapping_data(self):
        """🚀 Load comprehensive mapping data from JSON files"""
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
                
            # Extract competitor names for faster lookup
            self.all_competitors = set()
            for category, competitors in self.competitors_data.get("competitors", {}).items():
                self.all_competitors.update([comp.lower() for comp in competitors])
                
            debug_print(f"🚀 [BusinessReasoner] Enhanced mapping system loaded successfully!")
            debug_print(f"📊 [BusinessReasoner] Tracking {len(self.all_competitors)} competitor products")
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Failed to load mapping data: {e}")
            # Fallback to basic mappings
            self._initialize_fallback_mappings()
    
    def _initialize_fallback_mappings(self):
        """Initialize basic fallback mappings if JSON loading fails"""
        debug_print("⚠️ [BusinessReasoner] Using fallback mappings")
        self.competitors_data = {"competitors": {}, "response_strategies": {}}
        self.scenarios_data = {"tank_setup_scenarios": {}}
        self.product_groups_data = {"product_groups": {}}
        self.use_cases_data = {"use_cases": {}}
        self.all_competitors = set(comp.lower() for comp in self.competitors)
    
    def analyze(self, state: ConversationState) -> ConversationState:
        """🚀 Enhanced Main analysis method with comprehensive mapping"""
        debug_print(f"🧠 [BusinessReasoner] Analyzing query: '{state['user_query']}'", "🧠")
        
        # 🚀 ENHANCED COMPETITOR DETECTION  
        competitor_info = self._detect_competitors_enhanced(state["user_query"])
        if competitor_info:
            # ✅ NIE ZMIENIAMY INTENCJI - zachowujemy naturalny flow!
            state["competitor_info"] = competitor_info
            debug_print(f"🏢 [BusinessReasoner] Competitor detected: {competitor_info}")
            
            # 🎯 Znajdź najlepsze alternatywy AF przez LLM
            alternatives = self._find_af_alternatives_with_llm(competitor_info, state)
            if alternatives:
                state["af_alternatives_to_search"] = alternatives
                debug_print(f"🎯 [BusinessReasoner] Found AF alternatives: {alternatives}")
        
        # 🚀 SCENARIO DETECTION
        scenario_info = self._detect_scenario(state["user_query"])
        if scenario_info:
            state["scenario_info"] = scenario_info
            debug_print(f"📋 [BusinessReasoner] Scenario detected: {scenario_info['name']}")
        
        # 🚀 USE CASE ANALYSIS
        use_case_info = self._analyze_use_case(state["user_query"])
        if use_case_info:
            state["use_case_info"] = use_case_info
            debug_print(f"🎯 [BusinessReasoner] Use case identified: {use_case_info['name']}")
        
        # Create enhanced business context
        business_context = self._create_enhanced_business_context(state)
        
        # Analyze with GPT
        business_analysis = self._analyze_with_gpt(state, business_context)
        
        # Apply enhanced business intelligence
        if business_analysis:
            state = self._apply_enhanced_business_intelligence(state, business_analysis)
        
        return state
    
    def _detect_competitors_enhanced(self, query: str) -> Optional[Dict]:
        """🚀 Enhanced competitor detection with context and alternatives"""
        query_lower = query.lower()
        
        detected_competitors = []
        af_alternatives = {}
        
        # Check against comprehensive competitor mapping
        for comp_lower in self.all_competitors:
            if comp_lower in query_lower:
                # Find the original competitor name and category
                for category, competitors in self.competitors_data.get("competitors", {}).items():
                    for comp in competitors:
                        if comp.lower() == comp_lower:
                            detected_competitors.append({
                                "name": comp,
                                "category": category,
                                "original": comp_lower
                            })
                            
                            # Get AF alternative if available
                            alternatives = self.competitors_data.get("response_strategies", {}).get("af_alternatives", {})
                            if comp in alternatives:
                                af_alternatives[comp] = alternatives[comp]
                            break
        
        if detected_competitors:
            return {
                "competitors": detected_competitors,
                "af_alternatives": af_alternatives,
                "response_templates": self.competitors_data.get("response_strategies", {}).get("acknowledge_and_redirect", {}).get("templates", [])
            }
        
        # Fallback to legacy detection
        for comp in self.competitors:
            if comp.lower() in query_lower:
                return {
                    "competitors": [{"name": comp, "category": "unknown", "original": comp.lower()}],
                    "af_alternatives": {},
                    "response_templates": []
                }
        
        return None
    
    def _detect_scenario(self, query: str) -> Optional[Dict]:
        """🚀 Detect tank setup scenarios from query"""
        query_lower = query.lower()
        
        for scenario_key, scenario_data in self.scenarios_data.get("tank_setup_scenarios", {}).items():
            triggers = scenario_data.get("triggers", [])
            
            # Check if any trigger matches
            for trigger in triggers:
                if trigger.lower() in query_lower:
                    return {
                        "name": scenario_key,
                        "data": scenario_data,
                        "priority_order": scenario_data.get("priority_order", []),
                        "mandatory_categories": scenario_data.get("mandatory_categories", [])
                    }
        
        return None
    
    def _analyze_use_case(self, query: str) -> Optional[Dict]:
        """🚀 Analyze query for specific use cases"""
        query_lower = query.lower()
        
        for use_case_key, use_case_data in self.use_cases_data.get("use_cases", {}).items():
            keywords = use_case_data.get("context_keywords", [])
            
            # Check if any keyword matches
            matching_keywords = [kw for kw in keywords if kw.lower() in query_lower]
            
            if matching_keywords:
                return {
                    "name": use_case_key,
                    "data": use_case_data,
                    "matching_keywords": matching_keywords,
                    "priority_products": use_case_data.get("priority_products", []),
                    "timeline": use_case_data.get("timeline", "")
                }
        
        return None
    
    def _create_enhanced_business_context(self, state: ConversationState) -> str:
        """🚀 Create enhanced business context using all mapping data"""
        context_lines = []
        
        # Add competitor context if detected
        if "competitor_info" in state:
            context_lines.append("🏢 COMPETITOR CONTEXT:")
            for comp in state["competitor_info"]["competitors"]:
                alt = state["competitor_info"]["af_alternatives"].get(comp["name"], "AF equivalent available")
                context_lines.append(f"  - {comp['name']} → Recommend: {alt}")
        
        # Add scenario context
        if "scenario_info" in state:
            context_lines.append("📋 SCENARIO CONTEXT:")
            scenario = state["scenario_info"]
            context_lines.append(f"  - Detected: {scenario['name']}")
            context_lines.append(f"  - Priority order: {', '.join(scenario.get('priority_order', []))}")
            context_lines.append(f"  - Mandatory categories: {', '.join(scenario.get('mandatory_categories', []))}")
        
        # Add use case context
        if "use_case_info" in state:
            context_lines.append("🎯 USE CASE CONTEXT:")
            use_case = state["use_case_info"]
            context_lines.append(f"  - Identified: {use_case['name']}")
            context_lines.append(f"  - Priority products: {', '.join(use_case.get('priority_products', []))}")
            if use_case.get("timeline"):
                context_lines.append(f"  - Timeline: {use_case['timeline']}")
        
        # Add product group context
        context_lines.append("🛍️ PRODUCT GROUP RECOMMENDATIONS:")
        relevant_groups = self._get_relevant_product_groups(state)
        for group_name, group_data in relevant_groups.items():
            context_lines.append(f"  - {group_data['name']}: {', '.join(group_data['products'][:5])}")
        
        # Add legacy context as fallback
        legacy_context = self._create_business_context(state["user_query"])
        if legacy_context and "No directly relevant products found" not in legacy_context:
            context_lines.append("📦 PRODUCT MATCHES:")
            context_lines.extend(legacy_context.split("\n")[:10])
        
        return "\n".join(context_lines) if context_lines else "Enhanced context not available."
    
    def _get_relevant_product_groups(self, state: ConversationState) -> Dict:
        """🚀 Get relevant product groups based on context"""
        relevant_groups = {}
        
        # If scenario detected, get mandatory groups
        if "scenario_info" in state:
            scenario = state["scenario_info"]
            mandatory_categories = scenario.get("mandatory_categories", [])
            
            for group_key, group_data in self.product_groups_data.get("product_groups", {}).items():
                mandatory_for = group_data.get("mandatory_for", [])
                if scenario["name"] in mandatory_for or any(cat in group_key for cat in mandatory_categories):
                    relevant_groups[group_key] = group_data
        
        # If use case detected, get priority groups
        if "use_case_info" in state:
            use_case = state["use_case_info"]
            priority_products = use_case.get("priority_products", [])
            
            for group_key, group_data in self.product_groups_data.get("product_groups", {}).items():
                group_products = group_data.get("products", [])
                if any(prod in priority_products for prod in group_products):
                    relevant_groups[group_key] = group_data
        
        # If no specific context, return high-priority groups
        if not relevant_groups:
            for group_key, group_data in self.product_groups_data.get("product_groups", {}).items():
                if group_data.get("priority", 10) <= 3:  # High priority groups only
                    relevant_groups[group_key] = group_data
        
        return relevant_groups
    
    def _find_af_alternatives_with_llm(self, competitor_info: Dict, state: ConversationState) -> List[str]:
        """🚀 Użyj LLM do znalezienia najlepszych alternatyw AF"""
        
        competitors_list = [comp["name"] for comp in competitor_info.get("competitors", [])]
        
        prompt = f"""You are an Aquaforest product expert. Find the BEST Aquaforest alternatives for these competitor products.

COMPETITOR PRODUCTS: {', '.join(competitors_list)}

USER CONTEXT: "{state['user_query']}"

AVAILABLE AQUAFOREST PRODUCTS WITH DETAILS:
{json.dumps([{
    "name": p["product_name"], 
    "use_case": p["use_case"], 
    "category": p["category"]
} for p in self.products_knowledge], indent=2)}

TASK: For each competitor product, find the most suitable Aquaforest alternative based on:
1. Similar functionality and use case
2. Same category (salt, supplement, food, etc.)
3. User's specific needs from context

Return ONLY valid JSON:
{{
    "alternatives": {{
        "competitor_name": "best_af_alternative",
        "competitor_name2": "best_af_alternative2"
    }},
    "reasoning": "brief explanation of choices"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.1,
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            alternatives = list(result.get("alternatives", {}).values())
            
            # Weryfikuj że produkty istnieją
            verified_alternatives = []
            for alt in alternatives:
                if self._validate_product_exists(alt):
                    verified_alternatives.append(alt)
            
            debug_print(f"🔍 [BusinessReasoner] LLM found alternatives: {verified_alternatives}")
            return verified_alternatives
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] LLM alternatives error: {e}")
            # Fallback do statycznych mapowań
            fallback_alternatives = list(competitor_info.get("af_alternatives", {}).values())
            debug_print(f"🔄 [BusinessReasoner] Using fallback alternatives: {fallback_alternatives}")
            return fallback_alternatives
    
    def _check_competitors(self, query: str) -> bool:
        """Legacy method for backward compatibility"""
        return self._detect_competitors_enhanced(query) is not None
    
    def _find_category_for_query(self, query: str) -> Optional[str]:
        """Find which category the query is asking about"""
        query_lower = query.lower()
        
        # Direct category keywords
        category_keywords = {
            "salts": ["salt", "salts", "marine salt"],
            "bacteria": ["bacteria", "bacterial", "probiotic"],
            "test_kits": ["test", "testing", "test kit"],
            "filter_media": ["media", "filter media", "filtration"],
            "amino_acids": ["amino", "amino acids"],
            "foods": ["food", "feed", "feeding"],
            "substrates": ["substrate", "soil", "lava"],
            "trace_elements": ["trace", "trace elements", "microelements"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
    
    def _create_business_context(self, query: str) -> str:
        """Create enhanced business context"""
        query_words = set(query.lower().split())
        relevant_products = []
        
        # Check if query asks for category
        category_requested = self._find_category_for_query(query)
        if category_requested and category_requested in self.product_categories:
            # Add all products from category
            for product in self.product_categories[category_requested]:
                product_info = next((p for p in self.products_knowledge if p['product_name'] == product), None)
                if product_info:
                    relevant_products.append(product_info)
        
        # Also check for specific products
        for product in self.products_knowledge:
            product_text = " ".join([
                product.get("product_name", ""),
                " ".join(product.get("keywords", [])),
                " ".join(product.get("solves_problems", [])),
                product.get("use_case", "")
            ]).lower()
            
            if any(word in product_text for word in query_words if len(word) > 2):
                if product not in relevant_products:
                    relevant_products.append(product)
            
            if len(relevant_products) >= 20:
                break
        
        # Format context
        context_lines = []
        for p in relevant_products[:15]:
            context_lines.append(
                f"- {p['product_name']}: {p.get('use_case', 'N/A')[:100]}... "
                f"Solves: {', '.join(p.get('solves_problems', [])[:3])}"
            )
        
        return "\n".join(context_lines) if context_lines else "No directly relevant products found."
    
    def _analyze_with_gpt(self, state: ConversationState, business_context: str) -> Dict:
        """Enhanced GPT analysis"""
        chat_history_context = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history_context = "\nRECENT CONVERSATION:\n" + "\n".join([
                f"{msg['role']}: {msg['content'][:100]}..." for msg in recent_messages
            ])
        
        # Detect domain from context
        domain_hint = self._detect_domain(state)
        
        prompt = f"""You are an expert aquarium business analyst with deep product knowledge.

USER QUERY: "{state['user_query']}"
DETECTED INTENT: {state.get('intent', 'UNKNOWN')}
DETECTED LANGUAGE: {state.get('detected_language', 'unknown')}
DETECTED DOMAIN: {domain_hint}
{chat_history_context}

RELEVANT BUSINESS KNOWLEDGE:
{business_context}

AVAILABLE PRODUCT CATEGORIES:
{json.dumps(self.product_categories, indent=2)}

PROBLEM-SOLUTION MAPPING:
{json.dumps(self.problem_solutions, indent=2)}

PRODUCT PURPOSE CLASSIFICATION:
{json.dumps(self.product_purposes, indent=2)}

COMPLETE AQUAFOREST PRODUCT LIST:
{', '.join(self.products_list)}

IMPORTANT: When user asks about raising/correcting a SINGLE parameter:
- Prioritize "correction" products (Ca Plus, Mg Plus, KH Plus)
- If suggesting "maintenance" products (Component/Balling), MUST note they contain multiple elements

BUSINESS LOGIC ANALYSIS:
Analyze this query with aquarium business intelligence:

1. CATEGORY DETECTION: Is user asking about a product category?
   - "what salts do you have" → category: "salts", list all: ["Sea Salt", "Reef Salt", "Reef Salt Plus", "Hybrid Pro Salt"]
   - "what do you recommend for bacteria" → category: "bacteria"

2. PRODUCT NAME CORRECTIONS: Fix typos and common names using your knowledge
   - Look for common mistakes like: "ca+" → "Ca Plus", "bio s" → "Pro Bio S", "nitraphos" → "AF NitraPhos Minus"
   - Use the complete product list below to find correct names
   - Apply intelligent fuzzy matching for misspellings

3. PROBLEM ANALYSIS: What problem is user trying to solve?
   - "pH dropping" → solutions for dropping pH (KH buffers)
   - "pH rising" → solutions for rising pH (pH minus)
   - CRITICAL: pH dropping and pH rising are OPPOSITE problems!

4. BUSINESS INTERPRETATION: What does user REALLY want?

5. DOMAIN DETECTION: Freshwater, marine, or universal?

6. INTENT VERIFICATION: Is the detected intent correct?

Respond ONLY with valid JSON:
{{
  "business_interpretation": "clear explanation",
  "product_name_corrections": "corrected names or None",
  "category_requested": "category name if asking for category, else None",
  "products_in_category": ["list of products if category requested"],
  "problem_identified": "specific problem like 'pH dropping' or None",
  "solutions_for_problem": ["list of solutions"] OR {{"correction": ["products"], "maintenance": ["products"], "note": "explanation"}},
  "intent_correction": "corrected intent or same",
  "domain_hint": "freshwater|seawater|universal|unknown",
  "search_enhancement": "specific search terms"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.1,
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            debug_print(f"🤖 [BusinessReasoner] GPT analysis completed")
            return result
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] GPT analysis error: {e}")
            return {}
    
    def _detect_domain(self, state: ConversationState) -> str:
        """Detect domain from context"""
        text = state.get("user_query", "").lower()
        if state.get("chat_history"):
            for msg in state["chat_history"][-4:]:
                text += " " + msg["content"].lower()
        
        freshwater_keywords = ["freshwater", "gupik", "neon", "krewetk"]
        marine_keywords = ["marine", "reef", "koral", "sps", "lps", "salt water"]
        
        fresh_score = sum(1 for k in freshwater_keywords if k in text)
        marine_score = sum(1 for k in marine_keywords if k in text)
        
        if fresh_score > marine_score:
            return "freshwater"
        elif marine_score > fresh_score:
            return "seawater"
        return "unknown"
    
    def _apply_enhanced_business_intelligence(self, state: ConversationState, analysis: Dict) -> ConversationState:
        """🚀 Apply enhanced business intelligence with comprehensive logic"""
        debug_print("🎯 [BusinessReasoner] Applying enhanced business intelligence")
        
        # Start with legacy logic for backward compatibility
        state = self._apply_business_intelligence(state, analysis)
        
        # 🚀 ENHANCED COMPETITOR HANDLING
        if "competitor_info" in state:
            self._handle_competitor_response(state, analysis)
        
        # 🚀 SCENARIO-BASED RECOMMENDATIONS
        if "scenario_info" in state:
            self._apply_scenario_recommendations(state, analysis)
        
        # 🚀 USE CASE OPTIMIZATION
        if "use_case_info" in state:
            self._apply_use_case_optimization(state, analysis)
        
        # 🚀 MISSING PRODUCT ALERTS
        self._check_missing_product_groups(state, analysis)
        
        return state
    
    def _handle_competitor_response(self, state: ConversationState, analysis: Dict):
        """🚀 Handle competitor mentions with strategic responses"""
        competitor_info = state["competitor_info"]
        
        # Add competitor handling instructions to business_recommendations
        if "business_recommendations" not in state:
            state["business_recommendations"] = []
        
        # Add AF alternatives
        for comp_name, af_alternative in competitor_info["af_alternatives"].items():
            state["business_recommendations"].append({
                "type": "competitor_alternative",
                "competitor": comp_name,
                "af_alternative": af_alternative,
                "message": f"While {comp_name} is mentioned, I recommend our {af_alternative} for superior performance and compatibility."
            })
        
        debug_print(f"🏢 [BusinessReasoner] Added {len(competitor_info['af_alternatives'])} competitor alternatives")
    
    def _apply_scenario_recommendations(self, state: ConversationState, analysis: Dict):
        """🚀 Apply scenario-based product recommendations"""
        scenario_info = state["scenario_info"]
        scenario_data = scenario_info["data"]
        
        # Get comprehensive setup phases if this is a new tank scenario
        if "comprehensive_tank_setup" in self.scenarios_data:
            phases = self.scenarios_data["comprehensive_tank_setup"]
            
            if "business_recommendations" not in state:
                state["business_recommendations"] = []
            
            # Add phase-based recommendations
            for phase_key, phase_data in phases.items():
                state["business_recommendations"].append({
                    "type": "setup_phase",
                    "phase": phase_data["name"],
                    "duration": phase_data["duration"],
                    "products": phase_data["products"],
                    "priority": True if "foundation" in phase_key else False
                })
        
        debug_print(f"📋 [BusinessReasoner] Applied scenario recommendations for: {scenario_info['name']}")
    
    def _apply_use_case_optimization(self, state: ConversationState, analysis: Dict):
        """🚀 Apply use case specific optimizations"""
        use_case_info = state["use_case_info"]
        use_case_data = use_case_info["data"]
        
        if "business_recommendations" not in state:
            state["business_recommendations"] = []
        
        # Add priority products for this use case
        priority_products = use_case_data.get("priority_products", [])
        if priority_products:
            state["business_recommendations"].append({
                "type": "use_case_priority",
                "use_case": use_case_info["name"],
                "priority_products": priority_products,
                "timeline": use_case_data.get("timeline", ""),
                "approach": use_case_data.get("approach", "")
            })
        
        debug_print(f"🎯 [BusinessReasoner] Applied use case optimization for: {use_case_info['name']}")
    
    def _check_missing_product_groups(self, state: ConversationState, analysis: Dict):
        """🚀 Check for missing essential product groups and alert"""
        if "business_recommendations" not in state:
            state["business_recommendations"] = []
        
        # Get missing product alerts from mapping
        missing_alerts = self.product_groups_data.get("missing_product_alerts", {})
        
        # Analyze current recommendations to see what's missing
        current_products = set()
        for rec in state.get("business_recommendations", []):
            if isinstance(rec, dict):
                # Extract products from different recommendation types
                if "products" in rec:
                    if isinstance(rec["products"], dict):
                        for product_list in rec["products"].values():
                            current_products.update(product_list)
                    elif isinstance(rec["products"], list):
                        current_products.update(rec["products"])
                elif "priority_products" in rec:
                    current_products.update(rec["priority_products"])
        
        # Check for missing fish food
        has_coral_supplements = any("coral" in prod.lower() or "energy" in prod.lower() or "amino" in prod.lower() 
                                  for prod in current_products)
        has_fish_food = any("fish" in prod.lower() or "marine mix" in prod.lower() 
                           for prod in current_products)
        
        if has_coral_supplements and not has_fish_food and "no_fish_food" in missing_alerts:
            alert = missing_alerts["no_fish_food"]
            state["business_recommendations"].append({
                "type": "missing_alert",
                "alert_type": "no_fish_food", 
                "message": alert["message"],
                "suggest_products": alert["suggest_products"]
            })
            debug_print("⚠️ [BusinessReasoner] Added missing fish food alert")
        
        # Check for missing water chemistry (for new tank scenarios)
        if "scenario_info" in state and "new_tank" in state["scenario_info"]["name"]:
            has_water_chemistry = any("component" in prod.lower() or "calcium" in prod.lower() 
                                    for prod in current_products)
            
            if not has_water_chemistry and "no_water_chemistry" in missing_alerts:
                alert = missing_alerts["no_water_chemistry"]
                state["business_recommendations"].append({
                    "type": "missing_alert",
                    "alert_type": "no_water_chemistry",
                    "message": alert["message"], 
                    "suggest_products": alert["suggest_products"]
                })
                debug_print("⚠️ [BusinessReasoner] Added missing water chemistry alert")
    
    def _apply_business_intelligence(self, state: ConversationState, analysis: Dict) -> ConversationState:
        """Apply business analysis results to state"""
        state["business_analysis"] = analysis
        
        # Product corrections
        if analysis.get("product_name_corrections") and analysis["product_name_corrections"] != "None":
            corrected = analysis["product_name_corrections"]
            if self._validate_product_exists(corrected):
                debug_print(f"✅ [BusinessReasoner] Product validated: {corrected}")
            else:
                debug_print(f"⚠️ [BusinessReasoner] Product not found: {corrected}")
        
        # Category handling
        if analysis.get("category_requested") and analysis.get("products_in_category"):
            state["requested_category"] = analysis["category_requested"]
            state["category_products"] = analysis["products_in_category"]
            debug_print(f"📦 [BusinessReasoner] Category '{analysis['category_requested']}' with {len(analysis['products_in_category'])} products")
        
        # Problem-solution mapping
        if analysis.get("problem_identified") and analysis.get("solutions_for_problem"):
            state["identified_problem"] = analysis["problem_identified"]
            solutions = analysis["solutions_for_problem"]
            
            # 🆕 Separate correction vs maintenance products
            if isinstance(solutions, dict) and "correction" in solutions:
                state["recommended_solutions"] = solutions.get("correction", [])
                state["maintenance_solutions"] = solutions.get("maintenance", [])
                state["solution_note"] = solutions.get("note", "")
            else:
                state["recommended_solutions"] = solutions
                
            debug_print(f"🔧 [BusinessReasoner] Problem: {analysis['problem_identified']} → {len(state.get('recommended_solutions', []))} solutions")
        
        # Intent correction
        if analysis.get("intent_correction") and analysis["intent_correction"] != "same":
            old_intent = state.get("intent")
            try:
                state["intent"] = Intent(analysis["intent_correction"])
                debug_print(f"✅ [BusinessReasoner] Intent corrected: {old_intent} → {state['intent']}")
            except:
                debug_print(f"⚠️ [BusinessReasoner] Invalid intent correction: {analysis['intent_correction']}")
        
        # Domain hint
        if analysis.get("domain_hint") and analysis["domain_hint"] != "unknown":
            state["domain_filter"] = analysis["domain_hint"]
            debug_print(f"🎯 [BusinessReasoner] Domain: {analysis['domain_hint']}")
        
        # Search enhancement
        if analysis.get("search_enhancement"):
            state["search_context"] = analysis["search_enhancement"]
            debug_print(f"🔍 [BusinessReasoner] Search enhancement: {analysis['search_enhancement'][:50]}...")
        
        # Purchase product
        if state.get("intent") == Intent.PURCHASE_INQUIRY and analysis.get("product_name_corrections"):
            state["purchase_product"] = analysis["product_name_corrections"]
            debug_print(f"🛒 [BusinessReasoner] Purchase product: {state['purchase_product']}")
        
        debug_print(f"💡 [BusinessReasoner] Interpretation: {analysis.get('business_interpretation', 'N/A')[:100]}...")
        
        return state
    
    def _validate_product_exists(self, product_name: str) -> bool:
        """Validate if product exists in catalog"""
        if not product_name:
            return False
        
        # Check exact match first
        if product_name in self.products_list:
            return True
        
        # Check case-insensitive
        product_lower = product_name.lower()
        return any(product_lower == p.lower() for p in self.products_list)


def business_reasoner(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    reasoner = BusinessReasoner()
    return reasoner.analyze(state)