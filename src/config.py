"""
Configuration module for Aquaforest RAG System
Handles all environment variables and system settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- DEBUG ---
# Add test environment flag - can be dynamically changed
TEST_ENV = os.getenv("TEST_ENV", "false").lower() == "true"

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

# App Configuration
DEFAULT_K_VALUE = int(os.getenv("DEFAULT_K_VALUE", "12"))
ENHANCED_K_VALUE = int(os.getenv("ENHANCED_K_VALUE", "12"))

# 🆕 LOWERED CONFIDENCE THRESHOLD from 0.6 to 0.5
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "pl,en,de,fr,es,it").split(",")

# Paths
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH", "data/products.json")

# Server Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8080").split(",")

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

# Print configuration status on import (only in debug mode)
if TEST_ENV:
    print("\n" + "="*60)
    print("🔧 CONFIGURATION LOADED")
    print("="*60)
    print(f"📍 Debug Mode: ENABLED")
    print(f"📍 OpenAI Model (Complex): {OPENAI_MODEL}")
    print(f"📍 OpenAI Model (Simple): {OPENAI_MODEL2}")
    print(f"📍 Embedding Model: {OPENAI_EMBEDDING_MODEL}")
    print(f"📍 Pinecone Index: {PINECONE_INDEX_NAME}")
    print(f"📍 Default K Value: {DEFAULT_K_VALUE}")
    print(f"📍 Enhanced K Value: {ENHANCED_K_VALUE}")  
    print(f"📍 Confidence Threshold: {CONFIDENCE_THRESHOLD} (🆕 LOWERED)")
    print(f"📍 Supported Languages: {', '.join(SUPPORTED_LANGUAGES)}")
    print(f"📍 CORS Origins: {', '.join(CORS_ORIGINS)}")
    print(f"📍 Competitors tracked: {len(COMPETITORS)}")
    print("="*60 + "\n")