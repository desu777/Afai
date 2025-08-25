"""
Semantic Search Module for Pinecone Optimization

Optimized vector search combining batch embedding generation with parallel Pinecone queries.
Integrates with BatchEmbeddingGenerator for maximum efficiency.
"""

from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor
from models import SearchResult, Domain
from config import debug_print, MAX_CONCURRENT_QUERIES
from .batch_embeddings import BatchEmbeddingGenerator


class SemanticSearcher:
    """
    Handles optimized semantic search using batch embeddings and parallel queries.
    
    This searcher combines batch embedding generation with concurrent Pinecone
    queries to minimize total search time while maintaining search quality.
    """
    
    def __init__(self, index, openai_client):
        """
        Initialize SemanticSearcher with Pinecone index and OpenAI client.
        
        Args:
            index: Pinecone index instance
            openai_client: OpenAI client for embedding generation
        """
        self.index = index
        self.openai_client = openai_client
        self.batch_generator = BatchEmbeddingGenerator(openai_client)
    
    def batch_search(
        self, 
        queries: List[str], 
        k: int = 12, 
        domain_filter: Optional[Domain] = None
    ) -> Dict[str, SearchResult]:
        """
        Perform optimized batch semantic search.
        
        This method is the core optimization combining:
        1. Batch embedding generation (1 API call vs N calls)
        2. Parallel Pinecone queries (concurrent execution)
        
        Args:
            queries: List of search queries
            k: Number of results per query
            domain_filter: Optional domain constraint
            
        Returns:
            Dictionary mapping result IDs to SearchResult objects
        """
        if not queries:
            return {}
        
        debug_print(f"[SEMANTIC] SS Batch search: {len(queries)} queries, K={k}")
        
        # Step 1: Generate all embeddings in batch
        embeddings = self.batch_generator.generate_batch(queries)
        
        # Step 2: Execute parallel vector searches
        return self._execute_parallel_searches(queries, embeddings, k, domain_filter)
    
    def _execute_parallel_searches(
        self,
        queries: List[str],
        embeddings: List[Optional[List[float]]],
        k: int,
        domain_filter: Optional[Domain] = None
    ) -> Dict[str, SearchResult]:
        """
        Execute multiple vector searches in parallel.
        
        Args:
            queries: Original query texts
            embeddings: Generated embeddings (same order as queries)
            k: Results per query
            domain_filter: Optional domain constraint
            
        Returns:
            Combined search results from all queries
        """
        all_results = {}
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_QUERIES) as executor:
            futures = []
            
            for i, (query, embedding) in enumerate(zip(queries, embeddings)):
                if embedding is not None:
                    future = executor.submit(
                        self._single_vector_query,
                        query, embedding, k, domain_filter
                    )
                    futures.append((query, future))
                else:
                    debug_print(f"[SEMANTIC] SS Skipping query with null embedding: {query[:50]}")
            
            # Collect results from all parallel searches
            for query, future in futures:
                try:
                    query_results = future.result()
                    for result_id, result in query_results.items():
                        # Keep highest score if duplicate found across queries
                        if result_id not in all_results or result.score > all_results[result_id].score:
                            all_results[result_id] = result
                            
                except Exception as e:
                    debug_print(f"[ERROR] SS Query failed '{query[:30]}': {str(e)[:50]}")
        
        debug_print(f"[SEMANTIC] SS Batch complete: {len(all_results)} unique results")
        return all_results
    
    def _single_vector_query(
        self,
        query: str,
        embedding: List[float],
        k: int,
        domain_filter: Optional[Domain] = None
    ) -> Dict[str, SearchResult]:
        """
        Execute a single vector search query against Pinecone.
        
        Args:
            query: Original query text (for logging)
            embedding: Pre-generated embedding vector
            k: Number of results to return
            domain_filter: Optional domain constraint
            
        Returns:
            Dictionary of results from this query
        """
        try:
            filter_dict = {}
            if domain_filter:
                filter_dict["domain"] = {
                    "$in": [domain_filter.value, Domain.UNIVERSAL.value]
                }
            
            response = self.index.query(
                vector=embedding,
                top_k=k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None,
                namespace="aqua"
            )
            
            results = {}
            for match in response.get('matches', []):
                results[match['id']] = SearchResult(
                    id=match['id'],
                    score=match['score'],
                    metadata=match.get('metadata', {})
                )
            
            return results
            
        except Exception as e:
            debug_print(f"[ERROR] SS Single query failed: {str(e)[:50]}")
            return {}
    
    def search_with_fallback(
        self,
        queries: List[str],
        k: int = 12,
        domain_filter: Optional[Domain] = None,
        max_retries: int = 1
    ) -> Dict[str, SearchResult]:
        """
        Perform semantic search with automatic retry and fallback.
        
        This method provides additional reliability by retrying failed
        operations and gracefully handling partial failures.
        
        Args:
            queries: List of search queries
            k: Number of results per query
            domain_filter: Optional domain constraint
            max_retries: Maximum retry attempts
            
        Returns:
            Dictionary of search results
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    debug_print(f"[SEMANTIC] SS Retry attempt {attempt}/{max_retries}")
                
                return self.batch_search(queries, k, domain_filter)
                
            except Exception as e:
                if attempt < max_retries:
                    debug_print(f"[SEMANTIC] SS Attempt {attempt + 1} failed: {str(e)[:50]}")
                    continue
                else:
                    debug_print(f"[ERROR] SS All attempts failed: {str(e)[:50]}")
                    return self._fallback_individual_search(queries, k, domain_filter)
        
        return {}
    
    def _fallback_individual_search(
        self,
        queries: List[str],
        k: int,
        domain_filter: Optional[Domain] = None
    ) -> Dict[str, SearchResult]:
        """
        Fallback to individual query processing when batch fails.
        
        Args:
            queries: List of search queries
            k: Number of results per query
            domain_filter: Optional domain constraint
            
        Returns:
            Combined results from individual searches
        """
        debug_print(f"[FALLBACK] SS Individual search for {len(queries)} queries")
        
        all_results = {}
        
        for query in queries:
            try:
                # Generate single embedding
                embedding = self.batch_generator._generate_single_embedding(query)
                
                # Execute single search
                query_results = self._single_vector_query(query, embedding, k, domain_filter)
                
                # Merge results
                for result_id, result in query_results.items():
                    if result_id not in all_results or result.score > all_results[result_id].score:
                        all_results[result_id] = result
                        
            except Exception as e:
                debug_print(f"[ERROR] SS Fallback query failed '{query[:30]}': {str(e)[:50]}")
        
        debug_print(f"[FALLBACK] SS Individual complete: {len(all_results)} results")
        return all_results
    
    def estimate_performance_gain(self, num_queries: int) -> dict:
        """
        Calculate estimated performance improvements from optimization.
        
        Args:
            num_queries: Number of queries to process
            
        Returns:
            Performance metrics and estimates
        """
        # Traditional approach: sequential embedding + search
        traditional_time_ms = num_queries * (200 + 100)  # 200ms embedding + 100ms search
        
        # Optimized approach: batch embedding + parallel search  
        optimized_time_ms = 200 + 100  # Single batch embedding + parallel searches
        
        savings_ms = traditional_time_ms - optimized_time_ms
        savings_percent = (savings_ms / traditional_time_ms) * 100 if traditional_time_ms > 0 else 0
        
        return {
            "traditional_time_ms": traditional_time_ms,
            "optimized_time_ms": optimized_time_ms,
            "savings_ms": savings_ms,
            "savings_percent": round(savings_percent, 1),
            "queries_count": num_queries,
            "parallel_factor": min(num_queries, MAX_CONCURRENT_QUERIES)
        }