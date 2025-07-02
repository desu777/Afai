"""
Configuration module for Aquaforest RAG System
Handles all environment variables and system settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")  # Complex tasks (Business Reasoner, Response Formatter)
OPENAI_MODEL2 = os.getenv("OPENAI_MODEL2", "gpt-4o-mini")  # Simple tasks (Intent Detection, Query Optimizer, Confidence)
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "16384"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# 🆕 OpenRouter Configuration (2025)
USE_OPENROUTER = os.getenv("USE_OPENROUTER", "false").lower() == "true"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL_COMPLEX = os.getenv("OPENROUTER_MODEL_COMPLEX", "qwen/qwen3-32b")  # Default to Qwen3 32B

# App Configuration
DEFAULT_K_VALUE = int(os.getenv("DEFAULT_K_VALUE", "12"))
ENHANCED_K_VALUE = int(os.getenv("ENHANCED_K_VALUE", "12"))

SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "pl,en,de,fr,es,it").split(",")

# Paths - Use absolute path based on file location
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH") or str(Path(__file__).parent.parent / "data" / "products.json")

# Server Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8080").split(",")

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
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")
if MESSENGER_ON and not MESSENGER_PAGE_ACCESS_TOKEN:
    raise ValueError("MESSENGER_TOKEN is required when MESSENGER_ON=true")
if USE_OPENROUTER and not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is required when USE_OPENROUTER=true")

# Print configuration status on import (only in debug mode)
if TEST_ENV:
    print("\n" + "="*60)
    print("🔧 CONFIGURATION LOADED")
    print("="*60)
    print(f"📍 Debug Mode: ENABLED")
    print(f"📍 Business Mappings: {'DISABLED' if DISABLE_BUSINESS_MAPPINGS else 'ENABLED'}")
    print(f"📍 Competitors Only: {'ENABLED' if ENABLE_COMPETITORS_ONLY else 'DISABLED'}")
    print(f"📍 OpenAI Model (Complex): {OPENAI_MODEL}")
    print(f"📍 OpenAI Model (Simple): {OPENAI_MODEL2}")
    print(f"📍 Embedding Model: {OPENAI_EMBEDDING_MODEL}")
    print(f"🚀 OpenRouter: {'ENABLED' if USE_OPENROUTER else 'DISABLED'}")
    if USE_OPENROUTER:
        print(f"📍 OpenRouter Model (Complex): {OPENROUTER_MODEL_COMPLEX}")
    print(f"📍 Pinecone Index: {PINECONE_INDEX_NAME}")
    print(f"📍 Default K Value: {DEFAULT_K_VALUE}")
    print(f"📍 Enhanced K Value: {ENHANCED_K_VALUE}")  
    print(f"📍 Supported Languages: {', '.join(SUPPORTED_LANGUAGES)}")
    print(f"📍 CORS Origins: {', '.join(CORS_ORIGINS)}")
    print(f"📍 Competitors tracked: {len(COMPETITORS)}")
    print(f"📍 Messenger Integration: {'ENABLED' if MESSENGER_ON else 'DISABLED'}")
    print(f"📍 Facebook API Version: {FACEBOOK_API_VERSION}")
    print(f"🗑️ Confidence Scorer: REMOVED for better performance")
    print("="*60 + "\n")