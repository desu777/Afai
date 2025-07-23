"""
Business Reasoner Module - Refactored VERSION 6.0
Main BusinessReasoner class coordinating specialized modules
Uses configured provider (Vertex AI) with OpenRouter fallback
"""
from typing import Dict
from models import ConversationState, Intent
from config import TEST_ENV, debug_print, BUSINESS_REASONER_TEMPERATURE, LLM_PROVIDER
from llm_client_factory import create_business_reasoner_client

from .data_loader import DataLoader
from .llm_analyzer import LLMAnalyzer
from .decision_applier import DecisionApplier

class BusinessReasoner:
    """
    Complete LLM-based business intelligence with primary provider + fallback system
    Maintains same API for backward compatibility
    """
    def __init__(self):
        # Primary provider + fallback system
        self.client, self.model_name = self._create_client_with_fallback()
        
        if TEST_ENV:
            debug_print(f"[BRAIN] BusinessReasoner ready: {self.model_name}")
        
        # Initialize specialized components
        self.data_loader = DataLoader()
        self.llm_analyzer = LLMAnalyzer(self.client, self.model_name, self.data_loader)
        self.decision_applier = DecisionApplier(self.data_loader)
    
    def _create_client_with_fallback(self):
        """Create client with primary provider + OpenRouter fallback"""
        try:
            if LLM_PROVIDER == "gemini":
                # Try Gemini as primary
                from gemini_client_factory import VertexAIClientFactory
                client, model_name = VertexAIClientFactory.create_client("business_reasoner")
                if TEST_ENV:
                    debug_print(f"[>] Primary gemini: {model_name}")
                return client, model_name
            else:
                # Try OpenRouter as primary
                client, model_name = create_business_reasoner_client()
                if TEST_ENV:
                    debug_print(f"[>] Primary openrouter: {model_name}")
                return client, model_name
        except Exception as e:
            if TEST_ENV:
                debug_print(f"[!] Primary failed: {str(e)[:50]}")
            
        # Fallback to OpenRouter always
        try:
            client, model_name = create_business_reasoner_client()
            if TEST_ENV:
                debug_print(f"[RTY] Fallback openrouter: {model_name}")
            return client, model_name
        except Exception as e:
            if TEST_ENV:
                debug_print(f"[X] Fallback failed: {str(e)[:50]}")
            raise e

    def analyze(self, state: ConversationState) -> ConversationState:
        """
        Main analysis method - comprehensive LLM-based business intelligence
        """
        try:
            if TEST_ENV:
                debug_print(f"[BRAIN] Analyzing: {state.get('user_query', '')[:50]}...")
            
            # Full LLM analysis using comprehensive mapping data
            decision = self.llm_analyzer.analyze_with_full_llm(state)
            
            if decision:
                # Apply comprehensive LLM intelligence to state
                state = self.decision_applier.apply_llm_business_intelligence(state, decision)
            else:
                # Fallback to simple analysis
                state = self.decision_applier.apply_fallback_analysis(state)
            
            if TEST_ENV:
                debug_print(f"[OK] Analysis complete: {state.get('intent', 'unknown')}")
            
            return state
            
        except Exception as e:
            debug_print(f"[X] Analysis error: {e}")
            return self.decision_applier.apply_fallback_analysis(state)


    def _validate_product_exists(self, product_name: str) -> bool:
        """Validate if product exists in knowledge base"""
        return self.data_loader.validate_product_exists(product_name)

# Compatibility function for external modules
def business_reasoner(state: ConversationState) -> ConversationState:
    """Main entry point for business reasoning"""
    reasoner = BusinessReasoner()
    return reasoner.analyze(state)