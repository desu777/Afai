"""
Response Formatter Module - Refactored VERSION 8.0
Main ResponseFormatter class coordinating specialized modules
"""
import time
from typing import Dict, Any
from models import ConversationState, Intent
from config import TEST_ENV, RESPONSE_FORMATTER_TEMPERATURE, debug_print
from llm_client_factory import create_response_formatter_client
from prompt_saver import log_prompt_if_enabled

from .dosage_calculator import DosageCalculator
from .prompt_builder import PromptBuilder
from .cache_manager import CacheManager

class ResponseFormatter:
    def __init__(self):
        self.client, self.model_name = create_response_formatter_client()
        
        if TEST_ENV:
            debug_print(f"[LOG] RF Init: OpenRouter per-node")
            debug_print(f"[TARGET] RF model: {self.model_name}")
        
        # Initialize specialized components
        self.dosage_calculator = DosageCalculator()
        self.prompt_builder = PromptBuilder()
        self.cache_manager = CacheManager(self.client, self.model_name)
    
    def format_response(self, state: ConversationState) -> ConversationState:
        """Main response formatting method"""
        try:
            if TEST_ENV:
                print(f"\n[CONFIG] RF generating response...")
            
            # PRIORITY: Check if this is a follow-up with cache response data
            if state.get("cache_response_data"):
                if TEST_ENV:
                    print(f"[PROCESS] RF using cache for follow-up")
                return self.cache_manager.generate_cache_based_response(state)
            
            # Check if this is a special intent - use cheaper model
            intent = state.get("intent", "product_query")
            if intent in [Intent.GREETING, Intent.BUSINESS, Intent.PURCHASE_INQUIRY, 
                         Intent.COMPETITOR, Intent.CENSORED, Intent.SUPPORT, Intent.OTHER]:
                if TEST_ENV:
                    print(f"[MASK] RF cheap model: {intent}")
                state["final_response"] = self._generate_special_intent_response(state)
            else:
                # Use expensive model for complex product queries
                if TEST_ENV:
                    print(f"[AI] RF complex model: {intent}")
                prompt = self.prompt_builder.create_universal_prompt(state)
                
                # Log prompt to file if enabled
                log_prompt_if_enabled("response_formatter_complex", prompt, state, self.model_name, RESPONSE_FORMATTER_TEMPERATURE)
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    temperature=RESPONSE_FORMATTER_TEMPERATURE,
                    messages=[{"role": "system", "content": prompt}]
                )
                state["final_response"] = response.choices[0].message.content
            
            if TEST_ENV:
                print(f"[OK] RF response: {len(state['final_response'])} chars")
            
            # Cache metadata for follow-ups (only for product queries)
            if state.get("search_results") and intent not in [Intent.GREETING, Intent.BUSINESS, Intent.SUPPORT, Intent.OTHER, Intent.CENSORED, Intent.COMPETITOR, Intent.PURCHASE_INQUIRY]:
                # Cache ALL results (removed cache_size limit)
                state["context_cache"] = [r['metadata'] for r in state["search_results"]]
                if TEST_ENV:
                    print(f"[CACHE] RF cached: {len(state['context_cache'])} results")
                
                # Create extended cache for session-based follow-ups
                state["extended_cache"] = self.cache_manager.create_extended_cache(state)
                if TEST_ENV:
                    print(f"[CACHE] RF extended cache: {len(state['extended_cache'])} sections")
                
                # Save extended cache to SessionManager
                if state.get("session_id"):
                    from session_manager import get_session_manager
                    session_manager = get_session_manager()
                    session_manager.update_session_cache(state["session_id"], state["extended_cache"])
                    if TEST_ENV:
                        print(f"[CACHE] RF saved to session: {state['session_id']}")
                    
        except Exception as e:
            if TEST_ENV:
                print(f"[ERROR] RF formatting: {str(e)[:30]}")
            state["final_response"] = self._handle_error(e, state)
        
        return state

    def _generate_special_intent_response(self, state: ConversationState) -> str:
        """Generate response for special intents using prompt builder"""
        prompt = self.prompt_builder.create_special_intent_prompt(state)
        
        # Log prompt to file if enabled
        log_prompt_if_enabled("response_formatter_special", prompt, state, self.model_name, RESPONSE_FORMATTER_TEMPERATURE)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=RESPONSE_FORMATTER_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            if TEST_ENV:
                print(f"[ERROR] RF special intent: {str(e)[:30]}")
            return self._handle_error(e, state)

    def _handle_error(self, error: Exception, state: ConversationState) -> str:
        """Handle formatting errors"""
        lang = state.get("detected_language", "en")
        
        if TEST_ENV:
            debug_print(f"[ERROR] RF error: {str(error)[:30]}")
        
        if lang == "pl":
            return "Przepraszam, wystąpił problem z przetwarzaniem Twojego zapytania. Spróbuj ponownie lub skontaktuj się z pomocą techniczną."
        else:
            return "I apologize, there was an issue processing your request. Please try again or contact our support team."

# Compatibility functions for external modules
def format_final_response(state: ConversationState) -> ConversationState:
    """Main entry point for response formatting"""
    formatter = ResponseFormatter()
    return formatter.format_response(state)