"""
FastAPI App Factory
Application configuration and setup
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS, TEST_ENV, debug_print
from database import init_database, cleanup_old_messenger_history, DB_PATH
from security_middleware import setup_security_middleware, security_headers_middleware, create_auth_token_middleware
from utils.logger import logger

def create_app():
    """Create and configure FastAPI application"""
    
    # Initialize FastAPI app
    app = FastAPI(
        title="Aquaforest RAG API",
        description="AI Assistant API for Aquaforest products and solutions with analytics",
        version="2.2.0"
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Authentication middleware (first - before rate limiting)
    app.middleware("http")(create_auth_token_middleware())

    # Setup security middleware and rate limiting
    setup_security_middleware(app)

    # Add security headers middleware
    app.middleware("http")(security_headers_middleware)

    # Initialize database on startup
    init_database()

    return app

def run_server():
    """Run the FastAPI server"""
    # Always show server startup (not dependent on TEST_ENV)
    print("\n" + "="*60)
    print("🐠 Starting Aquaforest RAG API Server with Analytics")
    print("="*60)
    print(f"📍 Port: 2103")
    print(f"📍 Debug Mode: {'ON' if TEST_ENV else 'OFF'}")
    print(f"📍 CORS Origins: {CORS_ORIGINS}")
    print(f"📊 Analytics Database: {DB_PATH}")
    
    # Clean up old messenger history on startup
    cleanup_old_messenger_history()
    
    print("="*60 + "\n")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=2103,
        reload=True,
        access_log=TEST_ENV
    )