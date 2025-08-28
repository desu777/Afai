# Aquaforest RAG - AI Assistant for Aquarium Product Recommendations

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

An advanced AI-powered assistant system for aquarium product recommendations and support, featuring a sophisticated LangGraph workflow with specialized AI nodes, real-time streaming responses, and multi-language support.

## 🌟 Key Features

- **Multi-Language Support**: Supports 6 languages (Polish, English, German, French, Spanish, Italian)
- **Intelligent Product Recommendations**: AI-driven analysis using Gemini Flash 2.5 Thinking models
- **ICP Test Analysis**: Professional-grade water parameter analysis from laboratory reports
- **Image Analysis**: Visual analysis of aquarium problems through uploaded images
- **Session Management**: Intelligent conversation continuity with 10-minute context retention
- **Real-time Streaming**: Live workflow updates via Server-Sent Events
- **Advanced Security**: Multi-tier rate limiting, IP filtering, and authentication

## 🏗️ System Architecture

### AI Workflow Pipeline

The system employs a directed graph workflow with 6 specialized AI experts:

```
User Query → Intent Detector → Business Reasoner → Query Optimizer → Pinecone Search → Response Formatter → Session Cache
```

#### Expert Nodes:

1. **Intent Detector** - Language detection and query classification (3-5 seconds)
2. **Business Reasoner** - Deep business logic and product analysis (15-20 seconds)
3. **Query Optimizer** - Smart search query generation (3-4 seconds)
4. **Pinecone Search** - Vector database search across 1000+ products (300ms)
5. **Response Formatter** - Professional response composition (5-8 seconds)
6. **Session Manager** - Context preservation for follow-ups (50ms)

### Performance Metrics

- **Product Queries**: 30-50 seconds (comprehensive analysis with highest quality)
- **Follow-up Questions**: <10 seconds (leverages cached context)
- **Other Queries**: <10 seconds (greetings, support, business inquiries)
- **Concurrent Capacity**: Hundreds of simultaneous users
- **Availability**: 24/7/365

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- Access to required API keys (OpenRouter, Pinecone, Google Vertex AI)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Run development server
python src/server.py
```

The backend will start on `http://localhost:2103`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Set VITE_API_URL to your backend URL

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example` with the following key configurations:

#### Backend (.env)
```env
# Per-node API configurations
INTENT_DETECTOR_API=your_api_key_here
INTENT_DETECTOR_MODEL=gemini/gemini-2.0-flash-thinking-exp-1219

BUSINESS_REASONER_API=your_api_key_here
BUSINESS_REASONER_MODEL=gemini/gemini-2.0-flash-thinking-exp-1219

QUERY_OPTIMIZER_API=your_api_key_here
QUERY_OPTIMIZER_MODEL=gemini/gemini-2.0-flash-thinking-exp-1219

RESPONSE_FORMATTER_API=your_api_key_here
RESPONSE_FORMATTER_MODEL=gemini/gemini-2.0-flash-thinking-exp-1219

FOLLOW_UP_API=your_api_key_here
FOLLOW_UP_MODEL=gemini/gemini-2.0-flash-thinking-exp-1219

# Pinecone configuration
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=aquaforest-products
PINECONE_NAMESPACE=products

# Security
CORS_ORIGINS=["http://localhost:5173", "https://your-domain.com"]
RATE_LIMIT_TIER1=20
RATE_LIMIT_TIER2=60
RATE_LIMIT_TIER3=200
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:2103
VITE_TEST_ENV=false
VITE_TEST_ACCESS=your_test_password
VITE_ADMIN_ACCESS=your_admin_password
```

## 📁 Project Structure

```
aquaforest-rag/
├── backend/
│   ├── src/
│   │   ├── server.py                 # Main FastAPI server
│   │   ├── workflow.py               # LangGraph workflow orchestration
│   │   ├── config.py                 # Configuration management
│   │   ├── endpoints/                # API endpoints
│   │   │   ├── chat_endpoints.py     # Main chat API
│   │   │   ├── analytics_endpoints.py
│   │   │   ├── feedback_endpoints.py
│   │   │   └── security_endpoints.py
│   │   ├── business_reasoning/       # Business logic components
│   │   │   ├── data_loader.py
│   │   │   ├── llm_analyzer.py
│   │   │   └── decision_applier.py
│   │   ├── response_formatting/      # Response generation
│   │   │   ├── prompt_builder.py
│   │   │   ├── dosage_calculator.py
│   │   │   └── cache_manager.py
│   │   └── database/                 # Data persistence
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── api.ts                # API client with streaming
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript interfaces
│   │   └── components/               # React components
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🔌 API Documentation

### Main Endpoints

#### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "Your question here",
  "session_id": "optional-session-id",
  "language": "en",
  "access_level": "standard"
}
```

#### Streaming Chat
```http
POST /chat/stream
Content-Type: application/json

# Returns Server-Sent Events stream with real-time updates
```

### Authentication

Add authentication header for protected endpoints:
```http
X-Aquaforest-Auth: your-auth-token
```

### Rate Limits

- **Tier 1** (Chat): 20 requests/minute
- **Tier 2** (Analytics): 60 requests/minute  
- **Tier 3** (Export): 200 requests/minute

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend && pytest

# Frontend linting
cd frontend && npm run lint

# TypeScript checking
cd frontend && npx tsc --noEmit
```

### Debug Mode

Enable debug logging by setting:
- Backend: `TEST_ENV=true` in `.env`
- Frontend: `VITE_TEST_ENV=true` in `.env`

### Interactive Testing

Test individual workflow nodes:
```bash
cd backend
python src/main.py
```

## 🚢 Production Deployment

### Backend Deployment

1. Set up systemd service:
```bash
sudo cp aquaforest-backend.service /etc/systemd/system/
sudo systemctl enable aquaforest-backend
sudo systemctl start aquaforest-backend
```

2. Configure Nginx reverse proxy:
```nginx
server {
    listen 443 ssl http2;
    server_name api.aquaforest.eu;
    
    location / {
        proxy_pass http://localhost:2103;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Frontend Deployment

```bash
# Build production bundle
cd frontend
npm run build

# Serve static files with Nginx
sudo cp -r dist/* /var/www/aquaforest-assistant/
```

### SSL Configuration

Use Let's Encrypt for SSL certificates:
```bash
sudo certbot --nginx -d api.aquaforest.eu
```

## 📊 Monitoring & Analytics

The system includes comprehensive analytics:

- **Workflow Performance**: Timing for each AI expert node
- **Usage Metrics**: Request volume, user sessions, popular queries
- **Quality Metrics**: User feedback ratings, success rates
- **Security Monitoring**: Attack attempts, rate limit violations

Access analytics via:
```http
GET /analytics/summary
GET /analytics/export?format=csv
```

## 🛡️ Security Features

- **Multi-tier Rate Limiting**: Prevents abuse with automatic IP blacklisting
- **Authentication**: Header-based authentication for protected endpoints
- **CORS Protection**: Configurable allowed origins
- **Input Validation**: Comprehensive request validation
- **Secure Configuration**: External `.env` file management
- **Automatic Cleanup**: Session and data retention policies

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software owned by Aquaforest. All rights reserved.

## 📞 Support

For issues, questions, or feedback:
- Create an issue in this repository
- Contact the development team
- Check the documentation in `CLAUDE.md` for detailed technical information

## 🔗 Links

- [API Documentation](https://api.aquaforest.eu/docs)
- [Aquaforest Website](https://aquaforest.eu)
- [Product Catalog](https://aquaforest.eu/products)

---

Built with ❤️ by the Aquaforest Development Team