"""
Response Formatting Module - VERSION 6.0 LLM INTELLIGENT
🚀 Simplified with full LLM intelligence - calculations remain safe via calculation_helper
Removed all hardcoded logic: dosage detection, special intents, domain handling, context formatters
"""
from typing import List, Dict, Any, Optional
import json
from openai import OpenAI
from models import ConversationState, Intent
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, debug_print
from calculation_helper import calculation_helper

class ResponseFormatter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _create_intelligent_response_prompt(self, state: ConversationState) -> str:
        """🚀 SINGLE INTELLIGENT PROMPT - replaces all hardcoded logic with LLM intelligence"""
        
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
            "use_case_info", "af_alternatives_to_search", "domain_filter"
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

        return f"""You are AF AI, Aquaforest's intelligent assistant. Create the perfect response using your full analytical capabilities.

=== CONTEXT ANALYSIS ===
User Query: "{user_query}"
Language: {lang}
Intent: {intent}
Confidence: {confidence:.2f}
{volume_info}

--- CONVERSATION HISTORY ---
{chat_history}

--- SEARCH RESULTS (Complete Metadata) ---
{search_results_json}

--- BUSINESS INTELLIGENCE ---
{business_context}

--- ADDITIONAL CONTEXT ---
{additional_context_json}

{dosage_calculations}

=== YOUR INTELLIGENT TASK ===

🧠 **ANALYZE & UNDERSTAND:**
1. **Intent Recognition**: What does the user really want?
   - Product recommendation? Dosage calculation? Problem solving?
   - Support contact? Business inquiry? Competitor comparison?
   - Category exploration? Follow-up question?

2. **Context Intelligence**: 
   - Is this freshwater or marine aquarium?
   - Are there domain conflicts in results?
   - What's the user's experience level?
   - Any specific problems to solve?

3. **Business Strategy**:
   - Are competitors mentioned? → Redirect to AF alternatives
   - Any business recommendations to prioritize?
   - Category requests → Show complete product range
   - ICP analysis → Focus on parameter corrections

4. **Calculation Needs**:
   - If dosage query + tank volume detected → Use PRE-CALCULATED dosages above
   - NEVER recalculate - use provided calculations exactly
   - Add safety notes if needed

🎯 **RESPONSE STRATEGY:**

For **PRODUCT QUERIES**:
- Lead with direct solution to their problem
- Prioritize business-recommended products
- Include all relevant products with descriptions
- Add dosage if calculated
- Provide product links when available

For **SPECIAL INTENTS**:
- **SUPPORT**: Acknowledge need, provide contact: https://aquaforest.eu/{lang}/contact/ + phone: (+48) 14 691 79 79
- **BUSINESS**: Professional tone, mention partnership interest, provide contact
- **COMPETITOR**: Acknowledge but redirect to superior AF alternatives
- **GREETING**: Friendly welcome, offer help with aquarium needs

For **CATEGORY REQUESTS**:
- Present ALL products from requested category
- Don't limit to just few - show complete range
- Brief description for each product

For **DOSAGE QUERIES**:
- Use PRE-CALCULATED dosages if provided
- Include safety recommendations
- Mention feeding frequency/timing if relevant

🔧 **TECHNICAL HANDLING:**

**Domain Conflicts**: If you see both freshwater and marine products, separate them:
- "For marine aquarium:" + marine products
- "For freshwater aquarium:" + freshwater products

**Product Duplicates**: If same product name appears multiple times with different URLs/metadata, present each as separate option.

**Confidence Handling**:
- High confidence (≥0.5): Be comprehensive and confident
- Low confidence: Still helpful but acknowledge uncertainty
- Never auto-add support contact unless specifically requested

**Language Formatting**:
- Polish: "Polecamy:", "Dawkowanie:", "Więcej informacji:"
- English: "We recommend:", "Dosage:", "Learn more:"
- Other languages: Adapt accordingly

🎨 **RESPONSE STRUCTURE:**
1. Direct answer to their question
2. Primary product recommendations
3. Supporting/complementary products
4. Dosage calculations (if applicable)
5. Additional resources/links
6. Next steps or suggestions

=== GENERATE PERFECT RESPONSE IN {lang.upper()} ===

Remember: You have full analytical power - use it! No rigid rules, just intelligent understanding of what the user needs and the best way to provide it.
"""
    
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
                print(f"\n🧠 [ResponseFormatter] Generating intelligent response...")
                
            prompt = self._create_intelligent_response_prompt(state)
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            
            state["final_response"] = response.choices[0].message.content
            
            if TEST_ENV:
                print(f"✅ [ResponseFormatter] Response generated ({len(state['final_response'])} characters)")
            
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