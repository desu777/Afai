"""
Resilient Client Wrapper for Gemini → OpenRouter Fallback
Provides automatic failover capability for increased system reliability
"""
import time
from typing import Any, Dict, List, Optional, Union, Callable
from openai import OpenAI
from config import (
    TEST_ENV, 
    debug_print,
    # Fallback configuration
    ENABLE_GEMINI_FALLBACK,
    GEMINI_REQUEST_TIMEOUT,
    GEMINI_MAX_RETRIES,
    GEMINI_RETRY_DELAY,
    LOG_FALLBACK_EVENTS
)

class ResilientGeminiClient:
    """
    Wrapper around Gemini client that provides automatic fallback to OpenRouter
    Implements OpenAI-compatible interface for seamless integration
    """
    
    def __init__(self, gemini_client, fallback_api_key: str, fallback_model: str, node_name: str):
        """
        Initialize resilient client with primary Gemini and fallback OpenRouter
        
        Args:
            gemini_client: Primary Gemini client instance
            fallback_api_key: OpenRouter API key for fallback
            fallback_model: OpenRouter model name for fallback
            node_name: Name of the node for logging purposes
        """
        self.gemini_client = gemini_client
        self.fallback_api_key = fallback_api_key
        self.fallback_model = fallback_model
        self.node_name = node_name
        self.fallback_active = False
        
        # Create fallback client lazily (only when needed)
        self._fallback_client = None
        
        # Expose nested attributes for compatibility
        self.chat = self
        self.completions = self
        
        if TEST_ENV:
            debug_print(f"[RESILIENT] Init {node_name}: primary + fallback ready")
    
    @property
    def fallback_client(self) -> OpenAI:
        """Lazy initialization of fallback client"""
        if self._fallback_client is None:
            self._fallback_client = OpenAI(
                api_key=self.fallback_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            if TEST_ENV:
                debug_print(f"[RESILIENT] Created fallback client for {self.node_name}")
        return self._fallback_client
    
    def create(self, **kwargs) -> Any:
        """
        Create chat completion with automatic fallback on Gemini failure
        
        Implements retry logic and fallback to OpenRouter if Gemini fails
        """
        if not ENABLE_GEMINI_FALLBACK:
            # Fallback disabled, use Gemini directly
            return self.gemini_client.chat.completions.create(**kwargs)
        
        # Try Gemini first with retry logic
        last_error = None
        for attempt in range(GEMINI_MAX_RETRIES):
            try:
                if attempt > 0 and GEMINI_RETRY_DELAY > 0:
                    time.sleep(GEMINI_RETRY_DELAY)
                
                # Add timeout to kwargs if not present
                timeout_kwargs = kwargs.copy()
                if 'timeout' not in timeout_kwargs and GEMINI_REQUEST_TIMEOUT:
                    timeout_kwargs['timeout'] = GEMINI_REQUEST_TIMEOUT
                
                response = self.gemini_client.chat.completions.create(**timeout_kwargs)
                
                if self.fallback_active and LOG_FALLBACK_EVENTS:
                    debug_print(f"[RESILIENT] {self.node_name} recovered to Gemini")
                    self.fallback_active = False
                
                return response
                
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                error_msg = str(e)[:100]
                
                if TEST_ENV:
                    debug_print(f"[RESILIENT] {self.node_name} Gemini attempt {attempt+1} failed: {error_type}")
                
                # Check if error is retryable
                if self._is_retryable_error(e) and attempt < GEMINI_MAX_RETRIES - 1:
                    continue
                
                # All retries exhausted or non-retryable error
                break
        
        # Fallback to OpenRouter
        if LOG_FALLBACK_EVENTS:
            debug_print(f"[RESILIENT] {self.node_name} failing over to OpenRouter: {error_type}")
        
        try:
            # Adjust kwargs for OpenRouter
            fallback_kwargs = self._prepare_fallback_kwargs(kwargs)
            response = self.fallback_client.chat.completions.create(**fallback_kwargs)
            
            self.fallback_active = True
            
            if TEST_ENV:
                debug_print(f"[RESILIENT] {self.node_name} fallback successful")
            
            return response
            
        except Exception as fallback_error:
            # Both Gemini and OpenRouter failed
            if LOG_FALLBACK_EVENTS:
                debug_print(f"[RESILIENT] {self.node_name} fallback also failed: {type(fallback_error).__name__}")
            
            # Re-raise the original Gemini error for better debugging
            raise last_error
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable
        
        Args:
            error: The exception to check
            
        Returns:
            True if error is retryable, False otherwise
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Retryable errors
        retryable_patterns = [
            'timeout',
            'connection',
            'network',
            'temporary',
            '503',
            '502',
            'deadline exceeded',
            'rate limit',
            '429'
        ]
        
        # Non-retryable errors
        non_retryable_patterns = [
            'authentication',
            'unauthorized',
            '401',
            '403',
            'invalid api key',
            'project not found',
            'model not found',
            'invalid request',
            '400'
        ]
        
        # Check non-retryable first
        for pattern in non_retryable_patterns:
            if pattern in error_msg:
                return False
        
        # Check retryable
        for pattern in retryable_patterns:
            if pattern in error_msg:
                return True
        
        # Network-related exception types
        if error_type in ['ConnectionError', 'TimeoutError', 'NetworkError']:
            return True
        
        # Default to not retryable for unknown errors
        return False
    
    def _prepare_fallback_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare kwargs for OpenRouter fallback
        
        Args:
            kwargs: Original kwargs for Gemini
            
        Returns:
            Modified kwargs for OpenRouter
        """
        fallback_kwargs = kwargs.copy()
        
        # Replace model with fallback model
        fallback_kwargs['model'] = self.fallback_model
        
        # Remove Gemini-specific parameters if any
        gemini_specific = ['thinking_config', 'config']
        for param in gemini_specific:
            fallback_kwargs.pop(param, None)
        
        # Remove timeout as OpenRouter handles it differently
        fallback_kwargs.pop('timeout', None)
        
        return fallback_kwargs
    
    def __getattr__(self, name: str) -> Any:
        """
        Proxy all other attributes to the primary Gemini client
        This ensures full compatibility with the OpenAI interface
        """
        return getattr(self.gemini_client, name)