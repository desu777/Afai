"""
Domain Helper Functions
URL and domain grouping utilities extracted from response_formatter.py
"""
from typing import List, Dict

def get_product_url(product: Dict, language: str) -> str:
    """Get product URL based on language preference"""
    meta = product.get('metadata', {})
    if language == 'pl' and meta.get('url_pl'):
        return meta['url_pl']
    return meta.get('url_en', '')

def has_mixed_domains(results: List[Dict]) -> bool:
    """Check if results contain both freshwater and seawater products"""
    domains = set()
    for result in results:
        domain = result.get('metadata', {}).get('domain')
        if domain and domain != 'universal':
            domains.add(domain)
    return len(domains) > 1

def group_results_by_domain(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Group results by domain"""
    grouped = {
        'seawater': [],
        'freshwater': [],
        'universal': []
    }
    
    for result in results:
        domain = result.get('metadata', {}).get('domain', 'universal')
        if domain in grouped:
            grouped[domain].append(result)
    
    return grouped