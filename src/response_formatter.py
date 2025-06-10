"""
Response Formatting Module - VERSION 3.1 with MIXED DOMAIN SUPPORT
Complete metadata dump to LLM, knowledge-first approach, domain awareness
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from models import ConversationState, ProductInfo, Intent, Domain
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV
import re

class ResponseFormatter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _detect_dosage_query(self, query: str) -> bool:
        """Detect if query is about dosage/calculation"""
        dosage_keywords = [
            'dawkowanie', 'dawka', 'dawke', 'ile', 'oblicz', 'calculate', 'dosage', 'dose', 
            'how much', 'combien', 'quanto', 'dosierung', 'dosis', 'ile potrzebuję', 
            'jak dawkować', 'how to dose', 'ile dodać', 'ile stosować', 'jaka dawka'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in dosage_keywords)
    
    def _extract_volume_from_query(self, query: str) -> int:
        """Extract aquarium volume from query"""
        patterns = [
            r'(\d+)\s*[lL](?:iters?|itrów?)?',
            r'(\d+)\s*(?:liters?|litrów?)',
            r'akwarium\s+(\d+)\s*[lL]',
            r'zbiornik\s+(\d+)\s*[lL]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))
        return None
    
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
        
        # 🆕 CHECK FOR MIXED DOMAINS
        has_mixed = self._has_mixed_domains(state.get("search_results", []))
        domain_not_specified = not state.get("domain_filter")
        
        is_dosage_query = self._detect_dosage_query(state.get("user_query", ""))
        
        # Full metadata dump
        all_results_metadata = []
        
        if state.get("search_results"):
            if TEST_ENV:
                print(f"📊 [DEBUG ResponseFormatter] Processing {len(state.get('search_results', []))} results")
                if has_mixed and domain_not_specified:
                    print(f"🎯 [DEBUG ResponseFormatter] Mixed domains detected, will present both")
            
            # 🆕 GROUP BY DOMAIN IF MIXED
            if has_mixed and domain_not_specified:
                grouped_results = self._group_results_by_domain(state["search_results"])
                
                # Format grouped results
                for domain, results in grouped_results.items():
                    if results:
                        all_results_metadata.append(f"\n--- {domain.upper()} PRODUCTS ---\n")
                        for i, result in enumerate(results):
                            meta = result.get('metadata', {})
                            metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
                            all_results_metadata.append(f"""
Result {domain}_{i+1}:
COMPLETE METADATA:
{metadata_json}

""")
            else:
                # Normal formatting
                for i, result in enumerate(state["search_results"]):
                    meta = result.get('metadata', {})
                    metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
                    all_results_metadata.append(f"""
Result {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
        
        formatted_all_results = "".join(all_results_metadata) if all_results_metadata else "No search results found."

        return f"""
You are AF AI, a friendly and professional assistant for Aquaforest. Generate response in {lang} language.

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---

--- CURRENT CONTEXT ---
User's Query: "{state.get('original_query', '')}"
Response Language: "{lang}"
Search Results Confidence: {state.get('confidence', 0.0):.2f}
Evaluation Reasoning: "{state.get('evaluation_reasoning', 'N/A')}"
Is Dosage Query: {is_dosage_query}
🆕 Mixed Domains Detected: {has_mixed and domain_not_specified}

--- COMPLETE SEARCH RESULTS WITH FULL METADATA ---
{formatted_all_results}
---

TASK: Generate the best possible response based on the complete context and conversation history.

--- 🆕 ENHANCED RESPONSE RULES ---

1. **🆕 MIXED DOMAIN HANDLING**:
   - If Mixed Domains Detected = True, present products clearly separated by aquarium type
   - Use headers like "Dla akwarium morskiego:" and "Dla akwarium słodkowodnego:" (in appropriate language)
   - Explain that we offer solutions for both types of aquariums
   - Let user choose what fits their needs

2. **KNOWLEDGE-FIRST FOR BEGINNERS**:
   - If user asks about "starting", "beginning", "setup" → PRIORITIZE knowledge articles first!
   - Guides like "Kickstart Method", setup tutorials are GOLD for beginners
   - Present knowledge articles prominently, not just as "further reading"

3. **FULL METADATA UTILIZATION**:
   - You have access to COMPLETE metadata for each result
   - Use full_content_en, dosage information, URLs, everything available
   - Provide comprehensive answers based on complete data
   - Calculate dosages if user specifies aquarium volume

4. **Balanced Product + Knowledge Approach**:
   - Use BOTH products AND knowledge articles
   - For beginners: Start with knowledge, then recommend products
   - For specific products: Start with products, then add related guides

5. **Domain Awareness**: 
   - If discussing freshwater aquarium, recommend ONLY freshwater or universal products
   - If discussing marine/saltwater, recommend marine or universal products
   - If domain unclear and mixed results, PRESENT BOTH OPTIONS CLEARLY

6. **For High Confidence (>= 0.6)**:
   - Present comprehensive answer using complete metadata
   - Structure: Knowledge articles first (for beginners), then products
   - Include URLs and detailed information from metadata

7. **For Low Confidence (< 0.6) or Escalation**:
   - Do NOT recommend any products
   - Provide support channels: support@aquaforest.eu and +48 14 691 79 79

8. **Dosage Calculations**:
   - If user specifies aquarium volume and products have dosage info, calculate specific amounts
   - Use dosage_amount, dosage_volume, and dosage_frequency from metadata

--- GENERATE RESPONSE IN {lang.upper()} ---
"""

    def _create_special_intent_prompt(self, state: ConversationState) -> str:
        """Create prompts for special intents with product search support"""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "other")
        user_query = state.get("user_query", "")
        
        if TEST_ENV:
            print(f"🎯 [DEBUG ResponseFormatter] Creating prompt for special intent: {intent}")
        
        # 🆕 ENHANCED PURCHASE INQUIRY
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

