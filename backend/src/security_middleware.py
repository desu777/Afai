"""
Security middleware module for Aquaforest RAG System
Provides IP-based rate limiting and security headers
"""
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request, Response
from config import debug_print, TEST_ENV, AQUAFOREST_AUTH_TOKEN, ENABLE_AUTH_TOKEN

# Rate limiting configuration from environment variables
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
RATE_LIMIT_STORAGE = os.getenv("RATE_LIMIT_STORAGE", "memory://")  # memory:// or redis://host:port

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

# Auto-blacklisting configuration
AUTO_BLACKLIST_ENABLED = os.getenv("AUTO_BLACKLIST_ENABLED", "true").lower() == "true"
VIOLATION_THRESHOLD = int(os.getenv("VIOLATION_THRESHOLD", "2"))  # Number of violations before blacklist
BLACKLIST_DURATION_HOURS = int(os.getenv("BLACKLIST_DURATION_HOURS", "24"))  # Hours to keep in blacklist
VIOLATION_WINDOW_HOURS = int(os.getenv("VIOLATION_WINDOW_HOURS", "24"))  # Window to count violations

class ViolationTracker:
    """Track rate limit violations for automatic blacklisting"""
    
    def __init__(self):
        self.violations: Dict[str, list] = {}  # IP -> list of violation timestamps
        self.auto_blacklisted: Dict[str, datetime] = {}  # IP -> blacklist timestamp
    
    def add_violation(self, ip: str) -> bool:
        """Add violation for IP and return True if should be blacklisted"""
        if not AUTO_BLACKLIST_ENABLED:
            return False
            
        current_time = datetime.now()
        
        # Initialize IP if not exists
        if ip not in self.violations:
            self.violations[ip] = []
        
        # Add current violation
        self.violations[ip].append(current_time)
        
        # Clean old violations outside the window
        window_start = current_time - timedelta(hours=VIOLATION_WINDOW_HOURS)
        self.violations[ip] = [v for v in self.violations[ip] if v >= window_start]
        
        # Check if should blacklist
        if len(self.violations[ip]) >= VIOLATION_THRESHOLD:
            self.auto_blacklisted[ip] = current_time
            debug_print(f"[ALERT] SEC Auto-blacklisted IP {ip} after {len(self.violations[ip])} violations")
            return True
        
        debug_print(f"[WARN] SEC Violation #{len(self.violations[ip])} for IP {ip}")
        return False
    
    def is_auto_blacklisted(self, ip: str) -> bool:
        """Check if IP is auto-blacklisted and still within duration"""
        if ip not in self.auto_blacklisted:
            return False
        
        blacklist_time = self.auto_blacklisted[ip]
        expiry_time = blacklist_time + timedelta(hours=BLACKLIST_DURATION_HOURS)
        
        if datetime.now() > expiry_time:
            # Blacklist expired, remove it
            del self.auto_blacklisted[ip]
            debug_print(f"[OK] SEC Auto-blacklist expired for IP {ip}")
            return False
        
        return True
    
    def get_violation_count(self, ip: str) -> int:
        """Get current violation count for IP in the window"""
        if ip not in self.violations:
            return 0
        
        # Clean old violations
        current_time = datetime.now()
        window_start = current_time - timedelta(hours=VIOLATION_WINDOW_HOURS)
        self.violations[ip] = [v for v in self.violations[ip] if v >= window_start]
        
        return len(self.violations[ip])
    
    def remove_auto_blacklist(self, ip: str) -> bool:
        """Manually remove IP from auto-blacklist"""
        if ip in self.auto_blacklisted:
            del self.auto_blacklisted[ip]
            debug_print(f"[INFO] SEC Manually removed auto-blacklist for IP {ip}")
            return True
        return False
    
    def cleanup_expired(self):
        """Clean up expired blacklists and old violations"""
        current_time = datetime.now()
        
        # Clean expired blacklists
        expired_ips = []
        for ip, blacklist_time in self.auto_blacklisted.items():
            if current_time > blacklist_time + timedelta(hours=BLACKLIST_DURATION_HOURS):
                expired_ips.append(ip)
        
        for ip in expired_ips:
            del self.auto_blacklisted[ip]
            debug_print(f"[CLEANUP] SEC Cleaned expired blacklist for IP {ip}")
        
        # Clean old violations
        window_start = current_time - timedelta(hours=VIOLATION_WINDOW_HOURS)
        for ip in list(self.violations.keys()):
            self.violations[ip] = [v for v in self.violations[ip] if v >= window_start]
            if not self.violations[ip]:
                del self.violations[ip]
    
    def get_stats(self) -> Dict[str, any]:
        """Get violation tracking statistics"""
        self.cleanup_expired()
        
        return {
            "auto_blacklist_enabled": AUTO_BLACKLIST_ENABLED,
            "violation_threshold": VIOLATION_THRESHOLD,
            "blacklist_duration_hours": BLACKLIST_DURATION_HOURS,
            "violation_window_hours": VIOLATION_WINDOW_HOURS,
            "currently_blacklisted": len(self.auto_blacklisted),
            "ips_with_violations": len(self.violations),
            "total_violations": sum(len(violations) for violations in self.violations.values()),
            "blacklisted_ips": list(self.auto_blacklisted.keys())
        }

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

# Initialize rate limiter and violation tracker
limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=RATE_LIMIT_STORAGE,
    default_limits=[GLOBAL_LIMIT] if ENABLE_RATE_LIMITING else []
)

# Global violation tracker instance
violation_tracker = ViolationTracker()

