"""
Batch Embeddings Module for Pinecone Optimization

Optimized embedding generation using OpenAI's batch API.
Reduces embedding generation time from 15x200ms to 1x200ms (93% reduction).
"""

from typing import List, Optional
from config import debug_print, OPENAI_EMBEDDING_MODEL


class BatchEmbeddingGenerator:
    """
    Handles batch embedding generation using OpenAI API.
    
    This generator optimizes embedding creation by batching multiple texts
    into single API calls, dramatically reducing latency and API overhead.
    OpenAI supports up to 100 texts per batch request.
    """
    
    def __init__(self, openai_client):
        """
        Initialize BatchEmbeddingGenerator with OpenAI client.
        
        Args:
            openai_client: OpenAI client instance
        """
        self.openai_client = openai_client
        self.max_batch_size = 100  # OpenAI API limit
    
    def generate_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in a single API call.
        
        This method is the core optimization - instead of making N separate
        API calls for N texts, it makes 1 call for up to 100 texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embeddings (same order as input texts)
            None entries for texts that failed to generate embeddings
        """
        if not texts:
            return []
        
        # Handle large batches by splitting
        if len(texts) > self.max_batch_size:
            return self._generate_large_batch(texts)
        
        debug_print(f"[BATCH] BE Generating {len(texts)} embeddings")
        
        try:
            response = self.openai_client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=texts
            )
            
            embeddings = []
            for i, embedding_obj in enumerate(response.data):
                embeddings.append(embedding_obj.embedding)
            
            debug_print(f"[BATCH] BE Success: {len(embeddings)} embeddings generated")
            return embeddings
            
        except Exception as e:
            debug_print(f"[ERROR] BE Batch failed: {str(e)[:100]}")
            return self._fallback_individual_generation(texts)
    
    def _generate_large_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Handle batches larger than API limit by splitting into chunks.
        
        Args:
            texts: List of texts (> max_batch_size)
            
        Returns:
            Combined list of embeddings from all chunks
        """
        debug_print(f"[BATCH] BE Large batch: {len(texts)} texts, splitting into chunks")
        
        all_embeddings = []
        for i in range(0, len(texts), self.max_batch_size):
            chunk = texts[i:i + self.max_batch_size]
            chunk_embeddings = self.generate_batch(chunk)
            all_embeddings.extend(chunk_embeddings)
        
        return all_embeddings
    
    def _fallback_individual_generation(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Fallback to individual embedding generation when batch fails.
        
        This ensures system reliability - if batch processing fails,
        we gracefully degrade to individual generation.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embeddings (with None for failed generations)
        """
        debug_print(f"[FALLBACK] BE Individual generation for {len(texts)} texts")
        
        embeddings = []
        for text in texts:
            try:
                embedding = self._generate_single_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                debug_print(f"[ERROR] BE Individual failed for text: {str(e)[:50]}")
                embeddings.append(None)
        
        successful_count = sum(1 for emb in embeddings if emb is not None)
        debug_print(f"[FALLBACK] BE Individual results: {successful_count}/{len(texts)} successful")
        
        return embeddings
    
    def _generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        response = self.openai_client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def generate_with_retry(
        self, 
        texts: List[str], 
        max_retries: int = 2
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings with automatic retry on failure.
        
        This method provides additional reliability by retrying failed
        batch operations before falling back to individual generation.
        
        Args:
            texts: List of texts to generate embeddings for
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of embeddings (same order as input texts)
        """
        if not texts:
            return []
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    debug_print(f"[BATCH] BE Retry attempt {attempt}/{max_retries}")
                
                return self.generate_batch(texts)
                
            except Exception as e:
                if attempt < max_retries:
                    debug_print(f"[BATCH] BE Attempt {attempt + 1} failed: {str(e)[:50]}")
                    continue
                else:
                    debug_print(f"[ERROR] BE All attempts failed, using fallback")
                    return self._fallback_individual_generation(texts)
        
        return []
    
    def estimate_savings(self, num_texts: int) -> dict:
        """
        Calculate estimated time savings from batch processing.
        
        Args:
            num_texts: Number of texts to process
            
        Returns:
            Dictionary with time estimates and savings
        """
        individual_time_ms = num_texts * 200  # ~200ms per individual request
        batch_time_ms = 200  # Single batch request time
        
        savings_ms = individual_time_ms - batch_time_ms
        savings_percent = (savings_ms / individual_time_ms) * 100 if individual_time_ms > 0 else 0
        
        return {
            "individual_time_ms": individual_time_ms,
            "batch_time_ms": batch_time_ms,
            "savings_ms": savings_ms,
            "savings_percent": round(savings_percent, 1),
            "texts_count": num_texts
        }