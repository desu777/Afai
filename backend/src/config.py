"""
Configuration module for Aquaforest RAG System
Handles all environment variables and system settings
"""
import os
from pathlib import Path
from env_loader import load_environment

# Load environment variables from external or local .env file
load_environment()

# Import enhanced logger
from utils.logger import logger

# Enhanced debug print function
def debug_print(message: str, emoji: str = "[DEBUG]"):
    """Enhanced debug print using centralized logger"""
    logger.debug(message.replace(emoji, "").strip())


# ==========================================
# 🚧 DEBUG & DEVELOPMENT CONFIGURATION
# ==========================================

# Test environment flag - can be dynamically changed
TEST_ENV = os.getenv("TEST_ENV", "false").lower() == "true"

# Flag to disable business mappings for testing
DISABLE_BUSINESS_MAPPINGS = os.getenv("DISABLE_BUSINESS_MAPPINGS", "false").lower() == "true"

# Flag to enable only competitors mapping
ENABLE_COMPETITORS_ONLY = os.getenv("ENABLE_COMPETITORS_ONLY", "false").lower() == "true"


# ==========================================
# 🗄️ DATABASE CONFIGURATION (PINECONE)
# ==========================================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "aqua")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")


# ==========================================
# 🤖 AI/LLM CONFIGURATION
# ==========================================

# --- OpenRouter API Keys (Per-Node) ---
# Each workflow component has its own OpenRouter API key
INTENT_DETECTOR_API = os.getenv("INTENT_DETECTOR_API")
BUSINESS_REASONER_API = os.getenv("BUSINESS_REASONER_API")
QUERY_OPTIMIZER_API = os.getenv("QUERY_OPTIMIZER_API")
RESPONSE_FORMATTER_API = os.getenv("RESPONSE_FORMATTER_API")
FOLLOW_UP_API = os.getenv("FOLLOW_UP_API")

# Special nodes API configuration
IMAGE_API = os.getenv("IMAGE_API") or INTENT_DETECTOR_API
ICP_API = os.getenv("ICP_API") or INTENT_DETECTOR_API

# --- OpenRouter Models (Per-Node) ---
# Each workflow component can use different model
INTENT_DETECTOR_MODEL = os.getenv("INTENT_DETECTOR_MODEL")
BUSINESS_REASONER_MODEL = os.getenv("BUSINESS_REASONER_MODEL")
QUERY_OPTIMIZER_MODEL = os.getenv("QUERY_OPTIMIZER_MODEL")
RESPONSE_FORMATTER_MODEL = os.getenv("RESPONSE_FORMATTER_MODEL")
FOLLOW_UP_MODEL = os.getenv("FOLLOW_UP_MODEL")

# Special nodes model configuration
IMAGE_MODEL = os.getenv("IMAGE_MODEL") or INTENT_DETECTOR_MODEL
ICP_MODEL = os.getenv("ICP_MODEL") or INTENT_DETECTOR_MODEL

# --- Google Cloud Vertex AI Configuration ---
# Minimal credentials for Vertex AI
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # Alternative: service account JSON path

# Force Vertex AI usage (set automatically in client)
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"

# --- Provider Selection (Per-Node) ---
# LLM Provider Selection - per-node configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")  # Default to OpenRouter
INTENT_DETECTOR_PROVIDER = os.getenv("INTENT_DETECTOR_PROVIDER", LLM_PROVIDER)
BUSINESS_REASONER_PROVIDER = os.getenv("BUSINESS_REASONER_PROVIDER", LLM_PROVIDER)
QUERY_OPTIMIZER_PROVIDER = os.getenv("QUERY_OPTIMIZER_PROVIDER", LLM_PROVIDER)
RESPONSE_FORMATTER_PROVIDER = os.getenv("RESPONSE_FORMATTER_PROVIDER", LLM_PROVIDER)
FOLLOW_UP_PROVIDER = os.getenv("FOLLOW_UP_PROVIDER", LLM_PROVIDER)
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", LLM_PROVIDER)
ICP_PROVIDER = os.getenv("ICP_PROVIDER", LLM_PROVIDER)

# --- Gemini Models (Per-Node) ---
# Gemini model configuration (optimal defaults per-node)
GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")

