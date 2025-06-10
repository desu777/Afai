"""
Response Formatting Module - VERSION 4.0 with Safe Calculations
Enhanced metadata handling, category support, and calculation safety
"""
from typing import List, Dict, Any, Optional
import json
import re
from openai import OpenAI
from models import ConversationState, ProductInfo, Intent, Domain
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV
from calculation_helper import calculation_helper

class ResponseFormatter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _detect_dosage_query(self, query: str) -> bool:
        """Detect if query is about dosage/calculation"""
        dosage_keywords = [
            'dawkowanie', 'dawka', 'dawke', 'ile', 'oblicz', 'calculate', 'dosage', 'dose', 
            'how much', 'combien', 'quanto', 'dosierung', 'dosis', 'ile potrzebuję', 
            'jak dawkować', 'how to dose', 'ile dodać', 'ile stosować', 'jaka dawka',
            'dla', 'for', 'litrów', 'liters', 'L'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in dosage_keywords)
    
    def _extract_dosage_info(self, metadata: Dict) -> Dict[str, Any]:
        """Extract dosage information from product metadata"""
        dosage_info = {
            "has_dosage": False,
            "base_amount": None,
            "base_volume": 100,  # Default to 100L
            "unit": "ml",
            "frequency": "daily",
            "timing": None,
            "special_instructions": []
        }
        
        # Check various dosage fields
        if metadata.get("dosage_amount"):
            dosage_info["has_dosage"] = True
            dosage_info["base_amount"] = self._parse_amount(metadata["dosage_amount"])
            
        if metadata.get("dosage_volume"):
            volume = self._parse_volume(metadata["dosage_volume"])
            if volume:
                dosage_info["base_volume"] = volume
                
        if metadata.get("dosage_unit"):
            dosage_info["unit"] = metadata["dosage_unit"]
            
        if metadata.get("dosage_frequency"):
            dosage_info["frequency"] = metadata["dosage_frequency"]
            
        if metadata.get("dosage_timing"):
            dosage_info["timing"] = metadata["dosage_timing"]
            
        # Parse from full content if needed
        if not dosage_info["has_dosage"] and metadata.get("full_content_en"):
            dosage_info = self._parse_dosage_from_content(metadata["full_content_en"], dosage_info)
            
        return dosage_info
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount from string like '10 ml' or '1 drop'"""
        try:
            # Extract number from string
            match = re.search(r'(\d+(?:\.\d+)?)', str(amount_str))
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.0
    
    def _parse_volume(self, volume_str: str) -> Optional[int]:
        """Parse volume from string like '100L' or '100 liters'"""
        try:
            match = re.search(r'(\d+)\s*[lL]', str(volume_str))
            if match:
                return int(match.group(1))
        except:
            pass
        return None
    
    def _parse_dosage_from_content(self, content: str, dosage_info: Dict) -> Dict:
        """Try to parse dosage from full content"""
        # Common dosage patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(ml|drops?|kropli?|krople?)\s*(?:per|na)\s*(\d+)\s*[lL]',
            r'dawkowanie:?\s*(\d+(?:\.\d+)?)\s*(ml|drops?)',
            r'dose:?\s*(\d+(?:\.\d+)?)\s*(ml|drops?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                dosage_info["has_dosage"] = True
                dosage_info["base_amount"] = float(match.group(1))
                dosage_info["unit"] = match.group(2).lower()
                if len(match.groups()) >= 3:
                    dosage_info["base_volume"] = int(match.group(3))
                break
                
        return dosage_info
    
    def _get_product_url(self, product: Dict, language: str) -> str:
        meta = product.get('metadata', {})
        if language == 'pl' and meta.get('url_pl'):
            return meta['url_pl']
        return meta.get('url_en', '')
    
    def _has_mixed_domains(self, results: List[Dict]) -> bool:
        """Check if results contain both freshwater and seawater products"""
        domains = set()
        for result in results:
            domain = result.get('metadata', {}).get('domain')
            if domain and domain != 'universal':
                domains.add(domain)
        return len(domains) > 1
    
    def _group_results_by_domain(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """Group results by domain"""
        grouped = {
            'seawater': [],
            'freshwater': [],
            'universal': []
        }
        
        for result in results:
            domain = result.get('metadata', {}).get('domain', 'universal')
            if domain in grouped:
                grouped[domain].append(result)
        
        return grouped

    def _create_universal_prompt(self, state: ConversationState) -> str:
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "product_query")
        
        if TEST_ENV:
            print(f"\n📝 [DEBUG ResponseFormatter] Formatting response for intent='{intent}', language='{lang}'")
        
        # Handle special intents first
        if intent in [Intent.GREETING, Intent.BUSINESS, 
                     Intent.PURCHASE_INQUIRY, Intent.COMPETITOR, Intent.CENSORED]:
            if TEST_ENV:
                print(f"🎭 [DEBUG ResponseFormatter] Handling special intent: {intent}")
            return self._create_special_intent_prompt(state)
        
        # Format conversation history
        chat_history_formatted = ""
        if state.get("chat_history"):
            chat_history_formatted = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in state.get("chat_history", [])[-6:]
            ])
        
        # Check for mixed domains
        has_mixed = self._has_mixed_domains(state.get("search_results", []))
        domain_not_specified = not state.get("domain_filter")
        
        # Check for dosage query
        is_dosage_query = self._detect_dosage_query(state.get("user_query", ""))
        aquarium_volume = None
        if is_dosage_query:
            aquarium_volume = calculation_helper.extract_volume_from_query(state.get("user_query", ""))
        
        # Category context
        category_context = ""
        if state.get("requested_category") and state.get("category_products"):
            category_context = f"""
