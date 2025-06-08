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
    DEFAULT_K_VALUE, ENHANCED_K_VALUE, TEST_ENV
)

class PineconeSearchClient:
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
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
        all_results = {}
        for query in queries:
            try:
                embedding = self._get_embedding(query)
                filter_dict = {}
                if domain_filter:
                    filter_dict["domain"] = domain_filter.value
                
                response = self.index.query(
                    vector=embedding,
                    top_k=k,
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
                print(f"Search error for query '{query}': {e}")
                continue
        
        sorted_results = sorted(
            all_results.values(), 
            key=lambda x: x.score, 
            reverse=True
        )[:k]

        if TEST_ENV:
            print(f"\n🌲 [DEBUG PineconeSearch] Zwrócono {len(sorted_results)} wyników. Top 5:")
            for i, res in enumerate(sorted_results[:5]):
                product_name = res.metadata.get('product_name', 'Brak nazwy')
                score = res.score
                print(f"   {i+1}. '{product_name}' (Score: {score:.4f})")
        
        return sorted_results
    
    def _check_domain_conflict(self, results: List[SearchResult]) -> Optional[str]:
        """Check if results contain mixed domains"""
        domains = {r.metadata.get("domain") for r in results if r.metadata.get("domain")}
        return "⚠️ Found products for both marine and freshwater aquariums. Please specify which type!" if len(domains) > 1 else None

def search_products_k15(state: ConversationState) -> ConversationState:
    """Search with k=15 (initial search)"""
    client = PineconeSearchClient()
    results = client.search(
        queries=state["optimized_queries"],
        k=DEFAULT_K_VALUE,
        domain_filter=state.get("domain_filter")
    )
    
    # First, check for domain conflicts using the model instances
    domain_warning = client._check_domain_conflict(results)
    if domain_warning and not state.get("domain_filter"):
        state["domain_warning"] = domain_warning
        
    # Then, serialize the results for the state dictionary
    state["search_results"] = [{"id": r.id, "score": r.score, "metadata": r.metadata} for r in results]
    
    return state

def enhanced_search_k20(state: ConversationState) -> ConversationState:
    """This function is kept for potential future use but is removed from the main workflow."""
    return search_products_k15(state) # For now, it does the same as the initial search