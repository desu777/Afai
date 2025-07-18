"""
Improved ICP Data Preprocessor
Converts messy webscraper data into structured format for better LLM processing
"""

import re
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup

class ICPPreprocessor:
    """Enhanced preprocessor for ICP webscraper data"""
    
    def __init__(self):
        self.element_patterns = {
            'Zasolenie': r'(?:Zasolenie|Salinity)',
            'KH': r'(?:KH|Alkalinity)',
            'PO4': r'(?:PO4|Fosforany|Phosphate)',
            'NO3': r'(?:NO3|Azotany|Nitrate)',
            'Ca': r'(?:Ca|Wapń|Calcium)',
            'Mg': r'(?:Mg|Magnez|Magnesium)',
            'K': r'(?:K|Potas|Potassium)',
            'Na': r'(?:Na|Sód|Sodium)',
            'Sr': r'(?:Sr|Stront|Strontium)',
            'B': r'(?:B|Bor|Boron)',
            'Br': r'(?:Br|Brom|Bromine)',
            'I': r'(?:I|Jod|Iodine)',
            'Fe': r'(?:Fe|Żelazo|Iron)',
            'Mn': r'(?:Mn|Mangan|Manganese)',
            'Cu': r'(?:Cu|Miedź|Copper)',
            'Zn': r'(?:Zn|Cynk|Zinc)',
            'Co': r'(?:Co|Kobalt|Cobalt)',
            'Ni': r'(?:Ni|Nikiel|Nickel)',
            'Mo': r'(?:Mo|Molibden|Molybdenum)',
            'V': r'(?:V|Wanad|Vanadium)',
            'S': r'(?:S|Siarka|Sulfur)',
            'P': r'(?:P|Fosfor|Phosphorus)',
            'Li': r'(?:Li|Lit|Lithium)',
            'Se': r'(?:Se|Selen|Selenium)',
            'Al': r'(?:Al|Glin|Aluminum)',
            'As': r'(?:As|Arsen|Arsenic)',
            'Ba': r'(?:Ba|Bar|Barium)',
            'Be': r'(?:Be|Beryl|Beryllium)',
            'Cd': r'(?:Cd|Kadm|Cadmium)',
            'Cr': r'(?:Cr|Chrom|Chromium)',
            'Hg': r'(?:Hg|Rtęć|Mercury)',
            'La': r'(?:La|Lantan|Lanthanum)',
            'Pb': r'(?:Pb|Ołów|Lead)',
            'Sb': r'(?:Sb|Antymon|Antimony)',
            'Sc': r'(?:Sc|Skand|Scandium)',
            'Si': r'(?:Si|Krzem|Silicon)',
            'Sn': r'(?:Sn|Cyna|Tin)',
            'Ti': r'(?:Ti|Tytan|Titanium)',
            'W': r'(?:W|Wolfram|Tungsten)',
        }
    
    def preprocess_raw_content(self, raw_content: str) -> str:
        """Convert raw messy content into structured format for LLM"""
        
        # Extract metadata first
        metadata = self._extract_metadata(raw_content)
        
        # Extract parameters
        parameters = self._extract_parameters(raw_content)
        
        # Build structured format
        structured_content = self._build_structured_format(metadata, parameters)
        
        return structured_content
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extract test metadata from content"""
        metadata = {}
        
        # Test number
        test_match = re.search(r'Test wody #?(\d+)', content)
        if test_match:
            metadata['test_number'] = test_match.group(1)
        
        # Aquarium info
        aquarium_match = re.search(r'Akwarium \([^)]+\):\s*([^\n]+)', content)
        if aquarium_match:
            metadata['aquarium_info'] = aquarium_match.group(1).strip()
        
        # Date
        date_match = re.search(r'Data:\s*(\d{4}-\d{2}-\d{2})', content)
        if date_match:
            metadata['test_date'] = date_match.group(1)
        
        return metadata
    
    def _extract_parameters(self, content: str) -> List[Dict]:
        """Extract parameter data from content"""
        parameters = []
        
        # Split content into lines
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line contains a parameter name
            element_found = None
            for element, pattern in self.element_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    element_found = element
                    break
            
            if element_found:
                # Try to extract parameter data
                param_data = self._extract_single_parameter(lines, i, element_found)
                if param_data:
                    parameters.append(param_data)
                    i += param_data.get('lines_consumed', 1)
                else:
                    i += 1
            else:
                i += 1
        
        return parameters
    
    def _extract_single_parameter(self, lines: List[str], start_index: int, element_name: str) -> Dict:
        """Extract single parameter data starting from given line"""
        param_data = {
            'element': element_name,
            'lines_consumed': 1
        }
        
        # Look ahead for value patterns
        for i in range(start_index, min(start_index + 20, len(lines))):
            line = lines[i].strip()
            
            # Range pattern (e.g., "33 - 38" or "0 - 0.0300")
            range_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', line)
            if range_match and not param_data.get('range'):
                param_data['range'] = f"{range_match.group(1)} - {range_match.group(2)}"
            
            # Unit pattern (e.g., "mg/l", "ppt", "dKH")
            unit_match = re.search(r'(mg/l|ppt|dKH|%)', line)
            if unit_match and not param_data.get('unit'):
                param_data['unit'] = unit_match.group(1)
            
            # Result value pattern (e.g., "36 ppt", "0.0331 mg/l")
            result_match = re.search(r'(\d+\.?\d*)\s*(mg/l|ppt|dKH|%)', line)
            if result_match and not param_data.get('result'):
                param_data['result'] = result_match.group(1)
                param_data['result_unit'] = result_match.group(2)
            
            # Difference pattern (e.g., "+ 0.5 ppt", "- 1.12 mg/l")
            diff_match = re.search(r'([+-])\s*(\d+\.?\d*)\s*(mg/l|ppt|dKH|%)', line)
            if diff_match and not param_data.get('difference'):
                param_data['difference'] = f"{diff_match.group(1)} {diff_match.group(2)}"
            
            # Recommendation pattern
            if 'Zalecenia' in line or 'Uwaga!' in line:
                # Look for recommendation in next few lines
                rec_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    rec_line = lines[j].strip()
                    if rec_line and not re.search(r'^\w+$', rec_line):  # Not just element name
                        rec_lines.append(rec_line)
                    if len(rec_lines) >= 2:  # Got enough recommendation text
                        break
                
                if rec_lines:
                    param_data['recommendation'] = ' '.join(rec_lines)
                    param_data['lines_consumed'] = j - start_index + 1
                    break
        
        # If we found basic data, return it
        if param_data.get('range') and param_data.get('result'):
            return param_data
        
        return None
    
    def _build_structured_format(self, metadata: Dict, parameters: List[Dict]) -> str:
        """Build structured format for LLM processing"""
        sections = []
        
        # Header section
        sections.append("=== ICP TEST ANALYSIS ===")
        sections.append("")
        
        # Metadata section
        if metadata:
            sections.append("TEST INFORMATION:")
            for key, value in metadata.items():
                sections.append(f"  {key}: {value}")
            sections.append("")
        
        # Parameters section
        sections.append("PARAMETER RESULTS:")
        sections.append("")
        
        for param in parameters:
            element = param['element']
            range_val = param.get('range', 'N/A')
            result = param.get('result', 'N/A')
            unit = param.get('unit', param.get('result_unit', ''))
            difference = param.get('difference', 'N/A')
            
            sections.append(f"ELEMENT: {element}")
            sections.append(f"  Range: {range_val} {unit}")
            sections.append(f"  Result: {result} {unit}")
            sections.append(f"  Difference: {difference} {unit}")
            
            if param.get('recommendation'):
                sections.append(f"  Recommendation: {param['recommendation']}")
            
            sections.append("")
        
        return "\n".join(sections)
    
    def preprocess_html_content(self, html_content: str) -> str:
        """Preprocess HTML content for better structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unnecessary elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extract main table
        main_table = soup.find('table')
        if main_table:
            # Process table rows
            structured_data = self._process_table_rows(main_table)
            return structured_data
        
        # Fallback to text extraction
        text_content = soup.get_text(separator='\n', strip=True)
        return self.preprocess_raw_content(text_content)
    
    def _process_table_rows(self, table) -> str:
        """Process table rows into structured format"""
        rows = table.find_all('tr')
        structured_lines = []
        
        structured_lines.append("=== ICP TEST RESULTS TABLE ===")
        structured_lines.append("")
        
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:
                element = cells[0].get_text(strip=True)
                range_val = cells[1].get_text(strip=True)
                result = cells[2].get_text(strip=True)
                difference = cells[3].get_text(strip=True)
                
                # Clean up cell content
                element = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', element)
                
                structured_lines.append(f"PARAMETER: {element}")
                structured_lines.append(f"  Recommended: {range_val}")
                structured_lines.append(f"  Result: {result}")
                structured_lines.append(f"  Difference: {difference}")
                structured_lines.append("")
        
        return "\n".join(structured_lines)

# Test function
def test_preprocessor():
    """Test the preprocessor with sample data"""
    preprocessor = ICPPreprocessor()
    
    # Read the raw content file
    try:
        with open('/mnt/c/Users/kubas/Desktop/aquaforest-rag/backend/raw_icp_content.txt', 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # Preprocess it
        structured_content = preprocessor.preprocess_raw_content(raw_content)
        
        print("STRUCTURED OUTPUT:")
        print("=" * 80)
        print(structured_content)
        
        # Save structured content
        with open('/mnt/c/Users/kubas/Desktop/aquaforest-rag/backend/structured_icp_content.txt', 'w', encoding='utf-8') as f:
            f.write(structured_content)
        
        print(f"\n📁 Structured content saved to: structured_icp_content.txt")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_preprocessor()