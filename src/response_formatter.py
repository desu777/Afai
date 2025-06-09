"""
Response Formatting Module - Wersja 2.4 with Smart Dosage Calculation
Formats final response with proper language and structure
Enhanced with special intent handlers, debugging, and smart dosage calculations
"""
from typing import List, Dict, Any
from openai import OpenAI
from models import ConversationState, ProductInfo, Intent
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
        """Extract aquarium volume from query (e.g., '500L' -> 500)"""
        # Look for patterns like '500L', '500 L', '500 liters', '500 litrów'
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
    
    def _calculate_dosage(self, volume: int, dosage_amount: str, dosage_volume: str) -> dict:
        """Calculate dosage for given volume"""
        try:
            # Parse dosage amount (e.g., "1_drop", "10_ml", "1_scoop")
            if 'drop' in dosage_amount:
                amount_num = int(dosage_amount.split('_')[0])
                amount_unit = 'krople' if amount_num > 1 else 'kropla'
            elif 'ml' in dosage_amount:
                amount_num = int(dosage_amount.split('_')[0])
                amount_unit = 'ml'
            elif 'scoop' in dosage_amount:
                amount_num = int(dosage_amount.split('_')[0])
                amount_unit = 'miarki' if amount_num > 1 else 'miarka'
            else:
                amount_num = 1
                amount_unit = dosage_amount.replace('_', ' ')
            
            # Parse base volume (e.g., "100L")
            base_volume = int(dosage_volume.replace('L', ''))
            
            # Calculate dosage for target volume
            ratio = volume / base_volume
            calculated_amount = amount_num * ratio
            
            # Format result nicely
            if 'krople' in amount_unit or 'kropla' in amount_unit:
                if calculated_amount == int(calculated_amount):
                    calculated_amount = int(calculated_amount)
                unit = 'krople' if calculated_amount != 1 else 'kropla'
            elif 'ml' in amount_unit:
                unit = 'ml'
            elif 'miark' in amount_unit:
                if calculated_amount == int(calculated_amount):
                    calculated_amount = int(calculated_amount)
                unit = 'miarki' if calculated_amount != 1 else 'miarka'
            else:
                unit = amount_unit
            
            return {
                'calculated_amount': calculated_amount,
                'unit': unit,
                'base_dosage': f"{amount_num} {amount_unit} na {dosage_volume}",
                'target_volume': f"{volume}L"
            }
            
        except (ValueError, AttributeError):
            return None
    
    def _format_dosage_frequency(self, frequency: str) -> str:
        """Format dosage frequency in Polish"""
        frequency_map = {
            'daily': 'codziennie',
            'every_other_day': 'co drugi dzień',
            'weekly': 'co tydzień',
            'as_needed': 'w razie potrzeby',
            'after_lights_out': 'po wyłączeniu świateł',
            'during_feeding': 'podczas karmienia'
        }
        return frequency_map.get(frequency, frequency.replace('_', ' '))
    
    def _create_dosage_response(self, state: ConversationState, products_with_dosage: List[Dict]) -> str:
        """Create specialized dosage calculation response"""
        lang = state.get("detected_language", "pl")
        query = state.get("user_query", "")
        volume = self._extract_volume_from_query(query)
        
        if not volume:
            volume = 100  # Default to 100L if not specified
        
        dosage_info = []
        for product in products_with_dosage[:5]:  # Top 5 products with dosage
            meta = product.get('metadata', {})
            product_name = meta.get('product_name', 'N/A')
            dosage_amount = meta.get('dosage_amount', '')
            dosage_volume = meta.get('dosage_volume', '')
            dosage_frequency = meta.get('dosage_frequency', '')
            dosage_timing = meta.get('dosage_timing', '')
            url = self._get_product_url(product, lang)
            
            if dosage_amount and dosage_volume:
                calculation = self._calculate_dosage(volume, dosage_amount, dosage_volume)
                if calculation:
                    frequency_text = self._format_dosage_frequency(dosage_frequency)
                    timing_text = self._format_dosage_frequency(dosage_timing) if dosage_timing else ""
                    
                    dosage_text = f"**{product_name}**\\n"
                    dosage_text += f"Dla akwarium {volume}L: **{calculation['calculated_amount']} {calculation['unit']}**"
                    if frequency_text:
                        dosage_text += f" {frequency_text}"
                    if timing_text and timing_text != frequency_text:
                        dosage_text += f" ({timing_text})"
                    dosage_text += f"\\nPodstawowe dawkowanie: {calculation['base_dosage']}"
                    if url:
                        dosage_text += f"\\n[Więcej informacji]({url})"
                    
                    dosage_info.append(dosage_text)
        
        return "\\n\\n".join(dosage_info) if dosage_info else ""
        
    def _get_product_url(self, product: Dict, language: str) -> str:
        meta = product.get('metadata', {})
        if language == 'pl' and meta.get('url_pl'):
            return meta['url_pl']
        return meta.get('url_en', '')

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
        
        # Format conversation history for context
        chat_history_formatted = ""
        if state.get("chat_history"):
            chat_history_formatted = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in state.get("chat_history", [])[-6:]  # Last 3 exchanges
            ])
        
        # 🆕 SMART DOSAGE DETECTION AND CALCULATION
        is_dosage_query = self._detect_dosage_query(state.get("user_query", ""))
        dosage_response = ""
        products_with_dosage = []
        
        if is_dosage_query and state.get("search_results"):
            # Filter products that have dosage information
            for product in state["search_results"]:
                meta = product.get('metadata', {})
                if meta.get('dosage_amount') and meta.get('dosage_volume'):
                    products_with_dosage.append(product)
            
            if products_with_dosage:
                dosage_response = self._create_dosage_response(state, products_with_dosage)
                if TEST_ENV:
                    print(f"💊 [DEBUG ResponseFormatter] Generated dosage calculations for {len(products_with_dosage)} products")
        
        # Original product query handling
        results_info = []
        if state.get("search_results"):
            if TEST_ENV:
                print(f"📊 [DEBUG ResponseFormatter] Formatting {len(state.get('search_results', []))} search results")
            
            # Show all 15 results to give LLM more context
            for i, p in enumerate(state["search_results"][:15]):
                meta = p.get('metadata', {})
                url = self._get_product_url(p, lang)
                results_info.append(
                    f"Result {i+1}:\n"
                    f"  - Name: {meta.get('product_name', 'N/A')}\n"
                    f"  - Type: {meta.get('content_type', 'N/A')}\n"
                    f"  - Domain: {meta.get('domain', 'N/A')}\n"
                    f"  - Description: {meta.get('title_en', '')}\n"
                    f"  - Dosage: {meta.get('dosage_amount', 'N/A')} per {meta.get('dosage_volume', 'N/A')} {meta.get('dosage_frequency', '').replace('_', ' ')}\n"
                    f"  - URL: {url}\n"
                    f"  - Score: {p.get('score', 0):.3f}\n"
                )
        formatted_search_results = "\n".join(results_info) if results_info else "No search results found."

        if TEST_ENV:
            print(f"💭 [DEBUG ResponseFormatter] Confidence: {state.get('confidence', 0.0):.2f}")
            if state.get('evaluation_reasoning'):
                print(f"🧐 [DEBUG ResponseFormatter] Reasoning: {state.get('evaluation_reasoning', 'N/A')[:100]}...")

        # 🆕 SMART DOSAGE PROMPT ENHANCEMENT
        dosage_enhancement = ""
        if dosage_response:
            dosage_enhancement = f"""
--- 🆕 SMART DOSAGE CALCULATIONS AVAILABLE ---
The user is asking about dosage/calculation. Here are the calculated dosages ready to use:

{dosage_response}

IMPORTANT: Use these calculated dosages in your response! Don't make the user do the math.
---
"""

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
{dosage_enhancement}
--- ALL 15 SEARCH RESULTS ---
{formatted_search_results}
---