--- CATEGORY REQUEST ---
User asked for products in category: {state.get("requested_category")}
Expected products to show: {', '.join(state.get("category_products", []))}
Make sure to present ALL products from this category that were found!
---
"""
        
        # Problem-solution context
        problem_context = ""
        if state.get("identified_problem") and state.get("recommended_solutions"):
            problem_context = f"""
--- PROBLEM IDENTIFIED ---
Problem: {state.get("identified_problem")}
Recommended solutions: {', '.join(state.get("recommended_solutions", []))}
Focus on these solutions in your response!
---
"""
        
        # Balling method context
        balling_context = ""
        if state.get("maintenance_solutions") and state.get("solution_note"):
            balling_context = f"""
--- BALLING METHOD NOTE ---
User asked about correcting a single parameter.
Maintenance products suggested: {', '.join(state.get("maintenance_solutions", []))}
IMPORTANT NOTE: {state.get("solution_note", "")}
You MUST mention that Balling/Component products contain multiple elements and are for daily maintenance, not single corrections!
---
"""
        
        # Full metadata dump
        all_results_metadata = []
        dosage_calculations = []
        
        if state.get("search_results"):
            if TEST_ENV:
                print(f"📊 [DEBUG ResponseFormatter] Processing {len(state.get('search_results', []))} results")
                if has_mixed and domain_not_specified:
                    print(f"🎯 [DEBUG ResponseFormatter] Mixed domains detected, will present both")
            
            # Process results and prepare dosage calculations
            for i, result in enumerate(state["search_results"]):
                meta = result.get('metadata', {})
                
                # Extract dosage info if this is a dosage query
                if is_dosage_query and aquarium_volume:
                    dosage_info = self._extract_dosage_info(meta)
                    if dosage_info["has_dosage"]:
                        calc_result = calculation_helper.calculate_dosage(
                            dosage_info["base_amount"],
                            dosage_info["base_volume"],
                            aquarium_volume,
                            dosage_info["unit"]
                        )
                        if calc_result["success"]:
                            dosage_calculations.append({
                                "product": meta.get("product_name", "Unknown"),
                                "calculation": calc_result
                            })
                
                metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
                all_results_metadata.append(f"""
