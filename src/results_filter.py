"""
Dynamic Parallel Results Filter - VERSION 4.0 with ThreadPoolExecutor OPTIMIZATION
Replaced AsyncIO with ThreadPoolExecutor for better compatibility and performance
"""
import json
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from models import ConversationState
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, ENHANCED_K_VALUE
from prompts import load_prompt_template

class DynamicParallelResultsFilter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.chunk_size = ENHANCED_K_VALUE // 2
        if TEST_ENV:
            print(f"🔧 [DynamicFilter] Using ENHANCED_K_VALUE={ENHANCED_K_VALUE}, chunk_size={self.chunk_size}")
            print(f"🔧 [DynamicFilter] Using ThreadPoolExecutor optimization")
    
    def _create_chunk_filter_prompt(self, state: ConversationState, chunk_results: List[Dict], chunk_num: int) -> str:
        """Creates filtering prompt - LESS AGGRESSIVE, PRODUCT NAME FOCUSED"""
        user_query = state.get("user_query", "")
        optimized_queries = state.get("optimized_queries", [])
        business_analysis = state.get("business_analysis", {})
        
        # Extract mentioned product names from queries
        mentioned_products = []
        if business_analysis.get('product_name_corrections'):
            mentioned_products.append(business_analysis['product_name_corrections'])
        
        # Format conversation context
        chat_history_context = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        # Format business intelligence
        business_context = ""
        if business_analysis:
            business_context = f"""
BUSINESS INTELLIGENCE:
- Business Interpretation: {business_analysis.get('business_interpretation', 'N/A')}
- Product Corrections: {business_analysis.get('product_name_corrections', 'None')}
- Domain Hint: {business_analysis.get('domain_hint', 'unknown')}
- Search Enhancement: {business_analysis.get('search_enhancement', 'None')}
"""
        
        # Full metadata dump
        results_info = []
        for i, result in enumerate(chunk_results):
            meta = result.get('metadata', {})
            metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
            results_info.append(f"""
Result {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
        
        formatted_results = "".join(results_info)
        
        # Try to load prompt from template
        prompt = load_prompt_template(
            "results_filtering",
            chunk_num=chunk_num,
            user_query=user_query,
            optimized_queries=optimized_queries,
            mentioned_products=mentioned_products,
            business_context=business_context,
            chat_history_context=chat_history_context,
            num_results=len(chunk_results),
            formatted_results=formatted_results,
            max_index=len(chunk_results)-1
        )
        
        # Fallback to simple prompt if template fails
        if not prompt:
            if TEST_ENV:
                print(f"⚠️ [ResultsFilter] Using fallback hardcoded prompt for chunk {chunk_num}")
            prompt = f"""
Filter search results for: "{user_query}"
Return JSON: {{"keep_indices": {list(range(len(chunk_results)))}, "reasoning": "fallback - kept all"}}
"""
        
        return prompt

    def _filter_chunk_threaded(self, state: ConversationState, chunk_results: List[Dict], chunk_num: int) -> Dict:
        """Filter one chunk using synchronous OpenAI call - optimized for ThreadPoolExecutor"""
        try:
            prompt = self._create_chunk_filter_prompt(state, chunk_results, chunk_num)
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.1,
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if TEST_ENV:
                print(f"✅ [DynamicFilter] Chunk {chunk_num}: keeping {len(result.get('keep_indices', []))} of {len(chunk_results)} results")
                if result.get('mentioned_products_found'):
                    print(f"   🎯 Found mentioned products: {result['mentioned_products_found']}")
                print(f"   Best match: {result.get('best_match', 'N/A')}")
                print(f"   Quality: {result.get('chunk_quality', 'unknown')}")
                
            return {
                **result,
                "chunk_num": chunk_num,
                "success": True
            }
            
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DynamicFilter] Chunk {chunk_num} failed: {e}")
            # More conservative fallback - keep all on error
            return {
                "keep_indices": list(range(len(chunk_results))),
                "reasoning": f"Chunk {chunk_num} processing failed, kept all results as fallback",
                "chunk_num": chunk_num,
                "success": False,
                "error": str(e)
            }

    def _merge_chunk_results(self, chunk_results_list: List[Dict], original_results: List[Dict]) -> Tuple[List[Dict], str]:
        """Merge results from all chunks"""
        merged_results = []
        merge_reasoning = []
        total_knowledge = 0
        all_mentioned_products = []
        
        for chunk_result in chunk_results_list:
            chunk_num = chunk_result.get("chunk_num", 0)
            chunk_kept = 0
            
            # Calculate offset for this chunk
            offset = (chunk_num - 1) * self.chunk_size
            
            for idx in chunk_result.get("keep_indices", []):
                original_idx = idx + offset
                if 0 <= original_idx < len(original_results):
                    merged_results.append(original_results[original_idx])
                    chunk_kept += 1
            
            # Collect mentioned products
            if chunk_result.get("mentioned_products_found"):
                all_mentioned_products.extend(chunk_result["mentioned_products_found"])
            
            knowledge_found = chunk_result.get("knowledge_articles_found", 0)
            total_knowledge += knowledge_found
            
            merge_reasoning.append(
                f"Chunk {chunk_num}: kept {chunk_kept}/{min(self.chunk_size, len(original_results) - offset)}, "
                f"quality: {chunk_result.get('chunk_quality', 'unknown')}"
            )
        
        # Final summary
        final_reasoning = ". ".join(merge_reasoning)
        if all_mentioned_products:
            final_reasoning += f". Found mentioned products: {list(set(all_mentioned_products))}"
        final_reasoning += f". Total knowledge articles: {total_knowledge}"
        
        return merged_results, final_reasoning

    def filter_results_parallel(self, state: ConversationState) -> ConversationState:
        """Main filtering method using ThreadPoolExecutor for parallel processing"""
        if not state.get("search_results"):
            if TEST_ENV:
                print("\n🚀 [DynamicFilter] No search results to filter")
            return state
        
        original_count = len(state["search_results"])
        if TEST_ENV:
            print(f"\n🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of {original_count} results")
            print(f"🔧 [DynamicFilter] Using chunk_size={self.chunk_size}")
        
        try:
            # Split into chunks
            all_results = state["search_results"]
            chunks = []
            
            for i in range(0, len(all_results), self.chunk_size):
                chunk = all_results[i:i + self.chunk_size]
                if chunk:
                    chunks.append(chunk)
            
            if TEST_ENV:
                print(f"📦 [DynamicFilter] Split into {len(chunks)} chunks")
            
            # Process chunks in parallel using ThreadPoolExecutor
            if len(chunks) > 1:
                if TEST_ENV:
                    print(f"🔄 [DynamicFilter] Processing {len(chunks)} chunks in parallel with ThreadPoolExecutor")
                
                with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
                    # Submit all tasks
                    futures = []
                    for i, chunk in enumerate(chunks):
                        future = executor.submit(self._filter_chunk_threaded, state, chunk, i + 1)
                        futures.append(future)
                    
                    # Collect results
                    chunk_results = [future.result() for future in futures]
                
                filtered_results, merge_reasoning = self._merge_chunk_results(
                    chunk_results, all_results
                )
            else:
                # Single chunk - no need for ThreadPoolExecutor
                if TEST_ENV:
                    print(f"🔄 [DynamicFilter] Processing single chunk")
                chunk_result = self._filter_chunk_threaded(state, chunks[0], 1)
                filtered_results = [all_results[i] for i in chunk_result.get("keep_indices", []) 
                                  if 0 <= i < len(chunks[0])]
                merge_reasoning = chunk_result.get("reasoning", "Single chunk processed")
            
            # Update state
            state["search_results"] = filtered_results
            state["filter_reasoning"] = merge_reasoning
            
            if TEST_ENV:
                print(f"🎯 [DynamicFilter] ThreadPoolExecutor filtering: {original_count} → {len(filtered_results)} results")
                print(f"💭 [DynamicFilter] {merge_reasoning}")
                
        except Exception as e:
            if TEST_ENV:
                print(f"❌ [DynamicFilter] Filtering failed: {e}")
            state["filter_reasoning"] = f"Filtering failed, kept all {original_count} results"
            
        return state

    def filter_results_sync_fallback(self, state: ConversationState) -> ConversationState:
        """Synchronous fallback - keep all results"""
        if TEST_ENV:
            print("\n🔄 [DynamicFilter] Using sync fallback - keeping all results")
        state["filter_reasoning"] = "Sync fallback: kept all results"
        return state

def intelligent_results_filter(state: ConversationState) -> ConversationState:
    """Node function for LangGraph - now using ThreadPoolExecutor optimization"""
    filter_instance = DynamicParallelResultsFilter()
    
    try:
        # Direct call to synchronous method - no more asyncio.run()!
        return filter_instance.filter_results_parallel(state)
    except Exception as e:
        if TEST_ENV:
            print(f"⚠️ [DynamicFilter] ThreadPoolExecutor failed, using sync fallback: {e}")
        return filter_instance.filter_results_sync_fallback(state)