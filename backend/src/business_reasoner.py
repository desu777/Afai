"""
Business Reasoner Entry Point
Maintains backward compatibility by importing from business_reasoning module
"""
from business_reasoning import (
    BusinessReasoner,
    business_reasoner
)

# Re-export all public functions for backward compatibility
__all__ = [
    'BusinessReasoner',
    'business_reasoner'
]