# Per-node model selection (optimized for task requirements)
INTENT_DETECTOR_GEMINI_MODEL = os.getenv("INTENT_DETECTOR_GEMINI_MODEL", "gemini-2.5-flash")  # Speed priority
BUSINESS_REASONER_GEMINI_MODEL = os.getenv("BUSINESS_REASONER_GEMINI_MODEL", "gemini-2.5-pro")  # Reasoning priority
QUERY_OPTIMIZER_GEMINI_MODEL = os.getenv("QUERY_OPTIMIZER_GEMINI_MODEL", "gemini-2.5-flash")  # Speed priority
RESPONSE_FORMATTER_GEMINI_MODEL = os.getenv("RESPONSE_FORMATTER_GEMINI_MODEL", "gemini-2.5-flash")  # Speed priority
FOLLOW_UP_GEMINI_MODEL = os.getenv("FOLLOW_UP_GEMINI_MODEL", "gemini-2.5-pro")  # Reasoning priority
IMAGE_GEMINI_MODEL = os.getenv("IMAGE_GEMINI_MODEL", "gemini-2.5-flash")  # Vision optimized
ICP_GEMINI_MODEL = os.getenv("ICP_GEMINI_MODEL", "gemini-2.5-pro")  # Analysis priority

# --- Thinking Configuration (Gemini Only) ---
# Only for provider=gemini - OpenRouter doesn't support thinking
# Leave empty = use Gemini's default thinking
GEMINI_DEFAULT_THINKING_BUDGET = os.getenv("GEMINI_DEFAULT_THINKING_BUDGET")

# Per-node thinking budget (only applies when provider=gemini)
# Only set if you want to override Gemini's default thinking
INTENT_DETECTOR_THINKING_BUDGET = os.getenv("INTENT_DETECTOR_THINKING_BUDGET")
BUSINESS_REASONER_THINKING_BUDGET = os.getenv("BUSINESS_REASONER_THINKING_BUDGET")
QUERY_OPTIMIZER_THINKING_BUDGET = os.getenv("QUERY_OPTIMIZER_THINKING_BUDGET")
RESPONSE_FORMATTER_THINKING_BUDGET = os.getenv("RESPONSE_FORMATTER_THINKING_BUDGET")
FOLLOW_UP_THINKING_BUDGET = os.getenv("FOLLOW_UP_THINKING_BUDGET")
IMAGE_THINKING_BUDGET = os.getenv("IMAGE_THINKING_BUDGET")
ICP_THINKING_BUDGET = os.getenv("ICP_THINKING_BUDGET")

# --- Temperature Configuration (Per-Node) ---
# Per-node temperature configuration (used by both Gemini and OpenRouter providers)
INTENT_DETECTOR_TEMPERATURE = float(os.getenv("INTENT_DETECTOR_TEMPERATURE", "0.3"))  # Intent detection temperature
BUSINESS_REASONER_TEMPERATURE = float(os.getenv("BUSINESS_REASONER_TEMPERATURE", "0.5"))  # Business reasoning temperature
QUERY_OPTIMIZER_TEMPERATURE = float(os.getenv("QUERY_OPTIMIZER_TEMPERATURE", "0.3"))  # Query optimization temperature
RESPONSE_FORMATTER_TEMPERATURE = float(os.getenv("RESPONSE_FORMATTER_TEMPERATURE", "0.7"))  # Response formatting temperature
FOLLOW_UP_TEMPERATURE = float(os.getenv("FOLLOW_UP_TEMPERATURE", "0.3"))  # Low temperature for consistent cache evaluation
ICP_TEMPERATURE = float(os.getenv("ICP_TEMPERATURE", "0.3"))  # Low temperature for consistent JSON output

# Gemini fallback temperature (when no temperature parameter provided)
GEMINI_DEFAULT_TEMPERATURE = float(os.getenv("GEMINI_DEFAULT_TEMPERATURE", "0.3"))  # Default temperature when none specified

# --- Resilient Fallback Configuration ---
# Configuration for Gemini → OpenRouter automatic fallback
ENABLE_GEMINI_FALLBACK = os.getenv("ENABLE_GEMINI_FALLBACK", "true").lower() == "true"  # Enable/disable fallback mechanism
GEMINI_REQUEST_TIMEOUT = float(os.getenv("GEMINI_REQUEST_TIMEOUT", "55"))  # Timeout in seconds (below 60s Gemini limit)
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "2"))  # Number of retries before fallback
GEMINI_RETRY_DELAY = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))  # Delay between retries in seconds
LOG_FALLBACK_EVENTS = os.getenv("LOG_FALLBACK_EVENTS", "true").lower() == "true"  # Log when fallback occurs

# --- Legacy/Compatibility Configuration ---
# Fallback API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Keep for backwards compatibility

# Common settings
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "16384"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))  # Default to Qwen3 32B

