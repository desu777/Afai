"""
Response Formatting Module - VERSION 7.0 with OpenRouter Per-Node
🚀 Fully migrated to OpenRouter per-node configuration (2025)
Unified client management with per-node model selection
"""
from typing import List, Dict, Any, Optional
import json
import re
from openai import OpenAI
from models import ConversationState, ProductInfo, Intent, Domain
from config import OPENAI_TEMPERATURE, TEST_ENV, debug_print
from calculation_helper import calculation_helper
from prompts import load_prompt_template
from llm_client_factory import create_response_formatter_client

class ResponseFormatter:
    def __init__(self):
        self.client, self.model_name = create_response_formatter_client()
        
        if TEST_ENV:
            debug_print(f"📝 [ResponseFormatter] Initialized with OpenRouter per-node configuration")
            debug_print(f"🎯 [ResponseFormatter] Using model: {self.model_name}")
        
        self.dosage_keywords = [
            'how much', 'combien', 'quanto', 'dosierung', 'dosis', 'how much needed',
            'how to dose', 'how to dose', 'how much to add', 'how to apply', 'what dose',
            'for', 'for', 'liters', 'liters', 'L'
        ]
    
    def _detect_dosage_query(self, query: str) -> bool:
        """Detect if query is about dosage/calculation"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.dosage_keywords)
    
    def _extract_dosage_info(self, metadata: Dict) -> Dict[str, Any]:
        """Extract dosage information from product metadata"""
        dosage_info = {
            "has_dosage": False,
            "base_amount": None,
            "base_volume": 100,  # Default to 100L
            "unit": "ml",
            "frequency": "daily",
            "timing": None,
            "special_instructions": []
        }
        
        # Check various dosage fields
        if metadata.get("dosage_amount"):
            dosage_info["has_dosage"] = True
            dosage_info["base_amount"] = self._parse_amount(metadata["dosage_amount"])
            
        if metadata.get("dosage_volume"):
            volume = self._parse_volume(metadata["dosage_volume"])
            if volume:
                dosage_info["base_volume"] = volume
                
        if metadata.get("dosage_unit"):
            dosage_info["unit"] = metadata["dosage_unit"]
            
        if metadata.get("dosage_frequency"):
            dosage_info["frequency"] = metadata["dosage_frequency"]
            
        if metadata.get("dosage_timing"):
            dosage_info["timing"] = metadata["dosage_timing"]
            
        # Parse from full content if needed
        if not dosage_info["has_dosage"] and metadata.get("full_content_en"):
            dosage_info = self._parse_dosage_from_content(metadata["full_content_en"], dosage_info)
            
        return dosage_info
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount from string like '10 ml' or '1 drop'"""
        try:
            # Extract number from string
            match = re.search(r'(\d+(?:\.\d+)?)', str(amount_str))
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.0
    
    def _parse_volume(self, volume_str: str) -> Optional[int]:
        """Parse volume from string like '100L' or '100 liters'"""
        try:
            match = re.search(r'(\d+)\s*[lL]', str(volume_str))
            if match:
                return int(match.group(1))
        except:
            pass
        return None
    
    def _parse_dosage_from_content(self, content: str, dosage_info: Dict) -> Dict:
        """Try to parse dosage from full content"""
        # Common dosage patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(ml|drops?|kropli?|krople?)\s*(?:per|na)\s*(\d+)\s*[lL]',
            r'dawkowanie:?\s*(\d+(?:\.\d+)?)\s*(ml|drops?)',
            r'dose:?\s*(\d+(?:\.\d+)?)\s*(ml|drops?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                dosage_info["has_dosage"] = True
                dosage_info["base_amount"] = float(match.group(1))
                dosage_info["unit"] = match.group(2).lower()
                if len(match.groups()) >= 3:
                    dosage_info["base_volume"] = int(match.group(3))
                break
                
        return dosage_info
    
    def _get_product_url(self, product: Dict, language: str) -> str:
        meta = product.get('metadata', {})
        if language == 'pl' and meta.get('url_pl'):
            return meta['url_pl']
        return meta.get('url_en', '')
    
    def _has_mixed_domains(self, results: List[Dict]) -> bool:
        """Check if results contain both freshwater and seawater products"""
        domains = set()
        for result in results:
            domain = result.get('metadata', {}).get('domain')
            if domain and domain != 'universal':
                domains.add(domain)
        return len(domains) > 1
    
    def _group_results_by_domain(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """Group results by domain"""
        grouped = {
            'seawater': [],
            'freshwater': [],
            'universal': []
        }
        
        for result in results:
            domain = result.get('metadata', {}).get('domain', 'universal')
            if domain in grouped:
                grouped[domain].append(result)
        
        return grouped

    def _create_universal_prompt(self, state: ConversationState) -> str:
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "product_query")
        
        if TEST_ENV:
            print(f"\n📝 [DEBUG ResponseFormatter] Formatting response for intent='{intent}', language='{lang}'")
        
        # Handle special intents first
        if intent in [Intent.GREETING, Intent.BUSINESS, 
                     Intent.PURCHASE_INQUIRY, Intent.COMPETITOR, Intent.CENSORED, Intent.SUPPORT, Intent.OTHER]:
            if TEST_ENV:
                print(f"🎭 [DEBUG ResponseFormatter] Handling special intent: {intent}")
            return self._create_special_intent_prompt(state)
        
        # Format conversation history
        chat_history_formatted = ""
        if state.get("chat_history"):
            chat_history_formatted = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in state.get("chat_history", [])[-6:]
            ])
        
        # Check for mixed domains
        has_mixed = self._has_mixed_domains(state.get("search_results", []))
        domain_not_specified = not state.get("domain_filter")
        
        # Check for dosage query
        is_dosage_query = self._detect_dosage_query(state.get("user_query", ""))
        aquarium_volume = None
        if is_dosage_query:
            aquarium_volume = calculation_helper.extract_volume_from_query(state.get("user_query", ""))
            if TEST_ENV:
                print(f"💊 [DEBUG ResponseFormatter] Dosage query detected!")
                print(f"📏 [DEBUG ResponseFormatter] Extracted volume: {aquarium_volume}L" if aquarium_volume else "📏 [DEBUG ResponseFormatter] No volume extracted")
        
        # Category context
        category_context = ""
        if state.get("requested_category") and state.get("category_products"):
            category_context = f"""
--- CATEGORY REQUEST ---
User asked for products in category: {state.get("requested_category")}
Expected products to show: {', '.join(state.get("category_products", []))}
Make sure to present ALL products from this category that were found!
---
"""
        
        # Problem-solution context
        problem_context = ""
        if state.get("identified_problem") and state.get("recommended_solutions"):
            problem_context = f"""
--- PROBLEM IDENTIFIED ---
Problem: {state.get("identified_problem")}
Recommended solutions: {', '.join(state.get("recommended_solutions", []))}
Focus on these solutions in your response!
---
"""
        
        # Balling method context
        balling_context = ""
        if state.get("maintenance_solutions") and state.get("solution_note"):
            balling_context = f"""
--- BALLING METHOD NOTE ---
User asked about correcting a single parameter.
Maintenance products suggested: {', '.join(state.get("maintenance_solutions", []))}
IMPORTANT NOTE: {state.get("solution_note", "")}
You MUST mention that Balling/Component products contain multiple elements and are for daily maintenance, not single corrections!
---
"""
        
        # 🚀 ENHANCED BUSINESS RECOMMENDATIONS CONTEXT
        business_context = ""
        if state.get("business_recommendations"):
            business_context = self._format_business_recommendations_context(state["business_recommendations"])
        
        # 🚀 COMPETITOR CONTEXT
        competitor_context = ""
        if state.get("competitor_info"):
            competitor_context = self._format_competitor_context(state["competitor_info"])
        
        # 🚀 SCENARIO CONTEXT  
        scenario_context = ""
        if state.get("scenario_info"):
            scenario_context = self._format_scenario_context(state["scenario_info"])
        
        # 🚀 USE CASE CONTEXT
        use_case_context = ""
        if state.get("use_case_info"):
            use_case_context = self._format_use_case_context(state["use_case_info"])
        
        # Full metadata dump
        all_results_metadata = []
        dosage_calculations = []
        
        if state.get("search_results"):
            if TEST_ENV:
                print(f"📊 [DEBUG ResponseFormatter] Processing {len(state.get('search_results', []))} results")
                if has_mixed and domain_not_specified:
                    print(f"🎯 [DEBUG ResponseFormatter] Mixed domains detected, will present both")
            
            # Process results and prepare dosage calculations
            for i, result in enumerate(state["search_results"]):
                meta = result.get('metadata', {})
                
                # Extract dosage info if this is a dosage query
                if is_dosage_query and aquarium_volume:
                    dosage_info = self._extract_dosage_info(meta)
                    if dosage_info["has_dosage"]:
                        calc_result = calculation_helper.calculate_dosage(
                            dosage_info["base_amount"],
                            dosage_info["base_volume"],
                            aquarium_volume,
                            dosage_info["unit"]
                        )
                        if calc_result["success"]:
                            dosage_calculations.append({
                                "product": meta.get("product_name", "Unknown"),
                                "calculation": calc_result
                            })
                
                metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
                all_results_metadata.append(f"""
Result {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
        
        formatted_all_results = "".join(all_results_metadata) if all_results_metadata else "No search results found."
        
        # Format dosage calculations
        dosage_context = ""
        if dosage_calculations:
            dosage_context = f"""
--- DOSAGE CALCULATIONS ---
Aquarium volume: {aquarium_volume}L
Calculated dosages:
"""
            for calc in dosage_calculations:
                dosage_context += f"\n- {calc['product']}: {calc['calculation']['calculation']}"
            dosage_context += "\n---\n"

        # Try to load prompt from template
        prompt = load_prompt_template(
            "response_formatting",
            language=lang,
            chat_history_formatted=chat_history_formatted,
            user_query=state.get('user_query', ''),  # Fixed: user_query instead of original_query
            is_dosage_query=is_dosage_query,
            aquarium_volume=aquarium_volume if aquarium_volume else "Not specified",
            mixed_domains_detected=has_mixed and domain_not_specified,
            category_context=category_context,
            problem_context=problem_context,
            balling_context=balling_context,
            dosage_context=dosage_context,
            business_context=business_context,
            competitor_context=competitor_context,
            scenario_context=scenario_context,
            use_case_context=use_case_context,
            formatted_all_results=formatted_all_results,
            language_upper=lang.upper()
        )
        
        # Fallback to simple prompt if template fails
        if not prompt:
            if TEST_ENV:
                print("⚠️ [ResponseFormatter] Using fallback hardcoded prompt")
            prompt = f"""
You are AF AI, assistant for Aquaforest. 
Generate helpful response about: "{state.get('user_query', '')}"
Use search results to provide specific product recommendations.
Respond in {lang} language.
"""
        
        return prompt

    def _create_special_intent_prompt(self, state: ConversationState) -> str:
        """Create prompts for special intents using external template files"""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "other")
        user_query = state.get("user_query", "")
        
        if TEST_ENV:
            print(f"🎯 [DEBUG ResponseFormatter] Creating prompt for special intent: {intent}")
        
        # 🆕 SUPPORT intent using template
        if intent == Intent.SUPPORT:
            prompt = load_prompt_template(
                "intent_support",
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # 🆕 BUSINESS intent using template
        if intent == Intent.BUSINESS:
            prompt = load_prompt_template(
                "intent_business",
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # 🆕 PURCHASE inquiry using template
        if intent == Intent.PURCHASE_INQUIRY:
            purchase_product = state.get("purchase_product", "")
            product_url = ""
            
            # Try to find product in search results
            if state.get("search_results"):
                for result in state["search_results"]:
                    if result.get('metadata', {}).get('product_name', '').lower() == purchase_product.lower():
                        product_url = self._get_product_url(result, lang)
                        break
            
            prompt = load_prompt_template(
                "intent_purchase",
                user_query=user_query,
                language=lang,
                purchase_product=purchase_product,
                product_url=product_url
            )
            if prompt:
                return prompt
        
        # 🆕 GREETING intent using template
        if intent == Intent.GREETING:
            prompt = load_prompt_template(
                "intent_greeting",
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # 🆕 COMPETITOR intent using template
        if intent == Intent.COMPETITOR:
            prompt = load_prompt_template(
                "intent_competitor",
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # 🆕 CENSORED intent using template
        if intent == Intent.CENSORED:
            prompt = load_prompt_template(
                "intent_censored",
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # 🆕 OTHER intent using template
        if intent == Intent.OTHER:
            prompt = load_prompt_template(
                "intent_others",
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # 🚫 FALLBACK for unknown intents or template failures
        if TEST_ENV:
            print(f"⚠️ [ResponseFormatter] Using fallback for intent: {intent}")
        
        return f"""
You are AF AI, Aquaforest's passionate assistant.
User said: "{user_query}"

Respond helpfully and professionally in {lang} language.
Show enthusiasm for reef-keeping while addressing their needs.
"""

    def _generate_special_intent_response(self, state: ConversationState) -> str:
        """🆕 Generate response for special intents using per-node configured model"""
        prompt = self._create_special_intent_prompt(state)
        intent = state.get("intent", "other")
        
        if TEST_ENV:
            print(f"💰 [DEBUG ResponseFormatter] Using per-node model for special intent: {intent}")
        
        try:
            # Use configured model for simple intents
            client, model_name = create_response_formatter_client()
            response = client.chat.completions.create(
                model=model_name,  # 🆕 Use per-node configured model
                temperature=OPENAI_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ResponseFormatter] Error with special intent: {e}")
            return self._handle_error(e, state)

    def _format_business_recommendations_context(self, recommendations: List[Dict]) -> str:
        """🚀 Format business recommendations into context"""
        if not recommendations:
            return ""
            
        context_lines = ["--- ENHANCED BUSINESS RECOMMENDATIONS ---"]
        
        for rec in recommendations:
            rec_type = rec.get("type", "unknown")
            
            if rec_type == "competitor_alternative":
                context_lines.append(f"🏢 COMPETITOR ALTERNATIVE: {rec['competitor']} → {rec['af_alternative']}")
                context_lines.append(f"   Message: {rec['message']}")
                
            elif rec_type == "setup_phase":
                phase_priority = "HIGH PRIORITY" if rec.get("priority") else "STANDARD"
                context_lines.append(f"📋 SETUP PHASE [{phase_priority}]: {rec['phase']}")
                context_lines.append(f"   Duration: {rec['duration']}")
                products_str = ", ".join([f"{cat}: {', '.join(prods)}" for cat, prods in rec['products'].items()])
                context_lines.append(f"   Products: {products_str}")
                
            elif rec_type == "use_case_priority":
                context_lines.append(f"🎯 USE CASE PRIORITY: {rec['use_case']}")
                context_lines.append(f"   Priority products: {', '.join(rec['priority_products'])}")
                if rec.get("timeline"):
                    context_lines.append(f"   Timeline: {rec['timeline']}")
                    
            elif rec_type == "missing_alert":
                alert_info = rec.get('note', 'Missing essential product')
                context_lines.append(f"⚠️ MISSING PRODUCT ALERT: {alert_info}")
                if 'products' in rec:
                    context_lines.append(f"   Essential products: {', '.join(rec['products'])}")
        
        context_lines.append("---")
        return "\n".join(context_lines)
    
    def _format_competitor_context(self, competitor_info: Dict) -> str:
        """Format competitor context with DYNAMIC negative instructions for ALL detected competitors"""
        context_lines = ["--- COMPETITOR CONTEXT ---"]
        
        detected_competitors = []
        alternatives_mapping = []
        
        for comp in competitor_info.get("competitors", []):
            comp_name = comp["name"]
            detected_competitors.append(comp_name)
            context_lines.append(f"🏢 DETECTED COMPETITOR: {comp_name}")
            
            # Check if we have AF alternative
            af_alternatives = competitor_info.get("af_alternatives", {})
            if comp_name in af_alternatives:
                alt = af_alternatives[comp_name]
                context_lines.append(f"   → REDIRECT TO: {alt}")
                alternatives_mapping.append(f"{comp_name} → {alt}")
            else:
                context_lines.append(f"   → NO SPECIFIC AF ALTERNATIVE (do not praise)")
        
        # 🚨 DYNAMIC CRITICAL RULES for ALL detected competitors
        if detected_competitors:
            context_lines.append("")
            context_lines.append("🚨 CRITICAL COMPETITOR RULES:")
            context_lines.append(f"- NEVER praise these products: {', '.join(detected_competitors)}")
            context_lines.append(f"- NEVER write 'excellent choice', 'good decision', '{detected_competitors[0]} is great' about competitors")
            
            if alternatives_mapping:
                context_lines.append("- ALWAYS redirect using these mappings:")
                for mapping in alternatives_mapping:
                    context_lines.append(f"  * While {mapping.split(' → ')[0]} is mentioned, I recommend our {mapping.split(' → ')[1]}")
            
            context_lines.append("- Focus on AF alternatives' benefits, not competitor praise")
            context_lines.append("- If no AF alternative specified, simply avoid praising competitor")
            context_lines.append("END CRITICAL RULES")
        
        context_lines.append("---")
        return "\n".join(context_lines)
    
    def _format_scenario_context(self, scenario_info: Dict) -> str:
        """🚀 Format scenario context"""
        context_lines = ["--- SCENARIO CONTEXT ---"]
        
        context_lines.append(f"📋 DETECTED SCENARIO: {scenario_info['name']}")
        
        priority_order = scenario_info.get("priority_order", [])
        if priority_order:
            context_lines.append(f"⚡ PRIORITY ORDER: {' → '.join(priority_order)}")
        
        mandatory_categories = scenario_info.get("mandatory_categories", [])
        if mandatory_categories:
            context_lines.append(f"🎯 MANDATORY CATEGORIES: {', '.join(mandatory_categories)}")
        
        context_lines.append("---")
        return "\n".join(context_lines)
    
    def _format_use_case_context(self, use_case_info: Dict) -> str:
        """🚀 Format use case context"""
        context_lines = ["--- USE CASE CONTEXT ---"]
        
        context_lines.append(f"🎯 IDENTIFIED USE CASE: {use_case_info['name']}")
        
        matching_keywords = use_case_info.get("matching_keywords", [])
        if matching_keywords:
            context_lines.append(f"🔍 MATCHING KEYWORDS: {', '.join(matching_keywords)}")
        
        priority_products = use_case_info.get("priority_products", [])
        if priority_products:
            context_lines.append(f"⭐ PRIORITY PRODUCTS: {', '.join(priority_products)}")
        
        timeline = use_case_info.get("timeline", "")
        if timeline:
            context_lines.append(f"⏱️ TIMELINE: {timeline}")
        
        context_lines.append("---")
        return "\n".join(context_lines)

    def format_response(self, state: ConversationState) -> ConversationState:
        try:
            if TEST_ENV:
                print(f"\n🔨 [DEBUG ResponseFormatter] Generating final response...")
            
            # 🆕 Check if this is a special intent - use cheaper model
            intent = state.get("intent", "product_query")
            if intent in [Intent.GREETING, Intent.BUSINESS, Intent.PURCHASE_INQUIRY, 
                         Intent.COMPETITOR, Intent.CENSORED, Intent.SUPPORT, Intent.OTHER]:
                if TEST_ENV:
                    print(f"🎭 [DEBUG ResponseFormatter] Using cheaper model for special intent: {intent}")
                state["final_response"] = self._generate_special_intent_response(state)
            else:
                # Use expensive model for complex product queries
                if TEST_ENV:
                    print(f"🧠 [DEBUG ResponseFormatter] Using complex model for intent: {intent}")
                prompt = self._create_universal_prompt(state)
                response = self.client.chat.completions.create(
                    model=self.model_name,  # 🔥 Expensive model for complex tasks
                    temperature=OPENAI_TEMPERATURE,
                    messages=[{"role": "system", "content": prompt}]
                )
                state["final_response"] = response.choices[0].message.content
            
            if TEST_ENV:
                print(f"✅ [DEBUG ResponseFormatter] Response generated ({len(state['final_response'])} characters)")
            
            # Cache metadata for follow-ups (only for product queries)
            if state.get("search_results") and intent not in [Intent.GREETING, Intent.BUSINESS, Intent.SUPPORT, Intent.OTHER, Intent.CENSORED, Intent.COMPETITOR, Intent.PURCHASE_INQUIRY]:
                # Cache more results if category request
                cache_size = 10 if state.get("requested_category") else 5
                state["context_cache"] = [r['metadata'] for r in state["search_results"][:cache_size]]
                if TEST_ENV:
                    print(f"💾 [DEBUG ResponseFormatter] Cached metadata for {len(state['context_cache'])} results")
                    
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ResponseFormatter] Formatting error: {e}")
            state["final_response"] = self._handle_error(e, state)
        
        return state
    
    def _handle_error(self, error: Exception, state: ConversationState) -> str:
        """Enhanced error handling for formatting failures"""
        debug_print(f"❌ [ResponseFormatter] Error during formatting: {str(error)}")
        
        # Get user language for appropriate error response
        language = state.get("detected_language", "en")
        
        if language == "pl":
            return "Przepraszam, wystąpił błąd podczas przetwarzania. Spróbuj ponownie lub jeśli problem się powtarza, możesz skontaktować się z naszym supportem."
        else:
            return "Sorry, an error occurred during processing. Please try again or contact our support if the problem persists."


# Follow-up handling functions
def _create_follow_up_prompt(state: ConversationState) -> str:
    """Creates a prompt to answer a follow-up question using cached context and external template"""
    lang = state.get("detected_language", "en")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    if TEST_ENV:
        print(f"\n🔄 [DEBUG Follow-up] Creating prompt for follow-up in language: {lang}")
        print(f"📦 [DEBUG Follow-up] Cache contains {len(state.get('context_cache', []))} items")
    
    # Check if follow-up is about dosage
    is_dosage_followup = any(word in state["user_query"].lower() 
                           for word in ["dawkowanie", "ile", "how much", "dosage", "oblicz"])
    
    # Format cached metadata
    cached_full_metadata = []
    if state.get("context_cache"):
        for i, meta in enumerate(state.get("context_cache", [])):
            metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
            cached_full_metadata.append(f"""Cached Item {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
    
    cached_context_formatted = "".join(cached_full_metadata)
    
    dosage_followup_note = "The user might be asking about dosage. Use dosage information from cached metadata if available." if is_dosage_followup else ""

    # Try to load prompt from template
    prompt = load_prompt_template(
        "response_followup",
        chat_history_formatted=chat_history_formatted,
        user_query=state['user_query'],
        cached_context_formatted=cached_context_formatted,
        dosage_followup_note=dosage_followup_note,
        language=lang
    )
    
    # Fallback to simple prompt if template fails
    if not prompt:
        if TEST_ENV:
            print("⚠️ [Follow-up] Using fallback hardcoded prompt")
        prompt = f"""
Answer follow-up question: "{state['user_query']}"
Based on conversation history and cached product information.
Respond in {lang} language.
"""
    
    return prompt

def format_final_response(state: ConversationState) -> ConversationState:
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def escalate_to_human(state: ConversationState) -> ConversationState:
    """🆕 UPDATED: Escalate without automatically adding support contact"""
    if TEST_ENV:
        print(f"\n🚨 [DEBUG Escalate] Escalating due to routing decision")
    state["escalate"] = True
    
    # Create a custom prompt for escalation that doesn't include contact info
    lang = state.get("detected_language", "en")
    user_query = state.get("user_query", "")
    
    escalation_prompt = f"""
You are AF AI. This query needs special handling.
User asked: "{user_query}"

Generate a helpful response that:
1. Acknowledges you found some information but it might not be exactly what they're looking for
2. Share what relevant information you DID find (if any)
3. Suggest they rephrase their question or provide more details
4. DO NOT automatically provide support contact information unless they specifically ask for it

Be helpful and apologetic about not finding perfect matches.

Respond in {lang} language.
"""
    
    try:
        client, model_name = create_response_formatter_client()
        response = client.chat.completions.create(
            model=model_name,
            temperature=OPENAI_TEMPERATURE,
            messages=[{"role": "system", "content": escalation_prompt}]
        )
        state["final_response"] = response.choices[0].message.content
    except Exception as e:
        if TEST_ENV:
            print(f"❌ [DEBUG Escalate] Error generating escalation response: {e}")
        formatter = ResponseFormatter()
        state["final_response"] = formatter._handle_error(e, state)
    
    return state

def handle_follow_up(state: ConversationState) -> ConversationState:
    """Handle follow-up questions using cached metadata"""
    if TEST_ENV:
        print(f"\n🔄 [DEBUG Follow-up Handler] Handling follow-up question with cache")
        
    try:
        client, model_name = create_response_formatter_client()
        prompt = _create_follow_up_prompt(state)
        response = client.chat.completions.create(
            model=model_name,
            temperature=OPENAI_TEMPERATURE,
            messages=[{"role": "system", "content": prompt}]
        )
        state["final_response"] = response.choices[0].message.content
        
        if TEST_ENV:
            print(f"✅ [DEBUG Follow-up Handler] Response generated using cache")
            
    except Exception as e:
        if TEST_ENV:
            print(f"❌ [DEBUG Follow-up Handler] Follow-up handling error: {e}")
        
        formatter = ResponseFormatter()
        state["final_response"] = formatter._handle_error(e, state)
        
    return state