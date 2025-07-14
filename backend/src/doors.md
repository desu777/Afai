# ==========================================
# AQUAFOREST RAG - ACTUAL ENVIRONMENT VALUES
# ==========================================
# ⚠️  NEVER COMMIT THIS FILE TO GIT - CONTAINS SENSITIVE API KEYS
# This file shows actual values for development reference

# ==========================================
# 🔧 DEVELOPMENT CONFIGURATION  
# ==========================================
TEST_ENV=true
DISABLE_BUSINESS_MAPPINGS=true
ENABLE_COMPETITORS_ONLY=true

# ==========================================
# 🗄️ PINECONE VECTOR DATABASE
# ==========================================
PINECONE_API_KEY=pcsk_45KvHy_[TRUNCATED]
PINECONE_INDEX_NAME=aquaforestv2
PINECONE_ENVIRONMENT=us-east-1

# ==========================================
# 🤖 OPENROUTER API CONFIGURATION (Per-Node)
# ==========================================
INTENT_DETECTOR_API=sk-or-v1-cc2c[TRUNCATED]
BUSINESS_REASONER_API=sk-or-v1-76[TRUNCATED]
QUERY_OPTIMIZER_API=sk-or-v1-c8e552[TRUNCATED]
RESPONSE_FORMATTER_API=sk-or-v1-[MISSING]
FOLLOW_UP_API=sk-or-v1-e28535703[TRUNCATED]

INTENT_DETECTOR_MODEL=google/gemini-2.5-flash-preview-05-20
BUSINESS_REASONER_MODEL=google/gemini-2.5-flash-preview-05-20
QUERY_OPTIMIZER_MODEL=google/gemini-2.5-flash-preview-05-20
RESPONSE_FORMATTER_MODEL=google/gemini-2.5-flash-preview-05-20
FOLLOW_UP_MODEL=google/gemini-2.0-flash-001

# ==========================================
# 🔑 OPENAI CONFIGURATION
# ==========================================
OPENAI_API_KEY=sk-proj-y4M3DxsrsS8r[TRUNCATED]
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TEMPERATURE=0.3

# ==========================================
# ⚙️ APPLICATION SETTINGS
# ==========================================
ENHANCED_K_VALUE=8
CONFIDENCE_THRESHOLD=0.5
CONFIDENCE_THRESHOLD_HIGH=0.65
CONFIDENCE_THRESHOLD_LOW=0.5
SUPPORTED_LANGUAGES=pl,en,de,fr,es,it
PRODUCTS_FILE_PATH=data/products.json

# ==========================================
# 🌐 CORS & SERVER CONFIGURATION
# ==========================================
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:8080

# ==========================================
# 🔒 RATE LIMITING & SECURITY (2025)
# ==========================================
ENABLE_RATE_LIMITING=true
RATE_LIMIT_STORAGE=memory

# Rate limits per tier (increased as requested)
TIER1_RATE_LIMIT=20/minute
TIER2_RATE_LIMIT=60/minute  
TIER3_RATE_LIMIT=200/minute
VISION_RATE_LIMIT=10/minute
CSV_EXPORT_LIMIT=10/hour
GLOBAL_RATE_LIMIT=100/minute

# IP filtering (optional)
IP_WHITELIST=
IP_BLACKLIST=

# ==========================================
# 💬 FACEBOOK MESSENGER INTEGRATION
# ==========================================
MESSENGER_ON=true
MESSENGER_TOKEN=EAARJ3PRXndYBO2lEDGuV0keD2eSpH2G1zpS5zuZBaZCrtG4zCvMjig1WmREpDvXAZDZD[TRUNCATED]
MESSENGER_VERIFY_TOKEN=aquaforest_webhook_2025
FACEBOOK_API_VERSION=v22.0

