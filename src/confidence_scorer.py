"""
Confidence Scoring Module
Calculates confidence score for search results
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from models import ConversationState
from config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE,
    CONFIDENCE_THRESHOLD_HIGH, CONFIDENCE_THRESHOLD_LOW
)

class ConfidenceScorer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _create_evaluation_prompt(self, query: str, results: List[Dict]) -> str:
        # Format results for evaluation
        formatted_results = []
        for i, result in enumerate(results[:5]):  # Top 5 for evaluation
            meta = result['metadata']
            formatted_results.append(f"""
Product {i+1}: {meta.get('product_name', 'Unknown')}
Score: {result['score']:.3f}
Type: {meta.get('content_type', 'unknown')}
Domain: {meta.get('domain', 'unknown')}
Description: {meta.get('title_en', '')[:100]}...
""")
        
        return f"""
Evaluate how well these search results answer the user's query.

User Query: "{query}"

Top Search Results:
{''.join(formatted_results)}

Evaluate based on:
1. Semantic match score (how high are the scores?)
2. Problem-solution fit (do products solve the stated problem?)
3. Product relevance (are these the right products for this issue?)
4. Result quality (are results specific and helpful?)

Return JSON with:
{{
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "best_matches": ["product names that best match"],
    "addresses_problem": true/false
}}
"""
    
    def calculate_confidence(self, state: ConversationState) -> ConversationState:
        """Calculate confidence score for search results"""
        if not state["search_results"]:
            state["confidence"] = 0.0
            return state
        
        # Factor 1: Semantic scores
        scores = [r['score'] for r in state["search_results"][:5]]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Quick confidence based on scores
        if avg_score > 0.75:
            base_confidence = 0.8
        elif avg_score > 0.65:
            base_confidence = 0.65
        elif avg_score > 0.55:
            base_confidence = 0.5
        else:
            base_confidence = 0.4
        
        # Factor 2: LLM evaluation for complex queries
        if "problem" in state["original_query"].lower() or len(state["original_query"]) > 50:
            try:
                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    temperature=OPENAI_TEMPERATURE,
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
                llm_confidence = evaluation.get("confidence", base_confidence)
                
                # Weighted average
                state["confidence"] = (base_confidence * 0.4 + llm_confidence * 0.6)
                state["evaluation_reasoning"] = evaluation.get("reasoning", "")
                
            except Exception as e:
                print(f"LLM evaluation error: {e}")
                state["confidence"] = base_confidence
        else:
            # Simple queries - just use score-based confidence
            state["confidence"] = base_confidence
        
        return state

def evaluate_confidence(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    scorer = ConfidenceScorer()
    return scorer.calculate_confidence(state)

def route_based_on_confidence(state: ConversationState) -> str:
    """Routing function to decide next step based on confidence"""
    confidence = state.get("confidence", 0)
    
    if confidence >= CONFIDENCE_THRESHOLD_HIGH:
        return "format_response"
    elif confidence >= CONFIDENCE_THRESHOLD_LOW:
        if state.get("iteration", 1) == 1:
            return "reasoning_retry"
        else:
            return "add_llm_knowledge"
    else:
        return "escalate_support"