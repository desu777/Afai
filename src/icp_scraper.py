"""
ICP Scraper Module - Web scraping for Aquaforest Lab ICP test results
Extracted from business_reasoner.py for better code organization
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from config import debug_print
import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL2

class ICPScraper:
    """Web scraper for Aquaforest Lab ICP test results"""
    
    def extract_icp_data_from_url(self, url: str) -> Dict:
        """🆕 Extract ICP test data from Aquaforest Lab URL"""
        try:
            debug_print(f"🌐 [ICPScraper] Fetching ICP data from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 🔍 LOG: Response details
            debug_print(f"📊 [ICPScraper] HTTP Status: {response.status_code}")
            debug_print(f"📊 [ICPScraper] Content-Type: {response.headers.get('content-type', 'unknown')}")
            debug_print(f"📊 [ICPScraper] Content Length: {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 🔍 LOG: HTML structure analysis
            debug_print(f"📋 [ICPScraper] Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Find all tables
            tables = soup.find_all('table')
            debug_print(f"📋 [ICPScraper] Found {len(tables)} table(s) on page")
            
            # 🆕 EXTRACT ICP METADATA (test info)
            metadata = self._extract_icp_metadata(soup)
            
            # Structure based on typical ICP test results
            icp_data = {
                "url": url,
                "parameters": {},
                "metadata": metadata,  # 🆕 Add metadata
                "raw_data": soup.get_text(),  # 🆕 Add raw text for recommendations extraction
                "status": "success",
                "debug_info": {
                    "tables_found": len(tables),
                    "page_title": soup.title.string if soup.title else None
                }
            }
            
            # 🎯 EXTRACT ALL ICP DATA - Dynamic table parsing
            results_table = soup.find('table', class_='table-results') or soup.find('table')
            
            if results_table:
                debug_print(f"📋 [ICPScraper] Found results table")
                
                # Find all test result rows (skip header)
                test_rows = results_table.find_all('tr')[1:]  # Skip header
                debug_print(f"📋 [ICPScraper] Processing {len(test_rows)} parameter rows")
                
                for i, row in enumerate(test_rows):
                    # Extract all cells dynamically
                    all_cells = row.find_all('td')
                    if len(all_cells) >= 3:  # Need at least: element, range, result
                        
                        # 📊 COLUMN MAPPING (English workflow)
                        element = all_cells[0].get_text(strip=True)
                        recommended_range = all_cells[1].get_text(strip=True) 
                        user_result = all_cells[2].get_text(strip=True)
                        change = all_cells[3].get_text(strip=True) if len(all_cells) > 3 else ""
                        
                        # Skip empty or header-like rows
                        if not element or element.lower() in ['pierwiastek', 'element']:
                            continue
                        
                        debug_print(f"📊 [ICPScraper] ELEMENT: '{element}' | RECOMMENDED: '{recommended_range}' | RESULT: '{user_result}' | CHANGE: '{change}'")
                        
                        # 🧠 SMART ANALYSIS: Check if result is within recommended range
                        status = self._analyze_icp_parameter_status(element, recommended_range, user_result)
                        
                        icp_data["parameters"][element] = {
                            "element": element,
                            "recommended_range": recommended_range, 
                            "user_result": user_result,
                            "change": change,
                            "status": status,
                            "needs_correction": status in ["too_high", "too_low"]
                        }
                    else:
                        # Log incomplete rows
                        if all_cells:
                            cell_contents = [cell.get_text(strip=True) for cell in all_cells]
                            debug_print(f"📊 [ICPScraper] Row {i+1} (incomplete): {cell_contents}")
            else:
                debug_print(f"⚠️ [ICPScraper] No results table found")
            
            # 🔍 LOG: Final extraction summary
            debug_print(f"✅ [ICPScraper] Extracted {len(icp_data['parameters'])} ICP parameters")
            if icp_data["parameters"]:
                param_names = list(icp_data["parameters"].keys())[:5]  # First 5 parameters
                debug_print(f"📋 [ICPScraper] Sample parameters: {param_names}")
            
            return icp_data
            
        except requests.RequestException as e:
            debug_print(f"❌ [ICPScraper] HTTP error fetching ICP data: {e}")
            return {"url": url, "parameters": {}, "status": "http_error", "error": str(e)}
        except Exception as e:
            debug_print(f"❌ [ICPScraper] Error extracting ICP data: {e}")
            return {"url": url, "parameters": {}, "status": "parse_error", "error": str(e)}
    
    def _analyze_icp_parameter_status(self, element: str, recommended_range: str, user_result: str) -> str:
        """🧠 Analyze if ICP parameter result is within recommended range"""
        try:
            # Extract numeric values from strings
            def extract_number(text):
                # Find first number (including decimals)
                match = re.search(r'(\d+\.?\d*)', text.replace(',', '.'))
                return float(match.group(1)) if match else None
            
            # Parse recommended range (e.g., "33 - 38 ppt", "0 - 0.0300 mg/l")
            range_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', recommended_range.replace(',', '.'))
            if range_match:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
                
                # Extract result value
                result_val = extract_number(user_result)
                
                if result_val is not None:
                    debug_print(f"🧠 [ICPScraper] Analysis: {element} = {result_val} (range: {min_val}-{max_val})")
                    
                    if result_val < min_val:
                        return "too_low"
                    elif result_val > max_val:
                        return "too_high"
                    else:
                        return "optimal"
            
            # If can't parse range, check for single value or zero
            if "0 mg/l" in recommended_range or recommended_range.strip() == "0":
                result_val = extract_number(user_result)
                if result_val is not None and result_val > 0:
                    return "too_high"
                elif result_val == 0:
                    return "optimal"
            
            debug_print(f"⚠️ [ICPScraper] Could not analyze: {element} - {recommended_range} vs {user_result}")
            return "unknown"
            
        except Exception as e:
            debug_print(f"❌ [ICPScraper] Error analyzing {element}: {e}")
            return "unknown"
    
    def _extract_icp_metadata(self, soup) -> Dict:
        """🆕 Extract ICP test metadata (test number, aquarium info, date)"""
        metadata = {}
        
        try:
            # 🔍 DEBUG: Print all text content to see structure
            debug_print(f"📋 [ICPScraper] Searching for metadata in page content...")
            
            # Look for test number in page title first
            title = soup.title.string if soup.title else ""
            debug_print(f"📋 [ICPScraper] Page title: '{title}'")
            if "Test wody" in title or "#" in title:
                test_match = re.search(r'#?(\d+)', title)
                if test_match:
                    metadata["test_number"] = test_match.group(1)
                    debug_print(f"📋 [ICPScraper] Found test number in title: {metadata['test_number']}")
            
            # 🎯 IMPROVED: Look for specific patterns in all text elements
            all_text_elements = soup.find_all(['div', 'span', 'strong', 'p'])
            
            for element in all_text_elements:
                text = element.get_text(strip=True)
                
                # Look for "Badanie Woda morska: NUMBER"
                badanie_match = re.search(r'Badanie\s+Woda\s+morska:?\s*(\d+)', text, re.IGNORECASE)
                if badanie_match and not metadata.get("test_number"):
                    metadata["test_number"] = badanie_match.group(1)
                    debug_print(f"📋 [ICPScraper] Found test number: {metadata['test_number']} in text: '{text[:50]}...'")
                
                # Look for "Akwarium (SPS): INFO"
                aquarium_match = re.search(r'Akwarium\s*\([^)]+\):?\s*(.+)', text, re.IGNORECASE)
                if aquarium_match and not metadata.get("aquarium_info"):
                    aquarium_info = aquarium_match.group(1).strip()
                    if aquarium_info and aquarium_info != ":":  # Skip empty results
                        metadata["aquarium_info"] = aquarium_info
                        debug_print(f"📋 [ICPScraper] Found aquarium info: '{metadata['aquarium_info']}' in text: '{text[:50]}...'")
                
                # Look for "Data: DATE"
                date_match = re.search(r'Data:?\s*([\d-]+)', text, re.IGNORECASE)
                if date_match and not metadata.get("test_date"):
                    test_date = date_match.group(1).strip()
                    if test_date and test_date != "-":  # Skip empty results
                        metadata["test_date"] = test_date
                        debug_print(f"📋 [ICPScraper] Found test date: '{metadata['test_date']}' in text: '{text[:50]}...'")
            
            # 🔍 FALLBACK: Look for patterns in the entire page text
            if not metadata.get("test_number") or not metadata.get("aquarium_info") or not metadata.get("test_date"):
                full_text = soup.get_text()
                debug_print(f"📋 [ICPScraper] Fallback search in full page text...")
                
                # Extract test number from anywhere
                if not metadata.get("test_number"):
                    test_matches = re.findall(r'(\d{7})', full_text)
                    if test_matches:
                        metadata["test_number"] = test_matches[0]  # Take first 7-digit number
                        debug_print(f"📋 [ICPScraper] Fallback found test number: {metadata['test_number']}")
                
                # Extract aquarium info more broadly
                if not metadata.get("aquarium_info"):
                    aquarium_matches = re.findall(r'Domowe\s+\d+\s+LPS', full_text, re.IGNORECASE)
                    if aquarium_matches:
                        metadata["aquarium_info"] = aquarium_matches[0]
                        debug_print(f"📋 [ICPScraper] Fallback found aquarium: {metadata['aquarium_info']}")
                
                # Extract date more broadly
                if not metadata.get("test_date"):
                    date_matches = re.findall(r'20\d{2}-\d{2}-\d{2}', full_text)
                    if date_matches:
                        metadata["test_date"] = date_matches[0]
                        debug_print(f"📋 [ICPScraper] Fallback found date: {metadata['test_date']}")
            
            debug_print(f"📋 [ICPScraper] Final extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            debug_print(f"❌ [ICPScraper] Error extracting metadata: {e}")
            return {}

    def format_icp_data_for_llm(self, parameters: Dict, metadata: Dict = None) -> str:
        """📋 Format ICP data for LLM analysis with aquarium info for precise dosing calculations"""
        lines = []
        
        # 🎯 AQUARIUM INFO for dosing calculations
        if metadata:
            aquarium_info = metadata.get("aquarium_info", "")
            test_date = metadata.get("test_date", "")
            
            # Extract volume from aquarium_info (e.g., "Domowe 1150 LPS")
            volume_match = re.search(r'(\d+)', aquarium_info) if aquarium_info else None
            volume = volume_match.group(1) if volume_match else "unknown"
            
            lines.append(f"AQUARIUM: {volume}L | DATE: {test_date}")
            lines.append("")
        
        lines.append("ELEMENT | RECOMMENDED | RESULT | CHANGE | STATUS")
        lines.append("-" * 60)
        
        for param_name, data in parameters.items():
            element = data.get("element", param_name)
            
            # Format element name: "PO4Fosforany" → "PO4 Fosforany"
            match = re.match(r'^([A-Za-z0-9]+)([A-Z][a-z]+.*)$', element)
            if match:
                symbol = match.group(1)
                name = match.group(2)
                element_formatted = f"{symbol} {name}"
            else:
                element_formatted = element
            
            recommended = data.get("recommended_range", "")
            user_result = data.get("user_result", "")
            change = data.get("change", "")
            status = data.get("status", "unknown")
            
            status_icon = {
                "too_high": "⬆️ HIGH",
                "too_low": "⬇️ LOW", 
                "optimal": "✅ OK",
                "unknown": "❓"
            }.get(status, status)
            
            line = f"{element_formatted} | {recommended} | {user_result} | {change} | {status_icon}"
            lines.append(line)
        
        return "\n".join(lines)

    def extract_structured_recommendations(self, raw_data: str, metadata: Dict = None) -> Dict:
        """📋 Extract structured recommendations using GPT-4o-mini from raw ICP page data"""
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Create prompt for GPT-4o-mini to analyze raw ICP data
            prompt = f"""