Result {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
        
        formatted_all_results = "".join(all_results_metadata) if all_results_metadata else "No search results found."
        
        # Format dosage calculations
        dosage_context = ""
        if dosage_calculations:
            dosage_context = f"""
--- DOSAGE CALCULATIONS ---
Aquarium volume: {aquarium_volume}L
Calculated dosages:
"""
            for calc in dosage_calculations:
                dosage_context += f"\n- {calc['product']}: {calc['calculation']['calculation']}"
            dosage_context += "\n---\n"

        return f"""
You are AF AI, a friendly and professional assistant for Aquaforest. Generate response in {lang} language.

🚨 CRITICAL: Show ALL products from search results! Products with same names but different URLs are DIFFERENT products!

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---

--- CURRENT CONTEXT ---
User's Query: "{state.get('original_query', '')}"
Response Language: "{lang}"
Search Results Confidence: {state.get('confidence', 0.0):.2f}
Is Dosage Query: {is_dosage_query}
Aquarium Volume: {aquarium_volume if aquarium_volume else "Not specified"}
Mixed Domains Detected: {has_mixed and domain_not_specified}

{category_context}
{problem_context}
{balling_context}
{dosage_context}

--- COMPLETE SEARCH RESULTS WITH FULL METADATA ---
{formatted_all_results}
---

🚨 CRITICAL INSTRUCTION 🚨
Products with same names but different URLs/metadata are DIFFERENT products!
Example: If you see "Mg Plus" twice with different URLs, you MUST present BOTH as separate items.
DO NOT merge, skip, or combine products with same names!
Count each result as a separate product regardless of name similarity!

TASK: Generate the best possible response based on the complete context.

--- ENHANCED RESPONSE RULES ---

1. **CATEGORY REQUESTS** (HIGHEST PRIORITY):
   - If user asked for a category (e.g., "jakie sole macie"), LIST ALL products from that category
   - Present them clearly with brief descriptions
   - Don't just mention one or two - show the complete range!

2. **PROBLEM-SOLUTION FOCUS**:
   - If a problem was identified, focus on the recommended solutions
   - Explain why these solutions help with the specific problem

3. **BALLING METHOD CLARIFICATION**:
   - If showing Component/Balling products for single parameter correction
   - MUST explain they contain Ca, Mg, KH and trace elements
   - Suggest them for daily maintenance, not one-time corrections
   - Recommend specific single-element products first for corrections

4. **DOSAGE CALCULATIONS**:
   - If dosage calculations were provided, use them EXACTLY as calculated
   - NEVER recalculate or modify the provided calculations
   - Present calculations clearly: "For your {aquarium_volume}L aquarium: {{calculation}}"
   - Add safety notes if relevant

5. **MIXED DOMAIN HANDLING**:
   - If Mixed Domains = True, present products separated by aquarium type
   - Use headers like "Dla akwarium morskiego:" and "Dla akwarium słodkowodnego:"

6. **PRODUCT PRESENTATION**:
   - For each product, include:
     * Product name (bold)
     * Brief description from metadata
     * Key benefits or use case
     * Dosage (if relevant)
     * Available sizes (if mentioned)
     * Link to product page
   - 🚨 **CRITICAL: NEVER skip products with same names but different URLs!**
   - If "Mg Plus" appears twice, create TWO separate sections: "Mg Plus (version 1)" and "Mg Plus (version 2)"
   - Same product name = different valuable content if URLs differ


7. **KNOWLEDGE ARTICLES**:
   - Include relevant knowledge articles AFTER products
   - Present as "Additional resources" or "Learn more"

8. **For High Confidence (>= 0.5)**:
   - Be comprehensive and confident
   - Include product links
   - Provide specific recommendations

9. **For Low Confidence or Escalation**:
   - Still try to be helpful with general information
   - Clearly state uncertainty
   - Provide support contact: support@aquaforest.eu and +48 14 691 79 79

--- LANGUAGE-SPECIFIC FORMATTING ---
For Polish (pl):
- Use "Polecamy:" for recommendations
- "Dawkowanie:" for dosage
- "Więcej informacji:" for links

For English (en):
- Use "We recommend:" for recommendations  
- "Dosage:" for dosage
- "Learn more:" for links

--- GENERATE RESPONSE IN {lang.upper()} ---
"""

    def _create_special_intent_prompt(self, state: ConversationState) -> str:
        """Create prompts for special intents"""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "other")
        user_query = state.get("user_query", "")
        
        if TEST_ENV:
            print(f"🎯 [DEBUG ResponseFormatter] Creating prompt for special intent: {intent}")
        
        # Enhanced purchase inquiry
        if intent == Intent.PURCHASE_INQUIRY:
            purchase_product = state.get("purchase_product", "")
            product_url = ""
            
            # Try to find product in search results
            if state.get("search_results"):
                for result in state["search_results"]:
                    if result.get('metadata', {}).get('product_name', '').lower() == purchase_product.lower():
                        product_url = self._get_product_url(result, lang)
                        break
            
            return f"""
You are AF AI. The user is asking about purchasing/buying products.
User said: "{user_query}"

Product Context:
- Identified product: "{purchase_product}"
- Product URL: "{product_url}"

Respond helpfully:
1. If product was identified, acknowledge it specifically
2. If we have the product URL, provide it
3. Explain that Aquaforest sells only through authorized dealers
4. Direct to dealer map: {"https://aquaforest.eu/pl/gdzie-kupic/" if lang == "pl" else "https://aquaforest.eu/en/where-to-buy/"}
5. Be warm and helpful

Generate response in {lang} language.
"""

        # Business inquiry
        if intent == Intent.BUSINESS:
            return f"""
You are AF AI. The user is interested in business cooperation.
User said: "{user_query}"

Respond professionally but warmly:
- Thank them for interest in partnership
- Mention we're always looking for reliable partners
- Provide contact form: {"https://aquaforest.eu/pl/kontakt/" if lang == "pl" else "https://aquaforest.eu/en/contact-us/"}
- Business hotline: (+48) 14 691 79 79 (Monday-Friday, 8:00-16:00)
- Express enthusiasm about potential cooperation

Keep tone professional but friendly. Generate response in {lang} language.
"""

        # Other special intents remain similar...
        intent_instructions = {
            Intent.GREETING: f"""
You are AF AI, Aquaforest's friendly assistant. Greet warmly and offer help.
User said: "{user_query}"

Be friendly and welcoming. Ask how you can help with their aquarium.
Mention you can help with product recommendations, dosing calculations, or aquarium problems.

Generate greeting in {lang} language.
""",

            Intent.COMPETITOR: f"""
You are AF AI. The user mentioned a competitor.
User said: "{user_query}"

Be professional and confident without criticizing competitors.
Focus on Aquaforest's strengths:
- High quality and purity
- Complete product range
- Excellent customer support
- Proven results

Generate response in {lang} language.
""",

            Intent.CENSORED: f"""
You are AF AI. The user asked about proprietary information.
User said: "{user_query}"

Politely explain that detailed formulations are proprietary.
Offer to discuss product benefits and usage instead.
Be helpful while protecting company secrets.

Generate response in {lang} language.
"""
        }
        
        return intent_instructions.get(intent, f"Respond helpfully to: {user_query}")

    def format_response(self, state: ConversationState) -> ConversationState:
        try:
            if TEST_ENV:
                print(f"\n🔨 [DEBUG ResponseFormatter] Generating final response...")
                
            prompt = self._create_universal_prompt(state)
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            state["final_response"] = response.choices[0].message.content
            
            if TEST_ENV:
                print(f"✅ [DEBUG ResponseFormatter] Response generated ({len(state['final_response'])} characters)")
            
            # Cache metadata for follow-ups
            if state.get("search_results"):
                # Cache more results if category request
                cache_size = 10 if state.get("requested_category") else 5
                state["context_cache"] = [r['metadata'] for r in state["search_results"][:cache_size]]
                if TEST_ENV:
                    print(f"💾 [DEBUG ResponseFormatter] Cached metadata for {len(state['context_cache'])} results")
                    
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ResponseFormatter] Formatting error: {e}")
            state["final_response"] = self._get_error_message(state.get("detected_language", "en"))
        
        return state
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in appropriate language"""
        if language == "pl":
            return "Przepraszam, wystąpił błąd. Proszę skontaktować się z support@aquaforest.eu lub zadzwonić pod +48 14 691 79 79."
        else:
            return "I apologize, but I encountered an error. Please contact support@aquaforest.eu or call +48 14 691 79 79."


# Follow-up handling functions
def _create_follow_up_prompt(state: ConversationState) -> str:
    """Creates a prompt to answer a follow-up question using cached context"""
    lang = state.get("detected_language", "en")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    if TEST_ENV:
        print(f"\n🔄 [DEBUG Follow-up] Creating prompt for follow-up in language: {lang}")
        print(f"📦 [DEBUG Follow-up] Cache contains {len(state.get('context_cache', []))} items")
    
    # Check if follow-up is about dosage
    is_dosage_followup = any(word in state["user_query"].lower() 
                           for word in ["dawkowanie", "ile", "how much", "dosage", "oblicz"])
    
    # Format cached metadata
    cached_full_metadata = []
    if state.get("context_cache"):
        for i, meta in enumerate(state.get("context_cache", [])):
            metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
            cached_full_metadata.append(f"""
