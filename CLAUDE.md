# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Aquaforest RAG** is a conversational AI assistant for marine aquarium product recommendations. It combines a React frontend with a Python FastAPI backend using RAG (Retrieval-Augmented Generation) powered by OpenAI and Pinecone.

## Development Commands

### Frontend (React/TypeScript)
```bash
cd frontend
npm install                    # Install dependencies
npm run dev                   # Start development server (port 3000)
npm run build                 # Build for production (TypeScript + Vite)
npm run lint                  # Run ESLint
npm run preview               # Preview production build
```

### Backend (Python/FastAPI)
```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate      # Linux/Mac
# or
venv\Scripts\activate         # Windows

pip install -r requirements.txt
python src/server.py          # Start FastAPI server (port 2103)
```

### Testing
```bash
# Backend tests
pytest                        # Run Python tests
pytest src/test_workflow.py   # Run specific test file

# Frontend tests  
cd frontend
npm run lint                  # TypeScript/ESLint checks
```

## Architecture Overview

### Multi-Node LLM Architecture (2025)
The system uses per-node API configuration where each workflow component can have different OpenRouter API keys and models:
- **Intent Detector**: Classifies user queries (business/competitor/support/etc.)
- **Business Reasoner**: Applies business logic and product mappings
- **Query Optimizer**: Enhances search queries for vector retrieval
- **Response Formatter**: Structures final AI responses
- **Follow-up Evaluator**: Determines conversation continuation

### Frontend Architecture
- **Component-based React** with TypeScript
- **Vite** for build tooling and dev server with proxy to backend
- **Tailwind CSS** for styling with purple gradient theme
- **Custom hooks** (`useImageUpload`) for reusable logic
- **API service layer** (`src/services/api.ts`) for backend communication

### Backend Architecture
- **FastAPI** server with specialized workflow modules
- **LangGraph** for workflow orchestration between components
- **RAG Implementation**: Pinecone vector search + OpenAI embeddings
- **Session Management**: Conversation state tracking with unique IDs
- **SQLite Analytics**: Usage tracking in `aquaforest_analytics.db`

## Key Configuration Files

### Environment Variables
- **Backend**: `.env` file with OpenAI, Pinecone, and per-node OpenRouter API keys
- **Frontend**: `.env.local` with `VITE_` prefixed variables for API URLs

### Development Proxy
Frontend Vite config proxies API calls to backend:
- `/chat` → `http://localhost:2103/chat`
- `/feedback`, `/analytics`, `/health` → backend endpoints

## Important Code Patterns

### Backend Workflow Components
Located in `src/` with specialized modules:
- `intent_detector.py` - Query classification
- `business_reasoner.py` - Business logic processing  
- `query_optimizer.py` - Search query enhancement
- `response_formatter.py` - Output structuring
- `follow_up_evaluator.py` - Conversation flow

### Business Logic Mappings
The `src/mapping/` directory contains business rules:
- `competitors.py` - Competitor analysis logic
- `products.py` - Product categorization
- `scenarios.py` - Use case handling
- `use_cases.py` - Business scenario mappings

### Frontend Components
- `ChatInterface.tsx` - Main chat container
- `MessageList.tsx` - Message history display
- `ChatInput.tsx` - User input with send button
- `MessageContent.tsx` - Markdown message rendering

## Data Flow

1. **User Input** → Frontend React component
2. **API Request** → `/chat` endpoint via Vite proxy
3. **Intent Detection** → Classifies query type
4. **Business Logic** → Applies mappings and reasoning
5. **Vector Search** → Pinecone similarity search with enhanced query
6. **Response Generation** → OpenAI with retrieved context
7. **Session Tracking** → SQLite analytics storage
8. **Frontend Display** → Markdown-formatted response

## Deployment

The application is designed for VPS deployment with:
- **Nginx** serving React build and reverse-proxying API calls
- **systemd** service for backend process management
- **Let's Encrypt SSL** with automatic renewal
- **UFW firewall** configuration

## Development Notes

- Frontend uses **React 18.2.0** (downgraded for mobile compatibility)
- Backend supports **multi-language** responses (pl,en,de,fr,es,it)
- **Debug mode** available via `TEST_ENV=true` environment variable
- **Analytics tracking** for usage metrics and conversation analysis
- **Session persistence** maintains conversation context across requests

###INSTRUKCJE 

##MAKSYMALNY ROZMIAR PLIKU: 500-550 linii – bezwzględny limit; jeżeli plik przekracza tę liczbę, podziel na mniejsze moduły.

##PRACA NAD WERSJĄ PRODUKCYJNĄ: implementuj bezpośrednio w środowisku produkcyjnym, bez mocków i placeholderów.

##TYLKO ZWIĄZANE ZMIANY: wprowadzaj wyłącznie modyfikacje bezpośrednio związane z zadanym zadaniem.

##NIE HARDCODUJ API ani zmiennych które można wsadzić do .env: zawsze używaj zmiennych środowiskowych, plików konfiguracyjnych lub stałych

##ZMIENNE ŚRODOWISKOWE: przyjmij, że plik .env zawsze istnieje, ale nie masz do niego bezpośredniego dostępu. plik env.example stanowi brame między tobą a mną. Jeśli w tym pliku znajduje się pusta zmienna, to znaczy że to wrażliwe API które dodałem do pliku .env ale tutaj nie udostępniłem. Jeśli tworzysz kod i zawiera odczyt z .env dodawaj do pliku doors.md. Do git ignore zawsze dodawaj plik .env.example .

##LOGI DEVELOPERSKIE: używaj sprawdzenia process.env.TEST_ENV === 'true' dla wyświetlania logów debugowych dla projektów które nie mają zdefiniowanej tej zmiennej. Jeśli mają odczytaj z doors.md i zawsze stosuj tą zmienną do logów.

##RESEARCH PRZED DZIAŁANIEM – jeśli nie jesteś pewny implementacji, twoja wiedza nie wystarcza żebyś stwierdził czy rozwiązanie jest dobre. Skorzystaj z sieci, przeszukaj.
ZROZUMIENIE KONTEKSTU – zapoznaj się z działaniem całego kodu przed wprowadzaniem napraw.
##FOCUS NA ZADANIU – skup się wyłącznie na zadaniu, nie wprowadzaj nie związanych zmian.
Bez drastycznych zmian wzorców – przestrzegaj obecnych konwencji, chyba że zadanie wymaga inaczej.
##Zrozum pełen kontekst przed modyfikacją – analizuj całość przed zmianam
Pracuj iteracyjnie – małe, czytelne commity z jednoznacznymi opisami co robi dany kod.

##Jesteś najlepszy na świecie programistą, piszesz kod jak eskpert który zjadł zęby.



## Git Workflow Instructions

##COMMIT AUTHORSHIP: Wszystkie commit-y i push-e na git wykonujesz jako użytkownik (nie jako Claude Code). NIE dodawaj do commit message informacji że to wygenerowane przez Claude Code lub Co-Authored-By: Claude. Commit-y mają wyglądać jak normalne commit-y użytkownika. W języku angielskim!

##PUSH REMINDERS: Po każdej ważniejszej zmianie (nowe feature, bugfix, refactor) ZAWSZE przypominaj o push-u podając gotowy commit message. Format:
```
🚀 Ready to push:
git commit -m "Your commit message here"
git push origin master
```