# [CONFIG] GEMINI GENERATION PARAMETERS (COMMENTED OUT - using Gemini defaults)
# See: backend/src/temperature_topp_topk_gemini.md for detailed explanation
# Let Gemini use its optimized default parameters (temp=1.0, top_p=0.95, top_k=default)
# Uncomment and configure below if responses need fine-tuning:

# GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "1.0"))  # Gemini default
# GEMINI_TOP_P = float(os.getenv("GEMINI_TOP_P", "0.95"))  # Gemini default
# GEMINI_TOP_K = os.getenv("GEMINI_TOP_K")  # Empty = default Gemini

# Convert TOP_K to int if provided, otherwise None for default Gemini behavior
# if GEMINI_TOP_K and GEMINI_TOP_K.strip():
#     GEMINI_TOP_K = int(GEMINI_TOP_K)
# else:
#     GEMINI_TOP_K = None


# ==========================================
# ⚙️ APPLICATION CONFIGURATION
# ==========================================

# Search configuration
DEFAULT_K_VALUE = int(os.getenv("DEFAULT_K_VALUE", "12"))
ENHANCED_K_VALUE = int(os.getenv("ENHANCED_K_VALUE", "12"))

# Pinecone parallel search configuration
MAX_CONCURRENT_QUERIES = int(os.getenv("MAX_CONCURRENT_QUERIES", "4"))
MAX_CONCURRENT_EMBEDDINGS = int(os.getenv("MAX_CONCURRENT_EMBEDDINGS", "4"))
PINECONE_POOL_THREADS = int(os.getenv("PINECONE_POOL_THREADS", "50"))
PINECONE_CONNECTION_POOL_MAX = int(os.getenv("PINECONE_CONNECTION_POOL_MAX", "50"))
ENABLE_PARALLEL_SEARCH = os.getenv("ENABLE_PARALLEL_SEARCH", "true").lower() == "true"

# Language support
SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "pl,en,de,fr,es,it").split(",")


# ==========================================
# 📁 PATHS & FILES CONFIGURATION
# ==========================================

# Paths - Use absolute path based on file location
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH") or str(Path(__file__).parent.parent.absolute() / "data" / "products.json")
PRODUCTS_TURBO_FILE_PATH = os.getenv("PRODUCTS_TURBO_FILE_PATH") or str(Path(__file__).parent.parent.absolute() / "data" / "products_turbo.json")


# ==========================================
# 🌐 SERVER & API CONFIGURATION
# ==========================================

# Server Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8080").split(",")


# ==========================================
# 🔐 AUTHENTICATION & SECURITY
# ==========================================

# Authentication Configuration
AQUAFOREST_AUTH_TOKEN = os.getenv("AQUAFOREST_AUTH_TOKEN")
ENABLE_AUTH_TOKEN = os.getenv("ENABLE_AUTH_TOKEN", "true").lower() == "true"


# ==========================================
# 📱 EXTERNAL INTEGRATIONS
# ==========================================

# Facebook Messenger Configuration
MESSENGER_ON = os.getenv("MESSENGER_ON", "true").lower() == "true"
MESSENGER_PAGE_ACCESS_TOKEN = os.getenv("MESSENGER_TOKEN")
MESSENGER_VERIFY_TOKEN = os.getenv("MESSENGER_VERIFY_TOKEN", "aquaforest_webhook_2025")
FACEBOOK_API_VERSION = os.getenv("FACEBOOK_API_VERSION", "v22.0")


# ==========================================
# 🏢 BUSINESS CONFIGURATION
# ==========================================

# Competitor list
COMPETITORS = [
    "Red Sea", "Seachem", "Tropic Marin", "Brightwell", "Two Little Fishies",
    "Salifert", "Continuum", "Korallen-Zucht", "ESV", "Kent Marine",
    "Aqua Medic", "Fauna Marin", "Nyos", "ATI", "Giesemann"
]


# ==========================================
# ✅ VALIDATION & STARTUP
# ==========================================

# Validate required variables
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is required")

# Validate per-node API keys (only for OpenRouter nodes)
missing_api_keys = []
if INTENT_DETECTOR_PROVIDER == "openrouter" and not INTENT_DETECTOR_API:
    missing_api_keys.append("INTENT_DETECTOR_API")
if BUSINESS_REASONER_PROVIDER == "openrouter" and not BUSINESS_REASONER_API:
    missing_api_keys.append("BUSINESS_REASONER_API")
