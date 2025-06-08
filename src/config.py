"""
Configuration module for Aquaforest RAG System
Handles all environment variables and system settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- DEBUG ---
# Add test environment flag
TEST_ENV = os.getenv("TEST_ENV", "false").lower() == "true"
# --- END DEBUG ---

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "aqua")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "16384"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# App Configuration
DEFAULT_K_VALUE = int(os.getenv("DEFAULT_K_VALUE", "15"))
ENHANCED_K_VALUE = int(os.getenv("ENHANCED_K_VALUE", "20"))
# Ten próg jest teraz używany w nowej, uproszczonej logice routingu
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "pl,en,de,fr,es,it").split(",")

# Paths
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH", "data/products.json")

# Validate required variables
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")