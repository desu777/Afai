"""
Analytics Database Operations
Save workflow analytics to database and track Gemini API usage
"""
import json
from datetime import date, datetime, timedelta
from .connection import get_db
from config import debug_print

def save_analytics_to_db(analytics_instance, global_analytics=None):
    """Save analytics data to SQLite database"""
    # Use provided analytics instance or fallback to global
    analytics_obj = analytics_instance or global_analytics
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analyze (
                    user_query, detected_language, intent_detector_decision,
                    intent_confidence, business_reasoner_decision, business_corrections,
                    query_optimizer_queries, pinecone_results_count, pinecone_top_results,
                    filter_decision, filtered_results_count,
                    final_response, total_execution_time, node_timings, escalated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analytics_obj.data.get("user_query", ""),
                analytics_obj.data.get("detected_language", ""),
                analytics_obj.data.get("intent_detector_decision", ""),
                analytics_obj.data.get("intent_confidence", 0.0),
                analytics_obj.data.get("business_reasoner_decision", ""),
                analytics_obj.data.get("business_corrections", ""),
                analytics_obj.data.get("query_optimizer_queries", ""),
                analytics_obj.data.get("pinecone_results_count", 0),
                analytics_obj.data.get("pinecone_top_results", ""),
                analytics_obj.data.get("filter_decision", ""),
                analytics_obj.data.get("filtered_results_count", 0),
                analytics_obj.data.get("final_response", ""),
                analytics_obj.data.get("total_execution_time", 0.0),
                json.dumps(analytics_obj.data.get("node_timings", {})) if isinstance(analytics_obj.data.get("node_timings"), dict) else analytics_obj.data.get("node_timings", ""),
                analytics_obj.data.get("escalated", False)
            ))
            
            conn.commit()
            debug_print("[OK] Analytics saved to database")
            
    except Exception as e:
        debug_print(f"[ERROR] Error saving analytics: {e}")


def record_gemini_usage(node_name: str, api_key_hash: str, success: bool = True):
    """Record Gemini API usage in database with daily aggregation"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            today = date.today().isoformat()
            
            # Try to update existing record for today
            if success:
                cursor.execute("""
                    UPDATE gemini_api_usage 
                    SET success_count = success_count + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE node_name = ? AND api_key_hash = ? AND request_date = ?
                """, (node_name, api_key_hash, today))
            else:
                cursor.execute("""
                    UPDATE gemini_api_usage 
                    SET error_count = error_count + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE node_name = ? AND api_key_hash = ? AND request_date = ?
                """, (node_name, api_key_hash, today))
            
            # If no existing record, create new one
            if cursor.rowcount == 0:
                success_count = 1 if success else 0
                error_count = 0 if success else 1
                cursor.execute("""
                    INSERT INTO gemini_api_usage 
                    (node_name, api_key_hash, request_date, success_count, error_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (node_name, api_key_hash, today, success_count, error_count))
            
            conn.commit()
            debug_print(f"[AUTH] [DB] Recorded Gemini usage: {node_name} ({'success' if success else 'error'})")
            
    except Exception as e:
        debug_print(f"[ERROR] Error recording Gemini usage: {e}")


def get_daily_gemini_usage(node_name: str, api_key_hash: str, target_date: str = None) -> int:
    """Get daily Gemini API usage count for specific node and API key"""
    try:
        if target_date is None:
            target_date = date.today().isoformat()
            
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT success_count FROM gemini_api_usage
                WHERE node_name = ? AND api_key_hash = ? AND request_date = ?
            """, (node_name, api_key_hash, target_date))
            
            result = cursor.fetchone()
            usage_count = result["success_count"] if result else 0
            
            debug_print(f"[DEBUG] [DB] Daily usage for {node_name}: {usage_count}/500")
            return usage_count
            
    except Exception as e:
        debug_print(f"[ERROR] Error getting daily Gemini usage: {e}")
        return 0  # Safe fallback - assume no usage on error


def get_gemini_usage_stats(start_date: str = None, end_date: str = None) -> dict:
    """Get Gemini API usage statistics for analytics dashboard"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Default to last 30 days if no dates provided
            if start_date is None:
                start_date = (date.today() - timedelta(days=30)).isoformat()
            if end_date is None:
                end_date = date.today().isoformat()
            
            # Total usage per node
            cursor.execute("""
                SELECT 
                    node_name,
                    SUM(success_count) as total_success,
                    SUM(error_count) as total_errors,
                    COUNT(DISTINCT request_date) as active_days
                FROM gemini_api_usage 
                WHERE request_date BETWEEN ? AND ?
                GROUP BY node_name
                ORDER BY total_success DESC
            """, (start_date, end_date))
            
            node_stats = {}
            for row in cursor.fetchall():
                node_stats[row["node_name"]] = {
                    "total_success": row["total_success"],
                    "total_errors": row["total_errors"],
                    "active_days": row["active_days"],
                    "success_rate": round(row["total_success"] / (row["total_success"] + row["total_errors"]) * 100, 2) if (row["total_success"] + row["total_errors"]) > 0 else 0
                }
            
            # Daily usage trend
            cursor.execute("""
                SELECT 
                    request_date,
                    SUM(success_count) as daily_total
                FROM gemini_api_usage 
                WHERE request_date BETWEEN ? AND ?
                GROUP BY request_date
                ORDER BY request_date DESC
                LIMIT 30
            """, (start_date, end_date))
            
            daily_trend = [
                {"date": row["request_date"], "usage": row["daily_total"]}
                for row in cursor.fetchall()
            ]
            
            return {
                "node_stats": node_stats,
                "daily_trend": daily_trend,
                "date_range": {"start": start_date, "end": end_date}
            }
            
    except Exception as e:
        debug_print(f"[ERROR] Error getting Gemini usage stats: {e}")
        return {"node_stats": {}, "daily_trend": [], "date_range": {}}