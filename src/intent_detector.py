"""
Intent and Language Detection Module - Enhanced Version 2.2 with Debug
Detects user intent and language from the query with better context understanding
"""
import json
import re  # 🆕 For ICP URL detection
from typing import Dict
from openai import OpenAI
from models import ConversationState, Intent, IntentDetectionResult
from config import OPENAI_API_KEY, OPENAI_MODEL2, OPENAI_TEMPERATURE, TEST_ENV
from prompts import load_prompt_template

class IntentDetector:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _create_intent_prompt(self, state: ConversationState) -> str:
        """Create intent detection prompt using external template"""
        
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

        # 🆕 ICP URL Detection
        icp_url_hint = ""
        if re.search(r'aquaforestlab\.com/(?:pl|en)/results/\w+', state['user_query']):
            icp_url_hint = """
IMPORTANT: User provided an ICP test results URL from aquaforestlab.com
This is very likely intent: "analyze_icp" - user wants analysis of their water parameters!
"""

        # Try to load prompt from template
        prompt = load_prompt_template(
            "intent_detection",
            chat_history_formatted=chat_history_formatted,
            user_query=state['user_query'],
            conversation_context_hint=conversation_context_hint,
            icp_url_hint=icp_url_hint  # 🆕 Pass ICP URL hint to template
        )
        
        # Fallback to hardcoded prompt if template fails
        if not prompt:
            if TEST_ENV:
                print("⚠️ [IntentDetector] Using fallback hardcoded prompt")
            prompt = f"""
You are an intent and language detection system for Aquaforest aquarium products support.
Your task is to analyze the user's LATEST message in the context of the conversation history.

--- CONVERSATION HISTORY (for context) ---
{chat_history_formatted}
---
LATEST USER MESSAGE: "{state['user_query']}"
---

{conversation_context_hint}

Return ONLY a valid JSON object:
{{
    "intent": "product_query",
    "language": "en",
    "confidence": 0.8,
    "context_note": "fallback prompt used"
}}
"""
        
        return prompt

    def detect(self, state: ConversationState) -> ConversationState:
        """Detect intent and language from user query"""
        if TEST_ENV:
            print(f"\n🎯 [DEBUG IntentDetector] Analyzing query: '{state['user_query']}'")
            if state.get("chat_history"):
                print(f"💬 [DEBUG IntentDetector] Conversation history: {len(state.get('chat_history', []))} messages")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL2,
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
            
            # 🚨 CRITICAL FIX: Prevent follow_up without chat history
            chat_history = state.get("chat_history", [])
            if result.intent == Intent.FOLLOW_UP and (not chat_history or len(chat_history) == 0):
                if TEST_ENV:
                    print(f"🚨 [DEBUG IntentDetector] CRITICAL FIX: Preventing FOLLOW_UP intent without chat history")
                    print(f"📋 [DEBUG IntentDetector] Chat history length: {len(chat_history) if chat_history else 0}")
                result.intent = Intent.PRODUCT_QUERY  # Default to product_query for first messages
                if TEST_ENV:
                    print(f"✅ [DEBUG IntentDetector] Corrected intent from follow_up to product_query")
            
            # Update state
            state["intent"] = result.intent
            state["detected_language"] = result.language
            
            if TEST_ENV:
                print(f"✅ [DEBUG IntentDetector] Detected: Intent='{result.intent}', Language='{result.language}', Confidence={result.confidence}")
                if result_data.get("context_note"):
                    print(f"🧠 [DEBUG IntentDetector] Context note: {result_data['context_note']}")
            
            # If confidence is low, default to product_query
            if result.confidence < 0.5:
                if TEST_ENV:
                    print(f"⚠️ [DEBUG IntentDetector] Low confidence ({result.confidence}), changing to 'product_query'")
                state["intent"] = Intent.PRODUCT_QUERY
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG IntentDetector] Intent detection error: {e}")
                print(f"❌ [DEBUG IntentDetector] Detection error, using default values")
            # Default fallback
            state["intent"] = Intent.PRODUCT_QUERY
            state["detected_language"] = "en"
            
        return state

def detect_intent_and_language(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    detector = IntentDetector()
    return detector.detect(state)