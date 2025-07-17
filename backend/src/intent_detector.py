"""
Intent and Language Detection Module - Enhanced Version 3.0 with OpenRouter
🚀 Migrated to OpenRouter per-node configuration (2025)
Detects user intent and language from the query with better context understanding
"""
import json
import re  # 🆕 For ICP URL detection
import base64  # 🆕 For PDF processing
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI
from models import ConversationState, Intent, IntentDetectionResult
from config import OPENAI_TEMPERATURE, TEST_ENV, debug_print
from prompts import load_prompt_template
from llm_client_factory import create_intent_detector_client, create_image_analysis_client
from icp_scraper import ICPScraper

class IntentDetector:
    def __init__(self):
        # Intent detection client
        self.client, self.model_name = create_intent_detector_client()
        
        # Image analysis client (separate configuration)
        self.image_client, self.image_model_name = create_image_analysis_client()
        
        if TEST_ENV:
            debug_print(f"🎯 [IntentDetector] Initialized with model: {self.model_name}")
            debug_print(f"📸 [IntentDetector] Image analysis model: {self.image_model_name}")
        
        # 🆕 Load competitors mapping for better detection
        self.competitors_list = self._load_competitors()
        
        if TEST_ENV and self.competitors_list:
            debug_print(f"🏢 [IntentDetector] Loaded {len(self.competitors_list)} competitor names for detection")
        
        # 🆕 Initialize ICP scraper for ICP analysis
        self.icp_scraper = ICPScraper()
        
        if TEST_ENV:
            debug_print(f"🔬 [IntentDetector] Initialized ICP scraper for ICP analysis")
    
    def _load_competitors(self) -> list:
        """Load competitor names from mapping for better intent detection"""
        try:
            mapping_file = Path(__file__).parent.absolute() / "mapping" / "competitors.json"
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    competitors_data = json.load(f)
                
                # Extract all competitor names
                competitor_names = []
                for category, items in competitors_data.items():
                    if isinstance(items, dict):
                        competitor_names.extend(items.keys())
                    elif isinstance(items, list):
                        competitor_names.extend(items)
                
                return competitor_names
        except Exception as e:
            if TEST_ENV:
                debug_print(f"⚠️ [IntentDetector] Could not load competitors: {e}")
        return []

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

        # 🆕 IMAGE ANALYSIS HINT
        image_hint = ""
        if state.get("image_url") and state.get("image_analysis"):
            image_hint = f"""
IMPORTANT: User provided an image with their question!
Image description: {state['image_analysis']}
This is very likely intent: "product_query" - user wants help with aquarium problems shown in image!
"""

        # 🆕 ICP CONTENT HINT - NEW! For PDFs and enhanced queries with ICP data
        icp_content_hint = ""
        if state.get("icp_data") or state.get("icp_analysis"):
            icp_content_hint = """
DETECTED: User attached ICP results (PDF/URL) requesting water analysis!
This is DEFINITELY intent: "analyze_icp" - user wants analysis of their water parameters!
"""

        # Try to load prompt from template
        prompt = load_prompt_template(
            "intent_detection",
            chat_history_formatted=chat_history_formatted,
            user_query=state['user_query'],
            conversation_context_hint=conversation_context_hint,
            icp_url_hint=icp_url_hint,  # 🆕 Pass ICP URL hint to template
            image_hint=image_hint,  # 🆕 Pass image hint to template
            icp_content_hint=icp_content_hint,  # 🆕 NEW! Pass ICP content hint to template
            competitors=self.competitors_list  # 🆕 Pass competitors list to template
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
{image_hint}
{icp_content_hint}

Return ONLY a valid JSON object:
{{
    "intent": "product_query",
    "language": "en",
    "confidence": 0.8,
    "context_note": "fallback prompt used"
}}
"""
        
        return prompt

    def _create_vision_messages(self, state: ConversationState) -> list:
        """Create messages for vision analysis with OpenRouter/Gemini"""
        
        # Build system prompt for vision analysis
        system_prompt = f"""You are an aquarium expert AI assistant analyzing images for Aquaforest products support.

Your task is to:
1. Analyze the image carefully - describe what you see in the aquarium
2. Identify any problems, issues, or concerns visible in the image
3. Provide detailed image analysis that will help with product recommendations

Focus on:
- Water quality issues (algae, cloudiness, discoloration)
- Coral health problems (bleaching, diseases, pests)
- Equipment issues
- Tank setup problems
- Any visible aquarium problems

User's message: "{state['user_query']}"

Return ONLY a valid JSON object:
{{
    "image_analysis": "Detailed description of what you see in the image and any problems identified"
}}
"""
        
        # Create messages with image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": state["image_url"]
                        }
                    }
                ]
            }
        ]
        
        return messages

    def _analyze_image_content(self, state: ConversationState) -> ConversationState:
        """Analyze image content and extract problems/issues"""
        if not state.get("image_url"):
            return state
            
        if TEST_ENV:
            print(f"📸 [DEBUG IntentDetector] Analyzing image with {self.image_model_name}: {state['image_url'][:100]}...")
        
        try:
            # Create vision messages
            messages = self._create_vision_messages(state)
            
            # Call OpenRouter/Gemini with vision using dedicated image analysis client
            response = self.image_client.chat.completions.create(
                model=self.image_model_name,
                temperature=OPENAI_TEMPERATURE,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            result_data = json.loads(response.choices[0].message.content)
            
            if TEST_ENV:
                print(f"🤖 [DEBUG IntentDetector] Vision analysis result: {result_data}")
            
            # Extract image analysis
            image_analysis = result_data.get("image_analysis", "")
            if image_analysis:
                state["image_analysis"] = image_analysis
                
                # 🆕 ENHANCE USER QUERY with image description (use language from text analysis)
                detected_language = state.get("detected_language", "en")
                if detected_language == "pl":
                    enhanced_query = f"{state['user_query']}\n\nUser dodał zdjęcie -> Opis zdjęcia: {image_analysis}"
                else:
                    enhanced_query = f"{state['user_query']}\n\nUser added image -> Image description: {image_analysis}"
                
                state["user_query"] = enhanced_query
                
                if TEST_ENV:
                    print(f"📝 [DEBUG IntentDetector] Enhanced query with image analysis")
                    print(f"🔍 [DEBUG IntentDetector] Original: {state['user_query'].split('User added image')[0].split('User dodał zdjęcie')[0]}")
                    print(f"🖼️ [DEBUG IntentDetector] Image analysis: {image_analysis}")
                    print(f"✅ [DEBUG IntentDetector] Vision analysis complete - keeping language: {detected_language}")
                
            return state
            
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG IntentDetector] Vision analysis error: {e}")
            debug_print(f"❌ [IntentDetector] Vision analysis failed: {e}")
            
            # Fallback - still process as text-only
            return state
            
        return state

    def _analyze_icp_content(self, state: ConversationState) -> ConversationState:
        """Analyze ICP content from URL (in user_query or image_url) or PDF"""
        
        # Check for ICP URL in user_query first
        user_query = state.get("user_query", "")
        icp_url_in_query = re.search(r'https?://(?:www\.)?aquaforestlab\.com/(?:pl|en)/results/\w+', user_query)
        
        # Check for content in image_url (PDF or URL)
        image_url = state.get("image_url", "")
        is_icp_url_in_image = re.search(r'aquaforestlab\.com/(?:pl|en)/results/\w+', image_url) if image_url else None
        is_pdf = image_url.startswith("data:application/pdf;base64,") if image_url else False
        
        # Determine what type of content we have
        if icp_url_in_query:
            content_type = "url_in_query"
            icp_url = icp_url_in_query.group(0)
        elif is_icp_url_in_image:
            content_type = "url_in_image"
            icp_url = image_url
        elif is_pdf:
            content_type = "pdf"
            icp_url = None
        else:
            return state  # No ICP content found
            
        if TEST_ENV:
            debug_print(f"🔬 [IntentDetector] Analyzing ICP content: {content_type.upper()}")
            if icp_url:
                debug_print(f"🔗 [IntentDetector] ICP URL found: {icp_url}")
        
        try:
            icp_data = None
            
            if content_type in ["url_in_query", "url_in_image"]:
                # Process ICP URL
                if TEST_ENV:
                    debug_print(f"🌐 [IntentDetector] Processing ICP URL: {icp_url}")
                
                state["icp_url"] = icp_url
                icp_data = self.icp_scraper.extract_icp_data_from_url(icp_url)
                
            elif content_type == "pdf":
                # Process PDF data
                if TEST_ENV:
                    debug_print(f"📄 [IntentDetector] Processing PDF ICP data")
                
                # Extract PDF content from base64
                pdf_base64 = image_url.split(",")[1]
                pdf_content = base64.b64decode(pdf_base64)
                
                state["icp_url"] = "PDF upload"
                icp_data = self.icp_scraper.process_pdf_icp_data(pdf_content, "icp_results.pdf")
            
            if icp_data and icp_data.get("status") == "success":
                # Store raw ICP data
                state["icp_data"] = icp_data
                
                # Format ICP data for LLM analysis with diagnosis
                formatted_icp_data = self.icp_scraper.format_icp_data_for_llm(
                    icp_data.get("parameters", {}), 
                    icp_data.get("metadata", {}),
                    icp_data.get("diagnosis", {})
                )
                
                state["icp_analysis"] = formatted_icp_data
                
                # 🆕 ENHANCE USER QUERY with ICP analysis (use language from text analysis)
                detected_language = state.get("detected_language", "en")
                if detected_language == "pl":
                    enhanced_query = f"{state['user_query']}\n\nUser dodał wyniki ICP -> Analiza ICP:\n{formatted_icp_data}"
                else:
                    enhanced_query = f"{state['user_query']}\n\nUser added ICP results -> ICP Analysis:\n{formatted_icp_data}"
                
                state["user_query"] = enhanced_query
                
                if TEST_ENV:
                    debug_print(f"📝 [IntentDetector] Enhanced query with ICP analysis")
                    debug_print(f"🔬 [IntentDetector] Found {len(icp_data.get('parameters', {}))} ICP parameters")
                    debug_print(f"✅ [IntentDetector] ICP analysis complete")
                
            else:
                if TEST_ENV:
                    debug_print(f"❌ [IntentDetector] ICP analysis failed: {icp_data.get('error', 'Unknown error')}")
                
            return state
            
        except Exception as e:
            if TEST_ENV:
                debug_print(f"❌ [IntentDetector] ICP analysis error: {e}")
                import traceback
                debug_print(f"🔍 [IntentDetector] Error traceback: {traceback.format_exc()}")
            
            # Fallback - still process as text-only
            return state

    def detect(self, state: ConversationState) -> ConversationState:
        """Detect intent and language from user query"""
        if TEST_ENV:
            print(f"\n🎯 [DEBUG IntentDetector] Analyzing query: '{state['user_query']}'")
            if state.get("chat_history"):
                print(f"💬 [DEBUG IntentDetector] Conversation history: {len(state.get('chat_history', []))} messages")
            if state.get("image_url"):
                print(f"📸 [DEBUG IntentDetector] Image provided: {state['image_url'][:100]}...")
        
        # 🆕 CONTENT ANALYSIS FIRST - check for ICP URLs/PDFs and images BEFORE text analysis
        
        # Check for ICP URL in user_query first
        user_query = state.get("user_query", "")
        has_icp_url_in_query = re.search(r'https?://(?:www\.)?aquaforestlab\.com/(?:pl|en)/results/\w+', user_query)
        
        # Check image_url if provided
        image_url = state.get("image_url", "")
        has_icp_url_in_image = re.search(r'aquaforestlab\.com/(?:pl|en)/results/\w+', image_url) if image_url else None
        has_pdf = image_url.startswith("data:application/pdf;base64,") if image_url else False
        has_image = image_url.startswith("data:image/") if image_url else False
        
        # Determine what content to analyze
        if has_icp_url_in_query or has_icp_url_in_image or has_pdf:
            if TEST_ENV:
                content_desc = "URL in query" if has_icp_url_in_query else ("URL in image" if has_icp_url_in_image else "PDF")
                print(f"🔬 [DEBUG IntentDetector] Adding ICP analysis ({content_desc})...")
            # Analyze ICP content and enhance user query FIRST
            state = self._analyze_icp_content(state)
        elif has_image:
            if TEST_ENV:
                print(f"📸 [DEBUG IntentDetector] Adding vision analysis...")
            # Analyze image content and enhance user query
            state = self._analyze_image_content(state)
        elif image_url:
            if TEST_ENV:
                print(f"❓ [DEBUG IntentDetector] Unknown image_url type: {image_url[:100]}...")
        
        # 🔄 TEXT ANALYSIS SECOND - now with enhanced query that includes ICP/image context
        try:
            if TEST_ENV:
                print(f"🔍 [DEBUG IntentDetector] Processing text analysis...")
                
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": self._create_intent_prompt(state)}
                ],
                response_format={"type": "json_object"}
            )
            
            result_data = json.loads(response.choices[0].message.content)
            
            if TEST_ENV:
                print(f"🤖 [DEBUG IntentDetector] Text analysis result: {result_data}")
            
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
            
            # Update state with text analysis
            state["intent"] = result.intent
            state["detected_language"] = result.language
            
            if TEST_ENV:
                print(f"✅ [DEBUG IntentDetector] Text analysis: Intent='{result.intent}', Language='{result.language}', Confidence={result.confidence}")
                if result_data.get("context_note"):
                    print(f"🧠 [DEBUG IntentDetector] Context note: {result_data['context_note']}")
            
            # If confidence is low, default to product_query
            if result.confidence < 0.5:
                if TEST_ENV:
                    print(f"⚠️ [DEBUG IntentDetector] Low confidence ({result.confidence}), changing to 'product_query'")
                state["intent"] = Intent.PRODUCT_QUERY
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG IntentDetector] Text analysis error: {e}")
                print(f"❌ [DEBUG IntentDetector] Using default values")
            # Default fallback
            state["intent"] = Intent.PRODUCT_QUERY
            state["detected_language"] = "en"
            
        return state

def detect_intent_and_language(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    detector = IntentDetector()
    return detector.detect(state)