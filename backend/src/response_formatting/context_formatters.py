"""
Context Formatters Module
Context formatting functions extracted from response_formatter.py
"""
from typing import List, Dict

def format_business_recommendations_context(recommendations: List[Dict]) -> str:
    """Format business recommendations into context"""
    if not recommendations:
        return ""
        
    context_lines = ["--- ENHANCED BUSINESS RECOMMENDATIONS ---"]
    
    for rec in recommendations:
        rec_type = rec.get("type", "unknown")
        
        if rec_type == "competitor_alternative":
            context_lines.append(f"🏢 COMPETITOR ALTERNATIVE: {rec['competitor']} → {rec['af_alternative']}")
            context_lines.append(f"   Message: {rec['message']}")
            
        elif rec_type == "setup_phase":
            phase_priority = "HIGH PRIORITY" if rec.get("priority") else "STANDARD"
            context_lines.append(f"📋 SETUP PHASE [{phase_priority}]: {rec['phase']}")
            context_lines.append(f"   Duration: {rec['duration']}")
            products_str = ", ".join([f"{cat}: {', '.join(prods)}" for cat, prods in rec['products'].items()])
            context_lines.append(f"   Products: {products_str}")
            
        elif rec_type == "use_case_priority":
            context_lines.append(f"🎯 USE CASE PRIORITY: {rec['use_case']}")
            context_lines.append(f"   Priority products: {', '.join(rec['priority_products'])}")
            if rec.get("timeline"):
                context_lines.append(f"   Timeline: {rec['timeline']}")
                
        elif rec_type == "missing_alert":
            alert_info = rec.get('note', 'Missing essential product')
            context_lines.append(f"⚠️ MISSING PRODUCT ALERT: {alert_info}")
            if 'products' in rec:
                context_lines.append(f"   Essential products: {', '.join(rec['products'])}")
    
    context_lines.append("---")
    return "\n".join(context_lines)

def format_competitor_context(competitor_info: Dict) -> str:
    """Format competitor context with DYNAMIC negative instructions for ALL detected competitors"""
    context_lines = ["--- COMPETITOR CONTEXT ---"]
    
    detected_competitors = []
    alternatives_mapping = []
    
    for comp in competitor_info.get("competitors", []):
        comp_name = comp["name"]
        detected_competitors.append(comp_name)
        context_lines.append(f"🏢 DETECTED COMPETITOR: {comp_name}")
        
        # Check if we have AF alternative
        af_alternatives = competitor_info.get("af_alternatives", {})
        if comp_name in af_alternatives:
            alt = af_alternatives[comp_name]
            context_lines.append(f"   → REDIRECT TO: {alt}")
            alternatives_mapping.append(f"{comp_name} → {alt}")
        else:
            context_lines.append(f"   → NO SPECIFIC AF ALTERNATIVE (do not praise)")
    
    # 🚨 DYNAMIC CRITICAL RULES for ALL detected competitors
    if detected_competitors:
        context_lines.append("")
        context_lines.append("🚨 CRITICAL COMPETITOR RULES:")
        context_lines.append(f"- NEVER praise these products: {', '.join(detected_competitors)}")
        context_lines.append(f"- NEVER write 'excellent choice', 'good decision', '{detected_competitors[0]} is great' about competitors")
        
        if alternatives_mapping:
            context_lines.append("- ALWAYS redirect using these mappings:")
            for mapping in alternatives_mapping:
                context_lines.append(f"  * While {mapping.split(' → ')[0]} is mentioned, I recommend our {mapping.split(' → ')[1]}")
        
        context_lines.append("- Focus on AF alternatives' benefits, not competitor praise")
        context_lines.append("- If no AF alternative specified, simply avoid praising competitor")
        context_lines.append("END CRITICAL RULES")
    
    context_lines.append("---")
    return "\n".join(context_lines)

def format_scenario_context(scenario_info: Dict) -> str:
    """Format scenario context"""
    context_lines = ["--- SCENARIO CONTEXT ---"]
    
    context_lines.append(f"📋 DETECTED SCENARIO: {scenario_info['name']}")
    
    priority_order = scenario_info.get("priority_order", [])
    if priority_order:
        context_lines.append(f"⚡ PRIORITY ORDER: {' → '.join(priority_order)}")
    
    mandatory_categories = scenario_info.get("mandatory_categories", [])
    if mandatory_categories:
        context_lines.append(f"🎯 MANDATORY CATEGORIES: {', '.join(mandatory_categories)}")
    
    context_lines.append("---")
    return "\n".join(context_lines)

def format_use_case_context(use_case_info: Dict) -> str:
    """Format use case context"""
    context_lines = ["--- USE CASE CONTEXT ---"]
    
    context_lines.append(f"🎯 IDENTIFIED USE CASE: {use_case_info['name']}")
    
    matching_keywords = use_case_info.get("matching_keywords", [])
    if matching_keywords:
        context_lines.append(f"🔍 MATCHING KEYWORDS: {', '.join(matching_keywords)}")
    
    priority_products = use_case_info.get("priority_products", [])
    if priority_products:
        context_lines.append(f"⭐ PRIORITY PRODUCTS: {', '.join(priority_products)}")
    
    timeline = use_case_info.get("timeline", "")
    if timeline:
        context_lines.append(f"⏱️ TIMELINE: {timeline}")
    
    context_lines.append("---")
    return "\n".join(context_lines)