You are an expert marine aquarium analyst. Analyze the RAW ICP test results page content and extract structured recommendations with products and dosages.

RAW ICP PAGE DATA:
{raw_data}

METADATA (if available):
{json.dumps(metadata, indent=2, ensure_ascii=False) if metadata else "No metadata available"}

Analyze the complete page content and extract detailed information as JSON with these exact fields:

{{
    "recommendations": {{
        "increase": [
            {{
                "parameter": "element name",
                "current_value": "current measured value",
                "target_range": "recommended range",
                "suggested_products": ["product name 1", "product name 2"],
                "dosage": "dosage instruction if available"
            }}
        ],
        "decrease": [
            {{
                "parameter": "element name", 
                "current_value": "current measured value",
                "target_range": "recommended range",
                "suggested_products": ["product name 1"],
                "dosage": "dosage instruction if available"
            }}
        ],
        "maintain": [
            {{
                "parameter": "element name",
                "current_value": "current measured value", 
                "target_range": "recommended range",
                "suggested_products": ["maintenance product"],
                "dosage": "maintenance dosage"
            }}
        ]
    }},
    "aquarium_info": {{
        "volume": "tank volume in liters",
        "type": "reef type (SPS/LPS/Mixed)"
    }},
    "priority_actions": [
        "most critical correction needed",
        "second priority action"
    ]
}}

