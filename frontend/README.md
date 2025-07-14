# AF AI Assistant Frontend

React frontend application for Aquaforest RAG AI Assistant.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Backend server running on port 2103

### Installation & Run

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will be available at `http://localhost:3000`

## ⚙️ Configuration

Create `.env` file in frontend directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:2103

# Debug Mode (set to 'true' for development logging)
REACT_APP_TEST_ENV=false
```

## 🏗️ Project Structure

```
src/
├── components/           # React components
│   ├── ChatInterface.tsx # Main chat interface
│   ├── Header.tsx        # App header
│   ├── MessageList.tsx   # Messages container
│   ├── Message.tsx       # Single message
│   ├── MessageContent.tsx# Markdown message content
│   ├── LoadingMessage.tsx# Loading state
│   ├── ChatInput.tsx     # Input field
│   └── SuggestedQueries.tsx # Initial suggestions
├── services/            # API communication
│   └── api.ts
├── types/               # TypeScript definitions
│   └── index.ts
├── App.tsx              # Main app component
└── index.tsx            # Entry point
```

## 🎨 Design & Features

- **1:1 recreation** of original design
- **Purple gradient** color scheme  
- **Responsive** layout
- **Tailwind CSS** styling
- **Markdown formatting** - nagłówki, listy, linki z ikonkami
- **Send button inside input** - nowoczesny UX

## 🔌 API Integration

- **Real API calls** to backend (no mocks)
- **Error handling** with user-friendly messages
- **Debug logging** when TEST_ENV=true
- **Chat history** maintained across sessions 