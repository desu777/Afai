# Environment Variables - Aquaforest RAG System

## Core System Variables
- `OPENAI_API_KEY` - OpenAI API key for LLM services
- `PINECONE_API_KEY` - Pinecone vector database API key
- `PINECONE_INDEX_NAME` - Pinecone index name (default: "aqua")

## 🆕 OpenRouter Integration (2025)
- `USE_OPENROUTER` - Enable/disable OpenRouter (true/false, default: false)
- `OPENROUTER_API_KEY` - OpenRouter API key for model aggregation
- `OPENROUTER_MODEL_COMPLEX` - Model for complex tasks (default: "qwen/qwen3-32b")

### OpenRouter Model Recommendations:
**🔥 Best for halucination reduction (GPT-4.1 alternatives):**
- `qwen/qwen3-32b` - Excellent reasoning, dual-mode thinking/non-thinking
- `qwen/qwen3-30b-a3b` - MoE architecture, 30.5B params (3.3B activated)
- `deepseek/deepseek-r1-distill-qwen-1.5b` - Outperforms GPT-4o on math benchmarks!
- `anthropic/claude-3.7-sonnet:thinking` - Advanced reasoning mode

**💰 Cost-effective options:**
- `qwen/qwen3-30b-a3b:free` - Free version with rate limits
- `qwen/qwen3-4b` - Smaller but still dual-mode capable

**⚡ Performance shortcuts:**
- `:nitro` suffix - Prioritize speed over cost
- `:floor` suffix - Prioritize cost over speed

## Authentication & Access
- `MESSENGER_TOKEN` - Facebook Messenger page access token
- `MESSENGER_VERIFY_TOKEN` - Webhook verification token

## Model Configuration
- `OPENAI_MODEL` - Complex tasks model (default: "gpt-4.1-mini")
- `OPENAI_MODEL2` - Simple tasks model (default: "gpt-4o-mini")
- `OPENAI_TEMPERATURE` - LLM temperature setting (default: 0.3)

## System Features
- `TEST_ENV` - Enable debug mode (true/false)
- `DISABLE_BUSINESS_MAPPINGS` - Disable business logic mappings
- `ENABLE_COMPETITORS_ONLY` - Enable only competitors mapping
- `ENHANCED_K_VALUE` - Vector search result count (default: 12)

## Network & Storage
- `CORS_ORIGINS` - Allowed CORS origins for API
- `STORAGE_NETWORK` - 0G Storage network selection (standard/turbo)
- `STORAGE_GAS_PRICE` & `STORAGE_GAS_MULTIPLIER` - Dynamic gas optimization
- `STORAGE_WAIT_FINALITY` - Upload reliability setting

## Smart Contracts
- `DREAM_VERIFIER_ADDRESS` - Dream verifier contract address
- `DREAM_AGENT_NFT_ADDRESS` - Dream agent NFT contract address
- `OG_PRICE_USD` - Cost estimation variable

## Development Tools
- `WHISPER_API` - OpenAI API key for speech recognition 