Focus on:
- Only parameters that need correction (too high/too low)
- Generic product names (like "Calcium supplement", "Phosphate remover") 
- Practical dosage instructions
- Priority order of corrections

Return ONLY the JSON object, no explanations."""

            # Call GPT-4o-mini
            response = client.chat.completions.create(
                model=OPENAI_MODEL2,  # gpt-4o-mini
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            structured_data = json.loads(response.choices[0].message.content)
            debug_print(f"🤖 [ICPScraper] Structured recommendations extracted successfully")
            
            return structured_data
            
        except Exception as e:
            debug_print(f"❌ [ICPScraper] Error extracting structured recommendations: {e}")
            return {
                "recommendations": {"increase": [], "decrease": [], "maintain": []},
                "aquarium_info": {},
                "priority_actions": []
            }

    def extract_icp_recommendations_text(self, raw_data: str) -> List[str]:
        """📋 Extract individual recommendation sentences for each element from ICP raw data"""
        try:
            recommendations = []
            
            # 🎯 Lista pierwiastków jako separatorów
            elements = [
                "Al Glin", "As Arsen", "B Bor", "Ba Bar", "Be Beryl", "Cd Kadm", 
                "Co Kobalt", "Cr Chrom", "Cu Miedź", "Fe Żelazo", "Hg Rtęć", 
                "I Jod", "La Lantan", "Li Lit", "Mn Mangan", "Mo Molibden", 
                "Ni Nikiel", "Pb Ołów", "Sb Antymon", "Sc Skand", "Se Selen", 
                "Si Krzem", "Sn Cyna", "Ti Tytan", "V Wanad", "W Wolfram", 
                "Zn Cynk", "P Fosfor", "Na Sód", "Ca Wapń", "Mg Magnez", 
                "K Potas", "Br Brom", "Sr Stront", "S Siarka", "NO3 NO3",
                "PO4 Fosforany", "KH KH", "Zasolenie", "ALL RIGHTS RESERVED"
            ]
            
            # Escape special characters in element names for regex
            escaped_elements = [re.escape(elem) for elem in elements]
            elements_pattern = '|'.join(escaped_elements)
            
            # 🎯 Pattern that finds "Zalecenia" and stops at next element or end
            pattern = rf'Zalecenia(.*?)(?=({elements_pattern})|$)'
            
            matches = re.findall(pattern, raw_data, re.IGNORECASE | re.DOTALL)
            debug_print(f"🔬 [ICPScraper] Found {len(matches)} potential recommendation matches")
            
            for i, match_tuple in enumerate(matches):
                # match_tuple is (recommendation_text, element_name) due to groups in regex
                recommendation_text = match_tuple[0] if isinstance(match_tuple, tuple) else match_tuple
                
                # Clean up the text
                clean_text = re.sub(r'\s+', ' ', recommendation_text).strip()
                debug_print(f"🔬 [ICPScraper] Match {i+1} length: {len(clean_text)}")
                debug_print(f"🔬 [ICPScraper] Match {i+1} preview: {clean_text[:100]}...")
                
                # Filter: must be substantial text with key dosing terms
                if (len(clean_text) > 20 and 
                    ('Uwaga!' in clean_text or 'dawka' in clean_text or 'stosując' in clean_text or 
                     'podmień' in clean_text or 'użyj' in clean_text or 'zastosuj' in clean_text)):
                    
                    recommendations.append(f"🔬 ZALECENIE: {clean_text}")
                    debug_print(f"✅ [ICPScraper] Added recommendation {i+1}")
                else:
                    debug_print(f"❌ [ICPScraper] Skipped recommendation {i+1} (too short or no key terms)")
            
            debug_print(f"🔬 [ICPScraper] Final recommendations count: {len(recommendations)}")
            return recommendations
            
        except Exception as e:
            debug_print(f"❌ [ICPScraper] Error extracting recommendations: {e}")
            return []


# 🚀 UTILITY FUNCTIONS for backward compatibility
def extract_icp_data_from_url(url: str) -> Dict:
    """Convenience function for backward compatibility"""
    scraper = ICPScraper()
    return scraper.extract_icp_data_from_url(url)

def format_icp_data_for_llm(parameters: Dict, metadata: Dict = None) -> str:
    """Convenience function for backward compatibility"""
    scraper = ICPScraper()
    return scraper.format_icp_data_for_llm(parameters, metadata) 