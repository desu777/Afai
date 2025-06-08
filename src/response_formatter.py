"""
Response Formatting Module - Wersja 2.2
Formats final response with proper language and structure
Enhanced with special intent handlers
"""
from typing import List, Dict, Any
from openai import OpenAI
from models import ConversationState, ProductInfo, Intent
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV

class ResponseFormatter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _get_product_url(self, product: Dict, language: str) -> str:
        meta = product.get('metadata', {})
        if language == 'pl' and meta.get('url_pl'):
            return meta['url_pl']
        return meta.get('url_en', '')

    def _create_universal_prompt(self, state: ConversationState) -> str:
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "product_query")
        
        # Handle special intents first
        if intent in [Intent.GREETING, Intent.BUSINESS, Intent.CALCULATOR, 
                     Intent.PURCHASE_INQUIRY, Intent.COMPETITOR, Intent.CENSORED]:
            return self._create_special_intent_prompt(state)
        
        # Format conversation history for context
        chat_history_formatted = ""
        if state.get("chat_history"):
            chat_history_formatted = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in state.get("chat_history", [])[-6:]  # Last 3 exchanges
            ])
        
        # Original product query handling
        results_info = []
        if state.get("search_results"):
            # Show all 15 results to give LLM more context
            for i, p in enumerate(state["search_results"][:15]):
                meta = p.get('metadata', {})
                url = self._get_product_url(p, lang)
                results_info.append(
                    f"Result {i+1}:\n"
                    f"  - Name: {meta.get('product_name', 'N/A')}\n"
                    f"  - Type: {meta.get('content_type', 'N/A')}\n"
                    f"  - Domain: {meta.get('domain', 'N/A')}\n"
                    f"  - Description: {meta.get(f'title_{lang}', meta.get('title_en', ''))}\n"
                    f"  - Dosage: {meta.get('dosage_amount', 'N/A')} per {meta.get('dosage_volume', 'N/A')} {meta.get('dosage_frequency', '').replace('_', ' ')}\n"
                    f"  - URL: {url}\n"
                    f"  - Score: {p.get('score', 0):.3f}\n"
                )
        formatted_search_results = "\n".join(results_info) if results_info else "No search results found."

        return f"""
You are AF AI, a friendly and professional assistant for Aquaforest. Your responses must be helpful, accurate, and always in the detected language: "{lang}".

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---

--- CURRENT CONTEXT ---
User's Query: "{state.get('original_query', '')}"
Detected Language: "{lang}"
Search Results Confidence (from your own evaluation): {state.get('confidence', 0.0):.2f}
Your Reasoning: "{state.get('evaluation_reasoning', 'N/A')}"

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

1.  **Content-Type Priority (Non-Negotiable Rule):**
    -   Your recommendations **MUST** be based on items with `content_type: 'product'`.
    -   If you find a relevant result with `content_type: 'knowledge'`, you may mention it at the very end of your response as "Warto również przeczytać:" or "For further reading:", but **NEVER** list it as if it's a purchasable product.

2.  **Synthesizing Answers for High Confidence (>= 0.6):**
    -   **For "list" or "what do you have" queries (e.g., "jakie macie sole?"):**
        -   List **ALL** relevant products found in the search results.
        -   **Structure your answer by grouping similar products.** For example: "Oferujemy kilka rodzajów soli, które można podzielić na następujące kategorie:".
        -   For each product, state its name in **bold**, briefly explain its primary use, and provide the URL.
    -   **For "comparison" queries (e.g., "czym się różnią?"):**
        -   You **MUST** synthesize a comparison based on the `Description` of each relevant product found in the results.
        -   Explain the key differences. Example: "**Sea Salt** to nasza podstawowa sól, idealna do..., podczas gdy **Reef Salt** zawiera dodatkowo..., co sprawia, że jest lepsza dla...".
    -   **Nuanced Framing (Add-ons & Alternatives):**
        -   If a product is related but not a direct answer (e.g., user asks for dry salt mix, and you find ready-to-use water like **AF Perfect Water**), you MUST frame it correctly.
        -   Present it at the end of the relevant list as a "Wygodna alternatywa:" or a "Ciekawy produkt dodatkowy:".

3.  **Handling Low Confidence (< 0.6) or Escalation:**
    -   Do NOT recommend any products.
    -   Politely inform the user that you couldn't find a certain answer.
    -   Provide the official support channels: Email `support@aquaforest.eu` and Phone `+48 14 691 79 79`.

4.  **Handling Special Intents (Highest Priority):**
    -   Follow the specific instructions for `greeting`, `business`, `purchase_inquiry`, `calculator`, etc., as defined previously.

--- FINAL RESPONSE (in {lang} only) ---
"""

    def _create_special_intent_prompt(self, state: ConversationState) -> str:
        """Create prompts for special intents"""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "other")
        user_query = state.get("user_query", "")
        
        intent_instructions = {
            Intent.GREETING: f"""
You are AF AI, Aquaforest's friendly assistant. The user just greeted you.
User said: "{user_query}" in language: {lang}

Respond warmly in {lang}:
- Greet them back and introduce yourself as AF AI assistant
- Ask how you can help them today
- Suggest they can ask about specific products or aquarium problems they're facing
- Keep it friendly, concise (2-3 sentences)
""",

            Intent.BUSINESS: f"""
You are AF AI. The user is interested in business cooperation.
User said: "{user_query}" in language: {lang}

Respond professionally in {lang}:
- Thank them warmly for their interest in cooperation
- Provide the contact form link:
  {"https://aquaforest.eu/pl/kontakt/" if lang == "pl" else "https://aquaforest.eu/en/contact-us/"}
- Mention our business hotline: (+48) 14 691 79 79 (Monday-Friday, 8:00-16:00)
- Note that our specialists are ready to provide full support
- Be encouraging and professional
""",

            Intent.CALCULATOR: f"""
You are AF AI. The user is asking about dosage calculations.
User said: "{user_query}" in language: {lang}

Respond in {lang}:
- Acknowledge their interest in dosage calculations
- Inform them that we're building something special/deep for this feature
- Express that it's coming soon
- Be positive and build anticipation
""",

            Intent.PURCHASE_INQUIRY: f"""
You are AF AI. The user is asking about purchasing/buying products.
User said: "{user_query}" in language: {lang}

Respond helpfully in {lang}:
- Explain that Aquaforest doesn't sell directly, only through authorized dealers
- Direct them to our dealer map:
  {"https://aquaforest.eu/pl/gdzie-kupic/" if lang == "pl" else "https://aquaforest.eu/en/where-to-buy/"}
- Be helpful and informative
""",

            Intent.COMPETITOR: f"""
You are AF AI. The user mentioned a competitor.
User said: "{user_query}" in language: {lang}

Respond playfully in {lang} with just: "Who is this? ;)"
Keep it light and humorous.
""",

            Intent.CENSORED: f"""
You are AF AI. The user is asking about proprietary information (formulas, production secrets).
User said: "{user_query}" in language: {lang}

Respond politely in {lang}:
- Explain that this information is a company secret
- Be polite but firm
- You can suggest they contact support for general product information
"""
        }
        
        base_prompt = f"""
You are AF AI, a friendly and professional assistant for Aquaforest.
Your response MUST be in {lang} language.

{intent_instructions.get(intent, "Respond helpfully to the user's query.")}

Generate your response in {lang}:
"""
        
        return base_prompt

    def format_response(self, state: ConversationState) -> ConversationState:
        try:
            prompt = self._create_universal_prompt(state)
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            state["final_response"] = response.choices[0].message.content
            if state.get("search_results"):
                state["context_cache"] = [r['metadata'] for r in state["search_results"][:5]]
        except Exception as e:
            print(f"Universal formatting error: {e}")
            state["final_response"] = "I apologize, but I encountered an error while formulating my response. Please contact our support team at support@aquaforest.eu for assistance."
        return state

