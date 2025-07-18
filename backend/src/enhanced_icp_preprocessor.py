"""
Enhanced ICP Data Preprocessor - Based on Dev Tools Analysis
Correctly parses HTML structure where each parameter has its own <tbody> element
"""

import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup
import requests

class EnhancedICPPreprocessor:
    """Enhanced preprocessor based on actual HTML structure analysis"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def scrape_and_process_icp_url(self, url: str) -> Dict:
        """Main method: scrape URL and process ICP data"""
        try:
            print(f"🌐 Scraping ICP URL: {url}")
            
            # Fetch HTML content
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data using new structure-aware method
            metadata = self._extract_metadata_from_soup(soup)
            parameters = self._extract_parameters_from_table(soup)
            
            # Build structured output
            structured_data = self._build_structured_output(metadata, parameters)
            
            print(f"✅ Successfully processed {len(parameters)} parameters")
            return {
                "status": "success",
                "metadata": metadata,
                "parameters": parameters,
                "structured_output": structured_data
            }
            
        except Exception as e:
            print(f"❌ Error processing ICP URL: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {},
                "parameters": [],
                "structured_output": ""
            }
    
    def _extract_metadata_from_soup(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from HTML structure"""
        metadata = {}
        
        try:
            # Find metadata in the page content
            text_content = soup.get_text()
            
            # Test number - from "Test wody #6261549" or "Badanie Woda morska: 6261549"
            test_match = re.search(r'Test wody #?(\d+)', text_content)
            if not test_match:
                test_match = re.search(r'Badanie Woda morska:\s*(\d+)', text_content)
            if test_match:
                metadata['test_number'] = test_match.group(1)
            
            # Aquarium info - "Akwarium (SPS): Domowe 1150 LPS"
            aquarium_match = re.search(r'Akwarium \([^)]+\):\s*([^\n]+)', text_content)
            if aquarium_match:
                metadata['aquarium_info'] = aquarium_match.group(1).strip()
            
            # Date - "Data: 2025-06-17"
            date_match = re.search(r'Data:\s*(\d{4}-\d{2}-\d{2})', text_content)
            if date_match:
                metadata['test_date'] = date_match.group(1)
            
            print(f"📋 Extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            print(f"❌ Error extracting metadata: {e}")
            return {}
    
    def _extract_parameters_from_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract parameters using correct HTML structure (tbody per parameter)"""
        parameters = []
        
        try:
            # Find the main results table
            table = soup.find('table', class_='table table-results list')
            if not table:
                print("❌ Could not find main results table")
                return []
            
            print(f"✅ Found main results table")
            
            # Find all tbody elements - each tbody is one parameter
            tbody_elements = table.find_all('tbody')
            print(f"📊 Found {len(tbody_elements)} tbody elements")
            
            for i, tbody in enumerate(tbody_elements):
                try:
                    # Skip tbody elements that don't have x-data attribute (these are likely headers)
                    if not tbody.get('x-data'):
                        continue
                    
                    parameter_data = self._extract_single_parameter_from_tbody(tbody)
                    if parameter_data:
                        parameters.append(parameter_data)
                        print(f"✅ Parameter {i+1}: {parameter_data['element']} = {parameter_data['result']}")
                
                except Exception as e:
                    print(f"❌ Error processing tbody {i}: {e}")
                    continue
            
            print(f"📊 Successfully extracted {len(parameters)} parameters")
            return parameters
            
        except Exception as e:
            print(f"❌ Error extracting parameters: {e}")
            return []
    
    def _extract_single_parameter_from_tbody(self, tbody) -> Optional[Dict]:
        """Extract single parameter data from tbody element"""
        try:
            # Get all td elements from all tr elements in this tbody
            tds = tbody.find_all('td')
            
            if len(tds) < 3:
                return None
            
            # Extract element name (first td or look for strong/span elements)
            element_name = ""
            for td in tds:
                # Look for element name in strong or span tags
                strong_elem = td.find('strong')
                if strong_elem:
                    element_name = strong_elem.get_text(strip=True)
                    break
                
                # Or look for text that looks like element name
                text = td.get_text(strip=True)
                if text and len(text) < 20 and not any(char.isdigit() for char in text):
                    element_name = text
                    break
            
            # Extract range (look for td with class="code" or pattern like "33 - 38")
            range_value = ""
            range_unit = ""
            for td in tds:
                if 'code' in td.get('class', []):
                    range_text = td.get_text(strip=True)
                    # Look for pattern like "33 - 38" followed by unit
                    range_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', range_text)
                    if range_match:
                        range_value = f"{range_match.group(1)} - {range_match.group(2)}"
                        # Look for unit after the range
                        unit_match = re.search(r'(\w+/?\w*)$', range_text)
                        if unit_match:
                            range_unit = unit_match.group(1)
                    break
            
            # Extract result (look for td with class="result")
            result_value = ""
            result_unit = ""
            for td in tds:
                if 'result' in td.get('class', []):
                    result_text = td.get_text(strip=True)
                    # Extract numeric value and unit
                    result_match = re.search(r'(\d+\.?\d*)\s*([a-zA-Z/%]+)', result_text)
                    if result_match:
                        result_value = result_match.group(1)
                        result_unit = result_match.group(2)
                    break
            
            # Extract difference (look for td with class="diff")
            difference = ""
            for td in tds:
                if 'diff' in td.get('class', []):
                    difference = td.get_text(strip=True)
                    break
            
            # Determine status based on result vs range
            status = self._determine_parameter_status(range_value, result_value)
            
            if element_name and range_value and result_value:
                return {
                    "element": element_name,
                    "range": range_value,
                    "range_unit": range_unit,
                    "result": result_value,
                    "result_unit": result_unit,
                    "difference": difference,
                    "status": status,
                    "full_range": f"{range_value} {range_unit}",
                    "full_result": f"{result_value} {result_unit}"
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting parameter from tbody: {e}")
            return None
    
    def _determine_parameter_status(self, range_str: str, result_str: str) -> str:
        """Determine if parameter is optimal, too_high, or too_low"""
        try:
            # Parse range "33 - 38" or "0 - 0.0300"
            range_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', range_str)
            if not range_match:
                return "unknown"
            
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            
            # Parse result value
            result_match = re.search(r'(\d+\.?\d*)', result_str)
            if not result_match:
                return "unknown"
            
            result_val = float(result_match.group(1))
            
            # Determine status
            if result_val < min_val:
                return "too_low"
            elif result_val > max_val:
                return "too_high"
            else:
                return "optimal"
                
        except Exception as e:
            print(f"❌ Error determining status: {e}")
            return "unknown"
    
    def _build_structured_output(self, metadata: Dict, parameters: List[Dict]) -> str:
        """Build structured output for LLM processing"""
        lines = []
        
        # Header
        lines.append("=== ICP TEST RESULTS - STRUCTURED FORMAT ===")
        lines.append("")
        
        # Metadata
        if metadata:
            lines.append("TEST INFORMATION:")
            if metadata.get('test_number'):
                lines.append(f"  Test Number: {metadata['test_number']}")
            if metadata.get('aquarium_info'):
                lines.append(f"  Aquarium: {metadata['aquarium_info']}")
            if metadata.get('test_date'):
                lines.append(f"  Date: {metadata['test_date']}")
            lines.append("")
        
        # Group parameters by status
        optimal_params = []
        too_high_params = []
        too_low_params = []
        
        for param in parameters:
            status = param.get('status', 'unknown')
            if status == 'optimal':
                optimal_params.append(param)
            elif status == 'too_high':
                too_high_params.append(param)
            elif status == 'too_low':
                too_low_params.append(param)
        
        # Display parameters by status
        if optimal_params:
            lines.append("✅ OPTIMAL PARAMETERS:")
            for param in optimal_params:
                lines.append(f"  {param['element']}: {param['full_result']} (range: {param['full_range']})")
            lines.append("")
        
        if too_high_params:
            lines.append("❌ TOO HIGH (need to decrease):")
            for param in too_high_params:
                lines.append(f"  {param['element']}: {param['full_result']} (range: {param['full_range']}) {param.get('difference', '')}")
            lines.append("")
        
        if too_low_params:
            lines.append("⚠️ TOO LOW (need to increase):")
            for param in too_low_params:
                lines.append(f"  {param['element']}: {param['full_result']} (range: {param['full_range']}) {param.get('difference', '')}")
            lines.append("")
        
        # Summary
        lines.append("📊 SUMMARY:")
        lines.append(f"  Total parameters: {len(parameters)}")
        lines.append(f"  Optimal: {len(optimal_params)}")
        lines.append(f"  Need correction: {len(too_high_params) + len(too_low_params)}")
        
        return "\n".join(lines)

# Test function
def test_enhanced_preprocessor():
    """Test the enhanced preprocessor"""
    preprocessor = EnhancedICPPreprocessor()
    
    # Test URL
    url = "https://aquaforestlab.com/pl/results/v6GMFwU876171"
    
    print(f"🔍 Testing Enhanced ICP Preprocessor with URL: {url}")
    print("=" * 80)
    
    result = preprocessor.scrape_and_process_icp_url(url)
    
    if result["status"] == "success":
        print("\n" + "=" * 80)
        print("STRUCTURED OUTPUT FOR LLM:")
        print("=" * 80)
        print(result["structured_output"])
        
        # Save results
        with open('/mnt/c/Users/kubas/Desktop/aquaforest-rag/backend/enhanced_icp_output.txt', 'w', encoding='utf-8') as f:
            f.write(result["structured_output"])
        
        print(f"\n📁 Enhanced output saved to: enhanced_icp_output.txt")
    else:
        print(f"❌ Test failed: {result['error']}")

if __name__ == "__main__":
    test_enhanced_preprocessor()