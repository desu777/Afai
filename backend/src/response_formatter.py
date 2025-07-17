"""
Response Formatter Entry Point
Maintains backward compatibility by importing from response_formatting module
"""
from response_formatting import (
    ResponseFormatter,
    format_final_response,
    handle_follow_up,
    escalate_to_human
)

# Re-export all public functions for backward compatibility
__all__ = [
    'ResponseFormatter',
    'format_final_response', 
    'handle_follow_up',
    'escalate_to_human'
]