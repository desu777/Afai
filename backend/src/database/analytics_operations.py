"""
Analytics Database Operations
Save workflow analytics to database
"""
import json
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
            debug_print("✅ Analytics saved to database")
            
    except Exception as e:
        debug_print(f"❌ Error saving analytics: {e}")