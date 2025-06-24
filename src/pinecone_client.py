"""
Pinecone Search Module - Enhanced with dynamic K value from ENHANCED_K_VALUE
Handles all interactions with Pinecone vector database
"""
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from models import ConversationState, SearchResult, Domain
from config import (
    PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENVIRONMENT,
    OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL,
    DEFAULT_K_VALUE, ENHANCED_K_VALUE, TEST_ENV, debug_print
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
        
        debug_print(f"🔍 [PineconeSearch] Freshwater score: {freshwater_score}, Marine score: {marine_score}")
        
        if freshwater_score > marine_score:
            return Domain.FRESHWATER
        elif marine_score > freshwater_score:
            return Domain.SEAWATER
        
        return None  # No clear domain detected
    
    def search(
        self, 
        queries: List[str], 
        k: int = None,  # 🆕 DYNAMIC: Default to None, will use ENHANCED_K_VALUE
        state: Optional[ConversationState] = None
    ) -> List[SearchResult]:
        """
        🆕 HYBRID SEARCH: Combines vector search with guaranteed product search
        Now with dynamic K value from ENHANCED_K_VALUE
        """
        # 🆕 DYNAMIC K VALUE
        if k is None:
            k = ENHANCED_K_VALUE
        
        if TEST_ENV:
            print(f"🔍 [PineconeSearch] Using dynamic K={k} (ENHANCED_K_VALUE={ENHANCED_K_VALUE})")
        
        # Auto-detect domain if not explicitly set
        domain_filter = None
        if state:
            domain_filter = self._detect_domain_from_context(state)
            if domain_filter:
                debug_print(f"🎯 [PineconeSearch] Auto-detected domain filter: {domain_filter.value}")
        
        # 🆕 HYBRID SEARCH: Extract critical products for guaranteed search
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
        
        # 🚀 ENHANCED: Add AF alternatives from Business Reasoner
        if state and state.get("af_alternatives_to_search"):
            af_alternatives = state["af_alternatives_to_search"]
            debug_print(f"🎯 [PineconeSearch] Adding AF alternatives to guaranteed search: {af_alternatives}")
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
        
        # 🆕 GUARANTEED SEARCH for critical products + collect not found
        guaranteed_results = {}
        fallback_queries = []  # 🆕 Collect products not found for vector search
        if critical_products:
            debug_print(f"🎯 [PineconeSearch] Performing guaranteed search for: {critical_products}")
            guaranteed, not_found_products = self._guaranteed_product_search(critical_products, domain_filter)
            for result in guaranteed:
                guaranteed_results[result.id] = result
            
            # 🆕 FALLBACK: Add not found products to vector search
            if not_found_products:
                fallback_queries.extend(not_found_products)
                debug_print(f"🔄 [PineconeSearch] Fallback: Adding {len(not_found_products)} not found products to vector search: {not_found_products}")
        
        # 🆕 VECTOR SEARCH for all queries + fallback queries
        all_queries = queries + fallback_queries  # 🆕 Include fallback queries
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
                    top_k=k,  # 🆕 DYNAMIC K VALUE
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
                    print(f"❌ [DEBUG PineconeSearch] Search error for query '{query}': {e}")
                continue
        
        # 🚀 ENHANCED: K + AF alternatives mechanism
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
        
        # 🎯 K + AF alternatives: Take all AF alternatives + top K others
        final_count = len(guaranteed_af_results) + min(k, len(other_results))
        sorted_results = guaranteed_af_results + other_results[:k]
        
        debug_print(f"🎯 [PineconeSearch] K + AF alternatives: {len(guaranteed_af_results)} AF guaranteed + {min(k, len(other_results))} vector = {len(sorted_results)} total")

        debug_print(f"🌲 [PineconeSearch] Hybrid search: {len(guaranteed_results)} guaranteed + {len(all_results)} vector = {len(sorted_results)} final (K={k}). Top 5:")
        for i, res in enumerate(sorted_results[:5]):
            product_name = res.metadata.get('product_name', 'Brak nazwy')
            domain = res.metadata.get('domain', 'N/A')
            score = res.score
            guaranteed_marker = "🎯" if res.id in guaranteed_results else ""
            debug_print(f"   {i+1}. '{product_name}' [Domain: {domain}] (Score: {score:.4f}) {guaranteed_marker}")
        
        return sorted_results
    
    def _check_domain_conflict(self, results: List[SearchResult]) -> Optional[str]:
        """Check if results contain mixed domains"""
        domains = {r.metadata.get("domain") for r in results if r.metadata.get("domain")}
        # Don't warn if we have universal products
        domains.discard(Domain.UNIVERSAL.value)
        return "⚠️ Found products for both marine and freshwater aquariums. Please specify which type!" if len(domains) > 1 else None

    def _guaranteed_product_search(self, product_names: List[str], domain_filter: Optional[Domain] = None) -> tuple[List[SearchResult], List[str]]:
        """
        Guaranteed search for specific products using metadata filtering
        Returns: (found_results, not_found_product_names)
        """
        guaranteed_results = []
        not_found_products = []  # 🆕 Track products not found for fallback
        
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
                    debug_print(f"✅ [PineconeSearch] Guaranteed found: {product_name}")
                else:
                    debug_print(f"⚠️ [PineconeSearch] Product not found in database: {product_name}")
                    not_found_products.append(product_name)  # 🆕 Add to fallback list
                    
            except Exception as e:
                debug_print(f"❌ [PineconeSearch] Error in guaranteed search for {product_name}: {e}")
                not_found_products.append(product_name)  # 🆕 Add to fallback list on error
        
        return guaranteed_results, not_found_products  # �� Return both lists

# 🆕 UPDATED FUNCTIONS - now use dynamic ENHANCED_K_VALUE
def search_products_k20(state: ConversationState) -> ConversationState:
    """🆕 UPDATED: Uses dynamic ENHANCED_K_VALUE instead of hardcoded k=20"""
    client = PineconeSearchClient()
    results = client.search(
        queries=state["optimized_queries"],
        k=ENHANCED_K_VALUE,  # 🆕 DYNAMIC K VALUE FROM ENV
        state=state  # Pass the full state for context analysis
    )
    
    # First, check for domain conflicts using the model instances
    domain_warning = client._check_domain_conflict(results)
    if domain_warning and not state.get("domain_filter"):
        state["domain_warning"] = domain_warning
        
    # Then, serialize the results for the state dictionary
    state["search_results"] = [{"id": r.id, "score": r.score, "metadata": r.metadata} for r in results]
    
    if TEST_ENV:
        print(f"🎯 [PineconeSearch] Stored {len(state['search_results'])} results using dynamic K={ENHANCED_K_VALUE}")
    
    return state

def enhanced_search_k20(state: ConversationState) -> ConversationState:
    """🆕 UPDATED: Uses dynamic ENHANCED_K_VALUE instead of hardcoded k=20"""
    return search_products_k20(state)