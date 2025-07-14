"""
Security middleware module for Aquaforest RAG System
Provides IP-based rate limiting and security headers
"""
import os
import time
from typing import Dict, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request, Response
from config import debug_print, TEST_ENV

# Rate limiting configuration from environment variables
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
RATE_LIMIT_STORAGE = os.getenv("RATE_LIMIT_STORAGE", "memory")  # memory or redis

# Tier 1 - Critical endpoints (increased limits as requested)
TIER1_LIMIT = os.getenv("TIER1_RATE_LIMIT", "20/minute")  # /chat, /chat/stream
VISION_LIMIT = os.getenv("VISION_RATE_LIMIT", "10/minute")  # /debug/test-vision

# Tier 2 - Moderate endpoints  
TIER2_LIMIT = os.getenv("TIER2_RATE_LIMIT", "60/minute")   # /analytics, /session
CSV_EXPORT_LIMIT = os.getenv("CSV_EXPORT_LIMIT", "10/hour")  # CSV exports

# Tier 3 - Basic endpoints
TIER3_LIMIT = os.getenv("TIER3_RATE_LIMIT", "200/minute")  # /health, /feedback

# Global rate limiting (fallback for unspecified endpoints)
GLOBAL_LIMIT = os.getenv("GLOBAL_RATE_LIMIT", "100/minute")

class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def add_security_headers(response: Response) -> Response:
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Rate-Limit-Info"] = "Aquaforest RAG API v2.2.0"
        return response

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers from reverse proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP if multiple are present
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    return get_remote_address(request)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=RATE_LIMIT_STORAGE,
    default_limits=[GLOBAL_LIMIT] if ENABLE_RATE_LIMITING else []
)

def create_rate_limit_handler():
    """Create custom rate limit exceeded handler"""
    
    def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        client_ip = get_client_ip(request)
        endpoint = str(request.url.path)
        
        debug_print(f"🚨 [Security] Rate limit exceeded - IP: {client_ip}, Endpoint: {endpoint}")
        
        response = Response(
            content=f'{{"error": "Rate limit exceeded", "detail": "Too many requests from IP {client_ip}", "retry_after": {exc.retry_after}}}',
            status_code=429,
            media_type="application/json"
        )
        
        # Add rate limit headers
        response.headers["Retry-After"] = str(exc.retry_after)
        response.headers["X-RateLimit-Limit"] = str(exc.detail.split("per")[0].strip())
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + exc.retry_after))
        
        return SecurityHeaders.add_security_headers(response)
    
    return rate_limit_handler

def setup_security_middleware(app: FastAPI):
    """Setup security middleware and rate limiting for FastAPI app"""
    
    if not ENABLE_RATE_LIMITING:
        debug_print("⚠️ [Security] Rate limiting DISABLED")
        return app
    
    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, create_rate_limit_handler())
    app.add_middleware(SlowAPIMiddleware)
    
    debug_print("✅ [Security] Rate limiting middleware configured")
    debug_print(f"🔧 [Security] Tier 1 (Chat): {TIER1_LIMIT}")
    debug_print(f"🔧 [Security] Tier 2 (Analytics): {TIER2_LIMIT}")
    debug_print(f"🔧 [Security] Tier 3 (Basic): {TIER3_LIMIT}")
    debug_print(f"🔧 [Security] Vision API: {VISION_LIMIT}")
    debug_print(f"🔧 [Security] CSV Export: {CSV_EXPORT_LIMIT}")
    
    return app

# Rate limiting decorators for different tiers
def tier1_rate_limit():
    """Rate limit decorator for Tier 1 endpoints (chat)"""
    if not ENABLE_RATE_LIMITING:
        return lambda func: func
    return limiter.limit(TIER1_LIMIT)

def tier2_rate_limit():
    """Rate limit decorator for Tier 2 endpoints (analytics)"""
    if not ENABLE_RATE_LIMITING:
        return lambda func: func
    return limiter.limit(TIER2_LIMIT)

