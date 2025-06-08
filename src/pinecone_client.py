"""
Pinecone Search Module
Handles all interactions with Pinecone vector database
"""
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from models import ConversationState, SearchResult, Domain
from config import (
    PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENVIRONMENT,
    OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL,
    DEFAULT_K_VALUE, ENHANCED_K_VALUE
)

class PineconeSearchClient:
    def __init__(self):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        
        # Initialize OpenAI for embeddings
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text using OpenAI"""
        response = self.openai_client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def search(
        self, 
        queries: List[str], 
        k: int = DEFAULT_K_VALUE,
        domain_filter: Optional[Domain] = None
    ) -> List[SearchResult]:
        """
        Search Pinecone with multiple queries and merge results
        """
        all_results = {}  # id -> SearchResult
        
        for query in queries:
            try:
                # Get embedding
                embedding = self._get_embedding(query)
                
                # Prepare filter
                filter_dict = {}
                if domain_filter:
                    filter_dict["domain"] = domain_filter.value
                
                # Search Pinecone
                response = self.index.query(
                    vector=embedding,
                    top_k=k,
                    include_metadata=True,
                    filter=filter_dict if filter_dict else None,
                    namespace="aqua"
                )
                
                # Process results
                for match in response['matches']:
                    result_id = match['id']
                    score = match['score']
                    
                    # Keep highest scoring version
                    if result_id not in all_results or score > all_results[result_id].score:
                        all_results[result_id] = SearchResult(
                            id=result_id,
                            score=score,
                            metadata=match.get('metadata', {})
                        )
                        
            except Exception as e:
                print(f"Search error for query '{query}': {e}")
                continue
        
        # Sort by score and return top k
        sorted_results = sorted(
            all_results.values(), 
            key=lambda x: x.score, 
            reverse=True
        )[:k]
        
        return sorted_results
    
    def _check_domain_conflict(self, results: List[SearchResult]) -> Optional[str]:
        """Check if results contain mixed domains"""
        domains = set(r.domain for r in results if r.domain)
        if len(domains) > 1:
            return "⚠️ Found products for both marine and freshwater aquariums. Please specify which type!"
        return None

def search_products_k15(state: ConversationState) -> ConversationState:
    """Search with k=15 (initial search)"""
    client = PineconeSearchClient()
    
    results = client.search(
        queries=state["optimized_queries"],
        k=DEFAULT_K_VALUE,
        domain_filter=state.get("domain_filter")
    )
    
    # Convert to dict format for state
    state["search_results"] = [
        {
            "id": r.id,
            "score": r.score,
            "metadata": r.metadata
        }
        for r in results
    ]
    
    # Check for domain conflicts
    domain_warning = client._check_domain_conflict(results)
    if domain_warning and not state.get("domain_filter"):
        state["domain_warning"] = domain_warning
    
    state["iteration"] = 1
    return state

def enhanced_search_k20(state: ConversationState) -> ConversationState:
    """Enhanced search with k=20 (retry with more results)"""
    client = PineconeSearchClient()
    
    # Add more query variations for second attempt
    enhanced_queries = state["optimized_queries"].copy()
    
    # Add problem-focused queries
    if "high nitrates" in state["original_query"].lower():
        enhanced_queries.append("nitrate removal biological")
    if "brown" in state["original_query"].lower() or "brązow" in state["original_query"].lower():
        enhanced_queries.append("coral browning nutrient control")
    if "algae" in state["original_query"].lower() or "glon" in state["original_query"].lower():
        enhanced_queries.append("algae control phosphate removal")
    
    results = client.search(
        queries=enhanced_queries,
        k=ENHANCED_K_VALUE,
        domain_filter=state.get("domain_filter")
    )
    
    # Update results
    state["search_results"] = [
        {
            "id": r.id,
            "score": r.score,
            "metadata": r.metadata
        }
        for r in results
    ]
    
    state["iteration"] = 2
    return state