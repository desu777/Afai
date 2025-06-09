"""
Confidence Scoring Module - Wersja 2.1 (LLM with context awareness)
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from models import ConversationState
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, CONFIDENCE_THRESHOLD

class ConfidenceScorer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _create_evaluation_prompt(self, query: str, results: List[Dict], chat_history: List[Dict]) -> str:
        # Format conversation context
        context_summary = ""
        if chat_history:
            recent_exchanges = chat_history[-6:]  # Last 3 exchanges
            context_summary = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_exchanges])
        
        formatted_results = []
        for i, result in enumerate(results[:15]):
            meta = result.get('metadata', {})
            formatted_results.append(
                f"Result {i+1}: Name: {meta.get('product_name', 'Unknown')}, "
                f"Domain: {meta.get('domain', 'N/A')}, "
                f"Type: {meta.get('content_type', 'N/A')}, "
                f"Score: {result.get('score', 0):.3f}, "
                f"Description: {meta.get('title_en', '')[:100]}...\n"
            )
        
        return f"""
Evaluate how well these search results answer the user's query IN THE CONTEXT of the conversation.

{'--- CONVERSATION CONTEXT ---' if context_summary else ''}
{context_summary}
{'---' if context_summary else ''}

CURRENT USER QUERY: "{query}"

Top Search Results:
{''.join(formatted_results)}

CRITICAL EVALUATION CRITERIA:
1. **Context Coherence**: Do results match the conversation context? (e.g., if discussing freshwater, are results for freshwater?)
2. **Direct Relevance**: Do results directly answer the user's question?
3. **Domain Match**: Are product domains appropriate for the discussed aquarium type?
4. **Problem-Solution Fit**: Do products solve the user's stated problem?

IMPORTANT: If user references previous context (like "such aquarium" or "those products") but results don't match that context, significantly lower the confidence!

Return JSON with:
{{
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation including context analysis",
    "best_matches": ["list of best matching product names"],
    "context_mismatch": "describe any context mismatches if found"
}}
"""
    
    def calculate_confidence(self, state: ConversationState) -> ConversationState:
        """Calculate confidence score for search results using LLM evaluation with context."""
        if not state.get("search_results"):
            state["confidence"] = 0.0
            if TEST_ENV: 
                print("\n🤔 [DEBUG ConfidenceScorer] No search results, confidence: 0.0")
            return state
        
        if TEST_ENV:
            print(f"\n📊 [DEBUG ConfidenceScorer] Evaluating {len(state.get('search_results', []))} results for query: '{state.get('original_query', '')}'")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_evaluation_prompt(
                            state["original_query"],
                            state["search_results"],
                            state.get("chat_history", [])
                        )
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            state["confidence"] = evaluation.get("confidence", 0.0)
            state["evaluation_reasoning"] = evaluation.get("reasoning", "")
            
            # Add context mismatch warning if found
            if evaluation.get("context_mismatch"):
                state["context_warning"] = evaluation["context_mismatch"]
            
            if TEST_ENV:
                print(f"\n🤖 [DEBUG ConfidenceScorer] LLM evaluation with context:")
                print(f"   - Confidence: {evaluation.get('confidence', 0.0)}")
                print(f"   - Best matches: {evaluation.get('best_matches', [])}")
                if evaluation.get('context_mismatch'):
                    print(f"   - Context mismatch: {evaluation['context_mismatch']}")
                print(f"✅ [DEBUG ConfidenceScorer] Final calculated confidence: {state['confidence']:.4f}")

        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ConfidenceScorer] LLM evaluation error: {e}")
            state["confidence"] = 0.0
        
        return state

def evaluate_confidence(state: ConversationState) -> ConversationState:
    scorer = ConfidenceScorer()
    return scorer.calculate_confidence(state)

def route_based_on_confidence(state: ConversationState) -> str:
    """Routing function simplified to two paths."""
    confidence = state.get("confidence", 0.0)
    
    if confidence >= CONFIDENCE_THRESHOLD:
        if TEST_ENV: 
            print(f"🗺️ [DEBUG] Routing decision: 'format_response' (confidence {confidence:.2f} >= {CONFIDENCE_THRESHOLD})")
        return "format_response"
    else:
        if TEST_ENV: 
            print(f"🗺️ [DEBUG] Routing decision: 'escalate_support' (confidence {confidence:.2f} < {CONFIDENCE_THRESHOLD})")
        return "escalate_support"