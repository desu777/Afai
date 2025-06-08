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
        self.system_prompt = """
You are an intent and language detection system for Aquaforest aquarium products support.

Detect the intent and language from user messages.

INTENTS:
1. "greeting" - greetings like "cześć", "siema", "hello", "hi", "dzień dobry"
2. "business" - business inquiries: "współpraca", "partnership", "b2b", "dealer", "wholesale", "distributor"
3. "calculator" - dosage calculations: "oblicz", "calculate", "ile potrzebuję", "how much do I need"
4. "product_query" - questions about products, problems, solutions, symptoms in aquarium
5. "competitor" - mentions of competitor brands: "Red Sea", "Seachem", "Brightwell", "Tropic Marin"
6. "censored" - production methods, ingredients, formulas: "jak produkujecie", "składniki", "recepta", "formula", "production process"
7. "other" - anything else that doesn't fit above categories

LANGUAGES: pl, en, de, fr, es, it (detect the primary language)

Return ONLY valid JSON:
{
    "intent": "one_of_the_intents",
    "language": "detected_language_code",
    "confidence": 0.0-1.0
}
"""

    def detect(self, state: ConversationState) -> ConversationState:
        """Detect intent and language from user query"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": state["user_query"]}
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