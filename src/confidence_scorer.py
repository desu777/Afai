"""
Confidence Scoring Module - VERSION 4.0 with Category Bonus
Enhanced metadata evaluation with category matching bonus
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from models import ConversationState
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, CONFIDENCE_THRESHOLD

class ConfidenceScorer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _calculate_category_bonus(self, state: ConversationState) -> float:
        """Calculate bonus score for finding products from requested category"""
        # Check if a category was requested
        if not state.get("requested_category") or not state.get("category_products"):
            return 0.0
        
        requested_products = set(state.get("category_products", []))
        if not requested_products:
            return 0.0
        
        # Count how many requested products were found in results
        found_count = 0
        for result in state.get("search_results", []):
            product_name = result.get('metadata', {}).get('product_name', '')
            if product_name in requested_products:
                found_count += 1
        
        # Calculate bonus (up to 0.2)
        coverage = found_count / len(requested_products)
        bonus = min(0.2, coverage * 0.25)  # Max 0.2 bonus
        
        if TEST_ENV and bonus > 0:
            print(f"🎯 [ConfidenceScorer] Category bonus: +{bonus:.2f} (found {found_count}/{len(requested_products)} products)")
        
        return bonus
        
    def _create_evaluation_prompt(self, state: ConversationState) -> str:
        """Creates evaluation prompt with FULL metadata access"""
        
        # Gather all queries to evaluate
        original_query = state.get("user_query", "")
        optimized_queries = state.get("optimized_queries", [])
        business_analysis = state.get("business_analysis", {})
        results = state.get("search_results", [])
        chat_history = state.get("chat_history", [])
        
        # Include category information if present
        category_context = ""
        if state.get("requested_category") and state.get("category_products"):
            category_context = f"""
--- CATEGORY REQUEST CONTEXT ---
User asked for products in category: {state.get("requested_category")}
Expected products: {', '.join(state.get("category_products", []))}
This is a CRITICAL evaluation factor - results should contain these specific products!
---
"""
        
        # Include problem-solution context if present
        problem_context = ""
        if state.get("identified_problem") and state.get("recommended_solutions"):
            problem_context = f"""
--- PROBLEM-SOLUTION CONTEXT ---
Identified Problem: {state.get("identified_problem")}
Recommended Solutions: {', '.join(state.get("recommended_solutions", []))}
Results should ideally contain these solutions!
---
"""
        
        # NEW: Collect all queries to evaluate
        evaluation_queries = [original_query]
        
        # Add corrected names from Business Reasoner
        if business_analysis.get('product_name_corrections') and business_analysis['product_name_corrections'] != 'None':
            corrected_name = business_analysis['product_name_corrections']
            evaluation_queries.append(f"Query corrected by business logic: {corrected_name}")
        
        # Add optimized queries
        if optimized_queries:
            evaluation_queries.extend([f"Optimized query: {q}" for q in optimized_queries])
        
        # Format conversation context
        context_summary = ""
        if chat_history:
            recent_exchanges = chat_history[-6:]
            context_summary = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_exchanges])
        
        # Business Intelligence Context
        business_context = ""
        if business_analysis:
            business_context = f"""
--- BUSINESS INTELLIGENCE CONTEXT ---
Business Interpretation: {business_analysis.get('business_interpretation', 'N/A')}
Product Name Corrections: {business_analysis.get('product_name_corrections', 'None')}
Category Requested: {business_analysis.get('category_requested', 'None')}
Products in Category: {', '.join(business_analysis.get('products_in_category', []))}
Problem Identified: {business_analysis.get('problem_identified', 'None')}
Solutions: {', '.join(business_analysis.get('solutions_for_problem', []))}
Domain Hint: {business_analysis.get('domain_hint', 'unknown')}
Search Enhancement: {business_analysis.get('search_enhancement', 'None')}
"""
        
        # Format all evaluation queries
        queries_text = "\n".join([f"  - {q}" for q in evaluation_queries])
        
        # FULL METADATA DUMP FOR EVALUATION
        results_metadata = []
        for i, result in enumerate(results):
            meta = result.get('metadata', {})
            metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
            results_metadata.append(f"""
