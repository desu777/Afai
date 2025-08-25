"""
Pinecone Search Client - Optimized Modular Architecture
Main interface for Pinecone vector database operations with advanced optimizations
"""
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from openai import OpenAI
from models import ConversationState, SearchResult, Domain
from config import (
    PINECONE_API_KEY, PINECONE_INDEX_NAME, OPENAI_API_KEY,
    ENHANCED_K_VALUE, TEST_ENV, debug_print,
    PINECONE_POOL_THREADS, PINECONE_CONNECTION_POOL_MAX,
    ENABLE_PARALLEL_SEARCH
)
from concurrent.futures import ThreadPoolExecutor
import time

# Import optimized search modules
from pinecone_search import (
    MetadataSearcher,
    SemanticSearcher,
    SearchOptimizer,
    ResultMerger
)


class PineconeSearchClient:
    """
    Optimized Pinecone search client using modular architecture.
    
    This client provides ultra-fast search capabilities by combining:
    - Metadata-first search (no embeddings needed)
    - Batch semantic search (optimized embedding generation)
    - Intelligent result merging with proper prioritization
    """
    
    def __init__(self):
        """Initialize PineconeSearchClient with optimized modules."""
        # Initialize Pinecone connection
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(
            PINECONE_INDEX_NAME,
            pool_threads=PINECONE_POOL_THREADS,
            connection_pool_maxsize=PINECONE_CONNECTION_POOL_MAX
        )
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Initialize optimization modules
        self.metadata_searcher = MetadataSearcher(self.index)
        self.semantic_searcher = SemanticSearcher(self.index, self.openai_client)
        self.search_optimizer = SearchOptimizer()
        self.result_merger = ResultMerger()
        
        debug_print("[OPTIMIZED] Pinecone client initialized with modular architecture")
    
    def search(
        self, 
        queries: List[str], 
        k: int = None,
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        Main search interface using optimized modular architecture.
        
        This method provides the fastest possible search by intelligently
        routing queries to appropriate search strategies.
        
        Args:
            queries: List of search queries
            k: Maximum results to return (defaults to ENHANCED_K_VALUE)
            state: Conversation state for context analysis
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        if k is None:
            k = ENHANCED_K_VALUE
        
        if not queries:
            return []
        
        debug_print(f"[OPTIMIZED] Search started: {len(queries)} queries, K={k}")
        
        # Route to optimized search implementation
        if ENABLE_PARALLEL_SEARCH:
            results = self._optimized_search(queries, k, state)
        else:
            # Fallback to basic optimization (still better than original)
            results = self._basic_optimized_search(queries, k, state)
        
        # Check for domain conflicts
        if results and state:
            domain_warning = self._check_domain_conflict(results)
            if domain_warning and not state.get("domain_filter"):
                state["domain_warning"] = domain_warning
        
        debug_print(f"[OPTIMIZED] Search completed: {len(results)} results returned")
        return results
    
    def _optimized_search(
        self, 
        queries: List[str], 
        k: int, 
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        Core optimized search using modular architecture.
        
        This method implements the complete optimization strategy:
        1. Intelligent query separation
        2. Parallel metadata + semantic search
        3. Advanced result merging
        """
        start_time = time.time()
        
        # Detect domain context
        domain_filter = self._detect_domain_from_context(state) if state else None
        if domain_filter:
            debug_print(f"[OPTIMIZED] Domain detected: {domain_filter.value}")
        
        # Separate query types using SearchOptimizer
        guaranteed_products, semantic_queries = self.search_optimizer.separate_search_types(queries, state)
        
        # Optimize semantic query count to reduce latency
        semantic_queries = self.search_optimizer.optimize_query_count(semantic_queries, max_semantic_queries=5)
        
        debug_print(f"[OPTIMIZED] Query separation: {len(guaranteed_products)} metadata, {len(semantic_queries)} semantic")
        
        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            # Metadata search for guaranteed products (ultra-fast)
            if guaranteed_products:
                futures['metadata'] = executor.submit(
                    self.metadata_searcher.bulk_search_products,
                    guaranteed_products, domain_filter, max_workers=5
                )
            
            # Semantic search for contextual queries (batch optimized)
            if semantic_queries:
                futures['semantic'] = executor.submit(
                    self.semantic_searcher.batch_search,
                    semantic_queries, k, domain_filter
                )
            
            # Collect results
            metadata_results = []
            semantic_results = {}
            not_found_products = []
            
            for search_type, future in futures.items():
                try:
                    if search_type == 'metadata':
                        found, not_found = future.result()
                        metadata_results = found
                        not_found_products = not_found
                        debug_print(f"[METADATA] Found {len(found)}, missing {len(not_found)}")
                    elif search_type == 'semantic':
                        semantic_results = future.result()
                        debug_print(f"[SEMANTIC] Found {len(semantic_results)} results")
                        
                except Exception as e:
                    debug_print(f"[ERROR] {search_type} search failed: {str(e)[:50]}")
            
            # Fallback semantic search for not found guaranteed products
            if not_found_products:
                debug_print(f"[FALLBACK] Semantic search for {len(not_found_products)} missing products")
                try:
                    fallback_future = executor.submit(
                        self.semantic_searcher.batch_search,
                        not_found_products, k, domain_filter
                    )
                    fallback_results = fallback_future.result()
                    
                    # Merge fallback with semantic results
                    for result_id, result in fallback_results.items():
                        if result_id not in semantic_results:
                            semantic_results[result_id] = result
                            
                except Exception as e:
                    debug_print(f"[ERROR] Fallback search failed: {str(e)[:50]}")
        
        # Merge results using ResultMerger
        final_results = self.result_merger.merge_results(
            metadata_results, semantic_results, state, k
        )
        
        execution_time = time.time() - start_time
        debug_print(f"[OPTIMIZED] Search completed in {execution_time:.3f}s - {len(final_results)} results")
        
        return final_results
    
    def _basic_optimized_search(
        self, 
        queries: List[str], 
        k: int, 
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        Basic optimized search for when parallel search is disabled.
        
        Still uses modular architecture but executes sequentially.
        """
        debug_print("[OPTIMIZED] Using basic optimization (sequential)")
        
        domain_filter = self._detect_domain_from_context(state) if state else None
        guaranteed_products, semantic_queries = self.search_optimizer.separate_search_types(queries, state)
        
        # Metadata search first (fast)
        metadata_results = []
        if guaranteed_products:
            found, not_found = self.metadata_searcher.search_products(guaranteed_products, domain_filter)
            metadata_results = found
        
        # Semantic search (optimized with batch embeddings)
        semantic_results = {}
        if semantic_queries:
            semantic_results = self.semantic_searcher.batch_search(semantic_queries, k, domain_filter)
        
        # Merge results
        final_results = self.result_merger.merge_results(
            metadata_results, semantic_results, state, k
        )
        
        return final_results
    
    def _detect_domain_from_context(self, state: ConversationState) -> Optional[Domain]:
        """
        Detect aquarium domain (freshwater/seawater) from conversation context.
        
        Args:
            state: Conversation state with query and history
            
        Returns:
            Domain enum or None if not detected
        """
        if not state:
            return None
        
        # Check explicit domain filter first
        if state.get("domain_filter"):
            domain_value = state["domain_filter"]
            if isinstance(domain_value, str):
                if domain_value.lower() == "freshwater":
                    return Domain.FRESHWATER
                elif domain_value.lower() in ["seawater", "marine"]:
                    return Domain.SEAWATER
                elif domain_value.lower() == "universal":
                    return Domain.UNIVERSAL
            else:
                return domain_value  # Already Domain enum
        
        # Analyze conversation context for domain clues
        context_text = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-6:]  # Last 3 exchanges
            context_text = " ".join([msg["content"].lower() for msg in recent_messages])
        
        # Add current query
        context_text += " " + state.get("user_query", "").lower()
        
        # Domain detection keywords
        freshwater_keywords = ["freshwater", "gupik", "neon", "goldfish", "fresh water", "tropical fish"]
        marine_keywords = ["marine", "saltwater", "reef", "coral", "salt water", "koral"]
        
        freshwater_score = sum(1 for keyword in freshwater_keywords if keyword in context_text)
        marine_score = sum(1 for keyword in marine_keywords if keyword in context_text)
        
        if freshwater_score > marine_score:
            debug_print(f"[DOMAIN] Detected freshwater (score: {freshwater_score} vs {marine_score})")
            return Domain.FRESHWATER
        elif marine_score > freshwater_score:
            debug_print(f"[DOMAIN] Detected marine (score: {marine_score} vs {freshwater_score})")
            return Domain.SEAWATER
        
        return None  # No clear domain detected
    
    def _check_domain_conflict(self, results: List[SearchResult]) -> Optional[str]:
        """
        Check if search results contain conflicting domains.
        
        Args:
            results: List of search results
            
        Returns:
            Warning message if domain conflict detected, None otherwise
        """
        domains = {r.metadata.get("domain") for r in results if r.metadata.get("domain")}
        # Don't warn about universal products
        domains.discard(Domain.UNIVERSAL.value)
        
        if len(domains) > 1:
            debug_print(f"[WARNING] Domain conflict detected: {domains}")
            return "[WARN] Found products for both marine and freshwater aquariums. Please specify which type!"
        
        return None


# Workflow interface functions (maintain compatibility)
def search_products_k20(state: ConversationState) -> ConversationState:
    """
    Main workflow interface for Pinecone search.
    
    This function maintains compatibility with existing LangGraph workflow
    while using the new optimized architecture underneath.
    """
    client = PineconeSearchClient()
    results = client.search(
        queries=state["optimized_queries"],
        k=ENHANCED_K_VALUE,
        state=state
    )
    
    # Check for domain conflicts
    domain_warning = client._check_domain_conflict(results)
    if domain_warning and not state.get("domain_filter"):
        state["domain_warning"] = domain_warning
    
    # Serialize results for state
    state["search_results"] = [
        {"id": r.id, "score": r.score, "metadata": r.metadata} 
        for r in results
    ]
    
    if TEST_ENV:
        print(f"[OPTIMIZED] Workflow stored {len(state['search_results'])} results (K={ENHANCED_K_VALUE})")
    
    return state


def enhanced_search_k20(state: ConversationState) -> ConversationState:
    """
    Enhanced search function alias for backward compatibility.
    
    Args:
        state: Conversation state with queries
        
    Returns:
        Updated state with search results
    """
    return search_products_k20(state)