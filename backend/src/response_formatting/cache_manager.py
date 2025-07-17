"""
Cache Manager Module
Extended cache operations and cache-based response generation
"""
import time
from typing import Dict, Any
from models import ConversationState
from config import TEST_ENV, OPENAI_TEMPERATURE, debug_print
from prompts import load_prompt_template

class CacheManager:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name
    
    def create_extended_cache(self, state: ConversationState) -> Dict[str, Any]:
        """Create extended cache with metadata, responses, and conversation context"""
        extended_cache = {
            "metadata": [],
            "model_responses": [],
            "conversation_context": {},
            "user_query": state.get("user_query", ""),
            "timestamp": time.time()
        }
        
        # Add ALL metadata from search results (removed cache_size limit)
        if state.get("search_results"):
            extended_cache["metadata"] = [r['metadata'] for r in state["search_results"]]
        
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
                print(f"🔄 [DEBUG ResponseFormatter] Generating cache-based response")
            
            cached_data = state["cache_response_data"]
            lang = state.get("detected_language", "en")
            user_query = state.get("user_query", "")
            
            # Format cached metadata for prompt
            cached_metadata = cached_data.get("metadata", [])
            formatted_metadata = ""
            
            # Include ALL cached metadata items, not just top 5
            for i, meta in enumerate(cached_metadata):
                product_name = meta.get("product_name", "Unknown")
                description = meta.get("full_content_en", meta.get("full_content_pl", ""))
                if len(description) > 200:
                    description = description[:200] + "..."
                url = meta.get("url_pl" if lang == "pl" else "url_en", "")
                
                formatted_metadata += f"""
Product {i+1}: {product_name}
Description: {description}
URL: {url}

"""
            
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
                formatted_metadata=formatted_metadata,
                context_responses=context_responses,
                language_upper=lang.upper()
            )
            
            # Fallback prompt if template fails
            if not prompt:
                if TEST_ENV:
                    print("⚠️ [ResponseFormatter] Using fallback cache-based prompt")
                prompt = f"""
You are AF AI, Aquaforest's assistant. Answer follow-up question based on previous context.

Follow-up question: "{user_query}"

Previous responses context:
{context_responses}

Available product information:
{formatted_metadata}

Respond in {lang} language, referencing previous conversation naturally.
"""
            
            # Generate response using cheaper model for follow-ups
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=OPENAI_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            
            state["final_response"] = response.choices[0].message.content
            
            if TEST_ENV:
                print(f"✅ [DEBUG ResponseFormatter] Cache-based response generated ({len(state['final_response'])} characters)")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ResponseFormatter] Cache-based response error: {e}")
            state["final_response"] = self._handle_cache_error(e, state)
            
        return state
    
    def _handle_cache_error(self, error: Exception, state: ConversationState) -> str:
        """Handle errors in cache-based response generation"""
        lang = state.get("detected_language", "en")
        
        if lang == "pl":
            return "Przepraszam, wystąpił problem z przetwarzaniem Twojego pytania. Spróbuj ponownie."
        else:
            return "I apologize, there was an issue processing your follow-up question. Please try again."