"""
🔥 Gemini Rate Limit Manager - Smart Fallback System
Manages multiple Gemini API keys with rate limiting and automatic OpenRouter fallback
"""
import time
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from config import TEST_ENV, debug_print

@dataclass
class APIKeyStatus:
    """Status tracking for individual API key"""
    key: str
    node_name: str
    
    # Rate limiting counters
    minute_count: int = 0
    daily_count: int = 0
    
    # Timestamp tracking
    last_minute_reset: float = field(default_factory=time.time)
    last_daily_reset: float = field(default_factory=time.time)
    
    # Error tracking
    consecutive_errors: int = 0
    last_error_time: float = 0
    
    # Limits (Gemini Free Tier)
    minute_limit: int = 10
    daily_limit: int = 500
    
    def is_available(self) -> bool:
        """Check if API key is available for use"""
        now = time.time()
        
        # Reset counters if needed
        self._reset_counters(now)
        
        # Check rate limits
        if self.minute_count >= self.minute_limit:
            if TEST_ENV:
                debug_print(f"❌ [RateLimit] {self.node_name} minute limit exceeded: {self.minute_count}/{self.minute_limit}")
            return False
            
        if self.daily_count >= self.daily_limit:
            if TEST_ENV:
                debug_print(f"❌ [RateLimit] {self.node_name} daily limit exceeded: {self.daily_count}/{self.daily_limit}")
            return False
        
        # Check error cooldown (5 minutes after consecutive errors)
        if self.consecutive_errors >= 3:
            cooldown_time = 300  # 5 minutes
            if now - self.last_error_time < cooldown_time:
                if TEST_ENV:
                    debug_print(f"❌ [RateLimit] {self.node_name} in error cooldown: {self.consecutive_errors} errors")
                return False
            else:
                # Reset error counter after cooldown
                self.consecutive_errors = 0
        
        return True
    
    def record_request(self):
        """Record a successful request"""
        now = time.time()
        self._reset_counters(now)
        
        self.minute_count += 1
        self.daily_count += 1
        self.consecutive_errors = 0  # Reset error counter on success
        
        if TEST_ENV:
            debug_print(f"✅ [RateLimit] {self.node_name} request recorded: {self.minute_count}/10 min, {self.daily_count}/500 day")
    
    def record_error(self):
        """Record an API error"""
        self.consecutive_errors += 1
        self.last_error_time = time.time()
        
        if TEST_ENV:
            debug_print(f"❌ [RateLimit] {self.node_name} error recorded: {self.consecutive_errors} consecutive")
    
    def _reset_counters(self, now: float):
        """Reset counters if time windows have passed"""
        # Reset minute counter (60 seconds)
        if now - self.last_minute_reset >= 60:
            self.minute_count = 0
            self.last_minute_reset = now
            
        # Reset daily counter (24 hours)
        if now - self.last_daily_reset >= 86400:  # 24 * 60 * 60
            self.daily_count = 0
            self.last_daily_reset = now
    
    def get_status(self) -> Dict:
        """Get current status for monitoring"""
        now = time.time()
        self._reset_counters(now)
        
        return {
            "node_name": self.node_name,
            "minute_usage": f"{self.minute_count}/{self.minute_limit}",
            "daily_usage": f"{self.daily_count}/{self.daily_limit}",
            "consecutive_errors": self.consecutive_errors,
            "available": self.is_available(),
            "next_minute_reset": int(60 - (now - self.last_minute_reset)),
            "next_daily_reset": int(86400 - (now - self.last_daily_reset))
        }


class GeminiRateLimitManager:
    """Manages rate limits for multiple Gemini API keys with smart fallback"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKeyStatus] = {}
        self.lock = threading.Lock()
        
        if TEST_ENV:
            debug_print("🔥 [RateLimitManager] Initialized Gemini rate limit manager")
    
    def register_api_key(self, node_name: str, api_key: str):
        """Register an API key for a specific node"""
        with self.lock:
            self.api_keys[node_name] = APIKeyStatus(
                key=api_key,
                node_name=node_name
            )
            
            if TEST_ENV:
                debug_print(f"🔑 [RateLimitManager] Registered API key for {node_name}")
    
    def can_use_gemini(self, node_name: str) -> bool:
        """Check if Gemini API can be used for this node"""
        with self.lock:
            if node_name not in self.api_keys:
                return False
            
            return self.api_keys[node_name].is_available()
    
    def record_success(self, node_name: str):
        """Record successful API call"""
        with self.lock:
            if node_name in self.api_keys:
                self.api_keys[node_name].record_request()
    
    def record_error(self, node_name: str):
        """Record API error"""
        with self.lock:
            if node_name in self.api_keys:
                self.api_keys[node_name].record_error()
    
    def get_api_key(self, node_name: str) -> Optional[str]:
        """Get API key for node if available"""
        with self.lock:
            if node_name in self.api_keys and self.api_keys[node_name].is_available():
                return self.api_keys[node_name].key
            return None
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status for all registered API keys"""
        with self.lock:
            return {
                node_name: key_status.get_status() 
                for node_name, key_status in self.api_keys.items()
            }
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        with self.lock:
            total_minute_usage = sum(key.minute_count for key in self.api_keys.values())
            total_daily_usage = sum(key.daily_count for key in self.api_keys.values())
            available_keys = sum(1 for key in self.api_keys.values() if key.is_available())
            
            return {
                "total_keys": len(self.api_keys),
                "available_keys": available_keys,
                "total_minute_usage": total_minute_usage,
                "total_daily_usage": total_daily_usage,
                "keys_with_errors": sum(1 for key in self.api_keys.values() if key.consecutive_errors > 0)
            }


# Global instance
rate_limit_manager = GeminiRateLimitManager()

# Helper functions for easy import
def can_use_gemini(node_name: str) -> bool:
    """Check if Gemini can be used for this node"""
    return rate_limit_manager.can_use_gemini(node_name)

def record_gemini_success(node_name: str):
    """Record successful Gemini API call"""
    rate_limit_manager.record_success(node_name)

def record_gemini_error(node_name: str):
    """Record Gemini API error"""
    rate_limit_manager.record_error(node_name)

def get_gemini_api_key(node_name: str) -> Optional[str]:
    """Get Gemini API key if available"""
    return rate_limit_manager.get_api_key(node_name)

def get_rate_limit_status() -> Dict:
    """Get current rate limit status"""
    return rate_limit_manager.get_all_status()

def get_rate_limit_summary() -> Dict:
    """Get rate limit summary"""
    return rate_limit_manager.get_summary()