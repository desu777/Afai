"""
Feedback Endpoints Module
Feedback-related endpoints extracted from server.py
"""
from fastapi import HTTPException, Request
from database import get_db

def setup_feedback_endpoints(app, tier3_rate_limit, FeedbackRequest):
    """Setup feedback endpoints on FastAPI app"""
    
    @app.post("/feedback")
    @tier3_rate_limit()
    async def submit_feedback(feedback: FeedbackRequest, request: Request):
        """Submit user feedback"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback (
                        message_id, rating, comment, user_type
                    ) VALUES (?, ?, ?, ?)
                """, (
                    feedback.message_id,
                    feedback.rating,
                    feedback.comment,
                    feedback.user_type
                ))
                conn.commit()
                feedback_id = cursor.lastrowid
                
            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Thank you for your feedback!"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/feedback/summary")
    @tier3_rate_limit()
    async def get_feedback_summary(request: Request):
        """Get feedback summary statistics"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Total feedback
                cursor.execute("SELECT COUNT(*) as total FROM feedback")
                total_feedback = cursor.fetchone()["total"]
                
                # Average rating
                cursor.execute("SELECT AVG(rating) as avg_rating FROM feedback")
                avg_rating = cursor.fetchone()["avg_rating"] or 0
                
                # Rating distribution
                cursor.execute("""
                    SELECT rating, COUNT(*) as count
                    FROM feedback
                    GROUP BY rating
                """)
                rating_dist = {row["rating"]: row["count"] for row in cursor.fetchall()}
                
                # Recent feedback
                cursor.execute("""
                    SELECT * FROM feedback
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                recent_feedback = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "success": True,
                    "summary": {
                        "total_feedback": total_feedback,
                        "average_rating": round(avg_rating, 2),
                        "rating_distribution": rating_dist,
                        "recent_feedback": recent_feedback
                    }
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))