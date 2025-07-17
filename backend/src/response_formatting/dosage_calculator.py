"""
Dosage Calculator Module
Dosage detection and calculation functionality extracted from response_formatter.py
"""
import re
from typing import Dict, Any, Optional

class DosageCalculator:
    def __init__(self):
        self.dosage_keywords = [
            'how much', 'combien', 'quanto', 'dosierung', 'dosis', 'how much needed',
            'how to dose', 'how to dose', 'how much to add', 'how to apply', 'what dose',
            'for', 'for', 'liters', 'liters', 'L'
        ]
    
    def detect_dosage_query(self, query: str) -> bool:
        """Detect if query is about dosage/calculation"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.dosage_keywords)
    
    def extract_dosage_info(self, metadata: Dict) -> Dict[str, Any]:
        """Extract dosage information from product metadata"""
        dosage_info = {
            "has_dosage": False,
            "base_amount": None,
            "base_volume": 100,  # Default to 100L
            "unit": "ml",
            "frequency": "daily",
            "timing": None,
            "special_instructions": []
        }
        
        # Check various dosage fields
        if metadata.get("dosage_amount"):
            dosage_info["has_dosage"] = True
            dosage_info["base_amount"] = self._parse_amount(metadata["dosage_amount"])
            
        if metadata.get("dosage_volume"):
            volume = self._parse_volume(metadata["dosage_volume"])
            if volume:
                dosage_info["base_volume"] = volume
                
        if metadata.get("dosage_unit"):
            dosage_info["unit"] = metadata["dosage_unit"]
            
        if metadata.get("dosage_frequency"):
            dosage_info["frequency"] = metadata["dosage_frequency"]
            
        if metadata.get("dosage_timing"):
            dosage_info["timing"] = metadata["dosage_timing"]
            
        # Parse from full content if needed
        if not dosage_info["has_dosage"] and metadata.get("full_content_en"):
            dosage_info = self._parse_dosage_from_content(metadata["full_content_en"], dosage_info)
            
        return dosage_info
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount from string like '10 ml' or '1 drop'"""
        try:
            # Extract number from string
            match = re.search(r'(\d+(?:\.\d+)?)', str(amount_str))
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.0
    
    def _parse_volume(self, volume_str: str) -> Optional[int]:
        """Parse volume from string like '100L' or '100 liters'"""
        try:
            match = re.search(r'(\d+)\s*[lL]', str(volume_str))
            if match:
                return int(match.group(1))
        except:
            pass
        return None
    
    def _parse_dosage_from_content(self, content: str, dosage_info: Dict) -> Dict:
        """Try to parse dosage from full content"""
        # Common dosage patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(ml|drops?|kropli?|krople?)\s*(?:per|na)\s*(\d+)\s*[lL]',
            r'dawkowanie:?\s*(\d+(?:\.\d+)?)\s*(ml|drops?)',
            r'dose:?\s*(\d+(?:\.\d+)?)\s*(ml|drops?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                dosage_info["has_dosage"] = True
                dosage_info["base_amount"] = float(match.group(1))
                dosage_info["unit"] = match.group(2).lower()
                if len(match.groups()) >= 3:
                    dosage_info["base_volume"] = int(match.group(3))
                break
                
        return dosage_info