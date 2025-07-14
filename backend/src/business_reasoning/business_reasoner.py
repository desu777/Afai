"""
Business Reasoner Module - Refactored VERSION 6.0
Main BusinessReasoner class coordinating specialized modules
"""
import re
from typing import Dict
from models import ConversationState, Intent
from config import TEST_ENV, debug_print
from icp_scraper import ICPScraper
from llm_client_factory import create_business_reasoner_client

from .data_loader import DataLoader
from .llm_analyzer import LLMAnalyzer
from .decision_applier import DecisionApplier

class BusinessReasoner:
    """
    Complete LLM-based business intelligence with OpenRouter per-node configuration
    Maintains same API for backward compatibility
    """
    def __init__(self):
        self.client, self.model_name = create_business_reasoner_client()
        
        if TEST_ENV:
            debug_print(f"🧠 [BusinessReasoner] Initialized with model: {self.model_name}")
        
        self.icp_scraper = ICPScraper()
        
        # Initialize specialized components
        self.data_loader = DataLoader()
        self.llm_analyzer = LLMAnalyzer(self.client, self.model_name, self.data_loader)
        self.decision_applier = DecisionApplier(self.data_loader)

    def analyze(self, state: ConversationState) -> ConversationState:
        """
        Main analysis method - comprehensive LLM-based business intelligence
        """
        try:
            if TEST_ENV:
                debug_print(f"\n🧠 [BusinessReasoner] Analyzing: {state.get('user_query', '')[:50]}...")
            
            # Handle ICP URLs - enhance query with scraped data
            enhanced_query = self._handle_icp_enhancement(state)
            if enhanced_query != state.get('user_query', ''):
                state['user_query'] = enhanced_query
                debug_print(f"🔗 [BusinessReasoner] Enhanced query with ICP data")
            
            # Full LLM analysis using comprehensive mapping data
            decision = self.llm_analyzer.analyze_with_full_llm(state)
            
            if decision:
                # Apply comprehensive LLM intelligence to state
                state = self.decision_applier.apply_llm_business_intelligence(state, decision)
            else:
                # Fallback to simple analysis
                state = self.decision_applier.apply_fallback_analysis(state)
            
            if TEST_ENV:
                debug_print(f"✅ [BusinessReasoner] Business analysis completed for intent: {state.get('intent', 'unknown')}")
            
            return state
            
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Analysis error: {e}")
            return self.decision_applier.apply_fallback_analysis(state)

    def _handle_icp_enhancement(self, state: ConversationState) -> str:
        """Handle ICP URL enhancement if detected"""
        user_query = state.get('user_query', '')
        
        # Check for ICP URL pattern (updated for aquaforestlab.com)
        icp_url_pattern = r'https?://(?:www\.)?(?:aquaforestlab\.com|icpchem\.com|icp-test\.com|test\.icp-test\.com)[^\s]*'
        icp_match = re.search(icp_url_pattern, user_query, re.IGNORECASE)
        
        if icp_match:
            icp_url = icp_match.group(0)
            debug_print(f"🔗 [BusinessReasoner] ICP URL detected: {icp_url}")
            
            # Use ICPScraper to get enhanced query
            enhanced_query = self.icp_scraper.enhance_query_with_icp_data(user_query, icp_url)
            return enhanced_query
        
        return user_query

    def _validate_product_exists(self, product_name: str) -> bool:
        """Validate if product exists in knowledge base"""
        return self.data_loader.validate_product_exists(product_name)

# Compatibility function for external modules
def business_reasoner(state: ConversationState) -> ConversationState:
    """Main entry point for business reasoning"""
    reasoner = BusinessReasoner()
    return reasoner.analyze(state)