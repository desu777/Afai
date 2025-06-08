"""
Response Formatting Module
Formats final response with proper language and structure
"""
from typing import List, Dict, Any
from openai import OpenAI
from models import ConversationState, ProductInfo
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

class ResponseFormatter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _get_product_url(self, product: Dict, language: str) -> str:
        """Get appropriate URL based on language"""
        meta = product.get('metadata', {})
        if language == 'pl' and meta.get('url_pl'):
            return meta['url_pl']
        return meta.get('url_en', '')

    def _create_universal_prompt(self, state: ConversationState) -> str:
        """Create a single, powerful prompt for the LLM to format any response."""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "product_query")
        confidence = state.get("confidence", 0.0)
        escalate_flag = state.get("escalate", False)
        
        # Format search results for the prompt
        results_info = []
        if state.get("search_results"):
            for i, p in enumerate(state["search_results"][:5]):
                meta = p.get('metadata', {})
                url = self._get_product_url(p, lang)
                results_info.append(
                    f"Result {i+1}:\n"
                    f"  - Name: {meta.get('product_name', 'N/A')}\n"
                    f"  - Type: {meta.get('content_type', 'N/A')}\n"
                    f"  - Description: {meta.get(f'title_{lang}', meta.get('title_en', ''))}\n"
                    f"  - Dosage: {meta.get('dosage_amount', 'N/A')} per {meta.get('dosage_volume', 'N/A')} {meta.get('dosage_frequency', '').replace('_', ' ')}\n"
                    f"  - URL: {url}\n"
                    f"  - Score: {p.get('score', 0):.3f}\n"
                )
        formatted_search_results = "\n".join(results_info) if results_info else "No search results found."

        # Add language-specific sign-off instructions
        if lang == 'pl':
            sign_off_instruction = 'Na końcu odpowiedzi, jeśli jest to stosowne (np. przy powitaniu lub ogólnym zapytaniu), możesz dodać link do strony o naszej misji: "Więcej o naszej misji dowiesz się na: https://aquaforest.eu/pl/misja/". Nie dodawaj tego linku, jeśli eskalujesz problem do wsparcia lub odpowiadasz na zapytanie biznesowe, ponieważ tam podajesz już inne dane kontaktowe.'
        else:
            sign_off_instruction = 'At the end of the response, where appropriate (e.g., for a greeting or a general query), you can add a link to our contact page: "You can find more information or contact us at: https://aquaforest.eu/en/contact-us/". Do not add this link if you are escalating to support or responding to a business inquiry, as other contact details are already provided in those cases.'

        return f"""
You are AF AI, a friendly, expert, and professional assistant for Aquaforest, a manufacturer of high-quality aquarium products.
Your responses must be helpful, accurate, and reflect the brand's voice.

--- CONTEXT ---
User's Original Query: "{state.get('original_query', '')}"
Detected Language: "{lang}" (You MUST respond ONLY in this language)
Detected Intent: "{intent}"
Search Results Confidence: {confidence:.2f}
Escalation Flag: {escalate_flag}

--- SEARCH RESULTS (if any) ---
{formatted_search_results}
---

Your task is to generate the best possible response to the user based on all the context above.
Follow these rules based on the situation:

1.  **If 'Escalation Flag' is `True` OR Confidence is very low (< 0.45):**
    - Gently inform the user that you couldn't find a certain answer to their question.
    - Do NOT recommend any products.
    - Provide the official support channels for more complex issues:
      - Email: support@aquaforest.eu
      - Phone: +48 14 691 79 79

2.  **If Intent is `greeting`:**
    - Provide a warm and friendly greeting in "{lang}".
    - Introduce yourself as the Aquaforest AI assistant and ask how you can help.

3.  **If Intent is `business`:**
    - Thank the user for their interest in a partnership.
    - Provide the direct contact information for business inquiries:
      - Form: https://aquaforest.eu/en/contact-us/
      - Email: info@aquaforest.eu
      - Phone: +48 14 691 79 79

4.  **If Intent is `competitor`:**
    - Give a short, witty, and brand-loyal response in "{lang}". Be creative, for example: "We are focused on the quality and effectiveness of our own product line to ensure the best results for aquarists."

5.  **If Intent is `censored`:**
    - Politely explain that specific product formulas and production methods are proprietary business secrets.
    - Reassure the user about the quality and effectiveness of the products and pivot back to how you can help them achieve their aquarium goals.

6.  **If Intent is `purchase_inquiry`:**
    - Politely explain that Aquaforest does not sell products directly to retail customers.
    - Direct the user to the official "Where to buy" page to find a local or online distributor.
    - Provide the correct link based on the user's language:
      - For "pl": `https://aquaforest.eu/pl/gdzie-kupic/`
      - For all other languages: `https://aquaforest.eu/en/where-to-buy/`

7.  **If Intent is `product_query`:**
    - **High Confidence (>= 0.7):**
        - Directly recommend 1-3 of the most relevant products from the search results.
        - For each product, use its name in **bold**.
        - Explain BRIEFLY why it solves the user's problem, using information from the description.
        - Provide key dosage information if available in the search results.
        - Provide the direct URL for more information.
    - **Medium Confidence (0.45 to 0.7):**
        - Acknowledge that you found some potentially useful products but are not 100% certain.
        - Recommend 1-2 products that seem most relevant, presenting them as suggestions.
        - **CRUCIALLY, add general advice** about the user's problem. For example, for an "algae problem", give tips on water changes, lighting, and nutrient control. This adds value even if the product suggestion isn't perfect.
    - **General Rules for Product Queries:**
        - ONLY recommend items where `Type` is `product`.
        - You can cite articles (`Type: "article"`) as helpful resources, but do NOT present them as products.
        - If the results contain products for both marine and freshwater and the user hasn't specified, ask them to clarify which type of aquarium they have.

--- SIGN-OFF INSTRUCTIONS ---
{sign_off_instruction}

--- FINAL RESPONSE ---
Generate only the final response text for the user. Do not wrap it in JSON or add any other explanations.
"""

    def format_response(self, state: ConversationState) -> ConversationState:
        """Formats the final response using the universal LLM prompt."""
        try:
            prompt = self._create_universal_prompt(state)
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            state["final_response"] = response.choices[0].message.content

            # After generating a response, save the context for potential follow-ups
            if state.get("search_results"):
                state["context_cache"] = [r['metadata'] for r in state["search_results"][:5]]
            else:
                state["context_cache"] = []

        except Exception as e:
            print(f"Universal formatting error: {e}")
            state["final_response"] = "I apologize, but I encountered an error while formulating my response. Please contact our support team at support@aquaforest.eu for assistance."
            
        return state

