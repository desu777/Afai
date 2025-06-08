"""
Intent and Language Detection Module
Detects user intent and language from the query
"""
import json
from typing import Dict
from openai import OpenAI
from models import ConversationState, Intent, IntentDetectionResult
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

class IntentDetector:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _create_intent_prompt(self, state: ConversationState) -> str:
        
        chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])

        # --- ZMIANA --- Dodano polskie przykłady do kluczowych intencji
        return f"""
You are an intent and language detection system for Aquaforest aquarium products support.
Your task is to analyze the user's LATEST message in the context of the conversation history.

--- CONVERSATION HISTORY (for context) ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

INTENTS:
1. "greeting": Standard greetings (e.g., "hello", "hi", "good morning", "cześć", "dzień dobry").
2. "business": Business inquiries (e.g., "partnership", "b2b", "wholesale", "współpraca", "dystrybucja", "oferta biznesowa").
3. "calculator": Requests for dosage calculations (e.g., "calculate", "how much do I need", "oblicz", "ile potrzebuję").
4. "product_query": Specific questions about products, aquarium problems, symptoms, or solutions. This is the most common intent.
5. "purchase_inquiry": The user is asking where, how, or for how much they can buy a product (e.g., "how to buy", "price", "where can I get", "gdzie kupić", "jaka jest cena", "zamówienie").
6. "competitor": Mentions of competitor brands (e.g., "Red Sea", "Seachem", "Tropic Marin").
7. "censored": Questions about proprietary information like product formulas or production processes.
8. "follow_up": The user is asking a direct follow-up question about the assistant's PREVIOUS response. Examples:
    - "Can you give me the link for that?"
    - "A co z drugim produktem?"
    - "Tell me more."
    - "Dlaczego polecasz właśnie to?"
9. "other": Anything that doesn't fit the categories above.

LANGUAGES: Detect the primary language of the LATEST USER MESSAGE (pl, en, de, fr, es, it, etc.).

Return ONLY a valid JSON object with your analysis of the LATEST USER MESSAGE:
{{
    "intent": "one_of_the_intents",
    "language": "detected_language_code",
    "confidence": 0.0-1.0
}}
"""

    def detect(self, state: ConversationState) -> ConversationState:
        """Detect intent and language from user query"""
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
            result = IntentDetectionResult(**result_data)
            
            # Update state
            state["intent"] = result.intent
            state["detected_language"] = result.language
            
            # If confidence is low, default to product_query
            if result.confidence < 0.5:
                state["intent"] = Intent.PRODUCT_QUERY
                
        except Exception as e:
            print(f"Intent detection error: {e}")
            # Default fallback
            state["intent"] = Intent.PRODUCT_QUERY
            state["detected_language"] = "en"
            
        return state

def detect_intent_and_language(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    detector = IntentDetector()
    return detector.detect(state)