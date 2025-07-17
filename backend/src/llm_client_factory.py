"""
🚀 LLM Client Factory - Dual Provider Configuration (2025)
Universal client factory for all workflow nodes with per-node API/model selection
Supports both OpenRouter and Google Gemini APIs
"""
from typing import Tuple, Optional, Union
from openai import OpenAI
from config import (
    OPENAI_API_KEY,
    INTENT_DETECTOR_API, INTENT_DETECTOR_MODEL,
    BUSINESS_REASONER_API, BUSINESS_REASONER_MODEL,
    QUERY_OPTIMIZER_API, QUERY_OPTIMIZER_MODEL,
    RESPONSE_FORMATTER_API, RESPONSE_FORMATTER_MODEL,
    FOLLOW_UP_API, FOLLOW_UP_MODEL,
    IMAGE_API, IMAGE_MODEL,
    # Gemini configuration
    GEMINI_API_KEY,
    GEMINI_API_KEY_BUSINESS, GEMINI_API_KEY_RESPONSE, GEMINI_API_KEY_INTENT,
    GEMINI_API_KEY_QUERY, GEMINI_API_KEY_FOLLOWUP, GEMINI_API_KEY_IMAGE, GEMINI_API_KEY_ICP,
    INTENT_DETECTOR_PROVIDER, BUSINESS_REASONER_PROVIDER,
    QUERY_OPTIMIZER_PROVIDER, RESPONSE_FORMATTER_PROVIDER,
    FOLLOW_UP_PROVIDER, IMAGE_PROVIDER, ICP_PROVIDER,
    TEST_ENV, debug_print
)
from gemini_client_factory import GeminiClientFactory, GeminiClient
from gemini_rate_limit_manager import (
    rate_limit_manager, can_use_gemini, record_gemini_success, 
    record_gemini_error, get_gemini_api_key
)

