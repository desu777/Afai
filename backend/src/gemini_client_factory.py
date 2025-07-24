"""
Vertex AI Gemini Client Factory - Google Cloud Vertex AI Integration (2025)
Client factory using Google Gen AI SDK with Vertex AI backend and thinking support
"""
import json
import base64
import requests
import os
from typing import Dict, Any, List, Optional, Union
from google import genai
from google.genai import types
from config import (
    # Google Cloud Vertex AI configuration
    GOOGLE_CLOUD_PROJECT_ID,
    GOOGLE_CLOUD_API_KEY,
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_APPLICATION_CREDENTIALS,
    GOOGLE_GENAI_USE_VERTEXAI,
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
    # Generation parameters (commented out - using Gemini defaults)
    # GEMINI_TEMPERATURE,
    # GEMINI_TOP_P,
    # GEMINI_TOP_K,
    GEMINI_DEFAULT_TEMPERATURE,
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

class VertexAIGeminiClient:
    """OpenAI-compatible client for Vertex AI Gemini using google.genai SDK"""
    
    def __init__(self, model_name: str, thinking_budget: str = None):
        # Ensure required credentials are available
        if not GOOGLE_CLOUD_PROJECT_ID:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID is required for Vertex AI")
        if not GOOGLE_CLOUD_API_KEY and not GOOGLE_APPLICATION_CREDENTIALS:
            raise ValueError("Either GOOGLE_CLOUD_API_KEY or GOOGLE_APPLICATION_CREDENTIALS is required")
        
        # Set up environment variables for Vertex AI
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true" 
        os.environ["GOOGLE_CLOUD_PROJECT"] = GOOGLE_CLOUD_PROJECT_ID
        os.environ["GOOGLE_CLOUD_LOCATION"] = GOOGLE_CLOUD_LOCATION
        
        # Try API key authentication first (simpler)
        if GOOGLE_CLOUD_API_KEY:
            try:
                # Direct API key with Vertex AI endpoints
                self.client = genai.Client(
                    api_key=GOOGLE_CLOUD_API_KEY,
                    vertexai=True
                )
                auth_method = "API_KEY+VERTEX"
            except Exception as e:
                if TEST_ENV:
                    debug_print(f"[!] API key failed: {str(e)[:30]}")
                # Fallback to ADC
                self.client = genai.Client(vertexai=True)
                auth_method = "ADC_FALLBACK"
        else:
            # Use Application Default Credentials (service account)
            self.client = genai.Client(vertexai=True)
            auth_method = "SERVICE_ACCOUNT"
        
        self.model_name = model_name
        self.thinking_budget = thinking_budget
        self.chat = self  # For OpenAI compatibility
        self.completions = self  # For OpenAI compatibility
        
        if TEST_ENV:
            if thinking_budget is not None and thinking_budget.strip() != "":
                debug_print(f"[AI] Init: {model_name} (think: {thinking_budget}, auth: {auth_method})")
            else:
                debug_print(f"[AI] Init: {model_name} (think: default, auth: {auth_method})")
    
    def create(self, messages: List[Dict[str, str]], 
               temperature: Optional[float] = None,
               response_format: Optional[Dict[str, str]] = None, **kwargs) -> GeminiResponse:
        """
        Create a chat completion using Gemini API with OpenAI-compatible interface
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Temperature parameter for response generation (0.0-2.0)
            response_format: Optional response format (e.g., {"type": "json_object"})
            **kwargs: Additional parameters (for compatibility)
        
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
            
            # Use provided temperature or configured Gemini default
            temp = temperature if temperature is not None else GEMINI_DEFAULT_TEMPERATURE
            
            # Configure generation parameters with temperature support
            # Temperature is now configurable per-node from config.py for consistency with OpenRouter
            # See: backend/src/temperature_topp_topk_gemini.md for detailed explanation  
            generation_config = types.GenerateContentConfig(
                temperature=temp,
                thinking_config=thinking_config
                # top_p, top_k NOT specified - let Gemini use optimized defaults
            )
            
            # Log generation parameters in debug mode
            if TEST_ENV:
                params_used = [f"temp={temp}"]
                if thinking_config:
                    params_used.append(f"thinking={self.thinking_budget}")
                params_used.append("top_p=default")
                params_used.append("top_k=default")
                debug_print(f"[CFG] Params: {', '.join(params_used)}")
            
            # Log multimodal vs text-only mode
            if TEST_ENV:
                if isinstance(prompt, list):
                    debug_print(f"[IMG] Multimodal: {len([p for p in prompt if hasattr(p, 'mime_type')])} imgs")
                else:
                    debug_print(f"[TXT] Text-only mode")
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=generation_config
            )
            
            # Check if response was blocked or empty
            if not response.text or response.text.strip() == "":
                raise GeminiAPIError("Empty response from Vertex AI Gemini API")
            
            if TEST_ENV:
                debug_print(f"[OK] Response: {len(response.text)} chars")
            
            return GeminiResponse(response)
            
        except Exception as e:
            if TEST_ENV:
                debug_print(f"[X] Error: {e}")
            # Convert Vertex AI errors to OpenAI-compatible format
            raise self._convert_vertex_ai_error(e)
    
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
                        debug_print(f"[X] Base64 error: {str(e)[:30]}")
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
                        debug_print(f"[X] Download failed: {str(e)[:30]}")
                    return None
            
            else:
                if TEST_ENV:
                    debug_print(f"[X] Unsupported URL: {url[:50]}...")
                return None
                
        except Exception as e:
            if TEST_ENV:
                debug_print(f"[X] Image convert error: {str(e)[:30]}")
            return None
    
    def _convert_vertex_ai_error(self, error: Exception) -> Exception:
        """Convert Vertex AI Gemini errors to OpenAI-compatible format"""
        error_message = str(error)
        
        # Handle common Vertex AI errors
        if "API key not valid" in error_message or "API_KEY_INVALID" in error_message or "authentication" in error_message.lower():
            return GeminiAPIError(f"Invalid credentials: {error_message}")
        elif "quota exceeded" in error_message.lower() or "rate limit" in error_message.lower():
            return GeminiAPIError(f"Quota exceeded: {error_message}")
        elif "model not found" in error_message.lower() or "not found" in error_message.lower():
            return GeminiAPIError(f"Model not found: {error_message}")
        elif "safety" in error_message.lower() or "blocked" in error_message.lower():
            return GeminiAPIError(f"Content blocked by safety filter: {error_message}")
        elif "project" in error_message.lower() and "not found" in error_message.lower():
            return GeminiAPIError(f"Google Cloud project not found: {error_message}")
        elif "Empty response" in error_message:
            return GeminiAPIError("Empty response from Vertex AI - possibly blocked content")
        else:
            return GeminiAPIError(f"Vertex AI error: {error_message}")

class VertexAIClientFactory:
    """Factory for creating Vertex AI Gemini clients with per-node configuration"""
    
    @staticmethod
    def create_client(node_name: str) -> tuple[VertexAIGeminiClient, str]:
        """
        Create Vertex AI Gemini client and return (client, model_name) for specified node
        
        Args:
            node_name: One of 'intent_detector', 'business_reasoner', 'query_optimizer', 
                      'response_formatter', 'follow_up', 'image_analysis', 'icp_analysis'
        
        Returns:
            Tuple of (VertexAIGeminiClient, model_name)
        """
        # Get model name and thinking budget for this node
        model_name = VertexAIClientFactory._get_node_model(node_name)
        thinking_budget = VertexAIClientFactory._get_node_thinking_budget(node_name)
        
        # Create Vertex AI client (uses global Google Cloud credentials)
        client = VertexAIGeminiClient(model_name, thinking_budget)
        
        # Debug logging
        auth_method = "API KEY" if GOOGLE_CLOUD_API_KEY else "SERVICE ACCOUNT"
        
        if thinking_budget is not None and thinking_budget.strip() != "":
            debug_print(f"[VERTEX] {node_name}: {model_name} (think: {thinking_budget}, auth: {auth_method})")
            if TEST_ENV:
                print(f"[>] {node_name} → vertex-ai → {model_name} (thinking: {thinking_budget}, auth: {auth_method})")
        else:
            debug_print(f"[VERTEX] {node_name}: {model_name} (think: default, auth: {auth_method})")
            if TEST_ENV:
                print(f"[>] {node_name} → vertex-ai → {model_name} (thinking: default, auth: {auth_method})")
        
        return client, model_name
    
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

# Convenience functions for each node
def create_intent_detector_gemini_client() -> tuple[VertexAIGeminiClient, str]:
    """Create Vertex AI Gemini client for intent detector node"""
    return VertexAIClientFactory.create_client("intent_detector")

def create_business_reasoner_gemini_client() -> tuple[VertexAIGeminiClient, str]:
    """Create Vertex AI Gemini client for business reasoner node"""
    return VertexAIClientFactory.create_client("business_reasoner")

def create_query_optimizer_gemini_client() -> tuple[VertexAIGeminiClient, str]:
    """Create Vertex AI Gemini client for query optimizer node"""
    return VertexAIClientFactory.create_client("query_optimizer")

def create_response_formatter_gemini_client() -> tuple[VertexAIGeminiClient, str]:
    """Create Vertex AI Gemini client for response formatter node"""
    return VertexAIClientFactory.create_client("response_formatter")

def create_follow_up_gemini_client() -> tuple[VertexAIGeminiClient, str]:
    """Create Vertex AI Gemini client for follow-up evaluator node"""
    return VertexAIClientFactory.create_client("follow_up")

def create_image_analysis_gemini_client() -> tuple[VertexAIGeminiClient, str]:
    """Create Vertex AI Gemini client for image analysis node"""
    return VertexAIClientFactory.create_client("image_analysis")

def create_icp_analysis_gemini_client() -> tuple[VertexAIGeminiClient, str]:
    """Create Vertex AI Gemini client for ICP analysis node"""
    return VertexAIClientFactory.create_client("icp_analysis")