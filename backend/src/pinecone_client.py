"""
Pinecone Search Module - Enhanced with Parallel Search Architecture
Handles all interactions with Pinecone vector database with concurrent processing
"""
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from models import ConversationState, SearchResult, Domain
from config import (
    PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENVIRONMENT,
    OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL,
    DEFAULT_K_VALUE, ENHANCED_K_VALUE, TEST_ENV, debug_print,
    MAX_CONCURRENT_QUERIES, MAX_CONCURRENT_EMBEDDINGS, 
    PINECONE_POOL_THREADS, PINECONE_CONNECTION_POOL_MAX,
    ENABLE_PARALLEL_SEARCH
)
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class PineconeSearchClient:
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        # [PERF] PERFORMANCE: Configure connection pool for parallel operations
        self.index = self.pc.Index(
            PINECONE_INDEX_NAME,
            pool_threads=PINECONE_POOL_THREADS,
            connection_pool_maxsize=PINECONE_CONNECTION_POOL_MAX
        )
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text using OpenAI"""
        response = self.openai_client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def _detect_domain_from_context(self, state: ConversationState) -> Optional[Domain]:
        """Detect domain from conversation context"""
        if state.get("domain_filter"):
            # Handle both string and Domain enum from business_reasoner
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
        
        # Analyze recent conversation for domain clues
        context_text = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-6:]  # Last 3 exchanges
            context_text = " ".join([msg["content"].lower() for msg in recent_messages])
        
        # Add current query
        context_text += " " + state.get("user_query", "").lower()
        
        # Domain detection rules
        freshwater_keywords = ["freshwater", "gupik", "neon", "goldfish", "fresh water", "tropical fish"]
        marine_keywords = ["marine", "saltwater", "reef", "coral", "salt water", "koral"]
        
        freshwater_score = sum(1 for keyword in freshwater_keywords if keyword in context_text)
        marine_score = sum(1 for keyword in marine_keywords if keyword in context_text)
        
        debug_print(f"[SEARCH] PC Freshwater: {freshwater_score}, Marine: {marine_score}")
        
        if freshwater_score > marine_score:
            return Domain.FRESHWATER
        elif marine_score > freshwater_score:
            return Domain.SEAWATER
        
        return None  # No clear domain detected
    
    def search(
        self, 
        queries: List[str], 
        k: int = None,  # [NEW] DYNAMIC: Default to None, will use ENHANCED_K_VALUE
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        [NEW] HYBRID SEARCH: Combines vector search with guaranteed product search
        Now with dynamic K value from ENHANCED_K_VALUE
        """
        # [PERF] PARALLEL SEARCH: Route to parallel or sequential based on configuration
        if ENABLE_PARALLEL_SEARCH:
            return self._parallel_search(queries, k, state)
        else:
            return self._sequential_search(queries, k, state)
    
    def _sequential_search(
        self, 
        queries: List[str], 
        k: int = None,
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        [DATA] SEQUENTIAL SEARCH: Original implementation (fallback)
        """
        # [NEW] DYNAMIC K VALUE
        if k is None:
            k = ENHANCED_K_VALUE
        
        if TEST_ENV:
            print(f"[SEARCH] PC Dynamic K={k} (ENHANCED={ENHANCED_K_VALUE})")
        
        # Auto-detect domain if not explicitly set
        domain_filter = None
        if state:
            domain_filter = self._detect_domain_from_context(state)
            if domain_filter:
                debug_print(f"[TARGET] PC Domain: {domain_filter.value}")
        
        # [NEW] HYBRID SEARCH: Extract critical products for guaranteed search
        critical_products = []
        if state and state.get("business_analysis"):
            ba = state["business_analysis"]
            # Add corrected product names
            if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                critical_products.append(ba["product_name_corrections"])
            
            # Add products from category
            products_in_category = ba.get('products_in_category', [])
            if isinstance(products_in_category, list):
                critical_products.extend(products_in_category)
        
        # [PERF] ENHANCED: Add AF alternatives from Business Reasoner
        if state and state.get("af_alternatives_to_search"):
            af_alternatives = state["af_alternatives_to_search"]
            debug_print(f"[TARGET] PC AF alts: {af_alternatives}")
            critical_products.extend(af_alternatives)
        
        # Extract mentioned products from queries (first few queries are usually critical)
        mentioned_products = []
        for query in queries[:5]:  # Check first 5 queries for product names
            query_words = query.split()
            for word in query_words:
                if word in ["Zeo", "Mix"] and "Zeo Mix" not in mentioned_products:
                    mentioned_products.append("Zeo Mix")
                elif word in ["Ca", "Plus"] and "Ca Plus" not in mentioned_products:
                    mentioned_products.append("Ca Plus")
                elif word in ["AF", "NitraPhos", "Minus"] and "AF NitraPhos Minus" not in mentioned_products:
                    mentioned_products.append("AF NitraPhos Minus")
                elif word in ["Pro", "Bio", "S"] and "Pro Bio S" not in mentioned_products:
                    mentioned_products.append("Pro Bio S")
        
        critical_products.extend(mentioned_products)
        critical_products = list(set(critical_products))  # Remove duplicates
        
        # [NEW] GUARANTEED SEARCH for critical products + collect not found
        guaranteed_results = {}
        fallback_queries = []  # [NEW] Collect products not found for vector search
        if critical_products:
            debug_print(f"[TARGET] PC Guaranteed: {critical_products}")
            guaranteed, not_found_products = self._guaranteed_product_search(critical_products, domain_filter)
            for result in guaranteed:
                guaranteed_results[result.id] = result
            
            # [NEW] FALLBACK: Add not found products to vector search
            if not_found_products:
                fallback_queries.extend(not_found_products)
                debug_print(f"[INFO] PC Fallback: {len(not_found_products)} not found: {not_found_products}")
        
        # [NEW] VECTOR SEARCH for all queries + fallback queries
        all_queries = queries + fallback_queries  # [NEW] Include fallback queries
        all_results = {}
        for query in all_queries:
            try:
                embedding = self._get_embedding(query)
                filter_dict = {}
                if domain_filter:
                    # Include both specific domain and universal products
                    filter_dict["domain"] = {"$in": [domain_filter.value, Domain.UNIVERSAL.value]}
                
                response = self.index.query(
                    vector=embedding,
                    top_k=k,  # [NEW] DYNAMIC K VALUE
                    include_metadata=True,
                    filter=filter_dict if filter_dict else None,
                    namespace="aqua"
                )
                
                for match in response['matches']:
                    result_id = match['id']
                    score = match['score']
                    if result_id not in all_results or score > all_results[result_id].score:
                        all_results[result_id] = SearchResult(
                            id=result_id,
                            score=score,
                            metadata=match.get('metadata', {})
                        )
            except Exception as e:
                if TEST_ENV:
                    print(f"[ERROR] PC Search error '{query}': {str(e)[:30]}")
                continue
        
        # [PERF] ENHANCED: K + AF alternatives mechanism
        final_results = {}
        final_results.update(all_results)  # Add vector results first
        final_results.update(guaranteed_results)  # Override with guaranteed results (higher scores)
        
        # Separate guaranteed AF alternatives from other results
        guaranteed_af_results = []
        other_results = []
        af_alternatives = state.get("af_alternatives_to_search", []) if state else []
        
        for result in final_results.values():
            product_name = result.metadata.get('product_name', '')
            if product_name in af_alternatives:
                guaranteed_af_results.append(result)
            else:
                other_results.append(result)
        
        # Sort both groups by score
        guaranteed_af_results.sort(key=lambda x: x.score, reverse=True)
        other_results.sort(key=lambda x: x.score, reverse=True)
        
        # [TARGET] K + AF alternatives: Take all AF alternatives + top K others
        final_count = len(guaranteed_af_results) + min(k, len(other_results))
        sorted_results = guaranteed_af_results + other_results[:k]
        
        debug_print(f"[TARGET] PC K+AF: {len(guaranteed_af_results)} AF + {min(k, len(other_results))} vec = {len(sorted_results)}")

        debug_print(f"[DATA] PC Hybrid: {len(guaranteed_results)} guar + {len(all_results)} vec = {len(sorted_results)} (K={k})")
        for i, res in enumerate(sorted_results[:5]):
            product_name = res.metadata.get('product_name', 'Brak nazwy')
            domain = res.metadata.get('domain', 'N/A')
            score = res.score
            guaranteed_marker = "[TARGET]" if res.id in guaranteed_results else ""
            debug_print(f"   {i+1}. '{product_name}' [Domain: {domain}] (Score: {score:.4f}) {guaranteed_marker}")
        
        return sorted_results
    
    def _check_domain_conflict(self, results: List[SearchResult]) -> Optional[str]:
        """Check if results contain mixed domains"""
        domains = {r.metadata.get("domain") for r in results if r.metadata.get("domain")}
        # Don't warn if we have universal products
        domains.discard(Domain.UNIVERSAL.value)
        return "[WARN] Found products for both marine and freshwater aquariums. Please specify which type!" if len(domains) > 1 else None

    def _parallel_search(
        self, 
        queries: List[str], 
        k: int = None,
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        [PERF] PARALLEL SEARCH: Concurrent guaranteed + vector search with backup
        """
        start_time = time.time()
        
        # [NEW] DYNAMIC K VALUE
        if k is None:
            k = ENHANCED_K_VALUE
        
        debug_print(f"[PERF] PS Start K={k}")
        
        # Auto-detect domain if not explicitly set
        domain_filter = None
        if state:
            domain_filter = self._detect_domain_from_context(state)
            if domain_filter:
                debug_print(f"[TARGET] PS Domain: {domain_filter.value}")
        
        # Extract critical products for guaranteed search
        critical_products = self._extract_critical_products(queries, state)
        
        # [PERF] PARALLEL EXECUTION: Run guaranteed + vector search concurrently
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_QUERIES) as executor:
            futures = {}
            
            # [TARGET] GUARANTEED SEARCH (Thread 1)
            if critical_products:
                futures['guaranteed'] = executor.submit(
                    self._optimized_guaranteed_search, critical_products, domain_filter
                )
            
            # [SEARCH] VECTOR SEARCH (Thread 2)
            futures['vector'] = executor.submit(
                self._parallel_vector_search, queries, k, domain_filter
            )
            
            # [OK] COLLECT RESULTS
            guaranteed_results = {}
            not_found_products = []
            vector_results = {}
            
            for future_name, future in futures.items():
                try:
                    if future_name == 'guaranteed':
                        guaranteed, not_found = future.result()
                        for result in guaranteed:
                            guaranteed_results[result.id] = result
                        not_found_products = not_found
                    elif future_name == 'vector':
                        vector_results = future.result()
                except Exception as e:
                    debug_print(f"[ERROR] PS {future_name}: {str(e)[:30]}")
            
            # [INFO] BACKUP SEARCH for not found products
            if not_found_products:
                debug_print(f"[INFO] PS Backup: {not_found_products}")
                backup_future = executor.submit(
                    self._semantic_backup_search, not_found_products, k, domain_filter
                )
                try:
                    backup_results = backup_future.result()
                    # Merge backup results with vector results
                    for result_id, result in backup_results.items():
                        if result_id not in vector_results:
                            vector_results[result_id] = result
                except Exception as e:
                    debug_print(f"[ERROR] PS Backup: {str(e)[:30]}")
        
        # [TARGET] MERGE AND PRIORITIZE RESULTS
        final_results = self._merge_search_results(
            guaranteed_results, vector_results, state, k
        )
        
        execution_time = time.time() - start_time
        debug_print(f"[PERF] PS Done {execution_time:.3f}s - {len(final_results)} results")
        
        return final_results

    def _guaranteed_product_search(self, product_names: List[str], domain_filter: Optional[Domain] = None) -> tuple[List[SearchResult], List[str]]:
        """
        Guaranteed search for specific products using metadata filtering
        Returns: (found_results, not_found_product_names)
        """
        guaranteed_results = []
        not_found_products = []  # [NEW] Track products not found for fallback
        
        for product_name in product_names:
            try:
                # Use metadata filter to find exact product
                filter_dict = {"product_name": product_name}
                if domain_filter:
                    filter_dict["domain"] = {"$in": [domain_filter.value, Domain.UNIVERSAL.value]}
                
                # Use dummy vector for metadata-only search
                dummy_vector = [0.0] * 1536  # OpenAI embedding dimension
                
                response = self.index.query(
                    vector=dummy_vector,
                    top_k=1,
                    include_metadata=True,
                    filter=filter_dict,
                    namespace="aqua"
                )
                
                if response['matches']:
                    match = response['matches'][0]
                    guaranteed_results.append(SearchResult(
                        id=match['id'],
                        score=0.99,  # High score to ensure it appears at top
                        metadata=match.get('metadata', {})
                    ))
                    debug_print(f"[OK] PC Found: {product_name}")
                else:
                    debug_print(f"[WARN] PC Not found: {product_name}")
                    not_found_products.append(product_name)  # [NEW] Add to fallback list
                    
            except Exception as e:
                debug_print(f"[ERROR] PC Guaranteed {product_name}: {str(e)[:30]}")
                not_found_products.append(product_name)  # [NEW] Add to fallback list on error
        
        return guaranteed_results, not_found_products  # �� Return both lists

    def _extract_critical_products(self, queries: List[str], state: Optional[ConversationState] = None) -> List[str]:
        """Extract critical products from queries and state"""
        critical_products = []
        
        if state and state.get("business_analysis"):
            ba = state["business_analysis"]
            # Add corrected product names
            if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                critical_products.append(ba["product_name_corrections"])
            
            # Add products from category
            products_in_category = ba.get('products_in_category', [])
            if isinstance(products_in_category, list):
                critical_products.extend(products_in_category)
        
        # [PERF] ENHANCED: Add AF alternatives from Business Reasoner
        if state and state.get("af_alternatives_to_search"):
            af_alternatives = state["af_alternatives_to_search"]
            debug_print(f"[TARGET] Extract AF: {af_alternatives}")
            critical_products.extend(af_alternatives)
        
        # Extract mentioned products from queries
        mentioned_products = []
        for query in queries[:5]:  # Check first 5 queries for product names
            query_words = query.split()
            for word in query_words:
                if word in ["Zeo", "Mix"] and "Zeo Mix" not in mentioned_products:
                    mentioned_products.append("Zeo Mix")
                elif word in ["Ca", "Plus"] and "Ca Plus" not in mentioned_products:
                    mentioned_products.append("Ca Plus")
                elif word in ["AF", "NitraPhos", "Minus"] and "AF NitraPhos Minus" not in mentioned_products:
                    mentioned_products.append("AF NitraPhos Minus")
                elif word in ["Pro", "Bio", "S"] and "Pro Bio S" not in mentioned_products:
                    mentioned_products.append("Pro Bio S")
        
        critical_products.extend(mentioned_products)
        return list(set(critical_products))  # Remove duplicates

    def _optimized_guaranteed_search(self, product_names: List[str], domain_filter: Optional[Domain] = None) -> tuple[List[SearchResult], List[str]]:
        """
        [PERF] OPTIMIZED: Guaranteed search without dummy vectors
        """
        guaranteed_results = []
        not_found_products = []
        
        debug_print(f"[TARGET] OG Search: {product_names}")
        
        for product_name in product_names:
            try:
                # Use metadata filter to find exact product
                filter_dict = {"product_name": product_name}
                if domain_filter:
                    filter_dict["domain"] = {"$in": [domain_filter.value, Domain.UNIVERSAL.value]}
                
                # [PERF] OPTIMIZED: Use zero vector instead of dummy vector
                zero_vector = [0.0] * 1536  # OpenAI embedding dimension
                
                response = self.index.query(
                    vector=zero_vector,
                    top_k=1,
                    include_metadata=True,
                    filter=filter_dict,
                    namespace="aqua"
                )
                
                if response['matches']:
                    match = response['matches'][0]
                    guaranteed_results.append(SearchResult(
                        id=match['id'],
                        score=0.99,  # High score to ensure it appears at top
                        metadata=match.get('metadata', {})
                    ))
                    debug_print(f"[OK] OG Found: {product_name}")
                else:
                    debug_print(f"[WARN] OG Not found: {product_name}")
                    not_found_products.append(product_name)
                    
            except Exception as e:
                debug_print(f"[ERROR] OG {product_name}: {str(e)[:30]}")
                not_found_products.append(product_name)
        
        return guaranteed_results, not_found_products

    def _parallel_vector_search(self, queries: List[str], k: int, domain_filter: Optional[Domain] = None) -> Dict[str, SearchResult]:
        """
        [PERF] PARALLEL: Vector search with concurrent embedding generation
        """
        debug_print(f"[SEARCH] PV {len(queries)} queries K={k}")
        
        # [PERF] PARALLEL EMBEDDING GENERATION
        embeddings = self._parallel_embedding_generation(queries)
        
        # [PERF] PARALLEL PINECONE QUERIES
        all_results = {}
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_QUERIES) as executor:
            futures = []
            
            for i, (query, embedding) in enumerate(zip(queries, embeddings)):
                if embedding is not None:  # Skip failed embeddings
                    future = executor.submit(
                        self._single_vector_query, query, embedding, k, domain_filter
                    )
                    futures.append((query, future))
            
            # Collect results
            for query, future in futures:
                try:
                    results = future.result()
                    for result_id, result in results.items():
                        # Keep highest score if duplicate
                        if result_id not in all_results or result.score > all_results[result_id].score:
                            all_results[result_id] = result
                except Exception as e:
                    debug_print(f"[ERROR] PV '{query}': {str(e)[:30]}")
        
        debug_print(f"[SEARCH] PV Done - {len(all_results)} results")
        return all_results

    def _parallel_embedding_generation(self, queries: List[str]) -> List[Optional[List[float]]]:
        """
        [PERF] PARALLEL: Generate embeddings concurrently
        """
        embeddings = [None] * len(queries)
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_EMBEDDINGS) as executor:
            futures = {executor.submit(self._get_embedding, query): i for i, query in enumerate(queries)}
            
            for future in as_completed(futures):
                i = futures[future]
                try:
                    embeddings[i] = future.result()
                except Exception as e:
                    debug_print(f"[ERROR] PE Query {i}: {str(e)[:30]}")
                    embeddings[i] = None
        
        return embeddings

    def _single_vector_query(self, query: str, embedding: List[float], k: int, domain_filter: Optional[Domain] = None) -> Dict[str, SearchResult]:
        """
        [SEARCH] SINGLE: Execute single vector query
        """
        filter_dict = {}
        if domain_filter:
            filter_dict["domain"] = {"$in": [domain_filter.value, Domain.UNIVERSAL.value]}
        
        response = self.index.query(
            vector=embedding,
            top_k=k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None,
            namespace="aqua"
        )
        
        results = {}
        for match in response['matches']:
            results[match['id']] = SearchResult(
                id=match['id'],
                score=match['score'],
                metadata=match.get('metadata', {})
            )
        
        return results

    def _semantic_backup_search(self, not_found_products: List[str], k: int, domain_filter: Optional[Domain] = None) -> Dict[str, SearchResult]:
        """
        [INFO] BACKUP: Semantic search for products not found in guaranteed search
        """
        debug_print(f"[INFO] SB {len(not_found_products)} products")
        
        # Use parallel vector search for backup
        return self._parallel_vector_search(not_found_products, k, domain_filter)

    def _merge_search_results(self, guaranteed_results: Dict[str, SearchResult], vector_results: Dict[str, SearchResult], state: Optional[ConversationState] = None, k: int = 20) -> List[SearchResult]:
        """
        [TARGET] MERGE: Combine guaranteed, vector, and backup results with proper prioritization
        """
        # Merge all results
        final_results = {}
        final_results.update(vector_results)  # Add vector results first
        final_results.update(guaranteed_results)  # Override with guaranteed results (higher priority)
        
        # Separate guaranteed AF alternatives from other results
        guaranteed_af_results = []
        other_results = []
        af_alternatives = state.get("af_alternatives_to_search", []) if state else []
        
        for result in final_results.values():
            product_name = result.metadata.get('product_name', '')
            if product_name in af_alternatives:
                guaranteed_af_results.append(result)
            else:
                other_results.append(result)
        
        # Sort both groups by score
        guaranteed_af_results.sort(key=lambda x: x.score, reverse=True)
        other_results.sort(key=lambda x: x.score, reverse=True)
        
        # [TARGET] K + AF alternatives: Take all AF alternatives + top K others
        sorted_results = guaranteed_af_results + other_results[:k]
        
        debug_print(f"[TARGET] MR Final: {len(guaranteed_af_results)} AF + {min(k, len(other_results))} = {len(sorted_results)}")
        
        # Debug output
        for i, res in enumerate(sorted_results[:5]):
            product_name = res.metadata.get('product_name', 'Brak nazwy')
            domain = res.metadata.get('domain', 'N/A')
            score = res.score
            guaranteed_marker = "[TARGET]" if res.id in guaranteed_results else ""
            debug_print(f"   {i+1}. '{product_name}' [Domain: {domain}] (Score: {score:.4f}) {guaranteed_marker}")
        
        return sorted_results

# [NEW] UPDATED FUNCTIONS - now use dynamic ENHANCED_K_VALUE
def search_products_k20(state: ConversationState) -> ConversationState:
    """[NEW] UPDATED: Uses dynamic ENHANCED_K_VALUE instead of hardcoded k=20"""
    client = PineconeSearchClient()
    results = client.search(
        queries=state["optimized_queries"],
        k=ENHANCED_K_VALUE,  # [NEW] DYNAMIC K VALUE FROM ENV
        state=state  # Pass the full state for context analysis
    )
    
    # First, check for domain conflicts using the model instances
    domain_warning = client._check_domain_conflict(results)
    if domain_warning and not state.get("domain_filter"):
        state["domain_warning"] = domain_warning
        
    # Then, serialize the results for the state dictionary
    state["search_results"] = [{"id": r.id, "score": r.score, "metadata": r.metadata} for r in results]
    
    if TEST_ENV:
        print(f"[TARGET] PC Stored {len(state['search_results'])} K={ENHANCED_K_VALUE}")
    
    return state

def enhanced_search_k20(state: ConversationState) -> ConversationState:
    """[NEW] UPDATED: Uses dynamic ENHANCED_K_VALUE instead of hardcoded k=20"""
    return search_products_k20(state)