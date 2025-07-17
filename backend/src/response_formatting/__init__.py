"""
Response Formatting module exports
"""
from .response_formatter import ResponseFormatter, format_final_response
from .dosage_calculator import DosageCalculator
from .prompt_builder import PromptBuilder
from .cache_manager import CacheManager
from .followup_handler import handle_follow_up, escalate_to_human
from .context_formatters import (
    format_business_recommendations_context,
    format_competitor_context,
    format_scenario_context,
    format_use_case_context
)
from .domain_helpers import get_product_url, has_mixed_domains, group_results_by_domain

__all__ = [
    'ResponseFormatter',
    'format_final_response',
    'DosageCalculator',
    'PromptBuilder', 
    'CacheManager',
    'handle_follow_up',
    'escalate_to_human',
    'format_business_recommendations_context',
    'format_competitor_context',
    'format_scenario_context',
    'format_use_case_context',
    'get_product_url',
    'has_mixed_domains',
    'group_results_by_domain'
]