class LLMClientFactory:
    """Factory for creating LLM clients with per-node configuration"""
    
    @staticmethod
    def create_client(node_name: str) -> Tuple[Union[OpenAI, GeminiClient], str]:
        """
        Create LLM client and return (client, model_name) for specified node
        Smart fallback: Gemini (if available) → OpenRouter (fallback)
        
        Args:
            node_name: One of 'intent_detector', 'business_reasoner', 'query_optimizer', 'response_formatter', 'follow_up', 'image_analysis'
        
        Returns:
            Tuple of (LLM client, model_name) - client can be OpenAI or GeminiClient
        """
        # Initialize rate limit manager with per-node API keys
        LLMClientFactory._initialize_rate_limit_manager()
        
        # Get provider for this node
        provider = LLMClientFactory._get_node_provider(node_name)
        
        if provider == "gemini":
            # Check if Gemini can be used (rate limits, errors, etc.)
            if can_use_gemini(node_name):
                try:
                    # Create Gemini client
                    client, model_name = GeminiClientFactory.create_client(node_name)
                    
                    # Record successful Gemini usage
                    record_gemini_success(node_name)
                    
                    debug_print(f"🚀 [LLMClientFactory] Created Gemini client for {node_name}: {model_name}")
                    
                    if TEST_ENV:
                        print(f"🎯 [LLMClientFactory] {node_name} → gemini → {model_name}")
                    
                    return client, model_name
                    
                except Exception as e:
                    # Record error and fallback to OpenRouter
                    record_gemini_error(node_name)
                    debug_print(f"❌ [LLMClientFactory] Gemini error for {node_name}: {e}")
                    debug_print(f"🔄 [LLMClientFactory] Falling back to OpenRouter for {node_name}")
                    
                    if TEST_ENV:
                        print(f"⚠️ [LLMClientFactory] Gemini failed for {node_name}, using OpenRouter fallback")
            else:
                debug_print(f"⚠️ [LLMClientFactory] Gemini rate limit exceeded for {node_name}, using OpenRouter")
                
                if TEST_ENV:
                    print(f"⚠️ [LLMClientFactory] Rate limit exceeded for {node_name}, using OpenRouter")
        
        # Create OpenRouter client (default or fallback)
        api_key, model_name = LLMClientFactory._get_node_config(node_name)
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        debug_print(f"🚀 [LLMClientFactory] Created OpenRouter client for {node_name}: {model_name}")
        
        if TEST_ENV:
            print(f"🎯 [LLMClientFactory] {node_name} → openrouter → {model_name}")
        
        return client, model_name
    
    @staticmethod
    def _get_node_provider(node_name: str) -> str:
        """Get provider for specified node"""
        provider_map = {
            "intent_detector": INTENT_DETECTOR_PROVIDER,
            "business_reasoner": BUSINESS_REASONER_PROVIDER,
            "query_optimizer": QUERY_OPTIMIZER_PROVIDER,
            "response_formatter": RESPONSE_FORMATTER_PROVIDER,
            "follow_up": FOLLOW_UP_PROVIDER,
            "image_analysis": IMAGE_PROVIDER,
            "icp_analysis": ICP_PROVIDER
        }
        
        if node_name not in provider_map:
            raise ValueError(f"Unknown node name: {node_name}")
        
        return provider_map[node_name]
    
    @staticmethod
    def _initialize_rate_limit_manager():
        """Initialize rate limit manager with per-node API keys"""
        # Mapping of node names to their respective API keys
        api_key_map = {
            "intent_detector": GEMINI_API_KEY_INTENT,
            "business_reasoner": GEMINI_API_KEY_BUSINESS,
            "query_optimizer": GEMINI_API_KEY_QUERY,
            "response_formatter": GEMINI_API_KEY_RESPONSE,
            "follow_up": GEMINI_API_KEY_FOLLOWUP,
            "image_analysis": GEMINI_API_KEY_IMAGE,
            "icp_analysis": GEMINI_API_KEY_ICP
        }
        
        # Register API keys with rate limit manager
        for node_name, api_key in api_key_map.items():
            if api_key:  # Only register if API key exists
                rate_limit_manager.register_api_key(node_name, api_key)
                if TEST_ENV:
                    debug_print(f"🔑 [LLMClientFactory] Registered API key for {node_name}: {api_key[:12]}...")
    
    @staticmethod
    def _get_node_config(node_name: str) -> Tuple[str, str]:
        """Get API key and model name for specified node (OpenRouter only)"""
        config_map = {
            "intent_detector": (INTENT_DETECTOR_API, INTENT_DETECTOR_MODEL),
            "business_reasoner": (BUSINESS_REASONER_API, BUSINESS_REASONER_MODEL),
            "query_optimizer": (QUERY_OPTIMIZER_API, QUERY_OPTIMIZER_MODEL),
            "response_formatter": (RESPONSE_FORMATTER_API, RESPONSE_FORMATTER_MODEL),
            "follow_up": (FOLLOW_UP_API, FOLLOW_UP_MODEL),
            "image_analysis": (IMAGE_API, IMAGE_MODEL)
        }
        
        if node_name not in config_map:
            raise ValueError(f"Unknown node name: {node_name}")
        
        return config_map[node_name]

# 🎯 Convenience functions for each node
def create_intent_detector_client() -> Tuple[Union[OpenAI, GeminiClient], str]:
    """Create client for intent detector node"""
    return LLMClientFactory.create_client("intent_detector")

def create_business_reasoner_client() -> Tuple[Union[OpenAI, GeminiClient], str]:
    """Create client for business reasoner node"""
    return LLMClientFactory.create_client("business_reasoner")

def create_query_optimizer_client() -> Tuple[Union[OpenAI, GeminiClient], str]:
    """Create client for query optimizer node"""
    return LLMClientFactory.create_client("query_optimizer")

def create_response_formatter_client() -> Tuple[Union[OpenAI, GeminiClient], str]:
    """Create client for response formatter node"""
    return LLMClientFactory.create_client("response_formatter")

def create_follow_up_client() -> Tuple[Union[OpenAI, GeminiClient], str]:
    """Create client for follow-up evaluator node"""
    return LLMClientFactory.create_client("follow_up")

def create_image_analysis_client() -> Tuple[Union[OpenAI, GeminiClient], str]:
    """Create client for image analysis node"""
    return LLMClientFactory.create_client("image_analysis")

# 🔧 Legacy support functions (for gradual migration)
def create_llm_client_for_node(node_name: str) -> Union[OpenAI, GeminiClient]:
    """Legacy function - returns only client (without model name)"""
    client, _ = LLMClientFactory.create_client(node_name)
    return client

def get_model_name_for_node(node_name: str) -> str:
    """Legacy function - returns only model name"""
    _, model_name = LLMClientFactory.create_client(node_name)
    return model_name 