def _create_follow_up_prompt(state: ConversationState) -> str:
    """Creates a prompt to answer a follow-up question using cached context."""
    lang = state.get("detected_language", "en")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    cached_context_formatted = "\n".join([str(item) for item in state.get("context_cache", [])])

    return f"""
You are AF AI, an Aquaforest assistant. Your task is to answer a follow-up question based on the provided conversation history and cached information from the previous turn.

--- CONVERSATION HISTORY ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

--- CACHED INFORMATION (from the previous response) ---
Here is the data you used to construct your last answer. Use this to answer the user's new question without searching again.
{cached_context_formatted}
---

TASK:
1.  Analyze the "LATEST USER MESSAGE".
2.  Find the relevant information within the "CACHED INFORMATION" to answer it.
3.  Generate a concise and helpful response in the user's language ({lang}).
4.  If the cached information is insufficient to answer the question, politely say that you don't have enough details and suggest rephrasing or asking a new question.

Example: If the user asks for a link, and a URL is in the cached info, provide it. If they ask about dosage and it's in the cache, provide it.

--- FINAL RESPONSE ---
Generate only the final response text for the user.
"""

def format_final_response(state: ConversationState) -> ConversationState:
    """Node function for LangGraph - handles high confidence and simple intents."""
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def add_llm_knowledge(state: ConversationState) -> ConversationState:
    """Node function for LangGraph - handles medium confidence cases by using the same universal formatter."""
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def escalate_to_human(state: ConversationState) -> ConversationState:
    """Escalate to human support by setting the flag and using the universal formatter."""
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