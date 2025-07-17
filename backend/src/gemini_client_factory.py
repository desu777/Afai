"""
🚀 Gemini Client Factory - Google Gemini 2.5 API Integration (2025)
Client factory using the latest google.genai SDK with thinking support
"""
import json
import base64
import requests
from typing import Dict, Any, List, Optional, Union
from google import genai
from google.genai import types
from config import (
    GEMINI_API_KEY,
    # Per-node API keys
    GEMINI_API_KEY_BUSINESS, GEMINI_API_KEY_RESPONSE, GEMINI_API_KEY_INTENT,
    GEMINI_API_KEY_QUERY, GEMINI_API_KEY_FOLLOWUP, GEMINI_API_KEY_IMAGE, GEMINI_API_KEY_ICP,
    # Models
    GEMINI_DEFAULT_MODEL,
    INTENT_DETECTOR_GEMINI_MODEL,
    BUSINESS_REASONER_GEMINI_MODEL,
    QUERY_OPTIMIZER_GEMINI_MODEL,
    RESPONSE_FORMATTER_GEMINI_MODEL,
    FOLLOW_UP_GEMINI_MODEL,
    IMAGE_GEMINI_MODEL,
    ICP_GEMINI_MODEL,
    # Thinking budgets
    GEMINI_DEFAULT_THINKING_BUDGET,
    INTENT_DETECTOR_THINKING_BUDGET,
    BUSINESS_REASONER_THINKING_BUDGET,
    QUERY_OPTIMIZER_THINKING_BUDGET,
    RESPONSE_FORMATTER_THINKING_BUDGET,
    FOLLOW_UP_THINKING_BUDGET,
    IMAGE_THINKING_BUDGET,
    ICP_THINKING_BUDGET,
    TEST_ENV,
    debug_print
)

class GeminiAPIError(Exception):
    """OpenAI-compatible error for Gemini API issues"""
    pass

class GeminiResponse:
    """OpenAI-compatible response wrapper for Gemini API"""
    
    def __init__(self, gemini_response):
        self.choices = [GeminiChoice(gemini_response)]
        self.id = "gemini-response"
        self.object = "chat.completion"
        self.created = None
        self.model = None
        self.usage = None

class GeminiChoice:
    """OpenAI-compatible choice wrapper for Gemini API"""
    
    def __init__(self, gemini_response):
        self.message = GeminiMessage(gemini_response)
        self.finish_reason = "stop"
        self.index = 0

class GeminiMessage:
    """OpenAI-compatible message wrapper for Gemini API"""
    
    def __init__(self, gemini_response):
        self.content = gemini_response.text
        self.role = "assistant"

