"""
Intent and Language Detection Module - Enhanced Version 2.2 with Debug
Detects user intent and language from the query with better context understanding
"""
import json
from typing import Dict
from openai import OpenAI
from models import ConversationState, Intent, IntentDetectionResult
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV

class IntentDetector:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _create_intent_prompt(self, state: ConversationState) -> str:
        
        chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])

        # Check if this is likely a follow-up based on conversation history
        has_conversation_history = len(state.get("chat_history", [])) > 0
        conversation_context_hint = ""
        
        if has_conversation_history:
            conversation_context_hint = """
IMPORTANT: This conversation has existing history. Consider if the user's question is:
- A continuation of the previous topic/discussion
- Asking for clarification, recommendation, or more details about something already discussed  
- Using context from previous messages (even if not explicitly referencing them)
- A natural progression in the conversation flow

If the user's question builds upon or continues the conversation context, it's likely a FOLLOW-UP.
"""

        return f"""
You are an intent and language detection system for Aquaforest aquarium products support.
Your task is to analyze the user's LATEST message in the context of the conversation history.

--- CONVERSATION HISTORY (for context) ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

{conversation_context_hint}

CRITICAL CONTEXT ANALYSIS RULES:
1. If discussing a product and its target problem/pest, and user wants to buy "it" or mentions the pest name in purchase context - they mean the PRODUCT, not the pest!
   Example: After discussing "Aiptasia Shot" (product) and "Aiptasia" (pest), "buy aiptasia" = purchase_inquiry for the product

2. Common sense checks:
   - Nobody buys pests, diseases, or problems for their aquarium
   - If context shows discussion of a solution/product, purchase requests refer to that solution

3. References like "it", "that", "this" always refer to the most recently discussed PRODUCT or solution

INTENTS:
1. "greeting": Standard greetings (e.g., "hello", "hi", "good morning", "cześć", "dzień dobry", "siema", "siemanko").
2. "business": Business inquiries (e.g., "partnership", "b2b", "wholesale", "współpraca", "dystrybucja", "oferta biznesowa").
3. "product_query": Specific questions about products, aquarium problems, symptoms, or solutions when starting a NEW conversation topic. Also includes dosage and calculation questions about specific products.
4. "purchase_inquiry": The user is asking where, how, or for how much they can buy a product (e.g., "how to buy", "price", "where can I get", "gdzie kupić", "jaka jest cena", "zamówienie", "chcę kupić", "jak dokonać zakupu").
5. "competitor": Mentions of competitor brands (e.g., "Red Sea", "Seachem", "Tropic Marin").
6. "censored": Questions about proprietary information like product formulas or production processes.
7. "follow_up": The user is continuing an existing conversation - asking follow-up questions, seeking recommendations, clarifications, or additional details about topics already being discussed. This includes questions that naturally progress the conversation even if not directly referencing the previous response.
8. "other": Anything that doesn't fit the categories above.

LANGUAGES: Detect the primary language of the LATEST USER MESSAGE (pl, en, de, fr, es, it, etc.).

ANALYSIS PROCESS:
1. Read the conversation history to understand context
2. Check if this continues an existing conversation topic
3. Analyze the latest message
4. Apply common sense and context rules
5. Determine the most likely intent

Return ONLY a valid JSON object with your analysis of the LATEST USER MESSAGE:
{{
    "intent": "one_of_the_intents",
    "language": "detected_language_code",
    "confidence": 0.0-1.0,
    "context_note": "optional: brief note about context understanding"
}}
"""

    def detect(self, state: ConversationState) -> ConversationState:
        """Detect intent and language from user query"""
        if TEST_ENV:
            print(f"\n🎯 [DEBUG IntentDetector] Analizuję zapytanie: '{state['user_query']}'")
            if state.get("chat_history"):
                print(f"💬 [DEBUG IntentDetector] Historia konwersacji: {len(state.get('chat_history', []))} wiadomości")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": self._create_intent_prompt(state)}
                ],
                response_format={"type": "json_object"}
            )
            
            result_data = json.loads(response.choices[0].message.content)
            
            if TEST_ENV:
                print(f"🤖 [DEBUG IntentDetector] LLM Response: {result_data}")
            
            result = IntentDetectionResult(**result_data)
            
            # Update state
            state["intent"] = result.intent
            state["detected_language"] = result.language
            
            if TEST_ENV:
                print(f"✅ [DEBUG IntentDetector] Wykryto: Intent='{result.intent}', Language='{result.language}', Confidence={result.confidence}")
                if result_data.get("context_note"):
                    print(f"🧠 [DEBUG IntentDetector] Context note: {result_data['context_note']}")
            
            # If confidence is low, default to product_query
            if result.confidence < 0.5:
                if TEST_ENV:
                    print(f"⚠️ [DEBUG IntentDetector] Niska pewność ({result.confidence}), zmieniam na 'product_query'")
                state["intent"] = Intent.PRODUCT_QUERY
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG IntentDetector] Intent detection error: {e}")
                print(f"❌ [DEBUG IntentDetector] Błąd detekcji, używam domyślnych wartości")
            # Default fallback
            state["intent"] = Intent.PRODUCT_QUERY
            state["detected_language"] = "en"
            
        return state

def detect_intent_and_language(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    detector = IntentDetector()
    return detector.detect(state)