def tier3_rate_limit():
    """Rate limit decorator for Tier 3 endpoints (basic)"""
    if not ENABLE_RATE_LIMITING:
        return lambda func: func
    return limiter.limit(TIER3_LIMIT)

def vision_rate_limit():
    """Rate limit decorator for Vision API endpoints"""
    if not ENABLE_RATE_LIMITING:
        return lambda func: func
    return limiter.limit(VISION_LIMIT)

def csv_export_rate_limit():
    """Rate limit decorator for CSV export endpoints"""
    if not ENABLE_RATE_LIMITING:
        return lambda func: func
    return limiter.limit(CSV_EXPORT_LIMIT)

def global_rate_limit():
    """Rate limit decorator for unspecified endpoints"""
    if not ENABLE_RATE_LIMITING:
        return lambda func: func
    return limiter.limit(GLOBAL_LIMIT)

# Security middleware for responses
async def security_headers_middleware(request: Request, call_next):
    """Middleware to add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    response = SecurityHeaders.add_security_headers(response)
    
    # Add rate limit info if available
    if hasattr(request.state, "view_rate_limit"):
        response.headers["X-RateLimit-Remaining"] = str(request.state.view_rate_limit)
    
    return response

def log_security_event(event_type: str, client_ip: str, details: str):
    """Log security events for monitoring"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    debug_print(f"🔒 [Security] {timestamp} - {event_type} - IP: {client_ip} - {details}")

# IP whitelist/blacklist functionality (optional)
class IPFilter:
    """IP filtering functionality"""
    
    def __init__(self):
        self.whitelist = set(os.getenv("IP_WHITELIST", "").split(",")) if os.getenv("IP_WHITELIST") else set()
        self.blacklist = set(os.getenv("IP_BLACKLIST", "").split(",")) if os.getenv("IP_BLACKLIST") else set()
        
        # Remove empty strings
        self.whitelist.discard("")
        self.blacklist.discard("")
    
    def is_allowed(self, ip: str) -> bool:
        """Check if IP is allowed"""
        # Check blacklist first
        if ip in self.blacklist:
            return False
        
        # If whitelist is empty, allow all (except blacklisted)
        if not self.whitelist:
            return True
        
        # Check whitelist
        return ip in self.whitelist
    
    def add_to_blacklist(self, ip: str):
        """Add IP to blacklist"""
        self.blacklist.add(ip)
        debug_print(f"🚫 [Security] Added {ip} to blacklist")
    
    def remove_from_blacklist(self, ip: str):
        """Remove IP from blacklist"""
        self.blacklist.discard(ip)
        debug_print(f"✅ [Security] Removed {ip} from blacklist")

# Global IP filter instance
ip_filter = IPFilter()

def create_ip_filter_middleware():
    """Create IP filtering middleware"""
    
    async def ip_filter_middleware(request: Request, call_next):
        client_ip = get_client_ip(request)
        
        if not ip_filter.is_allowed(client_ip):
            log_security_event("IP_BLOCKED", client_ip, f"Access denied to {request.url.path}")
            return Response(
                content='{"error": "Access denied", "detail": "Your IP address is not allowed"}',
                status_code=403,
                media_type="application/json"
            )
        
        return await call_next(request)
    
    return ip_filter_middleware

def get_rate_limit_status() -> Dict[str, any]:
    """Get current rate limiting configuration status"""
    return {
        "rate_limiting_enabled": ENABLE_RATE_LIMITING,
        "storage_type": RATE_LIMIT_STORAGE,
        "limits": {
            "tier1_chat": TIER1_LIMIT,
            "tier2_analytics": TIER2_LIMIT, 
            "tier3_basic": TIER3_LIMIT,
            "vision_api": VISION_LIMIT,
            "csv_export": CSV_EXPORT_LIMIT,
            "global_fallback": GLOBAL_LIMIT
        },
        "ip_filter": {
            "whitelist_count": len(ip_filter.whitelist),
            "blacklist_count": len(ip_filter.blacklist)
        }
    }