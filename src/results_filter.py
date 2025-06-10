"""
Dynamic Parallel Results Filter - VERSION 3.1 with IMPROVED FILTERING
Less aggressive filtering, better product name matching
"""
import json
import asyncio
from typing import List, Dict, Any, Tuple
from openai import AsyncOpenAI, OpenAI
from models import ConversationState
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TEST_ENV, ENHANCED_K_VALUE

class DynamicParallelResultsFilter:
    def __init__(self):
        self.async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.sync_client = OpenAI(api_key=OPENAI_API_KEY)
        self.chunk_size = ENHANCED_K_VALUE // 2
        if TEST_ENV:
            print(f"🔧 [DynamicFilter] Using ENHANCED_K_VALUE={ENHANCED_K_VALUE}, chunk_size={self.chunk_size}")
    
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
        
        # 🆕 IMPROVED PROMPT - LESS AGGRESSIVE
        return f"""
You are analyzing CHUNK {chunk_num} of search results for Aquaforest customers. You have COMPLETE ACCESS to all metadata.

--- CONTEXT ---
Original User Query: "{user_query}"
Optimized Queries: {optimized_queries}
Mentioned Product Names: {mentioned_products}
{business_context}

--- CONVERSATION HISTORY ---
{chat_history_context}

--- CHUNK {chunk_num} RESULTS TO EVALUATE ({len(chunk_results)} results) ---
{formatted_results}

--- 🆕 IMPROVED FILTERING RULES ---

**CRITICAL RULE #1**: If a product name is DIRECTLY MENTIONED in the query or business corrections, 
and that product appears in results - ALWAYS KEEP IT! This is non-negotiable.

**INCLUDE results that match ANY of these criteria:**

1. **Direct Product Match** (HIGHEST PRIORITY):
   - Product name matches what user asked about
   - Product name matches business corrections
   - Example: User asks about "amino mix" → KEEP "AF Amino Mix"

2. **Directly Solve the Problem**:
   - Products that address the user's specific need
   - Solutions to mentioned problems or symptoms

3. **Valuable Educational Content**:
   - Knowledge articles relevant to the query
   - Guides that help understand the topic
   - Especially important for beginners!

4. **Related/Alternative Products**:
   - Similar products that might help
   - Complementary products for the same issue

5. **Domain Appropriate**:
   - Matches the aquarium type if specified
   - Universal products are always relevant

**EXCLUDE ONLY if ALL of these are true:**
- Not mentioned by name
- Completely unrelated to the query
- Wrong domain (if explicitly specified)
- No educational value for the topic
- Not a reasonable alternative

**🆕 CONSERVATIVE APPROACH**: When in doubt, KEEP the result. 
It's better to show more options than to miss the exact product the user wants.

--- YOUR TASK ---
Return a JSON with your analysis:
{{
    "keep_indices": [list of indices 0-{len(chunk_results)-1} to keep],
    "reasoning": "explanation focusing on why you kept key products",
    "chunk_quality": "high|medium|low",
    "best_match": "name of the most relevant result",
    "mentioned_products_found": ["list of directly mentioned products found in this chunk"],
    "domain_signals": "freshwater|marine|universal|mixed|unknown",
    "knowledge_articles_found": number
}}

Remember: BE CONSERVATIVE! Keep products that might be useful.
"""

    async def _filter_chunk_async(self, state: ConversationState, chunk_results: List[Dict], chunk_num: int) -> Dict:
        """Filter one chunk asynchronously"""
        try:
            prompt = self._create_chunk_filter_prompt(state, chunk_results, chunk_num)
            
            response = await self.async_client.chat.completions.create(
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

    async def filter_results_parallel(self, state: ConversationState) -> ConversationState:
        """Main filtering method - now less aggressive"""
        if not state.get("search_results"):
            if TEST_ENV:
                print("\n🚀 [DynamicFilter] No search results to filter")
            return state
        
        original_count = len(state["search_results"])
        if TEST_ENV:
            print(f"\n🚀 [DynamicFilter] Starting conservative filtering of {original_count} results")
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
            
            # Process chunks in parallel
            if len(chunks) > 1:
                tasks = []
                for i, chunk in enumerate(chunks):
                    task = self._filter_chunk_async(state, chunk, i + 1)
                    tasks.append(task)
                
                chunk_results = await asyncio.gather(*tasks)
                filtered_results, merge_reasoning = self._merge_chunk_results(
                    chunk_results, all_results
                )
            else:
                # Single chunk
                chunk_result = await self._filter_chunk_async(state, chunks[0], 1)
                filtered_results = [all_results[i] for i in chunk_result.get("keep_indices", []) 
                                  if 0 <= i < len(chunks[0])]
                merge_reasoning = chunk_result.get("reasoning", "Single chunk processed")
            
            # Update state
            state["search_results"] = filtered_results
            state["filter_reasoning"] = merge_reasoning
            
            if TEST_ENV:
                print(f"🎯 [DynamicFilter] Conservative filtering: {original_count} → {len(filtered_results)} results")
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
    """Node function for LangGraph"""
    filter_instance = DynamicParallelResultsFilter()
    
    try:
        return asyncio.run(filter_instance.filter_results_parallel(state))
    except Exception as e:
        if TEST_ENV:
            print(f"⚠️ [DynamicFilter] Async failed, using sync fallback: {e}")
        return filter_instance.filter_results_sync_fallback(state)