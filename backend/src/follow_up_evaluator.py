"""
Follow-up Evaluator for Aquaforest RAG System
Uses configured provider (Vertex AI) with OpenRouter fallback
"""
import json
import time  # For LLM performance monitoring
from typing import Dict, Any, Optional, List
from models import ConversationState
from llm_client_factory import create_follow_up_client
from config import debug_print, TEST_ENV, FOLLOW_UP_TEMPERATURE
from prompt_saver import log_prompt_if_enabled

class FollowUpEvaluator:
    """Evaluates cache sufficiency for follow-up questions with primary provider + fallback"""
    
    def __init__(self):
        # Use factory for client creation - it handles fallback internally
        self.client, self.model_name = create_follow_up_client()
        debug_print(f"[EVAL] Ready: {self.model_name}")
    
    def evaluate_cache_sufficiency(self, state: ConversationState, extended_cache: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if extended cache is sufficient to answer follow-up question
        
        Returns:
            {
                "sufficient": bool,
                "confidence": float,
                "reasoning": str,
                "response_data": Dict (if sufficient),
                "business_prompt": str (if insufficient)
            }
        """
        if TEST_ENV:
            query_display = state['user_query'][:40] + "..." if len(state['user_query']) > 40 else state['user_query']
            print(f"[EVAL] Cache for: '{query_display}'")
        
        try:
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(state, extended_cache)
            
            # Measure LLM response time
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=FOLLOW_UP_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}]
            )
            
            # Calculate response time and log performance
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Log performance to console if TEST_ENV enabled
            if TEST_ENV:
                print(f"[LLM_PERF] follow_up_evaluator: {response_time_ms:.2f}ms (model: {self.model_name})")
            
            # Update prompt file with response time if SAVE_PROMPT enabled
            from config import SAVE_PROMPT
            if SAVE_PROMPT:
                log_prompt_if_enabled("follow_up_evaluator", prompt, state, self.model_name, FOLLOW_UP_TEMPERATURE, response_time_ms)
            
            evaluation_text = response.choices[0].message.content.strip()
            
            if TEST_ENV:
                response_display = evaluation_text[:50] + "..." if len(evaluation_text) > 50 else evaluation_text
                print(f"[AI] Response: {response_display}")
            
            # Parse evaluation response
            evaluation = self._parse_evaluation_response(evaluation_text)
            
            if evaluation["sufficient"]:
                # Cache is sufficient - prepare response data
                evaluation["response_data"] = self._prepare_response_data(state, extended_cache)
                debug_print(f"[OK] Cache OK: {evaluation['confidence']}")
            else:
                # Cache insufficient - create smart business prompt
                evaluation["business_prompt"] = self._create_smart_business_prompt(state, extended_cache, evaluation["reasoning"])
                debug_print(f"[X] Cache miss - creating prompt")
            
            return evaluation
            
        except Exception as e:
            debug_print(f"[X] Error: {str(e)[:30]}")
            return {
                "sufficient": False,
                "confidence": 0.0,
                "reasoning": f"Evaluation error: {str(e)}",
                "business_prompt": f"User asked: {state['user_query']}\nPlease provide comprehensive information about this query."
            }
    
    def _create_evaluation_prompt(self, state: ConversationState, extended_cache: Dict[str, Any]) -> str:
        """Create prompt for cache sufficiency evaluation"""
        user_query = state['user_query']
        chat_history = state.get('chat_history', [])
        
        # Format chat history
        chat_history_text = ""
        if chat_history:
            for msg in chat_history[-6:]:  # Last 6 messages (3 exchanges)
                chat_history_text += f"{msg['role']}: {msg['content']}\n"
        
        # Format extended cache
        cache_metadata = extended_cache.get("metadata", [])
        cache_responses = extended_cache.get("model_responses", [])
        cache_context = extended_cache.get("conversation_context", {})
        
        # Create structured cache summary
        cache_summary = []
        if cache_metadata:
            cache_summary.append(f"[DATA] METADATA ({len(cache_metadata)} items):")
            for i, meta in enumerate(cache_metadata[:5]):  # Top 5 items
                product_name = meta.get("product_name", "Unknown")
                content_type = meta.get("content_type", "unknown")
                cache_summary.append(f"  {i+1}. {product_name} ({content_type})")
        
        if cache_responses:
            cache_summary.append(f"\n[AI] RESPONSES ({len(cache_responses)} items):")
            for i, resp in enumerate(cache_responses[-3:]):  # Last 3 responses
                snippet = resp[:100] + "..." if len(resp) > 100 else resp
                cache_summary.append(f"  {i+1}. {snippet}")
        
        if cache_context:
            cache_summary.append(f"\n[>] CONTEXT:")
            for key, value in cache_context.items():
                if isinstance(value, list):
                    cache_summary.append(f"  {key}: {len(value)} items")
                else:
                    cache_summary.append(f"  {key}: {str(value)[:50]}...")
        
        cache_summary_text = "\n".join(cache_summary) if cache_summary else "No cached data available"
        
        return f"""You are an AI assistant evaluating whether cached information is sufficient to answer a follow-up question.

--- CONVERSATION HISTORY ---
{chat_history_text}

--- CURRENT USER QUERY ---
{user_query}

--- AVAILABLE CACHE ---
{cache_summary_text}

--- EVALUATION TASK ---
Determine if the cached information is sufficient to provide a comprehensive answer to the user's query.

Consider:
1. Does the cache contain relevant product information?
2. Are there previous responses that address similar questions?
3. Is the context sufficient to understand what the user is asking about?
4. Can you provide specific details (dosage, usage, comparisons) from the cache?
5. Can you reliably **augment** the cached information with your own domain knowledge to fill minor gaps?

If you can combine the cache **plus** your own knowledge to generate a complete, helpful answer, mark it as **sufficient**.

Respond in JSON format:
{{
    "sufficient": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your decision",
    "key_findings": ["specific relevant information found in cache or domain knowledge"],
    "missing_info": ["what information is missing if insufficient"]
}}

Be conservative, but you may leverage your own knowledge to complement the cache when deciding sufficiency."""
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse evaluation response from Gemini Flash"""
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            evaluation = json.loads(json_text)
            
            # Validate required fields
            return {
                "sufficient": evaluation.get("sufficient", False),
                "confidence": float(evaluation.get("confidence", 0.0)),
                "reasoning": evaluation.get("reasoning", "No reasoning provided"),
                "key_findings": evaluation.get("key_findings", []),
                "missing_info": evaluation.get("missing_info", [])
            }
            
        except Exception as e:
            if TEST_ENV:
                print(f"[X] JSON error: {e}")
                response_display = response_text[:100] + "..." if len(response_text) > 100 else response_text
                print(f"Raw: {response_display}")
            
            # Fallback - look for keywords
            sufficient = any(word in response_text.lower() for word in ["sufficient", "yes", "true", "can answer"])
            
            return {
                "sufficient": sufficient,
                "confidence": 0.5 if sufficient else 0.0,
                "reasoning": f"Fallback: {sufficient}",
                "key_findings": [],
                "missing_info": []
            }
    
    def _prepare_response_data(self, state: ConversationState, extended_cache: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare response data for response formatter when cache is sufficient"""
        return {
            "metadata": extended_cache.get("metadata", []),
            "previous_responses": extended_cache.get("model_responses", []),
            "conversation_context": extended_cache.get("conversation_context", {}),
            "user_query": state["user_query"],
            "language": state.get("detected_language", "en"),
            "source": "extended_cache"
        }
    
    def _create_smart_business_prompt(self, state: ConversationState, extended_cache: Dict[str, Any], reasoning: str) -> str:
        """Create intelligent prompt for business reasoner when cache is insufficient"""
        user_query = state["user_query"]
        language = state.get("detected_language", "en")
        
        # Extract context from cache
        context_hints = []
        if extended_cache.get("metadata"):
            products_mentioned = [meta.get("product_name", "") for meta in extended_cache["metadata"][:3]]
            context_hints.append(f"Previously discussed products: {', '.join(filter(None, products_mentioned))}")
        
        if extended_cache.get("conversation_context"):
            context_data = extended_cache["conversation_context"]
            if context_data.get("requested_category"):
                context_hints.append(f"User interested in category: {context_data['requested_category']}")
            if context_data.get("domain_filter"):
                context_hints.append(f"Domain context: {context_data['domain_filter']}")
        
        context_text = "\n".join(context_hints) if context_hints else "No specific context from cache"
        
        return f"""BUSINESS REASONER CONTEXT:
User Query: {user_query}
Language: {language}
Cache Evaluation: {reasoning}

CONTEXT FROM PREVIOUS CONVERSATION:
{context_text}

INSTRUCTIONS:
The user is asking a follow-up question that requires new information beyond what's cached. 
Please analyze this query considering the conversation context and provide comprehensive business reasoning.
Focus on understanding the user's intent and providing detailed product recommendations."""

# Create global evaluator instance
follow_up_evaluator = FollowUpEvaluator()

def evaluate_follow_up_cache(state: ConversationState, extended_cache: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for follow-up cache evaluation"""
    return follow_up_evaluator.evaluate_cache_sufficiency(state, extended_cache) 