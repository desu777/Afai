"""
Decision Applier Module
Applying LLM decisions to conversation state extracted from business_reasoner.py
"""
from typing import Dict
from models import ConversationState
from config import debug_print

class DecisionApplier:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def apply_llm_business_intelligence(self, state: ConversationState, decision: Dict) -> ConversationState:
        """Apply comprehensive LLM decision to conversation state"""
        
        # Store the complete LLM analysis (maintains backward compatibility)
        state["business_analysis"] = {
            "business_interpretation": decision.get("business_interpretation", ""),
            "reasoning_steps": decision.get("reasoning_steps", {}),
            "confidence_level": decision.get("confidence_level", 0.8),
            "llm_based": True,  # Mark as full LLM decision
            
            # Backward compatibility fields
            "product_name_corrections": None,
            "category_requested": None,
            "products_in_category": [],
            "problem_identified": None,
            "solutions_for_problem": [],
            "intent_correction": "same",
            "domain_hint": decision.get("domain_hint", "unknown"),
            "search_enhancement": ", ".join(decision.get("search_keywords", []))
        }
        
        # COMPETITOR HANDLING
        self._apply_competitor_intelligence(state, decision)
        
        # SCENARIO DETECTION AND HANDLING
        self._apply_scenario_intelligence(state, decision)
        
        # USE CASE DETECTION AND HANDLING
        self._apply_use_case_intelligence(state, decision)
        
        # PRODUCT RECOMMENDATIONS - CRITICAL for Pinecone search
        self._apply_product_recommendations(state, decision)
        
        # COMPREHENSIVE BUSINESS RECOMMENDATIONS
        self._apply_business_recommendations(state, decision)
        
        return state

    def _apply_competitor_intelligence(self, state: ConversationState, decision: Dict):
        """Apply competitor detection and handling"""
        competitors = decision.get("detected_competitors", [])
        competitor_alternatives = decision.get("competitor_alternatives", {})
        if competitors:
            state["competitor_info"] = {
                "competitors": [{"name": comp, "category": "llm_detected", "original": comp.lower()} for comp in competitors],
                "af_alternatives": competitor_alternatives,
                "response_templates": []
            }
            debug_print(f"🏢 [BusinessReasoner] LLM detected competitors: {competitors}")
            debug_print(f"🔄 [BusinessReasoner] AF alternatives: {competitor_alternatives}")

    def _apply_scenario_intelligence(self, state: ConversationState, decision: Dict):
        """Apply scenario detection and handling"""
        scenario = decision.get("detected_scenario")
        if scenario and scenario != "null":
            scenario_data = self.data_loader.scenarios_data.get("tank_setup_scenarios", {}).get(scenario, {})
            state["scenario_info"] = {
                "name": scenario,
                "data": scenario_data,
                "priority_order": scenario_data.get("priority_order", []),
                "mandatory_categories": scenario_data.get("mandatory_categories", [])
            }
            debug_print(f"📋 [BusinessReasoner] LLM detected scenario: {scenario}")

    def _apply_use_case_intelligence(self, state: ConversationState, decision: Dict):
        """Apply use case detection and handling"""
        use_case = decision.get("detected_use_case") 
        if use_case and use_case != "null":
            use_case_data = self.data_loader.use_cases_data.get("use_cases", {}).get(use_case, {})
            state["use_case_info"] = {
                "name": use_case,
                "data": use_case_data,
                "matching_keywords": [],
                "priority_products": decision.get("priority_products", []),
                "timeline": use_case_data.get("timeline", "")
            }
            debug_print(f"🎯 [BusinessReasoner] LLM detected use case: {use_case}")

    def _apply_product_recommendations(self, state: ConversationState, decision: Dict):
        """Apply product recommendations - CRITICAL for Pinecone search"""
        product_recommendations = decision.get("product_recommendations", {})
        
        # INTELLIGENT CATEGORIZATION: Extract all products from categories
        all_products = []
        for category, products in product_recommendations.items():
            if isinstance(products, list):
                all_products.extend(products)
        
        # Backward compatibility: also check legacy priority_products field
        legacy_products = decision.get("priority_products", [])
        if legacy_products:
            all_products.extend(legacy_products)
        
        if all_products:
            state["af_alternatives_to_search"] = all_products
            debug_print(f"🧠 [BusinessReasoner] LLM selected {len(all_products)} products via intelligent categorization")
        
            # Store categorized structure for Response Formatter
            state["product_recommendations"] = product_recommendations
            debug_print(f"📊 [BusinessReasoner] Categorized into {len(product_recommendations)} categories: {list(product_recommendations.keys())}")
        
            # Set first product as main correction for backward compatibility
            if all_products:
                state["business_analysis"]["product_name_corrections"] = all_products[0]
        else:
            debug_print(f"⚠️ [BusinessReasoner] No products found by LLM analysis")

    def _apply_business_recommendations(self, state: ConversationState, decision: Dict):
        """Apply comprehensive business recommendations"""
        recommendations = []
        product_recommendations = decision.get("product_recommendations", {})
        competitors = decision.get("detected_competitors", [])
        
        # Categorized products recommendation
        if product_recommendations:
            recommendations.append({
                "type": "categorized_products",
                "categories": product_recommendations,
                "reasoning": decision.get("reasoning_steps", {}).get("categorization_logic", "LLM-organized into logical categories based on comprehensive analysis")
            })
        
        # Alternative products (ONLY for competitor situations)
        alternative_products = decision.get("alternative_products", [])
        if alternative_products and competitors:  # Only if competitors detected
            recommendations.append({
                "type": "competitor_alternatives",
                "alternatives": alternative_products,
                "reasoning": "LLM-detected competitor alternatives based on comprehensive mapping knowledge"
            })
        
        # Setup phase recommendations
        setup_phases = decision.get("setup_phases", [])
        if setup_phases:
            for phase in setup_phases:
                recommendations.append({
                    "type": "setup_phase",
                    "phase": phase.get("name", "Unknown Phase"),
                    "duration": phase.get("duration", "Variable"),
                    "products": phase.get("products", {}),
                    "priority": phase.get("priority", False)
                })
        
        # Use case priority recommendations
        use_case_priorities = decision.get("use_case_priorities", [])
        if use_case_priorities:
            for priority in use_case_priorities:
                recommendations.append({
                    "type": "use_case_priority",
                    "use_case": priority.get("name", "Unknown"),
                    "priority_products": priority.get("products", []),
                    "timeline": priority.get("timeline", "")
                })
        
        # Missing product alerts
        missing_products = decision.get("missing_product_alerts", [])
        if missing_products:
            for alert in missing_products:
                recommendations.append({
                    "type": "missing_alert",
                    "note": alert.get("note", "Missing essential product"),
                    "products": alert.get("products", [])
                })
        
        # Enhanced business context
        business_context = decision.get("business_context", {})
        if business_context:
            recommendations.append({
                "type": "business_context",
                "market_position": business_context.get("market_position", ""),
                "competitive_advantage": business_context.get("competitive_advantage", ""),
                "target_audience": business_context.get("target_audience", "")
            })
        
        # Store all recommendations
        if recommendations:
            state["business_recommendations"] = recommendations
            debug_print(f"💼 [BusinessReasoner] Applied {len(recommendations)} business recommendations")

    def apply_fallback_analysis(self, state: ConversationState) -> ConversationState:
        """Fallback analysis when LLM fails"""
        debug_print("🔄 [BusinessReasoner] Using fallback analysis")
        
        # Simple fallback business analysis
        state["business_analysis"] = {
            "business_interpretation": f"Standard inquiry about: {state.get('user_query', '')[:100]}",
            "product_name_corrections": None,
            "category_requested": None,
            "products_in_category": [],
            "problem_identified": None,
            "solutions_for_problem": [],
            "intent_correction": "same",
            "domain_hint": "unknown",
            "search_enhancement": "",
            "confidence_level": 0.6,
            "llm_based": False,
            "reasoning_steps": {}
        }
        
        return state