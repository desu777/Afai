"""
Configuration module for Aquaforest RAG System
Handles all environment variables and system settings
"""
import os
from pathlib import Path
from env_loader import load_environment

# Load environment variables from external or local .env file
load_environment()

# --- DEBUG ---
# Add test environment flag - can be dynamically changed
TEST_ENV = os.getenv("TEST_ENV", "false").lower() == "true"

# 🆕 FLAG TO DISABLE BUSINESS MAPPINGS FOR TESTING
DISABLE_BUSINESS_MAPPINGS = os.getenv("DISABLE_BUSINESS_MAPPINGS", "false").lower() == "true"

# 🆕 FLAG TO ENABLE ONLY COMPETITORS MAPPING
ENABLE_COMPETITORS_ONLY = os.getenv("ENABLE_COMPETITORS_ONLY", "false").lower() == "true"

# Debug print function
def debug_print(message: str, emoji: str = "🔍"):
    """Print debug message if TEST_ENV is True"""
    if TEST_ENV:
        print(f"{emoji} {message}")
# --- END DEBUG ---

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "aqua")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")

# 🚀 OpenRouter Per-Node Configuration (2025)
# Per-node API keys: each workflow component has its own OpenRouter API key
INTENT_DETECTOR_API = os.getenv("INTENT_DETECTOR_API")
BUSINESS_REASONER_API = os.getenv("BUSINESS_REASONER_API")
QUERY_OPTIMIZER_API = os.getenv("QUERY_OPTIMIZER_API")
RESPONSE_FORMATTER_API = os.getenv("RESPONSE_FORMATTER_API")
FOLLOW_UP_API = os.getenv("FOLLOW_UP_API")

# Per-node model selection: each workflow component can use different model
INTENT_DETECTOR_MODEL = os.getenv("INTENT_DETECTOR_MODEL")
BUSINESS_REASONER_MODEL = os.getenv("BUSINESS_REASONER_MODEL")
QUERY_OPTIMIZER_MODEL = os.getenv("QUERY_OPTIMIZER_MODEL")
RESPONSE_FORMATTER_MODEL = os.getenv("RESPONSE_FORMATTER_MODEL")
FOLLOW_UP_MODEL = os.getenv("FOLLOW_UP_MODEL")

# 📸 IMAGE ANALYSIS CONFIGURATION
IMAGE_API = os.getenv("IMAGE_API") or INTENT_DETECTOR_API
IMAGE_MODEL = os.getenv("IMAGE_MODEL") or INTENT_DETECTOR_MODEL

# 📄 ICP ANALYSIS CONFIGURATION
ICP_API = os.getenv("ICP_API") or INTENT_DETECTOR_API
ICP_MODEL = os.getenv("ICP_MODEL") or INTENT_DETECTOR_MODEL

# Fallback API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Keep for backwards compatibility

# 🚀 GEMINI API CONFIGURATION (2025)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# LLM Provider Selection - per-node configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")  # Default to OpenRouter
INTENT_DETECTOR_PROVIDER = os.getenv("INTENT_DETECTOR_PROVIDER", LLM_PROVIDER)
BUSINESS_REASONER_PROVIDER = os.getenv("BUSINESS_REASONER_PROVIDER", LLM_PROVIDER)
QUERY_OPTIMIZER_PROVIDER = os.getenv("QUERY_OPTIMIZER_PROVIDER", LLM_PROVIDER)
RESPONSE_FORMATTER_PROVIDER = os.getenv("RESPONSE_FORMATTER_PROVIDER", LLM_PROVIDER)
FOLLOW_UP_PROVIDER = os.getenv("FOLLOW_UP_PROVIDER", LLM_PROVIDER)
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", LLM_PROVIDER)
ICP_PROVIDER = os.getenv("ICP_PROVIDER", LLM_PROVIDER)

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

# 🧠 THINKING CONFIGURATION (per-node thinking budget)
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

# Common settings
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "16384"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))  # Default to Qwen3 32B

# Hyperbrowser Configuration
HYPERBROWSER_API_KEY = os.getenv("HYPERBROWSER_API_KEY")

# App Configuration
DEFAULT_K_VALUE = int(os.getenv("DEFAULT_K_VALUE", "12"))
ENHANCED_K_VALUE = int(os.getenv("ENHANCED_K_VALUE", "12"))