class GeminiClient:
    """OpenAI-compatible client for Gemini API using google.genai"""
    
    def __init__(self, api_key: str, model_name: str, thinking_budget: str = None):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.thinking_budget = thinking_budget
        self.chat = self  # For OpenAI compatibility
        self.completions = self  # For OpenAI compatibility
        
        if TEST_ENV:
            if thinking_budget is not None and thinking_budget.strip() != "":
                debug_print(f"🤖 [GeminiClient] Initialized with model: {model_name} (thinking: {thinking_budget})")
            else:
                debug_print(f"🤖 [GeminiClient] Initialized with model: {model_name} (thinking: default)")
    
    def create(self, messages: List[Dict[str, str]], temperature: float = 0.3,
               response_format: Optional[Dict[str, str]] = None, **kwargs) -> GeminiResponse:
        """
        Create a chat completion using Gemini API with OpenAI-compatible interface
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Temperature for generation (0.0 to 1.0)
            response_format: Optional response format (e.g., {"type": "json_object"})
            **kwargs: Additional parameters (ignored for compatibility)
        
        Returns:
            GeminiResponse: OpenAI-compatible response object
        """
        try:
            # Convert OpenAI messages to Gemini format (string for text-only, list for multimodal)
            prompt = self._convert_messages_to_prompt(messages)
            
            # Add JSON formatting instruction if needed (only for text-only prompts)
            if response_format and response_format.get("type") == "json_object":
                if isinstance(prompt, str):
                    prompt += "\n\nIMPORTANT: Respond with valid JSON only, no additional text."
                elif isinstance(prompt, list):
                    # For multimodal, add JSON instruction as text part
                    prompt.append("\n\nIMPORTANT: Respond with valid JSON only, no additional text.")
            
            # Configure thinking (only if thinking_budget is explicitly set)
            thinking_config = None
            if self.thinking_budget is not None and self.thinking_budget.strip() != "":
                thinking_config = types.ThinkingConfig(thinking_budget=int(self.thinking_budget))
            
            # Configure generation parameters
            generation_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=8192,
                top_p=0.95,
                top_k=40,
                thinking_config=thinking_config
            )
            
            # Log multimodal vs text-only mode
            if TEST_ENV:
                if isinstance(prompt, list):
                    debug_print(f"🖼️ [GeminiClient] Using multimodal mode with {len([p for p in prompt if hasattr(p, 'mime_type')])} images")
                else:
                    debug_print(f"📝 [GeminiClient] Using text-only mode")
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=generation_config
            )
            
            # Check if response was blocked or empty
            if not response.text or response.text.strip() == "":
                raise GeminiAPIError("Empty response from Gemini API")
            
            if TEST_ENV:
                debug_print(f"✅ [GeminiClient] Generated response: {len(response.text)} characters")
            
            return GeminiResponse(response)
            
        except Exception as e:
            if TEST_ENV:
                debug_print(f"❌ [GeminiClient] Error: {e}")
            # Convert Gemini errors to OpenAI-compatible format
            raise self._convert_gemini_error(e)
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, Any]]) -> Union[str, List[Any]]:
        """
        Convert OpenAI messages format to Gemini content format
        Returns either a string (text-only) or a list (multimodal with images)
        """
        # Check if any message contains image content
        has_images = any(
            isinstance(msg.get("content"), list) and 
            any(part.get("type") == "image_url" for part in msg.get("content", []))
            for msg in messages
        )
        
        if not has_images:
            # Text-only conversation - return as string
            prompt_parts = []
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
                else:
                    prompt_parts.append(f"{role}: {content}")
            
            return "\n\n".join(prompt_parts)
        else:
            # Multimodal conversation - return as list for Gemini
            content_list = []
            
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                # Add role prefix as text
                if role == "system":
                    content_list.append("System: ")
                elif role == "user":
                    content_list.append("User: ")
                elif role == "assistant":
                    content_list.append("Assistant: ")
                else:
                    content_list.append(f"{role}: ")
                
                # Handle content (string or list for multimodal)
                if isinstance(content, str):
                    content_list.append(content)
                elif isinstance(content, list):
                    # Process multimodal content
                    for part in content:
                        if part.get("type") == "text":
                            content_list.append(part.get("text", ""))
                        elif part.get("type") == "image_url":
                            # Convert image_url to Gemini format
                            image_part = self._convert_image_to_gemini_part(part)
                            if image_part:
                                content_list.append(image_part)
                
                content_list.append("\n\n")  # Separator between messages
            
            return content_list
    
    def _convert_image_to_gemini_part(self, image_part: Dict[str, Any]) -> Optional[Any]:
        """
        Convert OpenAI image_url format to Gemini Part format
        
        Args:
            image_part: OpenAI format like {"type": "image_url", "image_url": {"url": "..."}}
            
        Returns:
            Gemini Part object for the image or None if conversion fails
        """
        try:
            image_url_data = image_part.get("image_url", {})
            url = image_url_data.get("url", "")
            
            if not url:
                return None
            
            # Handle base64 data URLs
            if url.startswith("data:image/"):
                # Extract base64 data and MIME type
                # Format: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
                try:
                    header, base64_data = url.split(",", 1)
                    mime_type = header.split(";")[0].replace("data:", "")
                    
                    # Decode base64 to bytes
                    image_bytes = base64.b64decode(base64_data)
                    
                    # Create Gemini Part from bytes
                    return types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type
                    )
                except Exception as e:
                    if TEST_ENV:
                        debug_print(f"❌ [GeminiClient] Failed to process base64 image: {e}")
                    return None
            
            # Handle HTTP/HTTPS URLs
            elif url.startswith(("http://", "https://")):
                try:
                    # Download image data
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    # Detect MIME type from Content-Type header or URL extension
                    content_type = response.headers.get("content-type", "")
                    if content_type.startswith("image/"):
                        mime_type = content_type
                    else:
                        # Fallback: guess from URL extension
                        if url.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        elif url.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif url.lower().endswith('.gif'):
                            mime_type = "image/gif"
                        elif url.lower().endswith('.webp'):
                            mime_type = "image/webp"
                        else:
                            mime_type = "image/jpeg"  # Default fallback
                    
                    # Create Gemini Part from downloaded bytes
                    return types.Part.from_bytes(
                        data=response.content,
                        mime_type=mime_type
                    )
                except Exception as e:
                    if TEST_ENV:
                        debug_print(f"❌ [GeminiClient] Failed to download image from URL {url}: {e}")
                    return None
            
            else:
                if TEST_ENV:
                    debug_print(f"❌ [GeminiClient] Unsupported image URL format: {url[:100]}...")
                return None
                
        except Exception as e:
            if TEST_ENV:
                debug_print(f"❌ [GeminiClient] Error converting image to Gemini part: {e}")
            return None
    
    def _convert_gemini_error(self, error: Exception) -> Exception:
        """Convert Gemini API errors to OpenAI-compatible format"""
        error_message = str(error)
        
        # Handle common Gemini API errors
        if "API key not valid" in error_message or "API_KEY_INVALID" in error_message:
            return GeminiAPIError(f"Invalid API key: {error_message}")
        elif "quota exceeded" in error_message.lower() or "rate limit" in error_message.lower():
            return GeminiAPIError(f"Rate limit exceeded: {error_message}")
        elif "model not found" in error_message.lower() or "not found" in error_message.lower():
            return GeminiAPIError(f"Model not found: {error_message}")
        elif "safety" in error_message.lower() or "blocked" in error_message.lower():
            return GeminiAPIError(f"Content blocked by safety filter: {error_message}")
        elif "Empty response" in error_message:
            return GeminiAPIError("Empty response from Gemini API - possibly blocked content")
        else:
            return GeminiAPIError(f"Gemini API error: {error_message}")

