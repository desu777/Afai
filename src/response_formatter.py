"""
Response Formatting Module - VERSION 6.0 LLM INTELLIGENT
🚀 Simplified with full LLM intelligence - calculations remain safe via calculation_helper
🎭 Passionate expert persona with CoT framework using external prompt templates
"""
from typing import List, Dict, Any, Optional
import json
from openai import OpenAI
from models import ConversationState, Intent
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, debug_print
from calculation_helper import calculation_helper
from prompts import load_prompt_template

class ResponseFormatter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _create_intelligent_response_prompt(self, state: ConversationState) -> str:
        """🎭 PASSIONATE EXPERT PROMPT - uses external template with CoT framework"""
        
        # Basic context
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "product_query")
        user_query = state.get("user_query", "")
        confidence = state.get("confidence", 0.0)
        
        # Conversation history
        chat_history = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-6:]
            chat_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages])
        
        # Search results with full metadata
        search_results_json = json.dumps(state.get("search_results", []), indent=2, ensure_ascii=False)
        
        # Business intelligence context
        business_context = json.dumps(state.get("business_analysis", {}), indent=2, ensure_ascii=False)
        
        # All additional context
        additional_context = {}
        context_fields = [
            "requested_category", "category_products", "identified_problem", 
            "recommended_solutions", "maintenance_solutions", "solution_note",
            "business_recommendations", "competitor_info", "scenario_info", 
            "use_case_info", "af_alternatives_to_search", "domain_filter",
            "product_recommendations"  # 🆕 Add categorized products
        ]
        
        for field in context_fields:
            if state.get(field):
                additional_context[field] = state[field]
        
        additional_context_json = json.dumps(additional_context, indent=2, ensure_ascii=False)
        
        # Try to extract volume for potential dosage calculations
        extracted_volume = calculation_helper.extract_volume_from_query(user_query)
        volume_info = f"Detected tank volume: {extracted_volume}L" if extracted_volume else "No tank volume detected"
        
        # Prepare pre-calculated dosages if volume detected
        dosage_calculations = ""
        if extracted_volume:
            calculated_dosages = []
            for result in state.get("search_results", []):
                meta = result.get('metadata', {})
                product_name = meta.get('product_name', '')
                
                # Try to extract dosage info from metadata
                dosage_amount = self._extract_dosage_amount(meta)
                if dosage_amount > 0:
                    calc_result = calculation_helper.calculate_dosage(
                        dosage_amount, 100, extracted_volume, "ml"
                    )
                    if calc_result["success"]:
                        calculated_dosages.append(f"• {product_name}: {calc_result['calculation']}")
            
            if calculated_dosages:
                dosage_calculations = f"""
PRE-CALCULATED DOSAGES (use these exact calculations):
{chr(10).join(calculated_dosages)}
"""

        # Choose appropriate template based on intent
        if intent == Intent.FOLLOW_UP:
            template_name = "response_follow_up"
        else:
            template_name = "response_passionate_expert"
        
        # Try to load prompt from external template
        prompt = load_prompt_template(
            template_name,
            user_query=user_query,
            language=lang,
            intent=intent,
            confidence=confidence,
            volume_info=volume_info,
            chat_history=chat_history,
            search_results_json=search_results_json,
            business_context=business_context,
            additional_context_json=additional_context_json,
            dosage_calculations=dosage_calculations,
            language_upper=lang.upper()
        )
        
        # Fallback if template fails
        if not prompt:
            if TEST_ENV:
                print("⚠️ [ResponseFormatter] Template failed, using fallback prompt")
            prompt = f"""You are a passionate Aquaforest expert. Help the user with: "{user_query}"
Use the search results to provide detailed product recommendations in {lang} language.
Be enthusiastic and guide them toward Aquaforest solutions."""
        
        return prompt
    
    def _extract_dosage_amount(self, metadata: Dict) -> float:
        """Simple helper to extract dosage amount from metadata"""
        # Try various dosage fields
        for field in ['dosage_amount', 'amount', 'dose']:
            if metadata.get(field):
                try:
                    # Extract first number from string
                    import re
                    match = re.search(r'(\d+(?:\.\d+)?)', str(metadata[field]))
                    if match:
                        return float(match.group(1))
                except:
                    continue
        return 0.0
    
    def format_response(self, state: ConversationState) -> ConversationState:
        """🚀 SIMPLIFIED: Single LLM call with intelligent prompt"""
        try:
            if TEST_ENV:
                print(f"\n🧠 [ResponseFormatter] Generating passionate expert response...")
                print(f"🎯 [ResponseFormatter] Intent: {state.get('intent')}, Language: {state.get('detected_language')}")
                if state.get("business_analysis", {}).get("af_alternatives_to_search"):
                    print(f"⭐ [ResponseFormatter] Priority AF alternatives: {state['business_analysis']['af_alternatives_to_search']}")
                if state.get("product_recommendations"):
                    print(f"📊 [ResponseFormatter] Categorized products: {state['product_recommendations']}")
                    total_products = sum(len(products) for products in state['product_recommendations'].values() if isinstance(products, list))
                    print(f"🔢 [ResponseFormatter] Total categorized products: {total_products}")
                
                # Check for knowledge articles in search results
                knowledge_articles = [r for r in state.get("search_results", []) if r.get('metadata', {}).get('content_type') == 'knowledge']
                if knowledge_articles:
                    print(f"📚 [ResponseFormatter] Found {len(knowledge_articles)} knowledge articles:")
                    for article in knowledge_articles[:3]:  # Show first 3
                        title = article.get('metadata', {}).get('title_en', 'Unknown')
                        url_pl = article.get('metadata', {}).get('url_pl', 'No URL')
                        url_en = article.get('metadata', {}).get('url_en', 'No URL')
                        print(f"   - {title}")
                        print(f"     URL_PL: {url_pl}")
                        print(f"     URL_EN: {url_en}")
                else:
                    print(f"📚 [ResponseFormatter] NO knowledge articles found in search results")
                
            prompt = self._create_intelligent_response_prompt(state)
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            
            state["final_response"] = response.choices[0].message.content
            
            if TEST_ENV:
                print(f"✅ [ResponseFormatter] Passionate response generated ({len(state['final_response'])} characters)")
                # Check if response follows structure
                response_text = state["final_response"].lower()
                has_diagnosis = any(word in response_text for word in ["diagnosis", "diagnoza", "problem", "situation"])
                has_solutions = any(word in response_text for word in ["recommend", "polecam", "solution", "rozwiązanie"])
                print(f"📋 [ResponseFormatter] Structure check - Diagnosis: {has_diagnosis}, Solutions: {has_solutions}")
            
            # Cache metadata for follow-ups
            if state.get("search_results"):
                cache_size = 10 if state.get("requested_category") else 5
                state["context_cache"] = [r['metadata'] for r in state["search_results"][:cache_size]]
                if TEST_ENV:
                    print(f"💾 [ResponseFormatter] Cached metadata for {len(state['context_cache'])} results")
                    
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [ResponseFormatter] Error: {e}")
            state["final_response"] = self._handle_error(e, state)
        
        return state
    
    def _handle_error(self, error: Exception, state: ConversationState) -> str:
        """Simple error handling"""
        debug_print(f"❌ [ResponseFormatter] Error: {str(error)}")
        
        language = state.get("detected_language", "en")
        if language == "pl":
            return "Przepraszam, wystąpił błąd. Spróbuj ponownie lub skontaktuj się z naszym wsparciem."
        else:
            return "Sorry, an error occurred. Please try again or contact our support."

def format_final_response(state: ConversationState) -> ConversationState:
    """🚀 SIMPLIFIED: Main entry point"""
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def escalate_to_human(state: ConversationState) -> ConversationState:
    """🚀 SIMPLIFIED: LLM handles escalation intelligently"""
    if TEST_ENV:
        print(f"\n⚠️ [Escalate] Low confidence - LLM will handle gracefully")
    
    state["escalate"] = True
    
    # Let the main formatter handle escalation intelligently
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def handle_follow_up(state: ConversationState) -> ConversationState:
    """🚀 SIMPLIFIED: LLM handles follow-ups with cached context"""
    if TEST_ENV:
        print(f"\n🔄 [Follow-up] LLM handling with cached context")
        
    # Add follow-up context to prompt
    state["is_follow_up"] = True
    
    formatter = ResponseFormatter()
    return formatter.format_response(state)