# 🚀 PINECONE PARALLEL SEARCH CONFIGURATION
MAX_CONCURRENT_QUERIES = int(os.getenv("MAX_CONCURRENT_QUERIES", "4"))
MAX_CONCURRENT_EMBEDDINGS = int(os.getenv("MAX_CONCURRENT_EMBEDDINGS", "4"))
PINECONE_POOL_THREADS = int(os.getenv("PINECONE_POOL_THREADS", "50"))
PINECONE_CONNECTION_POOL_MAX = int(os.getenv("PINECONE_CONNECTION_POOL_MAX", "50"))
ENABLE_PARALLEL_SEARCH = os.getenv("ENABLE_PARALLEL_SEARCH", "true").lower() == "true"

SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "pl,en,de,fr,es,it").split(",")

# Paths - Use absolute path based on file location
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH") or str(Path(__file__).parent.parent.absolute() / "data" / "products.json")
PRODUCTS_TURBO_FILE_PATH = os.getenv("PRODUCTS_TURBO_FILE_PATH") or str(Path(__file__).parent.parent.absolute() / "data" / "products_turbo.json")

# Server Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8080").split(",")

# Authentication Configuration
AQUAFOREST_AUTH_TOKEN = os.getenv("AQUAFOREST_AUTH_TOKEN")
ENABLE_AUTH_TOKEN = os.getenv("ENABLE_AUTH_TOKEN", "true").lower() == "true"

# 🚀 FACEBOOK MESSENGER CONFIGURATION
MESSENGER_ON = os.getenv("MESSENGER_ON", "true").lower() == "true"
MESSENGER_PAGE_ACCESS_TOKEN = os.getenv("MESSENGER_TOKEN")
MESSENGER_VERIFY_TOKEN = os.getenv("MESSENGER_VERIFY_TOKEN", "aquaforest_webhook_2025")
FACEBOOK_API_VERSION = os.getenv("FACEBOOK_API_VERSION", "v22.0")

# 🆕 COMPETITOR LIST
COMPETITORS = [
    "Red Sea", "Seachem", "Tropic Marin", "Brightwell", "Two Little Fishies",
    "Salifert", "Continuum", "Korallen-Zucht", "ESV", "Kent Marine",
    "Aqua Medic", "Fauna Marin", "Nyos", "ATI", "Giesemann"
]

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

# Validate Gemini API key if any node uses Gemini
gemini_nodes = [
    INTENT_DETECTOR_PROVIDER, BUSINESS_REASONER_PROVIDER, QUERY_OPTIMIZER_PROVIDER,
    RESPONSE_FORMATTER_PROVIDER, FOLLOW_UP_PROVIDER, IMAGE_PROVIDER, ICP_PROVIDER
]
if "gemini" in gemini_nodes and not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is required when any node uses Gemini provider")

if MESSENGER_ON and not MESSENGER_PAGE_ACCESS_TOKEN:
    raise ValueError("MESSENGER_TOKEN is required when MESSENGER_ON=true")

if ENABLE_AUTH_TOKEN and not AQUAFOREST_AUTH_TOKEN:
    raise ValueError("AQUAFOREST_AUTH_TOKEN is required when ENABLE_AUTH_TOKEN=true")

if not HYPERBROWSER_API_KEY:
    raise ValueError("HYPERBROWSER_API_KEY is required for ICP analysis functionality")

