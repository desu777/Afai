"""
Search Optimizer Module for Pinecone Optimization

Intelligent separation of guaranteed products (metadata search) from semantic queries (vector search).
This separation is the key to the entire optimization strategy.
"""

from typing import List, Optional, Tuple
from models import ConversationState
from config import debug_print


class SearchOptimizer:
    """
    Optimizes search strategy by intelligently separating query types.
    
    This optimizer analyzes the conversation state to identify:
    - Guaranteed products: From Business Reasoner that can be found via metadata
    - Semantic queries: Contextual queries that require vector search
    
    This separation enables using the fastest search method for each query type.
    """
    
    def __init__(self):
        """Initialize SearchOptimizer."""
        pass
    
    def separate_search_types(
        self, 
        queries: List[str], 
        state: Optional[ConversationState] = None
    ) -> Tuple[List[str], List[str]]:
        """
        Separate queries into guaranteed products and semantic queries.
        
        This is the core optimization method that determines which queries
        can be handled by ultra-fast metadata search vs vector search.
        
        Args:
            queries: All search queries from Query Optimizer
            state: Conversation state with Business Reasoner data
            
        Returns:
            Tuple of (guaranteed_products, semantic_queries)
        """
        if not queries:
            return [], []
        
        guaranteed_products = []
        semantic_queries = []
        
        # Extract guaranteed products from Business Reasoner
        if state:
            guaranteed_products = self._extract_guaranteed_products(state)
        
        # Remove duplicates and clean up product names
        guaranteed_products = self._clean_product_names(guaranteed_products)
        
        # Separate semantic queries (exclude exact product matches)
        semantic_queries = self._filter_semantic_queries(queries, guaranteed_products)
        
        debug_print(f"[OPTIMIZER] SO Separated: {len(guaranteed_products)} guaranteed, {len(semantic_queries)} semantic")
        
        return guaranteed_products, semantic_queries
    
    def _extract_guaranteed_products(self, state: ConversationState) -> List[str]:
        """
        Extract all guaranteed products from Business Reasoner analysis.
        
        These products can be found via metadata search without embeddings.
        
        Args:
            state: Conversation state with business analysis
            
        Returns:
            List of product names that can be found via metadata
        """
        guaranteed_products = []
        
        # AF alternatives from competitor analysis
        if state.get("af_alternatives_to_search"):
            af_alternatives = state["af_alternatives_to_search"]
            guaranteed_products.extend(af_alternatives)
            debug_print(f"[OPTIMIZER] SO AF alternatives: {len(af_alternatives)}")
        
        # Business analysis products
        if state.get("business_analysis"):
            ba = state["business_analysis"]
            
            # Product name corrections
            if ba.get("product_name_corrections") and ba["product_name_corrections"] != "None":
                guaranteed_products.append(ba["product_name_corrections"])
                debug_print(f"[OPTIMIZER] SO Product corrections: {ba['product_name_corrections']}")
            
            # Products in requested category
            products_in_category = ba.get('products_in_category', [])
            if isinstance(products_in_category, list):
                guaranteed_products.extend(products_in_category)
                debug_print(f"[OPTIMIZER] SO Category products: {len(products_in_category)}")
            
            # Solution products for identified problems
            solutions_for_problem = ba.get('solutions_for_problem', [])
            if isinstance(solutions_for_problem, dict):
                # Extract from structured solution format
                if 'correction' in solutions_for_problem:
                    guaranteed_products.extend(solutions_for_problem['correction'])
                if 'maintenance' in solutions_for_problem:
                    guaranteed_products.extend(solutions_for_problem['maintenance'])
                debug_print(f"[OPTIMIZER] SO Solution products (dict): {len(solutions_for_problem)}")
            elif isinstance(solutions_for_problem, list):
                guaranteed_products.extend(solutions_for_problem)
                debug_print(f"[OPTIMIZER] SO Solution products (list): {len(solutions_for_problem)}")
        
        return guaranteed_products
    
    def _clean_product_names(self, product_names: List[str]) -> List[str]:
        """
        Clean and deduplicate product names.
        
        Args:
            product_names: Raw product names from various sources
            
        Returns:
            Cleaned list of unique product names
        """
        if not product_names:
            return []
        
        # Remove None, empty strings, and duplicates while preserving order
        cleaned = []
        seen = set()
        
        for product in product_names:
            if product and isinstance(product, str) and product.strip():
                clean_name = product.strip()
                if clean_name not in seen:
                    cleaned.append(clean_name)
                    seen.add(clean_name)
        
        debug_print(f"[OPTIMIZER] SO Cleaned: {len(product_names)} -> {len(cleaned)} products")
        return cleaned
    
    def _filter_semantic_queries(
        self, 
        queries: List[str], 
        guaranteed_products: List[str]
    ) -> List[str]:
        """
        Filter queries to identify those requiring semantic search.
        
        Excludes queries that are likely exact product names since those
        will be handled by metadata search.
        
        Args:
            queries: All search queries
            guaranteed_products: Products that will be found via metadata
            
        Returns:
            Queries that require semantic/vector search
        """
        if not queries:
            return []
        
        semantic_queries = []
        
        for query in queries:
            if not query or not isinstance(query, str):
                continue
            
            # Check if query looks like a product name we already have
            is_product_name = self._is_likely_product_name(query, guaranteed_products)
            
            if not is_product_name:
                semantic_queries.append(query)
                debug_print(f"[OPTIMIZER] SO Semantic: '{query[:50]}'")
            else:
                debug_print(f"[OPTIMIZER] SO Skipped product: '{query[:50]}'")
        
        return semantic_queries
    
    def _is_likely_product_name(self, query: str, guaranteed_products: List[str]) -> bool:
        """
        Determine if a query is likely an exact product name.
        
        Args:
            query: Search query to analyze
            guaranteed_products: Known product names
            
        Returns:
            True if query appears to be a product name
        """
        query_lower = query.lower().strip()
        
        # Check for exact or partial matches with guaranteed products
        for product in guaranteed_products:
            product_lower = product.lower().strip()
            
            # Exact match
            if query_lower == product_lower:
                return True
            
            # Query contains product name
            if product_lower in query_lower and len(product_lower) > 3:
                return True
            
            # Product name contains query (for abbreviated searches)
            if query_lower in product_lower and len(query_lower) > 3:
                return True
        
        return False
    
    def optimize_query_count(
        self, 
        queries: List[str], 
        max_semantic_queries: int = 5
    ) -> List[str]:
        """
        Optimize the number of semantic queries to reduce search time.
        
        Since guaranteed products are handled separately, we can be more
        selective about semantic queries and focus on the most important ones.
        
        Args:
            queries: Semantic queries to optimize
            max_semantic_queries: Maximum number of semantic queries to keep
            
        Returns:
            Optimized list of semantic queries
        """
        if not queries or len(queries) <= max_semantic_queries:
            return queries
        
        debug_print(f"[OPTIMIZER] SO Reducing queries: {len(queries)} -> {max_semantic_queries}")
        
        # Prioritize queries by length and complexity (longer = more specific/valuable)
        prioritized = sorted(queries, key=lambda x: len(x), reverse=True)
        
        optimized = prioritized[:max_semantic_queries]
        
        debug_print(f"[OPTIMIZER] SO Kept queries: {[q[:30] for q in optimized]}")
        
        return optimized
    
    def get_optimization_stats(
        self, 
        original_queries: List[str], 
        guaranteed_products: List[str], 
        semantic_queries: List[str]
    ) -> dict:
        """
        Generate optimization statistics for monitoring and debugging.
        
        Args:
            original_queries: Original query list from Query Optimizer
            guaranteed_products: Products for metadata search
            semantic_queries: Queries for semantic search
            
        Returns:
            Dictionary with optimization metrics
        """
        total_searches = len(guaranteed_products) + len(semantic_queries)
        metadata_percentage = (len(guaranteed_products) / total_searches * 100) if total_searches > 0 else 0
        
        return {
            "original_query_count": len(original_queries),
            "guaranteed_product_count": len(guaranteed_products),
            "semantic_query_count": len(semantic_queries),
            "total_search_operations": total_searches,
            "metadata_search_percentage": round(metadata_percentage, 1),
            "query_reduction": len(original_queries) - len(semantic_queries),
            "optimization_applied": len(guaranteed_products) > 0
        }