🆕 ENHANCED RESPONSE:
- If product was identified: "{purchase_product}"
- Product URL (if found): "{product_url}"

Respond helpfully:
1. If product identified, mention it specifically and provide its URL
2. Explain that Aquaforest doesn't sell directly, only through authorized dealers
3. Direct them to dealer map:
   {"https://aquaforest.eu/pl/gdzie-kupic/" if lang == "pl" else "https://aquaforest.eu/en/where-to-buy/"}
4. Be helpful and specific about the product they're interested in

Generate response in {lang} language.
"""

        intent_instructions = {
            Intent.GREETING: f"""
You are AF AI, Aquaforest's friendly assistant. The user just greeted you.
User said: "{user_query}"

Respond warmly:
- Greet them back and introduce yourself as AF AI assistant
- Ask how you can help them today
- Suggest they can ask about specific products or aquarium problems
- Keep it friendly, concise (2-3 sentences)

Generate greeting in {lang} language.
""",

            Intent.BUSINESS: f"""
You are AF AI. The user is interested in business cooperation.
User said: "{user_query}"

Respond professionally:
- Thank them warmly for their interest in cooperation
- Provide the contact form link:
  {"https://aquaforest.eu/pl/kontakt/" if lang == "pl" else "https://aquaforest.eu/en/contact-us/"}
- Mention our business hotline: (+48) 14 691 79 79 (Monday-Friday, 8:00-16:00)
- Note that our specialists are ready to provide full support

Generate response in {lang} language.
""",

            Intent.COMPETITOR: f"""
You are AF AI, the Aquaforest brand ambassador. The user mentioned a competitor or is asking for a comparison.
Your tone should be confident, professional, and focused on Aquaforest's strengths.

User's query: "{user_query}"

Response approach:
- Acknowledge the question professionally
- Focus on Aquaforest's unique advantages
- Mention our quality, research, and customer support
- Avoid directly criticizing competitors
- Be confident but respectful

Generate response in {lang} language.
""",

            Intent.CENSORED: f"""
You are AF AI. The user is asking about proprietary information.
User said: "{user_query}"

Respond politely:
- Explain that this information is a company secret
- Be polite but firm
- You can suggest they contact support for general product information

Generate response in {lang} language.
"""
        }
        
        return intent_instructions.get(intent, "Respond helpfully to the user's query.")

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
            
            # Cache full metadata for follow-ups
            if state.get("search_results"):
                state["context_cache"] = [r['metadata'] for r in state["search_results"][:5]]
                if TEST_ENV:
                    print(f"💾 [DEBUG ResponseFormatter] Cached metadata for {len(state['context_cache'])} results")
                    
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ResponseFormatter] Formatting error: {e}")
            state["final_response"] = "I apologize, but I encountered an error. Please contact support@aquaforest.eu"
        return state

def _create_follow_up_prompt(state: ConversationState) -> str:
    """Creates a prompt to answer a follow-up question using cached context."""
    lang = state.get("detected_language", "en")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    if TEST_ENV:
        print(f"\n🔄 [DEBUG Follow-up] Creating prompt for follow-up in language: {lang}")
        print(f"📦 [DEBUG Follow-up] Cache contains {len(state.get('context_cache', []))} items with FULL metadata")
    
    # Format cached FULL METADATA for LLM
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
You are AF AI, an Aquaforest assistant. Answer a follow-up question based on conversation history and cached FULL metadata.

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

--- CACHED FULL METADATA (from the previous response) ---
{cached_context_formatted}
---

TASK:
1. Analyze the LATEST USER MESSAGE as a direct response to your previous answer
2. Use the CACHED FULL METADATA to provide specific information
3. If user asks about a specific product from cache, provide detailed info
4. If cached information is insufficient, suggest rephrasing or searching again

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
    """Handle follow-up questions using cached metadata."""
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
        state["final_response"] = "I'm sorry, I had trouble processing that. Could you please rephrase?"
        
    return state