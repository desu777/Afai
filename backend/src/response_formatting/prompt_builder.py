"""
Prompt Builder Module
Prompt creation logic extracted from response_formatter.py
"""
import json
from typing import Dict, Any
from models import ConversationState, Intent
from config import TEST_ENV
from prompts import load_prompt_template
from calculation_helper import calculation_helper
from .domain_helpers import has_mixed_domains, get_product_url
from .dosage_calculator import DosageCalculator

class PromptBuilder:
    def __init__(self):
        self.dosage_calculator = DosageCalculator()
    
    def create_universal_prompt(self, state: ConversationState) -> str:
        """Create main response prompt with all context"""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "product_query")
        
        if TEST_ENV:
            print(f"\n📝 [DEBUG ResponseFormatter] Formatting response for intent='{intent}', language='{lang}'")
        
        # Handle ICP analysis with specialized prompt
        if intent == Intent.ANALYZE_ICP:
            if TEST_ENV:
                print(f"🔬 [DEBUG ResponseFormatter] Using specialized ICP analysis prompt")
            return self.create_icp_analysis_prompt(state)
        
        # Handle special intents first
        if intent in [Intent.GREETING, Intent.BUSINESS, 
                     Intent.PURCHASE_INQUIRY, Intent.COMPETITOR, Intent.CENSORED, Intent.SUPPORT, Intent.OTHER]:
            if TEST_ENV:
                print(f"🎭 [DEBUG ResponseFormatter] Handling special intent: {intent}")
            return self.create_special_intent_prompt(state)
        
        # Format conversation history
        chat_history_formatted = ""
        if state.get("chat_history"):
            chat_history_formatted = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in state.get("chat_history", [])[-6:]
            ])
        
        # Check for mixed domains
        has_mixed = has_mixed_domains(state.get("search_results", []))
        domain_not_specified = not state.get("domain_filter")
        
        # Check for dosage query
        is_dosage_query = self.dosage_calculator.detect_dosage_query(state.get("user_query", ""))
        aquarium_volume = None
        if is_dosage_query:
            aquarium_volume = calculation_helper.extract_volume_from_query(state.get("user_query", ""))
            if TEST_ENV:
                print(f"💊 [DEBUG ResponseFormatter] Dosage query detected!")
                print(f"📏 [DEBUG ResponseFormatter] Extracted volume: {aquarium_volume}L" if aquarium_volume else "📏 [DEBUG ResponseFormatter] No volume extracted")
        
        # Build context sections
        category_context = self._build_category_context(state)
        problem_context = self._build_problem_context(state)
        balling_context = self._build_balling_context(state)
        business_context = self._build_business_context(state)
        competitor_context = self._build_competitor_context(state)
        scenario_context = self._build_scenario_context(state)
        use_case_context = self._build_use_case_context(state)
        
        # Process search results
        formatted_all_results, dosage_context = self._process_search_results(
            state, is_dosage_query, aquarium_volume
        )
        
        # Try to load prompt from template
        prompt = load_prompt_template(
            "response_formatting",
            access_level=state.get("access_level"),
            language=lang,
            chat_history_formatted=chat_history_formatted,
            user_query=state.get('user_query', ''),
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

    def create_special_intent_prompt(self, state: ConversationState) -> str:
        """Create prompts for special intents using external template files"""
        lang = state.get("detected_language", "en")
        intent = state.get("intent", "other")
        user_query = state.get("user_query", "")
        
        if TEST_ENV:
            print(f"🎯 [DEBUG ResponseFormatter] Creating prompt for special intent: {intent}")
        
        # SUPPORT intent using template
        if intent == Intent.SUPPORT:
            prompt = load_prompt_template(
                "intent_support",
                access_level=state.get("access_level"),
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # BUSINESS intent using template
        if intent == Intent.BUSINESS:
            prompt = load_prompt_template(
                "intent_business",
                access_level=state.get("access_level"),
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # PURCHASE inquiry using template
        if intent == Intent.PURCHASE_INQUIRY:
            purchase_product = state.get("purchase_product", "")
            product_url = ""
            
            # Try to find product in search results
            if state.get("search_results"):
                for result in state["search_results"]:
                    if result.get('metadata', {}).get('product_name', '').lower() == purchase_product.lower():
                        product_url = get_product_url(result, lang)
                        break
            
            prompt = load_prompt_template(
                "intent_purchase",
                access_level=state.get("access_level"),
                user_query=user_query,
                language=lang,
                purchase_product=purchase_product,
                product_url=product_url
            )
            if prompt:
                return prompt
        
        # GREETING intent using template
        if intent == Intent.GREETING:
            prompt = load_prompt_template(
                "intent_greeting",
                access_level=state.get("access_level"),
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # COMPETITOR intent using template
        if intent == Intent.COMPETITOR:
            prompt = load_prompt_template(
                "intent_competitor",
                access_level=state.get("access_level"),
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # CENSORED intent using template
        if intent == Intent.CENSORED:
            prompt = load_prompt_template(
                "intent_censored",
                access_level=state.get("access_level"),
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # OTHER intent using template
        if intent == Intent.OTHER:
            prompt = load_prompt_template(
                "intent_others",
                access_level=state.get("access_level"),
                user_query=user_query,
                language=lang
            )
            if prompt:
                return prompt
        
        # FALLBACK for unknown intents or template failures
        if TEST_ENV:
            print(f"⚠️ [ResponseFormatter] Using fallback for intent: {intent}")
        
        return f"""
You are AF AI, Aquaforest's passionate assistant.
User said: "{user_query}"

Respond helpfully and professionally in {lang} language.
"""

    def create_icp_analysis_prompt(self, state: ConversationState) -> str:
        """Create specialized prompt for ICP analysis using external template"""
        lang = state.get("detected_language", "en")
        user_query = state.get("user_query", "")
        
        if TEST_ENV:
            print(f"🔬 [DEBUG PromptBuilder] Creating ICP analysis prompt")
        
        # Format conversation history
        chat_history_formatted = ""
        if state.get("chat_history"):
            chat_history_formatted = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in state.get("chat_history", [])[-6:]
            ])
        
        # Get ICP analysis data
        icp_analysis = state.get("icp_analysis", "No ICP data available")
        
        # Check for dosage query and extract volume
        is_dosage_query = self.dosage_calculator.detect_dosage_query(user_query)
        aquarium_volume = None
        if is_dosage_query:
            aquarium_volume = calculation_helper.extract_volume_from_query(user_query)
        
        # Build context sections
        business_context = self._build_business_context(state)
        competitor_context = self._build_competitor_context(state)
        
        # Process search results for ICP-specific formatting
        formatted_all_results, dosage_context = self._process_search_results(
            state, is_dosage_query, aquarium_volume
        )
        
        # Calculate confidence for ICP analysis
        confidence = state.get("confidence", 0.8)
        
        # Load ICP analysis template
        prompt = load_prompt_template(
            "icp_analysis",
            access_level=state.get("access_level"),
            language=lang,
            chat_history_formatted=chat_history_formatted,
            user_query=user_query,
            icp_analysis=icp_analysis,
            confidence=confidence,
            aquarium_volume=aquarium_volume if aquarium_volume else "Not specified",
            dosage_context=dosage_context,
            business_context=business_context,
            competitor_context=competitor_context,
            formatted_all_results=formatted_all_results
        )
        
        # Fallback if template loading fails
        if not prompt:
            if TEST_ENV:
                print("⚠️ [PromptBuilder] Using fallback for ICP analysis")
            prompt = f"""
You are AF AI, specialized in ICP water test analysis.
Analyze these ICP results: {icp_analysis}
User query: "{user_query}"
Provide expert recommendations for water parameter corrections.
Respond in {lang} language.
"""
        
        if TEST_ENV:
            print(f"✅ [DEBUG PromptBuilder] ICP analysis prompt created ({len(prompt)} characters)")
        
        return prompt

    def _build_category_context(self, state: ConversationState) -> str:
        """Build category context section"""
        if state.get("requested_category") and state.get("category_products"):
            return f"""
--- CATEGORY REQUEST ---
User asked for products in category: {state.get("requested_category")}
Expected products to show: {', '.join(state.get("category_products", []))}
Make sure to present ALL products from this category that were found!
---
"""
        return ""

    def _build_problem_context(self, state: ConversationState) -> str:
        """Build problem-solution context section"""
        if state.get("identified_problem") and state.get("recommended_solutions"):
            return f"""
--- PROBLEM IDENTIFIED ---
Problem: {state.get("identified_problem")}
Recommended solutions: {', '.join(state.get("recommended_solutions", []))}
Focus on these solutions in your response!
---
"""
        return ""

    def _build_balling_context(self, state: ConversationState) -> str:
        """Build balling method context section"""
        if state.get("maintenance_solutions") and state.get("solution_note"):
            return f"""
--- BALLING METHOD NOTE ---
User asked about correcting a single parameter.
Maintenance products suggested: {', '.join(state.get("maintenance_solutions", []))}
IMPORTANT NOTE: {state.get("solution_note", "")}
You MUST mention that Balling/Component products contain multiple elements and are for daily maintenance, not single corrections!
---
"""
        return ""

    def _build_business_context(self, state: ConversationState) -> str:
        """Build business recommendations context"""
        from .context_formatters import format_business_recommendations_context
        if state.get("business_recommendations"):
            return format_business_recommendations_context(state["business_recommendations"])
        return ""

    def _build_competitor_context(self, state: ConversationState) -> str:
        """Build competitor context"""
        from .context_formatters import format_competitor_context
        if state.get("competitor_info"):
            return format_competitor_context(state["competitor_info"])
        return ""

    def _build_scenario_context(self, state: ConversationState) -> str:
        """Build scenario context"""
        from .context_formatters import format_scenario_context
        if state.get("scenario_info"):
            return format_scenario_context(state["scenario_info"])
        return ""

    def _build_use_case_context(self, state: ConversationState) -> str:
        """Build use case context"""
        from .context_formatters import format_use_case_context
        if state.get("use_case_info"):
            return format_use_case_context(state["use_case_info"])
        return ""

    def _process_search_results(self, state: ConversationState, is_dosage_query: bool, aquarium_volume: int) -> tuple:
        """Process search results and prepare dosage calculations"""
        all_results_metadata = []
        dosage_calculations = []
        
        if state.get("search_results"):
            if TEST_ENV:
                print(f"📊 [DEBUG ResponseFormatter] Processing {len(state.get('search_results', []))} results")
            
            # Process results and prepare dosage calculations
            for i, result in enumerate(state["search_results"]):
                meta = result.get('metadata', {})
                
                # Extract dosage info if this is a dosage query
                if is_dosage_query and aquarium_volume:
                    dosage_info = self.dosage_calculator.extract_dosage_info(meta)
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

        return formatted_all_results, dosage_context