def create_rate_limit_handler():
    """Create custom rate limit exceeded handler"""
    
    def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        client_ip = get_client_ip(request)
        endpoint = str(request.url.path)
        
        debug_print(f"[ALERT] SEC Rate limit exceeded - IP: {client_ip}, Endpoint: {endpoint}")
        
        # Track violation and check for auto-blacklisting
        should_blacklist = violation_tracker.add_violation(client_ip)
        
        if should_blacklist:
            # Add to blacklist
            ip_filter.add_to_blacklist(client_ip)
            log_security_event("AUTO_BLACKLIST", client_ip, f"Auto-blacklisted after {VIOLATION_THRESHOLD} violations")
            
            # Return 403 for blacklisted IP
            response = Response(
                content=f'{{"error": "IP blacklisted", "detail": "Your IP has been temporarily blacklisted due to repeated violations. Duration: {BLACKLIST_DURATION_HOURS} hours.", "blacklisted": true}}',
                status_code=403,
                media_type="application/json"
            )
        else:
            # Regular rate limit response
            violation_count = violation_tracker.get_violation_count(client_ip)
            response = Response(
                content=f'{{"error": "Rate limit exceeded", "detail": "Too many requests from IP {client_ip}", "retry_after": {exc.retry_after}, "violations": {violation_count}, "threshold": {VIOLATION_THRESHOLD}}}',
                status_code=429,
                media_type="application/json"
            )
            
            # Add rate limit headers
            response.headers["Retry-After"] = str(exc.retry_after)
            response.headers["X-RateLimit-Limit"] = str(exc.detail.split("per")[0].strip())
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + exc.retry_after))
        
        # Add violation tracking headers
        response.headers["X-Violation-Count"] = str(violation_tracker.get_violation_count(client_ip))
        response.headers["X-Violation-Threshold"] = str(VIOLATION_THRESHOLD)
        
        return SecurityHeaders.add_security_headers(response)
    
    return rate_limit_handler

def setup_security_middleware(app: FastAPI):
    """Setup security middleware and rate limiting for FastAPI app"""
    
    if not ENABLE_RATE_LIMITING:
        debug_print("[WARN] SEC Rate limiting DISABLED")
        return app
    
    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, create_rate_limit_handler())
    app.add_middleware(SlowAPIMiddleware)
    
    debug_print("[OK] SEC Rate limiting middleware configured")
    debug_print(f"[CONFIG] SEC Tier 1 (Chat): {TIER1_LIMIT}")
    debug_print(f"[CONFIG] SEC Tier 2 (Analytics): {TIER2_LIMIT}")
    debug_print(f"[CONFIG] SEC Tier 3 (Basic): {TIER3_LIMIT}")
    debug_print(f"[CONFIG] SEC Vision API: {VISION_LIMIT}")
    debug_print(f"[CONFIG] SEC CSV Export: {CSV_EXPORT_LIMIT}")
    
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
    debug_print(f"[SECURE] SEC {timestamp} - {event_type} - IP: {client_ip} - {details}")

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
        # Check auto-blacklist first
        if violation_tracker.is_auto_blacklisted(ip):
            return False
            
        # Check manual blacklist
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
        debug_print(f"[INFO] SEC Added {ip} to blacklist")
    
    def remove_from_blacklist(self, ip: str):
        """Remove IP from blacklist"""
        self.blacklist.discard(ip)
        debug_print(f"[OK] SEC Removed {ip} from blacklist")

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
        },
        "auto_blacklist": violation_tracker.get_stats()
    }

# Export functions for use in server.py
def get_violation_stats() -> Dict[str, any]:
    """Get violation tracking statistics"""
    return violation_tracker.get_stats()

def get_ip_violations(ip: str) -> Dict[str, any]:
    """Get violation history for specific IP"""
    return {
        "ip": ip,
        "violation_count": violation_tracker.get_violation_count(ip),
        "is_auto_blacklisted": violation_tracker.is_auto_blacklisted(ip),
        "threshold": VIOLATION_THRESHOLD,
        "window_hours": VIOLATION_WINDOW_HOURS
    }

def remove_ip_from_auto_blacklist(ip: str) -> bool:
    """Manually remove IP from auto-blacklist"""
    # Remove from both auto-blacklist and manual blacklist
    auto_removed = violation_tracker.remove_auto_blacklist(ip)
    manual_removed = False
    
    if ip in ip_filter.blacklist:
        ip_filter.remove_from_blacklist(ip)
        manual_removed = True
    
    return auto_removed or manual_removed

def cleanup_expired_violations():
    """Clean up expired violations and blacklists"""
    violation_tracker.cleanup_expired()

def create_auth_token_middleware():
    """Create authentication token middleware for Aquaforest API access"""
    
    async def auth_token_middleware(request: Request, call_next):
        """Validate X-Aquaforest-Auth header before processing request"""
        
        # Skip auth if disabled
        if not ENABLE_AUTH_TOKEN:
            return await call_next(request)
        
        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check for auth header
        auth_header = request.headers.get("X-Aquaforest-Auth")
        client_ip = get_client_ip(request)
        endpoint = str(request.url.path)
        
        # Validate token
        if not auth_header or auth_header != AQUAFOREST_AUTH_TOKEN:
            log_security_event("AUTH_FAILED", client_ip, f"Invalid/missing auth token for {endpoint}")
            
            return Response(
                content='{"error": "Unauthorized", "detail": "Invalid or missing authentication token"}',
                status_code=401,
                media_type="application/json",
                headers={
                    "X-Auth-Required": "X-Aquaforest-Auth",
                    "X-Content-Type-Options": "nosniff"
                }
            )
        
        # Valid token - proceed with request
        debug_print(f"[OK] AUTH Valid token for IP {client_ip} -> {endpoint}")
        return await call_next(request)
    
    return auth_token_middleware