# --- UZUPEŁNIONA FUNKCJA ---
def _create_follow_up_prompt(state: ConversationState) -> str:
    """Creates a prompt to answer a follow-up question using cached context."""
    lang = state.get("detected_language", "en")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    # Format the cache to be more readable for the LLM
    cached_context_info = []
    if state.get("context_cache"):
        for i, meta in enumerate(state.get("context_cache", [])):
            cached_context_info.append(
                f"Item {i+1}:\n"
                f"  - Name: {meta.get('product_name', 'N/A')}\n"
                f"  - Domain: {meta.get('domain', 'N/A')}\n"
                f"  - Description: {meta.get(f'title_{lang}', meta.get('title_en', ''))}\n"
            )
    cached_context_formatted = "\n".join(cached_context_info)

    return f"""
You are AF AI, an Aquaforest assistant. Your task is to answer a follow-up question based on the provided conversation history and cached information from the previous turn.

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

--- CACHED INFORMATION (from the previous response) ---
{cached_context_formatted}
---

TASK:
1.  Analyze the "LATEST USER MESSAGE". It's a direct response to your previous question.
2.  Filter the "CACHED INFORMATION" based on the user's new input. For example, if the user says "freshwater", filter for items where Domain is 'freshwater' or 'universal'.
3.  Generate a concise and helpful response in the user's language ({lang}), recommending the filtered products.
4.  If the cached information is insufficient, politely say that you don't have enough details and suggest rephrasing or asking a new question.

--- FINAL RESPONSE (in {lang} only) ---
"""

def format_final_response(state: ConversationState) -> ConversationState:
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def escalate_to_human(state: ConversationState) -> ConversationState:
    state["escalate"] = True
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def handle_follow_up(state: ConversationState) -> ConversationState:
    """Node function for LangGraph - handles follow-up questions using cached context."""
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
    except Exception as e:
        print(f"Follow-up handling error: {e}")
        state["final_response"] = "I'm sorry, I had trouble processing that. Could you please rephrase?"
        
    return state