TASK: Generate the best possible response based on the context and conversation history.

--- CRITICAL THINKING RULES ---

1. **ALWAYS analyze the conversation history** to understand what the user is referring to. For example:
   - "such aquarium" = check what type was discussed before
   - "the second product" = refer to previous recommendations
   - Any reference to prior context MUST be properly understood

2. **Domain Awareness**: 
   - If discussing freshwater aquarium, recommend ONLY freshwater or universal products
   - If discussing marine/saltwater, recommend marine or universal products
   - NEVER mix domains unless explicitly comparing

3. **Smart Filtering of 15 Results**:
   - You have 15 results - use them wisely!
   - Filter out irrelevant domains first
   - Consider all relevant products, not just top 5
   - Group similar products logically

--- RESPONSE RULES (VERY IMPORTANT) ---

Your primary goal is to act as an expert Aquaforest consultant. You must synthesize a helpful, structured, and comprehensive answer from the provided search results.

1. **🆕 SMART DOSAGE PRIORITY (HIGHEST PRIORITY)**:
   - If "SMART DOSAGE CALCULATIONS AVAILABLE" section is provided, USE IT!
   - Present the calculated dosages prominently in your response
   - Include the exact calculated amounts (e.g., "Dla akwarium 500L: **5 kropli**")
   - Don't make the user calculate - give them ready-to-use dosages
   - Add any relevant timing and frequency information

2. **Content-Type Priority**:
   - Your recommendations MUST be based on items with content_type: 'product'
   - If you find relevant 'knowledge' content, mention it at the end as "For further reading:"

3. **For High Confidence (>= 0.6)**:
   - List ALL relevant products found in search results
   - Structure answers by grouping similar products
   - For each product: name in **bold**, brief explanation, and URL
   - For comparisons: synthesize based on product descriptions

4. **For Low Confidence (< 0.6) or Escalation**:
   - Do NOT recommend any products
   - Politely inform user you couldn't find a certain answer
   - Provide support channels: support@aquaforest.eu and +48 14 691 79 79

