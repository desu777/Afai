"""
Pinecone Search Optimization Module

Modułowa architektura dla optymalizacji wyszukiwania w Pinecone:
- MetadataSearcher: Szybkie wyszukiwanie przez metadane (bez embeddingów)
- SemanticSearcher: Zoptymalizowane wyszukiwanie wektorowe z batch processing
- BatchEmbeddingGenerator: Batch generation embeddingów OpenAI
- SearchOptimizer: Inteligentny podział zapytań na typy
- ResultMerger: Łączenie i priorytetyzacja wyników
"""

from .metadata_search import MetadataSearcher
from .batch_embeddings import BatchEmbeddingGenerator
from .semantic_search import SemanticSearcher
from .search_optimizer import SearchOptimizer
from .result_merger import ResultMerger

__all__ = [
    'MetadataSearcher',
    'BatchEmbeddingGenerator', 
    'SemanticSearcher',
    'SearchOptimizer',
    'ResultMerger'
]

__version__ = '1.0.0'