# Print configuration status on import (only in debug mode)
if TEST_ENV:
    print("\n" + "="*60)
    print("🔧 CONFIGURATION LOADED")
    print("="*60)
    print(f"📍 Debug Mode: ENABLED")
    print(f"📍 Business Mappings: {'DISABLED' if DISABLE_BUSINESS_MAPPINGS else 'ENABLED'}")
    print(f"📍 Competitors Only: {'ENABLED' if ENABLE_COMPETITORS_ONLY else 'DISABLED'}")
    print(f"🚀 Dual API Configuration (OpenRouter + Gemini 2.5)")
    
    # Helper function to format node info with thinking (only for Gemini provider)
    def format_node_info(provider, openrouter_model, gemini_model, thinking_budget):
        model = openrouter_model if provider == 'openrouter' else gemini_model
        if provider == 'gemini' and thinking_budget is not None and thinking_budget.strip() != "":
            return f"{provider} → {model} (thinking: {thinking_budget})"
        else:
            return f"{provider} → {model}"
    
    print(f"🎯 Intent Detector: {format_node_info(INTENT_DETECTOR_PROVIDER, INTENT_DETECTOR_MODEL, INTENT_DETECTOR_GEMINI_MODEL, INTENT_DETECTOR_THINKING_BUDGET)}")
    print(f"🧠 Business Reasoner: {format_node_info(BUSINESS_REASONER_PROVIDER, BUSINESS_REASONER_MODEL, BUSINESS_REASONER_GEMINI_MODEL, BUSINESS_REASONER_THINKING_BUDGET)}")
    print(f"🔍 Query Optimizer: {format_node_info(QUERY_OPTIMIZER_PROVIDER, QUERY_OPTIMIZER_MODEL, QUERY_OPTIMIZER_GEMINI_MODEL, QUERY_OPTIMIZER_THINKING_BUDGET)}")
    print(f"📝 Response Formatter: {format_node_info(RESPONSE_FORMATTER_PROVIDER, RESPONSE_FORMATTER_MODEL, RESPONSE_FORMATTER_GEMINI_MODEL, RESPONSE_FORMATTER_THINKING_BUDGET)}")
    print(f"🔄 Follow-up Evaluator: {format_node_info(FOLLOW_UP_PROVIDER, FOLLOW_UP_MODEL, FOLLOW_UP_GEMINI_MODEL, FOLLOW_UP_THINKING_BUDGET)}")
    print(f"📸 Image Analysis: {format_node_info(IMAGE_PROVIDER, IMAGE_MODEL, IMAGE_GEMINI_MODEL, IMAGE_THINKING_BUDGET)}")
    print(f"📄 ICP Analysis: {format_node_info(ICP_PROVIDER, ICP_MODEL, ICP_GEMINI_MODEL, ICP_THINKING_BUDGET)}")
    print(f"🔑 Gemini API: {'CONFIGURED' if GEMINI_API_KEY else 'NOT SET'}")
    if GEMINI_DEFAULT_THINKING_BUDGET is not None and GEMINI_DEFAULT_THINKING_BUDGET.strip() != "":
        print(f"🧠 Default Thinking Budget: {GEMINI_DEFAULT_THINKING_BUDGET}")
    else:
        print(f"🧠 Default Thinking Budget: Gemini default")
    print(f"📍 Embedding Model: {OPENAI_EMBEDDING_MODEL}")
    print(f"📍 Pinecone Index: {PINECONE_INDEX_NAME}")
    print(f"📍 Default K Value: {DEFAULT_K_VALUE}")
    print(f"📍 Enhanced K Value: {ENHANCED_K_VALUE}")
    print(f"🚀 Parallel Search: {'ENABLED' if ENABLE_PARALLEL_SEARCH else 'DISABLED'}")
    print(f"🔄 Max Concurrent Queries: {MAX_CONCURRENT_QUERIES}")
    print(f"🔄 Max Concurrent Embeddings: {MAX_CONCURRENT_EMBEDDINGS}")
    print(f"🔄 Pinecone Pool Threads: {PINECONE_POOL_THREADS}")
    print(f"🔄 Pinecone Connection Pool Max: {PINECONE_CONNECTION_POOL_MAX}")
    print(f"📍 Supported Languages: {', '.join(SUPPORTED_LANGUAGES)}")
    print(f"📍 CORS Origins: {', '.join(CORS_ORIGINS)}")
    print(f"📍 Competitors tracked: {len(COMPETITORS)}")
    print(f"📍 Messenger Integration: {'ENABLED' if MESSENGER_ON else 'DISABLED'}")
    print(f"📍 Facebook API Version: {FACEBOOK_API_VERSION}")
    print(f"🔐 Auth Token: {'ENABLED' if ENABLE_AUTH_TOKEN else 'DISABLED'}")
    print(f"🌐 Hyperbrowser API: {HYPERBROWSER_API_KEY[:12]}..." if HYPERBROWSER_API_KEY else "🌐 Hyperbrowser API: NOT SET")
    print(f"🗑️ Confidence Scorer: REMOVED for better performance")
    print("="*60 + "\n")