Cached Item {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
    
    cached_context_formatted = "".join(cached_full_metadata)

    return f"""
You are AF AI, an Aquaforest assistant. Answer a follow-up question based on conversation history and cached metadata.

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

--- CACHED FULL METADATA ---
{cached_context_formatted}
---

{"The user might be asking about dosage. Use dosage information from cached metadata if available." if is_dosage_followup else ""}

TASK:
1. Analyze the latest message as a follow-up to previous conversation
2. Use cached metadata to provide specific information
3. If asking about specific product from cache, give detailed info
4. For dosage questions, calculate if aquarium volume is provided
5. If information insufficient, suggest what additional details are needed

Generate response in {lang} language.
"""

def format_final_response(state: ConversationState) -> ConversationState:
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def escalate_to_human(state: ConversationState) -> ConversationState:
    if TEST_ENV:
        print(f"\n🚨 [DEBUG Escalate] Escalating to support (confidence < threshold)")
    state["escalate"] = True
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def handle_follow_up(state: ConversationState) -> ConversationState:
    """Handle follow-up questions using cached metadata"""
    if TEST_ENV:
        print(f"\n🔄 [DEBUG Follow-up Handler] Handling follow-up question with cache")
        
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = _create_follow_up_prompt(state)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            messages=[{"role": "system", "content": prompt}]
        )
        state["final_response"] = response.choices[0].message.content
        
        if TEST_ENV:
            print(f"✅ [DEBUG Follow-up Handler] Response generated using cache")
            
    except Exception as e:
        if TEST_ENV:
            print(f"❌ [DEBUG Follow-up Handler] Follow-up handling error: {e}")
        
        formatter = ResponseFormatter()
        state["final_response"] = formatter._get_error_message(state.get("detected_language", "en"))
        
    return state