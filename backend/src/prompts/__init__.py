"""
Prompts module for managing external prompt templates
"""
import os
from typing import Dict, Any

__all__ = ['load_prompt_template']

def load_prompt_template(template_name: str, access_level: str = None, **kwargs) -> str:
    """
    Load and format prompt template from file with access level support
    
    Args:
        template_name: Name of template file (without .txt extension)
        access_level: User access level ("support", "admin", "test", etc.)
        **kwargs: Variables to substitute in template
        
    Returns:
        Formatted prompt string
    """
    try:
        prompts_dir = os.path.dirname(__file__)
        
        # Determine template file based on access level
        actual_template_name = template_name
        if access_level == "support":
            # Try professional variant first
            professional_template = f"{template_name}_professional"
            professional_path = os.path.join(prompts_dir, f"{professional_template}.txt")
            if os.path.exists(professional_path):
                actual_template_name = professional_template
        
        template_path = os.path.join(prompts_dir, f"{actual_template_name}.txt")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        # Safe formatting - replace only known placeholders
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            template = template.replace(placeholder, str(value))
            
        return template
        
    except Exception as e:
        # Fallback - return empty string so calling code can handle
        print(f"❌ Error loading prompt template '{actual_template_name if 'actual_template_name' in locals() else template_name}': {e}")
        return "" 