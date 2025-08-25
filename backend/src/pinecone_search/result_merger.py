"""
Result Merger Module for Pinecone Optimization

Intelligent merging and prioritization of results from metadata and semantic searches.
Maintains AF alternatives priority while providing transparency about result sources.
"""

from typing import List, Dict, Optional
from models import SearchResult, ConversationState
from config import debug_print


class ResultMerger:
    """
    Handles intelligent merging of results from different search strategies.
    
    This merger combines results from metadata search (guaranteed products)
    and semantic search while maintaining proper prioritization and
    ensuring AF alternatives are always prioritized.
    """
    
    def __init__(self):
        """Initialize ResultMerger."""
        pass
    
    def merge_results(
        self,
        metadata_results: List[SearchResult],
        semantic_results: Dict[str, SearchResult],
        state: Optional[ConversationState] = None,
        k: int = 12
    ) -> List[SearchResult]:
        """
        Merge metadata and semantic search results with intelligent prioritization.
        
        Priority order:
        1. AF alternatives (from metadata or semantic) - always on top
        2. Other metadata results - high priority (score 0.99)
        3. Semantic results - sorted by actual score
        
        Args:
            metadata_results: Results from metadata-only search
            semantic_results: Results from semantic/vector search
            state: Conversation state for AF alternatives detection
            k: Maximum number of results to return
            
        Returns:
            Merged and prioritized list of SearchResult objects
        """
        debug_print(f"[MERGER] RM Merging: {len(metadata_results)} metadata + {len(semantic_results)} semantic")
        
        # Convert to common format for processing
        all_results = self._combine_result_sources(metadata_results, semantic_results)
        
        # Separate AF alternatives from other results
        af_alternatives = state.get("af_alternatives_to_search", []) if state else []
        af_results, other_results = self._separate_af_alternatives(all_results, af_alternatives)
        
        # Sort each group by score
        af_results.sort(key=lambda x: x.score, reverse=True)
        other_results.sort(key=lambda x: x.score, reverse=True)
        
        # Combine with AF alternatives first, then top K others
        final_results = af_results + other_results[:k]
        
        # Limit to K total results if needed
        if len(final_results) > k:
            final_results = final_results[:k]
        
        debug_print(f"[MERGER] RM Final: {len(af_results)} AF + {min(k, len(other_results))} others = {len(final_results)}")
        
        # Log result sources for debugging
        self._log_result_sources(final_results, metadata_results, semantic_results)
        
        return final_results
    
    def _combine_result_sources(
        self,
        metadata_results: List[SearchResult],
        semantic_results: Dict[str, SearchResult]
    ) -> Dict[str, SearchResult]:
        """
        Combine results from both sources, prioritizing metadata results.
        
        Args:
            metadata_results: Results from metadata search
            semantic_results: Results from semantic search
            
        Returns:
            Combined results with metadata taking priority for duplicates
        """
        combined = {}
        
        # Add semantic results first (lower priority)
        for result_id, result in semantic_results.items():
            combined[result_id] = result
        
        # Add metadata results (higher priority - will override semantic)
        for result in metadata_results:
            combined[result.id] = result
        
        debug_print(f"[MERGER] RM Combined: {len(combined)} unique results")
        return combined
    
    def _separate_af_alternatives(
        self,
        all_results: Dict[str, SearchResult],
        af_alternatives: List[str]
    ) -> tuple[List[SearchResult], List[SearchResult]]:
        """
        Separate AF alternative products from other results.
        
        AF alternatives always get highest priority regardless of source.
        
        Args:
            all_results: All combined search results
            af_alternatives: List of AF alternative product names
            
        Returns:
            Tuple of (af_results, other_results)
        """
        af_results = []
        other_results = []
        
        for result in all_results.values():
            product_name = result.metadata.get('product_name', '')
            
            if product_name in af_alternatives:
                af_results.append(result)
                debug_print(f"[MERGER] RM AF alternative: {product_name}")
            else:
                other_results.append(result)
        
        debug_print(f"[MERGER] RM Separated: {len(af_results)} AF, {len(other_results)} others")
        return af_results, other_results
    
    def _log_result_sources(
        self,
        final_results: List[SearchResult],
        metadata_results: List[SearchResult],
        semantic_results: Dict[str, SearchResult]
    ):
        """
        Log the source of each result for debugging and monitoring.
        
        Args:
            final_results: Final merged results
            metadata_results: Original metadata results
            semantic_results: Original semantic results
        """
        metadata_ids = {r.id for r in metadata_results}
        
        for i, result in enumerate(final_results[:5]):  # Log top 5
            product_name = result.metadata.get('product_name', 'Unknown')
            domain = result.metadata.get('domain', 'N/A')
            score = result.score
            
            source = "[METADATA]" if result.id in metadata_ids else "[SEMANTIC]"
            
            debug_print(f"   {i+1}. '{product_name}' [Domain: {domain}] (Score: {score:.4f}) {source}")
    
    def merge_with_deduplication(
        self,
        metadata_results: List[SearchResult],
        semantic_results: Dict[str, SearchResult],
        state: Optional[ConversationState] = None,
        k: int = 12,
        score_boost_metadata: float = 0.1
    ) -> List[SearchResult]:
        """
        Advanced merge with score boosting for metadata results.
        
        This method gives metadata results a slight score boost to ensure
        they rank higher than semantic results for the same product.
        
        Args:
            metadata_results: Results from metadata search
            semantic_results: Results from semantic search
            state: Conversation state
            k: Maximum results to return
            score_boost_metadata: Score boost for metadata results (0.0-0.2)
            
        Returns:
            Merged and optimized results list
        """
        # Apply score boost to metadata results
        boosted_metadata = []
        for result in metadata_results:
            boosted_result = SearchResult(
                id=result.id,
                score=min(1.0, result.score + score_boost_metadata),
                metadata=result.metadata
            )
            boosted_metadata.append(boosted_result)
        
        debug_print(f"[MERGER] RM Applied {score_boost_metadata} score boost to {len(boosted_metadata)} metadata results")
        
        return self.merge_results(boosted_metadata, semantic_results, state, k)
    
    def get_merge_statistics(
        self,
        metadata_results: List[SearchResult],
        semantic_results: Dict[str, SearchResult],
        final_results: List[SearchResult],
        af_alternatives: List[str]
    ) -> dict:
        """
        Generate statistics about the merge operation.
        
        Args:
            metadata_results: Original metadata results
            semantic_results: Original semantic results  
            final_results: Final merged results
            af_alternatives: AF alternative product names
            
        Returns:
            Dictionary with merge statistics
        """
        metadata_ids = {r.id for r in metadata_results}
        af_count = sum(1 for r in final_results 
                      if r.metadata.get('product_name', '') in af_alternatives)
        
        metadata_in_final = sum(1 for r in final_results if r.id in metadata_ids)
        semantic_in_final = len(final_results) - metadata_in_final
        
        return {
            "input_metadata_count": len(metadata_results),
            "input_semantic_count": len(semantic_results),
            "output_total_count": len(final_results),
            "output_af_alternatives": af_count,
            "output_metadata_source": metadata_in_final,
            "output_semantic_source": semantic_in_final,
            "deduplication_removed": len(metadata_results) + len(semantic_results) - len(final_results),
            "af_alternatives_available": len(af_alternatives),
            "merge_efficiency": round(len(final_results) / max(1, len(metadata_results) + len(semantic_results)) * 100, 1)
        }
    
    def validate_merge_quality(
        self,
        final_results: List[SearchResult],
        expected_af_alternatives: List[str]
    ) -> dict:
        """
        Validate the quality of the merge operation.
        
        Args:
            final_results: Final merged results
            expected_af_alternatives: Expected AF alternatives
            
        Returns:
            Validation results and quality metrics
        """
        found_af_alternatives = []
        score_distribution = []
        
        for result in final_results:
            product_name = result.metadata.get('product_name', '')
            score_distribution.append(result.score)
            
            if product_name in expected_af_alternatives:
                found_af_alternatives.append(product_name)
        
        missing_af = set(expected_af_alternatives) - set(found_af_alternatives)
        
        return {
            "total_results": len(final_results),
            "af_alternatives_found": len(found_af_alternatives),
            "af_alternatives_missing": len(missing_af),
            "missing_af_products": list(missing_af),
            "average_score": round(sum(score_distribution) / len(score_distribution), 3) if score_distribution else 0,
            "max_score": max(score_distribution) if score_distribution else 0,
            "min_score": min(score_distribution) if score_distribution else 0,
            "score_range": round(max(score_distribution) - min(score_distribution), 3) if score_distribution else 0,
            "quality_score": round((len(found_af_alternatives) / max(1, len(expected_af_alternatives))) * 100, 1)
        }