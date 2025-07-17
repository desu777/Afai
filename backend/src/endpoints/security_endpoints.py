"""
Security Endpoints Module
Security and rate limiting endpoints extracted from server.py
"""
from fastapi import HTTPException, Request
from security_middleware import (
    get_rate_limit_status,
    get_violation_stats, 
    get_ip_violations, 
    remove_ip_from_auto_blacklist,
    cleanup_expired_violations
)

def setup_security_endpoints(app, global_rate_limit):
    """Setup security endpoints on FastAPI app"""
    
    @app.get("/security/status")
    @global_rate_limit()
    async def get_security_status(request: Request):
        """Get current security and rate limiting configuration"""
        return get_rate_limit_status()

    @app.get("/security/violations/stats")
    @global_rate_limit()
    async def get_security_violations_stats(request: Request):
        """Get violation tracking statistics"""
        cleanup_expired_violations()  # Clean up before getting stats
        return get_violation_stats()

    @app.get("/security/violations/{ip}")
    @global_rate_limit()
    async def get_ip_violation_history(ip: str, request: Request):
        """Get violation history for specific IP"""
        return get_ip_violations(ip)

    @app.delete("/security/blacklist/{ip}")
    @global_rate_limit()
    async def remove_ip_blacklist(ip: str, request: Request):
        """Manually remove IP from blacklist (both auto and manual)"""
        removed = remove_ip_from_auto_blacklist(ip)
        
        if removed:
            return {
                "success": True,
                "message": f"IP {ip} removed from blacklist",
                "ip": ip
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"IP {ip} not found in blacklist"
            )

    @app.post("/security/cleanup")
    @global_rate_limit()
    async def manual_cleanup_violations(request: Request):
        """Manually trigger cleanup of expired violations and blacklists"""
        cleanup_expired_violations()
        stats = get_violation_stats()
        
        return {
            "success": True,
            "message": "Cleanup completed",
            "current_stats": stats
        }