--- GENERATE RESPONSE IN {lang.upper()} ---
"""

    def _create_special_intent_prompt(self, state: ConversationState) -> str:
        """Create prompts for special intents"""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "other")
        user_query = state.get("user_query", "")
        
        if TEST_ENV:
            print(f"🎯 [DEBUG ResponseFormatter] Creating prompt for special intent: {intent}")
            if state.get('context_cache'):
                print(f"📦 [DEBUG ResponseFormatter] Context cache contains {len(state.get('context_cache', []))} products")
                for i, item in enumerate(state.get('context_cache', [])[:3]):
                    print(f"   - {item.get('product_name', 'Unknown')}")
        
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

            Intent.PURCHASE_INQUIRY: f"""
You are AF AI. The user is asking about purchasing/buying products.
User said: "{user_query}"

IMPORTANT: Analyze the conversation history to understand what product they want to buy!
{f"Recent context shows discussion about: {state.get('context_cache', [{}])[0].get('product_name', 'products')}" if state.get('context_cache') else ""}

Respond helpfully:
- First, acknowledge what specific product they want to purchase (based on conversation context)
- Explain that Aquaforest doesn't sell directly, only through authorized dealers
- Direct them to our dealer map:
  {"https://aquaforest.eu/pl/gdzie-kupic/" if lang == "pl" else "https://aquaforest.eu/en/where-to-buy/"}
- Be helpful and specific about the product they're interested in

Generate response in {lang} language.
""",

            Intent.COMPETITOR: f"""
You are AF AI, the Aquaforest brand ambassador. The user mentioned a competitor or is asking for a comparison.
Your tone should be confident, a bit witty, and always pro-Aquaforest, without being aggressive. You subtly dismiss competitors and highlight Aquaforest's quality.

User's query: "{user_query}"

Here are some examples of the attitude you should have:
- If the user asks about a competitor (e.g., "Red Sea"): "Red Sea? Never heard of them ;)"
- If the user asks for a comparison (e.g., "Aquaforest vs. Competitor"): "If you're here, you already know the answer."
- If the user asks for a recommendation between brands: "If quality matters, there's only one answer: Aquaforest."
- If the user asks about a competitor's product: "I can't help with [Competitor Name], but I'm sure our products will exceed your expectations."

Now, based on this personality, generate a short, witty, and confident response in {lang} language for the user's query.
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
        
        base_prompt = f"""
You are AF AI, a friendly and professional assistant for Aquaforest.

{intent_instructions.get(intent, "Respond helpfully to the user's query.")}
"""
        
        return base_prompt

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
            
            if state.get("search_results"):
                state["context_cache"] = [r['metadata'] for r in state["search_results"][:5]]
                if TEST_ENV:
                    print(f"💾 [DEBUG ResponseFormatter] Saved {len(state['context_cache'])} products to cache")
                    
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ResponseFormatter] Universal formatting error: {e}")
            state["final_response"] = "I apologize, but I encountered an error while formulating my response. Please contact our support team at support@aquaforest.eu for assistance."
        return state

def _create_follow_up_prompt(state: ConversationState) -> str:
    """Creates a prompt to answer a follow-up question using cached context."""
    lang = state.get("detected_language", "en")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    if TEST_ENV:
        print(f"\n🔄 [DEBUG Follow-up] Creating prompt for follow-up in language: {lang}")
        print(f"📦 [DEBUG Follow-up] Cache contains {len(state.get('context_cache', []))} items")
    
    # Format the cache to be more readable for the LLM
    cached_context_info = []
    if state.get("context_cache"):
        for i, meta in enumerate(state.get("context_cache", [])):
            cached_context_info.append(
                f"Item {i+1}:\n"
                f"  - Name: {meta.get('product_name', 'N/A')}\n"
                f"  - Domain: {meta.get('domain', 'N/A')}\n"
                f"  - Description: {meta.get('title_en', '')}\n"
            )
    cached_context_formatted = "\n".join(cached_context_info)

    return f"""
You are AF AI, an Aquaforest assistant. Answer a follow-up question based on conversation history and cached information.

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

--- CACHED INFORMATION (from the previous response) ---
{cached_context_formatted}
---

TASK:
1. Analyze the LATEST USER MESSAGE as a direct response to your previous question
2. Filter the CACHED INFORMATION based on user's new input
3. Generate a helpful response, recommending the filtered products
4. If cached information is insufficient, politely suggest rephrasing

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
    """Node function for LangGraph - handles follow-up questions using cached context."""
    if TEST_ENV:
        print(f"\n🔄 [DEBUG Follow-up Handler] Handling follow-up question")
        
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = _create_follow_up_prompt(state)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        state["final_response"] = response.choices[0].message.content
        
        if TEST_ENV:
            print(f"✅ [DEBUG Follow-up Handler] Response generated")
            
    except Exception as e:
        if TEST_ENV:
            print(f"❌ [DEBUG Follow-up Handler] Follow-up handling error: {e}")
        state["final_response"] = "I'm sorry, I had trouble processing that. Could you please rephrase?"
        
    return state