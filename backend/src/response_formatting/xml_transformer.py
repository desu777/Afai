"""
XML Metadata Transformer Module
Converts JSON metadata to optimized XML structures for LLM processing
Implements Operation "Krystaliczny Kontekst" for 10x performance improvement
"""
import re
from typing import Dict, Any, List

class XMLMetadataTransformer:
    """Transforms JSON metadata into ultra-efficient XML blocks for Response Formatter"""
    
    @staticmethod
    def transform_metadata(metadata: Dict[str, Any]) -> str:
        """
        Main entry point - detects content type and applies appropriate transformer
        
        Args:
            metadata: Dictionary containing product or knowledge base metadata
            
        Returns:
            Formatted XML string (PRODUCT_CARD or AQUAFOREST_KNOWLEDGE)
        """
        content_type = metadata.get("content_type", "").lower()
        
        if content_type == "product":
            return XMLMetadataTransformer.transform_product_to_xml(metadata)
        elif content_type == "knowledge":
            return XMLMetadataTransformer.transform_knowledge_to_xml(metadata)
        else:
            # Fallback for unknown content types - assume product
            return XMLMetadataTransformer.transform_product_to_xml(metadata)
    
    @staticmethod
    def transform_product_to_xml(metadata: Dict[str, Any]) -> str:
        """
        Transform product metadata to PRODUCT_CARD XML format
        
        Args:
            metadata: Product metadata dictionary
            
        Returns:
            Formatted PRODUCT_CARD XML block
        """
        # Extract and format dosage information
        dosage = XMLMetadataTransformer._format_dosage(metadata)
        
        # Extract compatible products
        compatible_products = metadata.get("compatible_products", [])
        compatible_str = ", ".join(compatible_products) if compatible_products else "None specified"
        
        # Extract sizes
        sizes = metadata.get("sizes_available", [])
        sizes_str = ", ".join(sizes) if sizes else "Not specified"
        
        # Build the PRODUCT_CARD XML
        xml_block = f"""<PRODUCT_CARD>
  <NAME>{metadata.get("product_name", "Unknown Product")}</NAME>
  <TITLE>{metadata.get("title_en", metadata.get("product_name", ""))}</TITLE>
  <CATEGORY>{metadata.get("product_family", metadata.get("category", ""))}</CATEGORY>
  <DOMAIN>{metadata.get("domain", "universal")}</DOMAIN>
  <DIFFICULTY>{metadata.get("difficulty", "intermediate")}</DIFFICULTY>
  <DOSAGE>{dosage}</DOSAGE>
  <COMPATIBLE_WITH>{compatible_str}</COMPATIBLE_WITH>
  <SIZES>{sizes_str}</SIZES>
  <FULL_CONTENT>{metadata.get("full_content_en", "No description available")}</FULL_CONTENT>
  <URL_EN>{metadata.get("url_en", "")}</URL_EN>
  <URL_PL>{metadata.get("url_pl", "")}</URL_PL>
</PRODUCT_CARD>"""
        
        return xml_block
    
    @staticmethod
    def transform_knowledge_to_xml(metadata: Dict[str, Any]) -> str:
        """
        Transform knowledge base metadata to AQUAFOREST_KNOWLEDGE XML format
        
        Args:
            metadata: Knowledge base metadata dictionary
            
        Returns:
            Formatted AQUAFOREST_KNOWLEDGE XML block
        """
        # Extract full text content
        full_text = metadata.get("full_content_en", "")
        
        # Intelligently extract product names from the content
        applicable_products = XMLMetadataTransformer._extract_products_from_text(full_text)
        
        # If no products found in text, check compatible_products field as fallback
        if not applicable_products:
            compatible = metadata.get("compatible_products", "")
            if compatible and isinstance(compatible, str):
                # Parse comma-separated string
                applicable_products = [p.strip() for p in compatible.split(",") if p.strip()]
        
        # Format applicable products list
        if applicable_products:
            products_formatted = "\n".join([f"    - {product}" for product in applicable_products])
        else:
            products_formatted = "    - No specific products mentioned"
        
        # Extract topic from title or category
        topic = XMLMetadataTransformer._extract_topic(metadata)
        
        # Build the AQUAFOREST_KNOWLEDGE XML
        xml_block = f"""<AQUAFOREST_KNOWLEDGE>
  <TITLE>{metadata.get("title_en", metadata.get("product_name", ""))}</TITLE>
  <CATEGORY>{metadata.get("category", "general")}</CATEGORY>
  <TOPIC>{topic}</TOPIC>
  <APPLICABLE_PRODUCTS>
{products_formatted}
  </APPLICABLE_PRODUCTS>
  <FULL_TEXT>{full_text}</FULL_TEXT>
  <URL_EN>{metadata.get("url_en", "")}</URL_EN>
  <URL_PL>{metadata.get("url_pl", "")}</URL_PL>
</AQUAFOREST_KNOWLEDGE>"""
        
        return xml_block
    
    @staticmethod
    def _format_dosage(metadata: Dict[str, Any]) -> str:
        """
        Combine dosage fields into a single readable text
        
        Args:
            metadata: Product metadata containing dosage fields
            
        Returns:
            Formatted dosage string
        """
        # Check if dosage_amount already contains complete info
        dosage_amount = metadata.get("dosage_amount", "")
        if dosage_amount and "(" in dosage_amount and ")" in dosage_amount:
            # Already formatted like "1 drop per 100L (every other day, after lights out)"
            return dosage_amount
        
        # Build dosage from components
        components = []
        
        # Amount and volume
        if dosage_amount:
            volume = metadata.get("dosage_volume", "")
            if volume:
                components.append(f"{dosage_amount} per {volume}")
            else:
                components.append(dosage_amount)
        
        # Frequency
        frequency = metadata.get("dosage_frequency", "")
        if frequency:
            # Convert underscores to spaces
            frequency_readable = frequency.replace("_", " ")
            components.append(frequency_readable)
        
        # Timing
        timing = metadata.get("dosage_timing", "")
        if timing:
            # Convert underscores to spaces
            timing_readable = timing.replace("_", " ")
            components.append(timing_readable)
        
        # Combine all components
        if components:
            return ", ".join(components)
        else:
            return "See product instructions"
    
    @staticmethod
    def _extract_products_from_text(text: str) -> List[str]:
        """
        Intelligently extract Aquaforest product names from text content
        
        Args:
            text: Full text content to analyze
            
        Returns:
            List of detected product names
        """
        products = []
        
        # Common Aquaforest product patterns
        # Pattern 1: "AF [Product]" or "AF[Product]"
        af_pattern = r'AF\s*[A-Z][a-zA-Z\s]+'
        af_matches = re.findall(af_pattern, text)
        for match in af_matches:
            # Clean up the match
            product = match.strip()
            if len(product) > 2 and product not in products:
                products.append(product)
        
        # Pattern 2: Specific known product names
        known_products = [
            "Pro Bio S", "Pro Bio F", "-NP Pro", "NP Pro",
            "Life Bio Fil", "Bio S", "Reef Salt", "Reef Salt+",
            "Hybrid Pro Salt", "Sea Salt", "AF Rock", "Stone Fix",
            "AF Bio Sand", "Zeo Mix", "Carbon", "Phosphate Minus",
            "KH Buffer", "Calcium", "Magnesium", "Reef Mineral Salt",
            "Component A", "Component B", "Component C",
            "AF Amino Mix", "AF Energy", "AF Build", "AF Vitality",
            "AF Power Food", "AF Life Source", "AF Life Essence",
            "NitraPhos Minus", "TestPro Pack", "ICP Test"
        ]
        
        for product in known_products:
            # Case-insensitive search but preserve original case
            if re.search(r'\b' + re.escape(product) + r'\b', text, re.IGNORECASE):
                if product not in products:
                    products.append(product)
        
        # Pattern 3: Products mentioned after "use", "dose", "add", "apply"
        action_pattern = r'(?:use|dose|add|apply|with)\s+([A-Z][a-zA-Z\s]+?)(?:\s+to|\s+for|\s+in|\s+at|\.|,)'
        action_matches = re.findall(action_pattern, text, re.IGNORECASE)
        for match in action_matches:
            product = match.strip()
            # Filter to likely product names (capitalized, reasonable length)
            if product[0].isupper() and 2 < len(product) < 30 and product not in products:
                # Check if it looks like a product name (not a common word)
                if not product.lower() in ["the", "your", "this", "that", "these", "those"]:
                    products.append(product)
        
        # Sort products for consistent output
        products.sort()
        
        return products[:15]  # Limit to 15 most relevant products
    
    @staticmethod
    def _extract_topic(metadata: Dict[str, Any]) -> str:
        """
        Extract main topic from metadata
        
        Args:
            metadata: Knowledge base metadata
            
        Returns:
            Main topic string
        """
        # Try to get from title first
        title = metadata.get("title_en", metadata.get("product_name", ""))
        
        # Extract topic from title (usually after dash or colon)
        if "–" in title:
            topic = title.split("–")[0].strip()
        elif ":" in title:
            topic = title.split(":")[0].strip()
        elif "-" in title:
            parts = title.split("-")
            if len(parts) > 1:
                topic = parts[0].strip()
            else:
                topic = title
        else:
            topic = title
        
        # Fallback to category if topic is too short
        if len(topic) < 5:
            topic = metadata.get("category", "General aquarium knowledge")
        
        return topic