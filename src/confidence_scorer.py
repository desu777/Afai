"""
Confidence Scoring Module - VERSION 3.0 with FULL METADATA ACCESS
Complete metadata evaluation with business intelligence integration
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from models import ConversationState
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, CONFIDENCE_THRESHOLD

class ConfidenceScorer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _create_evaluation_prompt(self, state: ConversationState) -> str:
        """Creates evaluation prompt with FULL metadata access"""
        
        # Zbierz wszystkie queries do oceny
        original_query = state.get("user_query", "")
        optimized_queries = state.get("optimized_queries", [])
        business_analysis = state.get("business_analysis", {})
        results = state.get("search_results", [])
        chat_history = state.get("chat_history", [])
        
        # 🆕 NEW: Zbierz wszystkie queries do oceny
        evaluation_queries = [original_query]  # Start z oryginalnym
        
        # Dodaj poprawione nazwy z Business Reasoner
        if business_analysis.get('product_name_corrections') and business_analysis['product_name_corrections'] != 'None':
            corrected_name = business_analysis['product_name_corrections']
            evaluation_queries.append(f"Query corrected by business logic: {corrected_name}")
        
        # Dodaj optimized queries z Query Optimizer
        if optimized_queries:
            evaluation_queries.extend([f"Optimized query: {q}" for q in optimized_queries])
        
        # Format conversation context
        context_summary = ""
        if chat_history:
            recent_exchanges = chat_history[-6:]  # Last 3 exchanges
            context_summary = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_exchanges])
        
        # 🆕 NEW: Business Intelligence Context
        business_context = ""
        if business_analysis:
            business_context = f"""
--- BUSINESS INTELLIGENCE CONTEXT ---
Business Interpretation: {business_analysis.get('business_interpretation', 'N/A')}
Product Name Corrections: {business_analysis.get('product_name_corrections', 'None')}
Domain Hint: {business_analysis.get('domain_hint', 'unknown')}
Search Enhancement: {business_analysis.get('search_enhancement', 'None')}

IMPORTANT: The user's original query may contain typos or informal names that were corrected by business logic.
The search results should be evaluated against BOTH the original query AND the corrected versions.
"""
        
        # Format all evaluation queries
        queries_text = "\n".join([f"  - {q}" for q in evaluation_queries])
        
        # 🚀 FULL METADATA DUMP FOR EVALUATION
        results_metadata = []
        for i, result in enumerate(results):
            meta = result.get('metadata', {})
            
            # 🔥 COMPLETE METADATA DUMP - LLM sees EVERYTHING!
            metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
            
            results_metadata.append(f"""
Result {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
        
        formatted_results = "".join(results_metadata)
        
        return f"""
Evaluate how well these search results answer the user's query considering BUSINESS INTELLIGENCE, COMPLETE METADATA, and CONTEXT.

{'--- CONVERSATION CONTEXT ---' if context_summary else ''}
{context_summary}
{'---' if context_summary else ''}

{business_context}

ORIGINAL USER QUERY: "{original_query}"

🆕 ALL QUERIES TO EVALUATE AGAINST:
{queries_text}

--- COMPLETE SEARCH RESULTS WITH FULL METADATA ---
{formatted_results}

--- ENHANCED EVALUATION CRITERIA ---

1. **Business Intelligence Alignment**: Do results match corrected product names and business interpretation?
2. **Multi-Query Relevance**: Do results answer ANY of the evaluation queries well?
3. **Context Coherence**: Do results match the conversation context?
4. **Domain Match**: Are product domains appropriate for the discussed aquarium type?
5. **Problem-Solution Fit**: Do products/knowledge solve the user's stated problem?
6. **Knowledge Value**: Are there valuable educational materials for the user's needs?

🆕 CRITICAL EVALUATION FACTORS:

- **Business Logic Corrections**: If business logic corrected the query (e.g., "nitraphos" → "AF NitraPhos Minus"), 
  and results contain "AF NitraPhos Minus", this should be HIGHLY RELEVANT even if it doesn't 
  match the original misspelled query perfectly.

- **Full Content Analysis**: Use the complete metadata to understand true value of each result.
  A knowledge article with comprehensive setup guide is VERY valuable for beginners.

- **Context References**: If user references previous context (like "such aquarium" or "those products") 
  but results don't match that context, significantly lower the confidence!

- **Educational Content**: Knowledge articles and guides can be MORE valuable than products for certain queries,
  especially for beginners or setup questions.

IMPORTANT: You have COMPLETE access to all metadata. Use this comprehensive information to make accurate assessments!

Return JSON with:
{{
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation including business intelligence, full metadata analysis, and multi-query evaluation",
    "best_matches": ["list of best matching product/content names"],
    "context_mismatch": "describe any context mismatches if found",
    "knowledge_value": "assessment of educational content value",
    "domain_consistency": "evaluation of domain matching"
}}
"""
    
    def calculate_confidence(self, state: ConversationState) -> ConversationState:
        """Calculate confidence score using FULL metadata and business intelligence."""
        if not state.get("search_results"):
            state["confidence"] = 0.0
            if TEST_ENV: 
                print("\n🤔 [DEBUG ConfidenceScorer] No search results, confidence: 0.0")
            return state
        
        if TEST_ENV:
            print(f"\n📊 [DEBUG ConfidenceScorer] Evaluating {len(state.get('search_results', []))} results with FULL metadata")
            print(f"🎯 [DEBUG ConfidenceScorer] Query: '{state.get('user_query', '')}'")
            
            # 🆕 NEW: Log business intelligence usage
            if state.get("business_analysis"):
                ba = state["business_analysis"]
                if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                    print(f"🔧 [DEBUG ConfidenceScorer] Will evaluate against corrected product: {ba['product_name_corrections']}")
                if state.get("optimized_queries"):
                    print(f"🎯 [DEBUG ConfidenceScorer] Will evaluate against {len(state['optimized_queries'])} optimized queries")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_evaluation_prompt(state)
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            state["confidence"] = evaluation.get("confidence", 0.0)
            state["evaluation_reasoning"] = evaluation.get("reasoning", "")
            
            # Add additional context information
            if evaluation.get("context_mismatch"):
                state["context_warning"] = evaluation["context_mismatch"]
            
            if evaluation.get("knowledge_value"):
                state["knowledge_assessment"] = evaluation["knowledge_value"]
                
            if evaluation.get("domain_consistency"):
                state["domain_assessment"] = evaluation["domain_consistency"]
            
            if TEST_ENV:
                print(f"\n🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:")
                print(f"   - Confidence: {evaluation.get('confidence', 0.0)}")
                print(f"   - Best matches: {evaluation.get('best_matches', [])}")
                print(f"   - Knowledge value: {evaluation.get('knowledge_value', 'N/A')}")
                print(f"   - Domain consistency: {evaluation.get('domain_consistency', 'N/A')}")
                if evaluation.get('context_mismatch'):
                    print(f"   - Context mismatch: {evaluation['context_mismatch']}")
                print(f"✅ [DEBUG ConfidenceScorer] Final calculated confidence: {state['confidence']:.4f}")

        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DEBUG ConfidenceScorer] LLM evaluation error: {e}")
            state["confidence"] = 0.0
            state["evaluation_reasoning"] = f"Evaluation failed: {str(e)}"
        
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