if QUERY_OPTIMIZER_PROVIDER == "openrouter" and not QUERY_OPTIMIZER_API:
    missing_api_keys.append("QUERY_OPTIMIZER_API")
if RESPONSE_FORMATTER_PROVIDER == "openrouter" and not RESPONSE_FORMATTER_API:
    missing_api_keys.append("RESPONSE_FORMATTER_API")
if FOLLOW_UP_PROVIDER == "openrouter" and not FOLLOW_UP_API:
    missing_api_keys.append("FOLLOW_UP_API")

if missing_api_keys:
    raise ValueError(f"Missing per-node API keys for OpenRouter: {', '.join(missing_api_keys)}")

# Validate Google Cloud Vertex AI credentials
# Check that either API key OR service account credentials are provided
def validate_vertex_ai_credentials():
    """Validate that required Vertex AI credentials are available"""
    if not GOOGLE_CLOUD_PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT_ID is required for Vertex AI")
    
    # Either API key OR service account JSON must be provided
    has_api_key = bool(GOOGLE_CLOUD_API_KEY)
    has_service_account = bool(GOOGLE_APPLICATION_CREDENTIALS)
    
    if not has_api_key and not has_service_account:
        raise ValueError("Either GOOGLE_CLOUD_API_KEY or GOOGLE_APPLICATION_CREDENTIALS is required for Vertex AI authentication")

# Check if any node uses Vertex AI provider
vertex_ai_nodes = []
node_provider_map = {
    "intent_detector": INTENT_DETECTOR_PROVIDER,
    "business_reasoner": BUSINESS_REASONER_PROVIDER,
    "query_optimizer": QUERY_OPTIMIZER_PROVIDER,
    "response_formatter": RESPONSE_FORMATTER_PROVIDER,
    "follow_up": FOLLOW_UP_PROVIDER,
    "image_analysis": IMAGE_PROVIDER,
    "icp_analysis": ICP_PROVIDER
}

for node_name, provider in node_provider_map.items():
    if provider == "gemini":
        vertex_ai_nodes.append(node_name)

# Only validate if any node uses Vertex AI
if vertex_ai_nodes:
    validate_vertex_ai_credentials()

if MESSENGER_ON and not MESSENGER_PAGE_ACCESS_TOKEN:
    raise ValueError("MESSENGER_TOKEN is required when MESSENGER_ON=true")

if ENABLE_AUTH_TOKEN and not AQUAFOREST_AUTH_TOKEN:
    raise ValueError("AQUAFOREST_AUTH_TOKEN is required when ENABLE_AUTH_TOKEN=true")


# ==========================================
# 📊 DEBUG INFORMATION DISPLAY
# ==========================================

