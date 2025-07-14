"""
Prompts module for managing external prompt templates
"""
import os
from typing import Dict, Any

__all__ = ['load_prompt_template']

def load_prompt_template(template_name: str, **kwargs) -> str:
    """
    Load and format prompt template from file
    
    Args:
        template_name: Name of template file (without .txt extension)
        **kwargs: Variables to substitute in template
        
    Returns:
        Formatted prompt string
    """
    try:
        prompts_dir = os.path.dirname(__file__)
        template_path = os.path.join(prompts_dir, f"{template_name}.txt")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        # Safe formatting - replace only known placeholders
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            template = template.replace(placeholder, str(value))
            
        return template
        
    except Exception as e:
        # Fallback - return empty string so calling code can handle
        print(f"❌ Error loading prompt template '{template_name}': {e}")
        return "" 