class GeminiClientFactory:
    """Factory for creating Gemini clients with per-node configuration"""
    
    @staticmethod
    def create_client(node_name: str) -> tuple[GeminiClient, str]:
        """
        Create Gemini client and return (client, model_name) for specified node
        
        Args:
            node_name: One of 'intent_detector', 'business_reasoner', 'query_optimizer', 
                      'response_formatter', 'follow_up', 'image_analysis', 'icp_analysis'
        
        Returns:
            Tuple of (GeminiClient, model_name)
        """
        # Get per-node API key (with fallback to global)
        api_key = GeminiClientFactory._get_node_api_key(node_name)
        if not api_key:
            raise ValueError(f"No Gemini API key found for node {node_name}. Set GEMINI_API_KEY_{node_name.upper()} or GEMINI_API_KEY")
        
        # Get model name and thinking budget for this node
        model_name = GeminiClientFactory._get_node_model(node_name)
        thinking_budget = GeminiClientFactory._get_node_thinking_budget(node_name)
        
        # Create Gemini client with per-node API key
        client = GeminiClient(api_key, model_name, thinking_budget)
        
        # Debug logging with API key info
        api_key_type = "per-node" if api_key != GEMINI_API_KEY else "global"
        api_key_preview = f"{api_key[:12]}..." if api_key else "NOT SET"
        
        if thinking_budget is not None and thinking_budget.strip() != "":
            debug_print(f"🚀 [GeminiClientFactory] Created Gemini client for {node_name}: {model_name} (thinking: {thinking_budget}, key: {api_key_type})")
            if TEST_ENV:
                print(f"🎯 [GeminiClientFactory] {node_name} → gemini → {model_name} (thinking: {thinking_budget}, key: {api_key_preview})")
        else:
            debug_print(f"🚀 [GeminiClientFactory] Created Gemini client for {node_name}: {model_name} (thinking: default, key: {api_key_type})")
            if TEST_ENV:
                print(f"🎯 [GeminiClientFactory] {node_name} → gemini → {model_name} (thinking: default, key: {api_key_preview})")
        
        return client, model_name
    
    @staticmethod
    def _get_node_api_key(node_name: str) -> str:
        """Get API key for specified node (per-node key or fallback to global)"""
        api_key_map = {
            "intent_detector": GEMINI_API_KEY_INTENT,
            "business_reasoner": GEMINI_API_KEY_BUSINESS,
            "query_optimizer": GEMINI_API_KEY_QUERY,
            "response_formatter": GEMINI_API_KEY_RESPONSE,
            "follow_up": GEMINI_API_KEY_FOLLOWUP,
            "image_analysis": GEMINI_API_KEY_IMAGE,
            "icp_analysis": GEMINI_API_KEY_ICP
        }
        
        if node_name not in api_key_map:
            raise ValueError(f"Unknown node name: {node_name}")
        
        # Return per-node API key if available, otherwise fallback to global
        return api_key_map[node_name] or GEMINI_API_KEY
    
    @staticmethod
    def _get_node_model(node_name: str) -> str:
        """Get model name for specified node"""
        model_map = {
            "intent_detector": INTENT_DETECTOR_GEMINI_MODEL,
            "business_reasoner": BUSINESS_REASONER_GEMINI_MODEL,
            "query_optimizer": QUERY_OPTIMIZER_GEMINI_MODEL,
            "response_formatter": RESPONSE_FORMATTER_GEMINI_MODEL,
            "follow_up": FOLLOW_UP_GEMINI_MODEL,
            "image_analysis": IMAGE_GEMINI_MODEL,
            "icp_analysis": ICP_GEMINI_MODEL
        }
        
        if node_name not in model_map:
            raise ValueError(f"Unknown node name: {node_name}")
        
        return model_map[node_name]
    
    @staticmethod
    def _get_node_thinking_budget(node_name: str) -> str:
        """Get thinking budget for specified node (returns string or None)"""
        thinking_map = {
            "intent_detector": INTENT_DETECTOR_THINKING_BUDGET,
            "business_reasoner": BUSINESS_REASONER_THINKING_BUDGET,
            "query_optimizer": QUERY_OPTIMIZER_THINKING_BUDGET,
            "response_formatter": RESPONSE_FORMATTER_THINKING_BUDGET,
            "follow_up": FOLLOW_UP_THINKING_BUDGET,
            "image_analysis": IMAGE_THINKING_BUDGET,
            "icp_analysis": ICP_THINKING_BUDGET
        }
        
        if node_name not in thinking_map:
            raise ValueError(f"Unknown node name: {node_name}")
        
        return thinking_map[node_name]

