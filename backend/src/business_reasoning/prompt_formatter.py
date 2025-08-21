"""
Prompt Formatter Module
Transforms JSON data into optimized XML-structured formats for LLM processing
"""
from typing import Dict, List, Any

class PromptDataFormatter:
    """Formats JSON data into structured XML blocks optimized for LLM processing"""
    
    @staticmethod
    def format_products_catalog(products_data: Dict[str, Any]) -> str:
        """
        Convert products_turbo.json into structured PRODUCT_CARD format
        
        Args:
            products_data: Dictionary containing product categories and their products
            
        Returns:
            Formatted string with PRODUCT_CARD blocks
        """
        formatted_cards = []
        
        # Process each category and its products
        for category, products in products_data.items():
            if isinstance(products, list):
                for product in products:
                    if isinstance(product, dict):
                        card = PromptDataFormatter._create_product_card(
                            category=category,
                            product=product
                        )
                        formatted_cards.append(card)
        
        return "\n\n".join(formatted_cards)
    
    @staticmethod
    def _create_product_card(category: str, product: Dict[str, Any]) -> str:
        """Create a single PRODUCT_CARD block"""
        product_name = product.get("product_name", "")
        keywords = ", ".join(product.get("keywords", []))
        problems = "; ".join(product.get("solves_problems", []))
        use_case = product.get("use_case", "")
        
        return f"""<PRODUCT_CARD>
  <CATEGORY>{category}</CATEGORY>
  <NAME>{product_name}</NAME>
  <KEYWORDS>{keywords}</KEYWORDS>
  <SOLVES>{problems}</SOLVES>
  <USE_CASE>{use_case}</USE_CASE>
</PRODUCT_CARD>"""
    
    @staticmethod
    def format_competitors_map(competitors_data: Dict[str, Any]) -> str:
        """
        Convert competitors.json into structured COMPETITOR_MAP format
        
        Args:
            competitors_data: Dictionary containing competitor mappings
            
        Returns:
            Formatted string with COMPETITOR_MAP blocks
        """
        formatted_maps = []
        
        # Process competitors section
        competitors_section = competitors_data.get("competitors", {})
        af_alternatives = competitors_data.get("response_strategies", {}).get("af_alternatives", {})
        
        for category, competitor_list in competitors_section.items():
            if isinstance(competitor_list, list):
                aliases = ", ".join(competitor_list)
                
                # Find AF alternatives for this category
                category_alternatives = set()
                for competitor in competitor_list:
                    # Try exact match first
                    if competitor in af_alternatives:
                        category_alternatives.add(af_alternatives[competitor])
                    else:
                        # Try to find partial matches (e.g., "Red Sea Salt" -> "Red Sea")
                        for af_comp, af_alt in af_alternatives.items():
                            if af_comp.lower() in competitor.lower() or competitor.lower() in af_comp.lower():
                                category_alternatives.add(af_alt)
                
                af_products = ", ".join(sorted(category_alternatives)) if category_alternatives else "Multiple AF alternatives available"
                
                map_block = PromptDataFormatter._create_competitor_map(
                    category=category,
                    aliases=aliases,
                    af_alternative=af_products
                )
                formatted_maps.append(map_block)
        
        return "\n\n".join(formatted_maps)
    
    @staticmethod
    def _create_competitor_map(category: str, aliases: str, af_alternative: str) -> str:
        """Create a single COMPETITOR_MAP block"""
        return f"""<COMPETITOR_MAP>
  <CATEGORY>{category}</CATEGORY>
  <ALIASES>{aliases}</ALIASES>
  <AQUAFOREST_ALTERNATIVE>{af_alternative}</AQUAFOREST_ALTERNATIVE>
</COMPETITOR_MAP>"""
    
    @staticmethod
    def format_icp_corrections_map(icp_corrections: Dict[str, Any]) -> str:
        """
        Convert ICP parameter correction mapping to structured XML format
        
        Args:
            icp_corrections: Dictionary containing ICP correction mapping from products_groups.json
            
        Returns:
            Formatted string with ICP_CORRECTION blocks
        """
        formatted_corrections = []
        
        # Process icp_parameter_correction section
        parameter_map = icp_corrections.get("parameter_map", {})
        
        for param, conditions in parameter_map.items():
            if isinstance(conditions, dict):
                for condition, products in conditions.items():
                    if isinstance(products, list) and products:
                        products_str = ", ".join(products)
                        
                        correction_block = f"""<ICP_CORRECTION>
  <PARAMETER>{param}</PARAMETER>
  <CONDITION>{condition}</CONDITION>
  <PRODUCTS>{products_str}</PRODUCTS>
</ICP_CORRECTION>"""
                        formatted_corrections.append(correction_block)
        
        return "\n\n".join(formatted_corrections)