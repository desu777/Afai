"""
Cache Manager Module
Extended cache operations and cache-based response generation
"""
import time
from typing import Dict, Any
from models import ConversationState
from config import TEST_ENV, RESPONSE_FORMATTER_TEMPERATURE, debug_print
from prompts import load_prompt_template
from prompt_saver import log_prompt_if_enabled

class CacheManager:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name
    
    def create_extended_cache(self, state: ConversationState) -> Dict[str, Any]:
        """Create extended cache with metadata, responses, and conversation context"""
        extended_cache = {
            "metadata": [],           # Zachowujemy dla kompatybilności
            "product_cards_xml": [],  # NOWE: Pełne XML PRODUCT_CARD
            "knowledge_xml": [],      # NOWE: Pełne XML AQUAFOREST_KNOWLEDGE
            "model_responses": [],
            "conversation_context": {},
            "user_query": state.get("user_query", ""),
            "timestamp": time.time()
        }
        
        # Import XML transformer
        from response_formatting.xml_transformer import XMLMetadataTransformer
        
        # Transform and save complete XML data
        if state.get("search_results"):
            for result in state["search_results"]:
                meta = result['metadata']
                extended_cache["metadata"].append(meta)  # Dla kompatybilności
                
                # Generate and save XML content
                xml_content = XMLMetadataTransformer.transform_metadata(meta)
                if "<PRODUCT_CARD>" in xml_content:
                    extended_cache["product_cards_xml"].append(xml_content)
                elif "<AQUAFOREST_KNOWLEDGE>" in xml_content:
                    extended_cache["knowledge_xml"].append(xml_content)
        
        # Add model responses from chat history
        if state.get("chat_history"):
            extended_cache["model_responses"] = [
                msg["content"] for msg in state["chat_history"][-6:] 
                if msg.get("role") == "assistant"
            ]
        
        # Add current response
        if state.get("final_response"):
            extended_cache["model_responses"].append(state["final_response"])
        
        # Add conversation context
        context_fields = [
            "intent", "detected_language", "requested_category", "domain_filter",
            "identified_problem", "business_analysis", "competitor_info",
            "scenario_info", "use_case_info", "business_recommendations"
        ]
        
        for field in context_fields:
            if state.get(field):
                extended_cache["conversation_context"][field] = state[field]
        
        return extended_cache

    def generate_cache_based_response(self, state: ConversationState) -> ConversationState:
        """Generate response for follow-up questions using cached data"""
        try:
            if TEST_ENV:
                print(f"[PROCESS] CM cache-based response")
            
            cached_data = state["cache_response_data"]
            lang = state.get("detected_language", "en")
            user_query = state.get("user_query", "")
            
            # Get complete XML data from cache instead of reconstructing from metadata
            product_cards = cached_data.get("product_cards_xml", [])
            knowledge_cards = cached_data.get("knowledge_xml", [])
            
            # Build full XML context for prompt
            formatted_context = ""
            for card in product_cards[:10]:  # Limit for context size
                formatted_context += card + "\n\n"
            for card in knowledge_cards[:5]:  # Limit knowledge cards
                formatted_context += card + "\n\n"
            
            # Get previous responses for context
            previous_responses = cached_data.get("previous_responses", [])
            context_responses = ""
            if previous_responses:
                # Include ALL previous responses for full context
                for i, resp in enumerate(previous_responses):
                    snippet = resp if len(resp) <= 300 else resp[:300] + "..."
                    context_responses += f"Previous Response {i+1}: {snippet}\n\n"
            
            # Create prompt for cache-based response using external template
            prompt = load_prompt_template(
                "response_followup_cache",
                language=lang,
                user_query=user_query,
                formatted_metadata=formatted_context,  # Using full XML context
                context_responses=context_responses,
                language_upper=lang.upper()
            )
            
            # Fallback prompt if template fails
            if not prompt:
                if TEST_ENV:
                    print("[WARN] CM fallback prompt")
                prompt = f"""
You are AF AI, Aquaforest's assistant. Answer follow-up question based on previous context.

Follow-up question: "{user_query}"

Previous responses context:
{context_responses}

Available product information:
{formatted_context}

Respond in {lang} language, referencing previous conversation naturally.
"""
            
            # Measure LLM response time
            start_time = time.time()
            
            # Generate response using cheaper model for follow-ups
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=RESPONSE_FORMATTER_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            
            # Calculate response time and log performance
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Log performance to console if TEST_ENV enabled
            if TEST_ENV:
                print(f"[LLM_PERF] cache_manager_followup: {response_time_ms:.2f}ms (model: {self.model_name})")
            
            # Update prompt file with response time if SAVE_PROMPT enabled
            from config import SAVE_PROMPT
            if SAVE_PROMPT:
                log_prompt_if_enabled("cache_manager_followup", prompt, state, self.model_name, RESPONSE_FORMATTER_TEMPERATURE, response_time_ms)
            
            state["final_response"] = response.choices[0].message.content
            
            if TEST_ENV:
                print(f"[OK] CM response: {len(state['final_response'])} chars")
                
        except Exception as e:
            if TEST_ENV:
                print(f"[ERROR] CM cache error: {str(e)[:30]}")
            state["final_response"] = self._handle_cache_error(e, state)
            
        return state
    
    def _handle_cache_error(self, error: Exception, state: ConversationState) -> str:
        """Handle errors in cache-based response generation"""
        lang = state.get("detected_language", "en")
        
        if lang == "pl":
            return "Przepraszam, wystąpił problem z przetwarzaniem Twojego pytania. Spróbuj ponownie."
        else:
            return "I apologize, there was an issue processing your follow-up question. Please try again."