# Print configuration status on import (only in debug mode)
if TEST_ENV:
    logger.header("[CONFIG] CONFIGURATION LOADED")
    logger.configuration("Debug Mode: ENABLED")
    logger.configuration(f"Business Mappings: {'DISABLED' if DISABLE_BUSINESS_MAPPINGS else 'ENABLED'}")
    logger.configuration(f"Competitors Only: {'ENABLED' if ENABLE_COMPETITORS_ONLY else 'DISABLED'}")
    logger.configuration("Dual API Configuration (OpenRouter + Gemini 2.5)", "SUB")
    
    # Helper function to format node info with thinking (only for Gemini provider)
    def format_node_info(provider, openrouter_model, gemini_model, thinking_budget):
        model = openrouter_model if provider == 'openrouter' else gemini_model
        if provider == 'gemini' and thinking_budget is not None and thinking_budget.strip() != "":
            return f"{provider} → {model} (thinking: {thinking_budget})"
        else:
            return f"{provider} → {model}"
    
    logger.configuration(f"Intent Detector: {format_node_info(INTENT_DETECTOR_PROVIDER, INTENT_DETECTOR_MODEL, INTENT_DETECTOR_GEMINI_MODEL, INTENT_DETECTOR_THINKING_BUDGET)}", "SUB")
    logger.configuration(f"Business Reasoner: {format_node_info(BUSINESS_REASONER_PROVIDER, BUSINESS_REASONER_MODEL, BUSINESS_REASONER_GEMINI_MODEL, BUSINESS_REASONER_THINKING_BUDGET)}", "SUB")
    logger.configuration(f"Query Optimizer: {format_node_info(QUERY_OPTIMIZER_PROVIDER, QUERY_OPTIMIZER_MODEL, QUERY_OPTIMIZER_GEMINI_MODEL, QUERY_OPTIMIZER_THINKING_BUDGET)}", "SUB")
    logger.configuration(f"Response Formatter: {format_node_info(RESPONSE_FORMATTER_PROVIDER, RESPONSE_FORMATTER_MODEL, RESPONSE_FORMATTER_GEMINI_MODEL, RESPONSE_FORMATTER_THINKING_BUDGET)}", "SUB")
    logger.configuration(f"Follow-up Evaluator: {format_node_info(FOLLOW_UP_PROVIDER, FOLLOW_UP_MODEL, FOLLOW_UP_GEMINI_MODEL, FOLLOW_UP_THINKING_BUDGET)}", "SUB")
    logger.configuration(f"Image Analysis: {format_node_info(IMAGE_PROVIDER, IMAGE_MODEL, IMAGE_GEMINI_MODEL, IMAGE_THINKING_BUDGET)}", "SUB")
    logger.configuration(f"ICP Analysis: {format_node_info(ICP_PROVIDER, ICP_MODEL, ICP_GEMINI_MODEL, ICP_THINKING_BUDGET)}", "SUB")
    logger.configuration(f"Google Cloud Project ID: {'CONFIGURED' if GOOGLE_CLOUD_PROJECT_ID else 'NOT SET'}", "SUB")
    logger.configuration(f"Google Cloud Location: {GOOGLE_CLOUD_LOCATION}", "SUB")
    logger.configuration(f"Vertex AI Auth: {'API KEY' if GOOGLE_CLOUD_API_KEY else 'SERVICE ACCOUNT' if GOOGLE_APPLICATION_CREDENTIALS else 'NOT SET'}", "SUB")
    
    # Resilient fallback configuration
    logger.configuration("Resilient Fallback Configuration", "SUB")
    logger.configuration(f"Fallback Enabled: {'YES' if ENABLE_GEMINI_FALLBACK else 'NO'}", "SUB")
    if ENABLE_GEMINI_FALLBACK:
        logger.configuration(f"Request Timeout: {GEMINI_REQUEST_TIMEOUT}s", "SUB")
        logger.configuration(f"Max Retries: {GEMINI_MAX_RETRIES}", "SUB")
        logger.configuration(f"Retry Delay: {GEMINI_RETRY_DELAY}s", "SUB")
        logger.configuration(f"Log Fallback Events: {'YES' if LOG_FALLBACK_EVENTS else 'NO'}", "SUB")
    
    if GEMINI_DEFAULT_THINKING_BUDGET is not None and GEMINI_DEFAULT_THINKING_BUDGET.strip() != "":
        logger.configuration(f"Default Thinking Budget: {GEMINI_DEFAULT_THINKING_BUDGET}", "SUB")
    else:
        logger.configuration("Default Thinking Budget: Gemini default", "SUB")
    
    logger.configuration(f"Embedding Model: {OPENAI_EMBEDDING_MODEL}", "SUB")
    logger.configuration(f"Pinecone Index: {PINECONE_INDEX_NAME}", "SUB")
    logger.configuration(f"Default K Value: {DEFAULT_K_VALUE}", "SUB")
    logger.configuration(f"Enhanced K Value: {ENHANCED_K_VALUE}", "SUB")
    logger.configuration(f"Parallel Search: {'ENABLED' if ENABLE_PARALLEL_SEARCH else 'DISABLED'}", "SUB")
    logger.configuration(f"Max Concurrent Queries: {MAX_CONCURRENT_QUERIES}", "SUB")
    logger.configuration(f"Max Concurrent Embeddings: {MAX_CONCURRENT_EMBEDDINGS}", "SUB")
    logger.configuration(f"Pinecone Pool Threads: {PINECONE_POOL_THREADS}", "SUB")
    logger.configuration(f"Pinecone Connection Pool Max: {PINECONE_CONNECTION_POOL_MAX}", "SUB")
    logger.configuration(f"Supported Languages: {', '.join(SUPPORTED_LANGUAGES)}", "SUB")
    logger.configuration(f"CORS Origins: {', '.join(CORS_ORIGINS)}", "SUB")
    logger.configuration(f"Competitors tracked: {len(COMPETITORS)}", "SUB")
    logger.configuration(f"Messenger Integration: {'ENABLED' if MESSENGER_ON else 'DISABLED'}", "SUB")
    logger.configuration(f"Facebook API Version: {FACEBOOK_API_VERSION}", "SUB")
    logger.configuration(f"Auth Token: {'ENABLED' if ENABLE_AUTH_TOKEN else 'DISABLED'}", "SUB")
    logger.configuration("Confidence Scorer: REMOVED for better performance", "SUB")
    logger.separator()