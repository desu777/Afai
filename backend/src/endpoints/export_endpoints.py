"""
Export Endpoints Module
CSV export endpoints extracted from server.py
"""
import csv
import io
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from database import get_db

def setup_export_endpoints(app, csv_export_rate_limit):
    """Setup export endpoints on FastAPI app"""
    
    @app.get("/analytics/export/csv")
    @csv_export_rate_limit()
    async def export_analytics_csv(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Export analytics data as CSV"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                sql = "SELECT * FROM analyze WHERE 1=1"
                params = []
                
                if start_date:
                    sql += " AND created_at >= ?"
                    params.append(start_date)
                
                if end_date:
                    sql += " AND created_at <= ?"
                    params.append(end_date)
                
                sql += " ORDER BY created_at DESC"
                
                cursor.execute(sql, params)
                
                # Create CSV in memory with proper formatting for Excel
                output = io.StringIO()
                writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                
                # CSV headers
                headers = [
                    "ID", "User Query", "Detected Language", "Intent Decision", "Intent Confidence",
                    "Business Decision", "Business Corrections", "Query Optimizer", 
                    "Pinecone Results", "Top Results", "Filter Decision", 
                    "Filtered Results Count", "Final Response",
                    "Total Time", "Node Timings", "Escalated", "Created At"
                ]
                writer.writerow(headers)
                
                def clean_text(text):
                    """Clean text for CSV export"""
                    if not text:
                        return ""
                    # Remove newlines and extra whitespace
                    cleaned = str(text).replace('\n', ' ').replace('\r', ' ')
                    # Limit length to prevent huge CSV cells
                    return cleaned[:500] + "..." if len(cleaned) > 500 else cleaned
                
                # Write data
                for row in cursor.fetchall():
                    writer.writerow([
                        row["id"],
                        clean_text(row["user_query"]),
                        row["detected_language"] or "",
                        row["intent_detector_decision"] or "",
                        row["intent_confidence"] or 0,
                        clean_text(row["business_reasoner_decision"]),
                        clean_text(row["business_corrections"]),
                        clean_text(row["query_optimizer_queries"]),
                        row["pinecone_results_count"] or 0,
                        clean_text(row["pinecone_top_results"]),
                        clean_text(row["filter_decision"]),
                        row["filtered_results_count"] or 0,
                        clean_text(row["final_response"]),
                        row["total_execution_time"] or 0,
                        clean_text(row["node_timings"]),
                        "Yes" if row["escalated"] else "No",
                        row["created_at"]
                    ])
                
                # Create response
                output.seek(0)
                filename = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                return StreamingResponse(
                    io.BytesIO(output.getvalue().encode('utf-8-sig')),  # UTF-8 with BOM for Excel
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/feedback/export/csv")
    @csv_export_rate_limit()
    async def export_feedback_csv(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Export feedback data as CSV"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                sql = "SELECT * FROM feedback WHERE 1=1"
                params = []
                
                if start_date:
                    sql += " AND created_at >= ?"
                    params.append(start_date)
                
                if end_date:
                    sql += " AND created_at <= ?"
                    params.append(end_date)
                
                sql += " ORDER BY created_at DESC"
                
                cursor.execute(sql, params)
                
                # Create CSV in memory with proper formatting for Excel
                output = io.StringIO()
                writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                
                # Write headers - complete feedback export
                headers = [
                    "Feedback ID", "Message ID", "Rating (1-5)", "Comment", "User Type", "Created At"
                ]
                writer.writerow(headers)
                
                # Helper function to clean text for CSV
                def clean_text(text):
                    if not text:
                        return ""
                    # Replace problematic characters and normalize newlines
                    return str(text).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
                
                # Write data - complete feedback data
                for row in cursor.fetchall():
                    writer.writerow([
                        row["id"],
                        row["message_id"] or "",
                        row["rating"] or "",
                        clean_text(row["comment"]),
                        row["user_type"] or "test",
                        row["created_at"] or ""
                    ])
                
                # Create response
                output.seek(0)
                filename = f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                return StreamingResponse(
                    io.BytesIO(output.getvalue().encode('utf-8-sig')),  # UTF-8 with BOM for Excel
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))