# 🎯 Convenience functions for each node
def create_intent_detector_gemini_client() -> tuple[GeminiClient, str]:
    """Create Gemini client for intent detector node"""
    return GeminiClientFactory.create_client("intent_detector")

def create_business_reasoner_gemini_client() -> tuple[GeminiClient, str]:
    """Create Gemini client for business reasoner node"""
    return GeminiClientFactory.create_client("business_reasoner")

def create_query_optimizer_gemini_client() -> tuple[GeminiClient, str]:
    """Create Gemini client for query optimizer node"""
    return GeminiClientFactory.create_client("query_optimizer")

def create_response_formatter_gemini_client() -> tuple[GeminiClient, str]:
    """Create Gemini client for response formatter node"""
    return GeminiClientFactory.create_client("response_formatter")

def create_follow_up_gemini_client() -> tuple[GeminiClient, str]:
    """Create Gemini client for follow-up evaluator node"""
    return GeminiClientFactory.create_client("follow_up")

def create_image_analysis_gemini_client() -> tuple[GeminiClient, str]:
    """Create Gemini client for image analysis node"""
    return GeminiClientFactory.create_client("image_analysis")

def create_icp_analysis_gemini_client() -> tuple[GeminiClient, str]:
    """Create Gemini client for ICP analysis node"""
    return GeminiClientFactory.create_client("icp_analysis")