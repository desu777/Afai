"""
Business Logic Reasoner - VERSION 2.0 with Product Categories
Enhanced business intelligence with category mapping and context understanding
"""
import json
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from models import ConversationState, Intent
from config import OPENAI_API_KEY, OPENAI_MODEL, TEST_ENV, debug_print, PRODUCTS_FILE_PATH

class BusinessReasoner:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.products_list = self._load_products_list()
        self.products_knowledge = self._load_products_knowledge()
        
        # 🆕 ENHANCED PRODUCT CATEGORY MAPPING
        self.product_categories = {
            "sole": ["Sea Salt", "Reef Salt", "Reef Salt Plus", "Hybrid Pro Salt"],
            "bakterie": ["Pro Bio S", "Pro Bio F", "Life Source", "Life Essence", "Bio S"],
            "suplementy_wapń": ["Ca Plus", "Calcium", "Ca plus"],
            "suplementy_magnez": ["Mg Plus", "Magnesium"],
            "suplementy_kh": ["KH Plus", "KH Buffer", "KH Pro"],
            "aminokwasy": ["AF Amino Mix", "AF Power Elixir", "AF Vitality"],
            "pokarmy": ["AF Marine Mix S", "AF Marine Mix M", "AF Marine Flakes", "AF Algae Feed", "AF Vege Clip"],
            "testy": ["Calcium Test Kit", "Magnesium Test Kit", "Alkanity Test Kit", "Nitrate Test Kit", "Phosphate Test Kit"],
            "media": ["Phosphate Minus", "Carbon", "AF Carbon", "Zeo Mix"],
            "metoda_balling": ["Component 1+2+3+", "Components Pro", "Components Strong"],
            "podłoża": ["AF Lava Soil", "AF Lava Soil Black", "AF Natural Substrate"],
            "probiotyki": ["Pro Bio S", "Pro Bio F", "-NP Pro", "AF NitraPhos Minus"],
            "oczyszczanie": ["Aiptasia Shot", "AF Protect Dip"],
            "wzrost_korali": ["AF Growth Boost", "AF Build", "AF Energy"],
            "kolorystyka": ["AF Amino Mix", "AF Power Elixir", "AF Vitality", "Kalium", "Iron"],
            "kontrola_ph": ["KH Buffer", "KH Plus", "AF Minus pH", "AF Air Scrubber"],
            "mikroelementy": ["Iodum", "Strontium", "Kalium", "Fluorum", "Component A", "Component B", "Component C"],
            "woda_morska": ["AF Perfect Water", "Sea Salt", "Reef Salt", "Reef Salt Plus", "Hybrid Pro Salt"]
        }
        
        # 🆕 ENHANCED PROBLEM-SOLUTION MAPPING  
        self.problem_solutions = {
            "ph_spada": {
                "marine": ["KH Buffer", "KH Plus", "AF Air Scrubber", "KalkMedia"],
                "freshwater": ["KH Plus", "AF Remineralizer"],
                "explanation": "pH drops require alkalinity buffers"
            },
            "ph_rośnie": {
                "marine": ["CO2 system", "reduce aeration"],
                "freshwater": ["AF Minus pH", "CO2 injection"],
                "explanation": "pH rises need acidification"
            },
            "glony": ["Phosphate Minus", "-NP Pro", "Pro Bio S", "AF NitraPhos Minus"],
            "korale_brązowieją": ["AF Amino Mix", "AF Power Elixir", "AF Vitality", "Kalium", "Iron"],
            "aiptasia": ["Aiptasia Shot"],
            "cyjanobakterie": ["Pro Bio S", "-NP Pro", "AF NitraPhos Minus"],
            "niski_wapń": {
                "correction": ["Ca Plus", "Calcium"],
                "maintenance": ["Component 1+2+3+", "Components Pro", "Components Strong"],
                "note": "Balling products contain multiple elements for stability"
            },
            "niski_magnez": {
                "correction": ["Mg Plus", "Magnesium"],
                "maintenance": ["Component 1+2+3+", "Components Pro", "Components Strong"],
                "note": "Balling products contain multiple elements for stability"
            },
            "niskie_kh": {
                "correction": ["KH Plus", "KH Buffer"],
                "maintenance": ["Component 1+2+3+", "Components Pro", "Components Strong"],
                "note": "Balling products contain multiple elements for stability"
            },
            "wysokie_no3": ["AF NitraPhos Minus", "Pro Bio S", "-NP Pro", "Phosphate Minus"],
            "wysokie_po4": ["Phosphate Minus", "AF Anti Phosphate", "AF NitraPhos Minus"]
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
        
        # 🆕 COMMON TYPOS AND CORRECTIONS
        self.common_corrections = {
            "nitraphos": "AF NitraPhos Minus",
            "bio s": "Pro Bio S",
            "np pro": "-NP Pro",
            "amino mix": "AF Amino Mix",
            "ca+": "Ca Plus",
            "ca +": "Ca Plus",
            "mg+": "Mg Plus",
            "kh+": "KH Plus",
            "component abc": "Component A, Component B, Component C",
            "aiptasja": "Aiptasia Shot",
            "aiptazja": "Aiptasia Shot",
            "aptazja": "Aiptasia Shot"
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
    
    def analyze(self, state: ConversationState) -> ConversationState:
        """Main analysis method"""
        debug_print(f"🧠 [BusinessReasoner] Analyzing query: '{state['user_query']}'", "🧠")
        
        # Check for competitors
        if self._check_competitors(state["user_query"]):
            state["intent"] = Intent.COMPETITOR
            debug_print(f"🏢 [BusinessReasoner] Competitor detected in query")
        
        # Create business context
        business_context = self._create_business_context(state["user_query"])
        
        # Analyze with GPT
        business_analysis = self._analyze_with_gpt(state, business_context)
        
        # Apply analysis results
        if business_analysis:
            state = self._apply_business_intelligence(state, business_analysis)
        
        return state
    
    def _check_competitors(self, query: str) -> bool:
        """Check if query mentions competitors"""
        query_lower = query.lower()
        return any(comp.lower() in query_lower for comp in self.competitors)
    
    def _find_category_for_query(self, query: str) -> Optional[str]:
        """Find which category the query is asking about"""
        query_lower = query.lower()
        
        # Direct category keywords
        category_keywords = {
            "sole": ["sole", "sól", "salt", "salts"],
            "bakterie": ["bakterie", "bacteria", "bacterial"],
            "testy": ["test", "testy", "testing"],
            "media": ["media", "filter media", "filtracja"],
            "aminokwasy": ["amino", "aminokwasy"],
            "pokarmy": ["pokarm", "food", "feed", "karmienie"],
            "podłoża": ["podłoże", "substrate", "soil", "lava"],
            "mikroelementy": ["mikroelement", "trace", "pierwiastki śladowe"]
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
DETECTED INTENT: {state['intent']}
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

IMPORTANT: When user asks about raising/correcting a SINGLE parameter:
- Prioritize "correction" products (Ca Plus, Mg Plus, KH Plus)
- If suggesting "maintenance" products (Component/Balling), MUST note they contain multiple elements

BUSINESS LOGIC ANALYSIS:
Analyze this query with aquarium business intelligence:

1. CATEGORY DETECTION: Is user asking about a product category?
   - "jakie sole macie" → category: "sole", list all: ["Sea Salt", "Reef Salt", "Reef Salt Plus", "Hybrid Pro Salt"]
   - "co polecacie na bakterie" → category: "bakterie"

2. PRODUCT NAME CORRECTIONS: Fix typos and common names
   - Check against: {json.dumps(self.common_corrections)}

3. PROBLEM ANALYSIS: What problem is user trying to solve?
   - "pH spada" → solutions for dropping pH (KH buffers)
   - "pH rośnie" → solutions for rising pH (pH minus)
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
        
        freshwater_keywords = ["słodkowod", "freshwater", "gupik", "neon", "krewetk"]
        marine_keywords = ["morsk", "marine", "reef", "koral", "sps", "lps", "salt water"]
        
        fresh_score = sum(1 for k in freshwater_keywords if k in text)
        marine_score = sum(1 for k in marine_keywords if k in text)
        
        if fresh_score > marine_score:
            return "freshwater"
        elif marine_score > fresh_score:
            return "seawater"
        return "unknown"
    
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
            old_intent = state["intent"]
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
        if state["intent"] == Intent.PURCHASE_INQUIRY and analysis.get("product_name_corrections"):
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