Result {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
        
        formatted_results = "".join(results_metadata)
        
        return f"""
Evaluate how well these search results answer the user's query considering ALL CONTEXT.

{'--- CONVERSATION CONTEXT ---' if context_summary else ''}
{context_summary}
{'---' if context_summary else ''}

{business_context}

{category_context}

{problem_context}

ORIGINAL USER QUERY: "{original_query}"

ALL QUERIES TO EVALUATE AGAINST:
{queries_text}

--- COMPLETE SEARCH RESULTS WITH FULL METADATA ---
{formatted_results}

--- ENHANCED EVALUATION CRITERIA ---

1. **Category Match** (HIGHEST PRIORITY for category queries):
   - If user asked for a category (like "sole" or "bakterie"), did we find those specific products?
   - Finding all products from requested category = EXCELLENT confidence
   - Missing key products from category = LOWER confidence

2. **Business Intelligence Alignment**: Do results match corrected product names and business interpretation?

3. **Problem-Solution Fit**: If a problem was identified, do results contain the recommended solutions?

4. **Multi-Query Relevance**: Do results answer ANY of the evaluation queries well?

5. **Context Coherence**: Do results match the conversation context?

6. **Domain Match**: Are product domains appropriate for the discussed aquarium type?

7. **Knowledge Value**: Are there valuable educational materials for the user's needs?

CRITICAL EVALUATION FACTORS:

- **Category Queries**: If user asked "jakie sole macie?" and we found Sea Salt, Reef Salt, etc. = HIGH confidence!
  Missing these specific products = LOW confidence regardless of other factors.

- **Business Logic Corrections**: If business logic corrected the query, results matching corrections = bonus points

- **Full Content Analysis**: Use complete metadata to understand true value of each result

- **Educational Content**: Knowledge articles can be valuable, but for category queries, products are primary

Return JSON with:
{{
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation including category coverage analysis",
    "best_matches": ["list of best matching product/content names"],
    "category_coverage": "assessment of how well category request was fulfilled",
    "context_mismatch": "describe any context mismatches if found",
    "knowledge_value": "assessment of educational content value",
    "domain_consistency": "evaluation of domain matching"
}}
"""
    
    def calculate_confidence(self, state: ConversationState) -> ConversationState:
        """Calculate confidence score with category bonus"""
        if not state.get("search_results"):
            state["confidence"] = 0.0
            if TEST_ENV: 
                print("\n🤔 [DEBUG ConfidenceScorer] No search results, confidence: 0.0")
            return state
        
        if TEST_ENV:
            print(f"\n📊 [DEBUG ConfidenceScorer] Evaluating {len(state.get('search_results', []))} results with FULL metadata")
            print(f"🎯 [DEBUG ConfidenceScorer] Query: '{state.get('user_query', '')}'")
            
            # Log business intelligence usage
            if state.get("business_analysis"):
                ba = state["business_analysis"]
                if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                    print(f"🔧 [DEBUG ConfidenceScorer] Will evaluate against corrected product: {ba['product_name_corrections']}")
                if ba.get("category_requested"):
                    print(f"📦 [DEBUG ConfidenceScorer] Category requested: {ba['category_requested']}")
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
            
            # Base confidence from LLM
            base_confidence = evaluation.get("confidence", 0.0)
            
            # Calculate category bonus
            category_bonus = self._calculate_category_bonus(state)
            
            # Final confidence with bonus
            final_confidence = min(1.0, base_confidence + category_bonus)
            
            state["confidence"] = final_confidence
            state["evaluation_reasoning"] = evaluation.get("reasoning", "")
            
            # Add category coverage info
            if evaluation.get("category_coverage"):
                state["category_coverage"] = evaluation["category_coverage"]
            
            # Add other context information
            if evaluation.get("context_mismatch"):
                state["context_warning"] = evaluation["context_mismatch"]
            
            if evaluation.get("knowledge_value"):
                state["knowledge_assessment"] = evaluation["knowledge_value"]
                
            if evaluation.get("domain_consistency"):
                state["domain_assessment"] = evaluation["domain_consistency"]
            
            if TEST_ENV:
                print(f"\n🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:")
                print(f"   - Base confidence: {base_confidence}")
                print(f"   - Category bonus: +{category_bonus}")
                print(f"   - Final confidence: {final_confidence}")
                print(f"   - Best matches: {evaluation.get('best_matches', [])}")
                if evaluation.get('category_coverage'):
                    print(f"   - Category coverage: {evaluation['category_coverage']}")
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