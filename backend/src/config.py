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

# Validate per-node API keys
missing_api_keys = []
if not INTENT_DETECTOR_API:
    missing_api_keys.append("INTENT_DETECTOR_API")
if not BUSINESS_REASONER_API:
    missing_api_keys.append("BUSINESS_REASONER_API")
if not QUERY_OPTIMIZER_API:
    missing_api_keys.append("QUERY_OPTIMIZER_API")
if not RESPONSE_FORMATTER_API:
    missing_api_keys.append("RESPONSE_FORMATTER_API")
if not FOLLOW_UP_API:
    missing_api_keys.append("FOLLOW_UP_API")

if missing_api_keys:
    raise ValueError(f"Missing per-node API keys: {', '.join(missing_api_keys)}")

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
    print(f"🚀 OpenRouter Per-Node Configuration (2025)")
    print(f"🎯 Intent Detector: {INTENT_DETECTOR_API[:12]}... → {INTENT_DETECTOR_MODEL}")
    print(f"🧠 Business Reasoner: {BUSINESS_REASONER_API[:12]}... → {BUSINESS_REASONER_MODEL}")
    print(f"🔍 Query Optimizer: {QUERY_OPTIMIZER_API[:12]}... → {QUERY_OPTIMIZER_MODEL}")
    print(f"📝 Response Formatter: {RESPONSE_FORMATTER_API[:12]}... → {RESPONSE_FORMATTER_MODEL}")
    print(f"🔄 Follow-up Evaluator: {FOLLOW_UP_API[:12]}... → {FOLLOW_UP_MODEL}")
    print(f"📸 Image Analysis: {IMAGE_API[:12]}... → {IMAGE_MODEL}")
    print(f"📄 ICP Analysis: {ICP_API[:12]}... → {ICP_MODEL}")
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