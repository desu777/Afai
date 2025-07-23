"""
Analytics Endpoints Module
Analytics-related endpoints extracted from server.py
"""
import json
from datetime import datetime
from fastapi import HTTPException, Request
from database import get_db
from database.analytics_operations import get_gemini_usage_stats
from config import debug_print

def setup_analytics_endpoints(app, tier2_rate_limit, AnalyticsQuery):
    """Setup analytics endpoints on FastAPI app"""
    
    @app.post("/analytics/query")
    @tier2_rate_limit()
    async def get_analytics(query: AnalyticsQuery, request: Request):
        """Get analytics data with optional filtering"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                sql = "SELECT * FROM analyze WHERE 1=1"
                params = []
                
                if query.start_date:
                    sql += " AND created_at >= ?"
                    params.append(query.start_date)
                
                if query.end_date:
                    sql += " AND created_at <= ?"
                    params.append(query.end_date)
                
                sql += " ORDER BY created_at DESC LIMIT ?"
                params.append(query.limit)
                
                cursor.execute(sql, params)
                
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    
                    # Parse JSON fields with error handling
                    try:
                        result["query_optimizer_queries"] = json.loads(result.get("query_optimizer_queries") or "[]")
                    except (json.JSONDecodeError, TypeError):
                        result["query_optimizer_queries"] = []
                        debug_print(f"⚠️ [Analytics] Failed to parse query_optimizer_queries for record {result.get('id')}")
                    
                    try:
                        result["pinecone_top_results"] = json.loads(result.get("pinecone_top_results") or "[]")
                    except (json.JSONDecodeError, TypeError):
                        result["pinecone_top_results"] = []
                        debug_print(f"⚠️ [Analytics] Failed to parse pinecone_top_results for record {result.get('id')}")
                    
                    try:
                        result["node_timings"] = json.loads(result.get("node_timings") or "{}")
                    except (json.JSONDecodeError, TypeError):
                        result["node_timings"] = {}
                        debug_print(f"⚠️ [Analytics] Failed to parse node_timings for record {result.get('id')}")
                    
                    # Add missing fields required by frontend types
                    result["confidence_score"] = result.get("intent_confidence", 0)
                    result["confidence_reasoning"] = "Based on intent confidence score"
                    
                    results.append(result)
                
                return {
                    "success": True,
                    "count": len(results),
                    "data": results
                }
        except Exception as e:
            debug_print(f"❌ [Analytics] Error in get_analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/analytics/summary")
    @tier2_rate_limit()
    async def get_analytics_summary(request: Request):
        """Get analytics summary statistics"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Total queries
                cursor.execute("SELECT COUNT(*) as total FROM analyze")
                total_queries = cursor.fetchone()["total"]
                
                # Average execution time
                cursor.execute("SELECT AVG(total_execution_time) as avg_time FROM analyze")
                avg_time = cursor.fetchone()["avg_time"] or 0
                
                # Intent distribution
                cursor.execute("""
                    SELECT intent_detector_decision, COUNT(*) as count
                    FROM analyze 
                    WHERE intent_detector_decision != ''
                    GROUP BY intent_detector_decision 
                    ORDER BY count DESC
                """)
                intent_dist = {row["intent_detector_decision"]: row["count"] for row in cursor.fetchall()}
                
                # Language distribution
                cursor.execute("""
                    SELECT detected_language, COUNT(*) as count
                    FROM analyze 
                    WHERE detected_language != ''
                    GROUP BY detected_language 
                    ORDER BY count DESC
                """)
                language_dist = {row["detected_language"]: row["count"] for row in cursor.fetchall()}
                
                # Confidence distribution
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN intent_confidence >= 0.8 THEN 1 ELSE 0 END) as high_confidence,
                        SUM(CASE WHEN intent_confidence >= 0.5 AND intent_confidence < 0.8 THEN 1 ELSE 0 END) as medium_confidence,
                        SUM(CASE WHEN intent_confidence < 0.5 THEN 1 ELSE 0 END) as low_confidence
                    FROM analyze
                    WHERE intent_confidence IS NOT NULL
                """)
                confidence_stats = cursor.fetchone()
                
                # Escalation rate
                cursor.execute("SELECT SUM(CASE WHEN escalated THEN 1 ELSE 0 END) as escalated FROM analyze")
                escalated_count = cursor.fetchone()["escalated"] or 0
                escalation_rate = (escalated_count / total_queries * 100) if total_queries > 0 else 0
                
                return {
                    "success": True,
                    "summary": {
                        "total_queries": total_queries,
                        "average_execution_time": round(avg_time, 3),
                        "confidence_distribution": {
                            "high_confidence": confidence_stats["high_confidence"] or 0,
                            "medium_confidence": confidence_stats["medium_confidence"] or 0,
                            "low_confidence": confidence_stats["low_confidence"] or 0
                        },
                        "intent_distribution": intent_dist,
                        "language_distribution": language_dist,
                        "escalation_rate": round(escalation_rate, 1)
                    }
                }
        except Exception as e:
            debug_print(f"❌ [Analytics] Error in get_analytics_summary: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/analytics/vertex-ai-usage")
    @tier2_rate_limit()
    async def get_vertex_ai_usage_analytics(request: Request, start_date: str = None, end_date: str = None):
        """Get Vertex AI usage analytics (historical data only - no rate limits)"""
        try:
            # Get usage statistics from database
            usage_stats = get_gemini_usage_stats(start_date, end_date)
            
            return {
                "success": True,
                "message": "Vertex AI has enterprise quotas - no rate limiting needed",
                "historical_usage": usage_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            debug_print(f"❌ [Analytics] Error in get_vertex_ai_usage_analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))