"""
Pinecone Search Module - Enhanced with smart domain detection
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
    
    def _detect_domain_from_context(self, state: ConversationState) -> Optional[Domain]:
        """Detect domain from conversation context"""
        if state.get("domain_filter"):
            return state["domain_filter"]
        
        # Analyze recent conversation for domain clues
        context_text = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-6:]  # Last 3 exchanges
            context_text = " ".join([msg["content"].lower() for msg in recent_messages])
        
        # Add current query
        context_text += " " + state.get("user_query", "").lower()
        
        # Domain detection rules
        freshwater_keywords = ["słodkowod", "freshwater", "gupik", "neon", "złota rybka", "fresh water", "tropical fish"]
        marine_keywords = ["morsk", "marine", "saltwater", "reef", "coral", "salt water", "koral"]
        
        freshwater_score = sum(1 for keyword in freshwater_keywords if keyword in context_text)
        marine_score = sum(1 for keyword in marine_keywords if keyword in context_text)
        
        if TEST_ENV and (freshwater_score > 0 or marine_score > 0):
            print(f"\n🔍 [DEBUG Domain Detection] Freshwater score: {freshwater_score}, Marine score: {marine_score}")
        
        if freshwater_score > marine_score:
            return Domain.FRESHWATER
        elif marine_score > freshwater_score:
            return Domain.SEAWATER
        
        return None  # No clear domain detected
    
    def search(
        self, 
        queries: List[str], 
        k: int = DEFAULT_K_VALUE,
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        Search Pinecone with multiple queries and merge results
        Now with smart domain filtering based on context
        """
        # Auto-detect domain if not explicitly set
        domain_filter = None
        if state:
            domain_filter = self._detect_domain_from_context(state)
            if TEST_ENV and domain_filter:
                print(f"🎯 [DEBUG PineconeSearch] Auto-detected domain filter: {domain_filter.value}")
        
        all_results = {}
        for query in queries:
            try:
                embedding = self._get_embedding(query)
                filter_dict = {}
                if domain_filter:
                    # Include both specific domain and universal products
                    filter_dict["domain"] = {"$in": [domain_filter.value, Domain.UNIVERSAL.value]}
                
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
                domain = res.metadata.get('domain', 'N/A')
                score = res.score
                print(f"   {i+1}. '{product_name}' [Domain: {domain}] (Score: {score:.4f})")
        
        return sorted_results
    
    def _check_domain_conflict(self, results: List[SearchResult]) -> Optional[str]:
        """Check if results contain mixed domains"""
        domains = {r.metadata.get("domain") for r in results if r.metadata.get("domain")}
        # Don't warn if we have universal products
        domains.discard(Domain.UNIVERSAL.value)
        return "⚠️ Found products for both marine and freshwater aquariums. Please specify which type!" if len(domains) > 1 else None

def search_products_k15(state: ConversationState) -> ConversationState:
    """Search with k=15 (initial search) with smart domain detection"""
    client = PineconeSearchClient()
    results = client.search(
        queries=state["optimized_queries"],
        k=DEFAULT_K_VALUE,
        state=state  # Pass the full state for context analysis
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