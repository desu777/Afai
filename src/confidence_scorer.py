"""
Confidence Scoring Module - Wersja 2.0 (LLM-first)
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from models import ConversationState
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, CONFIDENCE_THRESHOLD

class ConfidenceScorer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _create_evaluation_prompt(self, query: str, results: List[Dict]) -> str:
        formatted_results = []
        for i, result in enumerate(results[:15]):
            meta = result.get('metadata', {})
            formatted_results.append(
                f"Result {i+1}: Name: {meta.get('product_name', 'Unknown')}, "
                f"Score: {result.get('score', 0):.3f}, "
                f"Description: {meta.get('title_en', '')[:100]}...\n"
            )
        
        return f"""
Evaluate how well these search results answer the user's query.

User Query: "{query}"

Top Search Results:
{''.join(formatted_results)}

Evaluate based on relevance, problem-solution fit, and score quality. Return JSON with:
{{
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "best_matches": ["list of best matching product names"]
}}
"""
    
    def calculate_confidence(self, state: ConversationState) -> ConversationState:
        """Calculate confidence score for search results using only LLM evaluation."""
        if not state.get("search_results"):
            state["confidence"] = 0.0
            if TEST_ENV: print("\n🤔 [DEBUG ConfidenceScorer] Brak wyników, pewność: 0.0")
            return state
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_evaluation_prompt(
                            state["original_query"],
                            state["search_results"]
                        )
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            state["confidence"] = evaluation.get("confidence", 0.0)
            state["evaluation_reasoning"] = evaluation.get("reasoning", "")
            
            if TEST_ENV:
                print(f"\n🤖 [DEBUG ConfidenceScorer] Ocena LLM: {evaluation}")
                print(f"✅ [DEBUG ConfidenceScorer] Finalna obliczona pewność (tylko LLM): {state['confidence']:.4f}")

        except Exception as e:
            print(f"LLM evaluation error: {e}")
            state["confidence"] = 0.0
        
        return state

def evaluate_confidence(state: ConversationState) -> ConversationState:
    scorer = ConfidenceScorer()
    return scorer.calculate_confidence(state)

def route_based_on_confidence(state: ConversationState) -> str:
    """Routing function simplified to two paths."""
    confidence = state.get("confidence", 0.0)
    
    if confidence >= CONFIDENCE_THRESHOLD:
        if TEST_ENV: print(f"🗺️ [DEBUG] Decyzja routingu: 'format_response' (pewność {confidence:.2f} >= {CONFIDENCE_THRESHOLD})")
        return "format_response"
    else:
        if TEST_ENV: print(f"🗺️ [DEBUG] Decyzja routingu: 'escalate_support' (pewność {confidence:.2f} < {CONFIDENCE_THRESHOLD})")
        return "escalate_support"