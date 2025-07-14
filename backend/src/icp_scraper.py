"""
ICP Scraper Module - Enhanced web scraping for Aquaforest Lab ICP test results
Uses LangChain Hyperbrowser for advanced scraping + Gemini 2.0 Flash analysis
"""
import re
import base64
from typing import Dict, List
from config import debug_print, TEST_ENV, FOLLOW_UP_API, FOLLOW_UP_MODEL, HYPERBROWSER_API_KEY
import json
from langchain_openai import ChatOpenAI
from langchain_hyperbrowser import HyperbrowserScrapeTool
from langchain_community.document_loaders import PyMuPDFLoader
import tempfile
import os

class ICPScraper:
    """Enhanced web scraper for Aquaforest Lab ICP test results with LangChain"""
    
    def __init__(self):
        # Use FOLLOW_UP variables (Gemini 2.0 Flash) for ICP analysis
        self.llm = ChatOpenAI(
            api_key=FOLLOW_UP_API,
            model=FOLLOW_UP_MODEL,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.1
        )
        
        # Initialize LangChain tools
        self.scraper = HyperbrowserScrapeTool(api_key=HYPERBROWSER_API_KEY)
        
        if TEST_ENV:
            debug_print(f"🔬 [ICPScraper] Initialized with LangChain + model: {FOLLOW_UP_MODEL}")
    
    def extract_icp_data_from_url(self, url: str) -> Dict:
        """🆕 Extract ICP test data from Aquaforest Lab URL using LangChain Hyperbrowser"""
        try:
            debug_print(f"🌐 [ICPScraper] Fetching ICP data with Hyperbrowser from: {url}")
            
            # Use Hyperbrowser for advanced web scraping
            scraped_content = self.scraper.run(url)
            debug_print(f"📊 [ICPScraper] Scraped content length: {len(scraped_content)} chars")
            
            # Use Gemini 2.0 Flash to analyze and extract structured data
            extraction_prompt = f"""
Analyze this ICP test results page and extract structured data.

URL: {url}
Content: {scraped_content}

Extract the following information as JSON:
{{
    "metadata": {{
        "test_number": "test ID number",
        "aquarium_info": "aquarium details",
        "test_date": "test date",
        "aquarium_volume": "volume in liters if mentioned"
    }},
    "parameters": {{
        "ElementName": {{
            "element": "element name",
            "recommended_range": "recommended range",
            "user_result": "measured value",
            "change": "change value",
            "status": "too_high/too_low/optimal/unknown"
        }}
    }}
}}

Focus on extracting all chemical parameters with their values and status.
Return ONLY valid JSON, no explanations.
"""
            
            response = self.llm.invoke(extraction_prompt)
            structured_data = json.loads(response.content)
            
            # Enhance with our analysis
            for param_name, param_data in structured_data.get("parameters", {}).items():
                if param_data.get("status") == "unknown":
                    # Use our analysis method as fallback
                    status = self._analyze_icp_parameter_status(
                        param_data.get("element", ""),
                        param_data.get("recommended_range", ""),
                        param_data.get("user_result", "")
                    )
                    param_data["status"] = status
                
                param_data["needs_correction"] = param_data["status"] in ["too_high", "too_low"]
            
            icp_data = {
                "url": url,
                "parameters": structured_data.get("parameters", {}),
                "metadata": structured_data.get("metadata", {}),
                "raw_data": scraped_content,
                "status": "success",
                "debug_info": {
                    "scraping_method": "hyperbrowser",
                    "llm_analysis": "gemini-2.0-flash"
                }
            }
            
            debug_print(f"✅ [ICPScraper] Extracted {len(icp_data['parameters'])} ICP parameters with LangChain")
            return icp_data
            
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
    
    def enhance_query_with_icp_data(self, user_query: str, icp_url: str) -> str:
        """🆕 Enhanced query with ICP data analysis - MISSING METHOD FIXED"""
        try:
            debug_print(f"🔗 [ICPScraper] Enhancing query with ICP data from: {icp_url}")
            
            # Extract ICP data using new LangChain method
            icp_data = self.extract_icp_data_from_url(icp_url)
            
            if icp_data["status"] != "success":
                debug_print(f"❌ [ICPScraper] Failed to extract ICP data: {icp_data.get('error', 'Unknown error')}")
                return user_query
            
            # Format data for LLM analysis
            formatted_data = self.format_icp_data_for_llm(icp_data["parameters"], icp_data["metadata"])
            
            # Enhanced query with structured ICP analysis
            enhanced_query = f"""{user_query}

🔬 ICP TEST ANALYSIS:
{formatted_data}

🎯 AQUARIUM INFO:
{icp_data["metadata"]}

📊 PARAMETERS NEEDING CORRECTION:
{self._format_corrections_needed(icp_data["parameters"])}"""
            
            debug_print(f"✅ [ICPScraper] Enhanced query with {len(icp_data['parameters'])} parameters")
            return enhanced_query
            
        except Exception as e:
            debug_print(f"❌ [ICPScraper] Error enhancing query: {e}")
            return user_query
    
    def process_pdf_icp_data(self, pdf_content: bytes, filename: str = "icp_results.pdf") -> Dict:
        """🆕 Process PDF ICP results using LangChain PyMuPDF"""
        try:
            debug_print(f"📄 [ICPScraper] Processing PDF: {filename}")
            
            # Save PDF to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Use PyMuPDF loader to extract text
                loader = PyMuPDFLoader(tmp_file_path)
                docs = loader.load()
                
                # Combine all document pages
                full_text = "\n".join([doc.page_content for doc in docs])
                debug_print(f"📋 [ICPScraper] Extracted {len(full_text)} chars from PDF")
                
                # Use Gemini 2.0 Flash to analyze PDF content
                pdf_analysis_prompt = f"""
Analyze this PDF content containing ICP test results and extract structured data.

PDF Content: {full_text}

Extract the following information as JSON:
{{
    "metadata": {{
        "test_number": "test ID number",
        "aquarium_info": "aquarium details",
        "test_date": "test date",
        "aquarium_volume": "volume in liters if mentioned"
    }},
    "parameters": {{
        "ElementName": {{
            "element": "element name",
            "recommended_range": "recommended range",
            "user_result": "measured value",
            "change": "change value",
            "status": "too_high/too_low/optimal/unknown"
        }}
    }}
}}

Focus on extracting all chemical parameters with their values and status.
Return ONLY valid JSON, no explanations.
"""
                
                response = self.llm.invoke(pdf_analysis_prompt)
                structured_data = json.loads(response.content)
                
                # Enhance with our analysis
                for param_name, param_data in structured_data.get("parameters", {}).items():
                    if param_data.get("status") == "unknown":
                        status = self._analyze_icp_parameter_status(
                            param_data.get("element", ""),
                            param_data.get("recommended_range", ""),
                            param_data.get("user_result", "")
                        )
                        param_data["status"] = status
                    
                    param_data["needs_correction"] = param_data["status"] in ["too_high", "too_low"]
                
                icp_data = {
                    "source": f"PDF: {filename}",
                    "parameters": structured_data.get("parameters", {}),
                    "metadata": structured_data.get("metadata", {}),
                    "raw_data": full_text,
                    "status": "success",
                    "debug_info": {
                        "processing_method": "pymupdf",
                        "llm_analysis": "gemini-2.0-flash"
                    }
                }
                
                debug_print(f"✅ [ICPScraper] Processed PDF with {len(icp_data['parameters'])} parameters")
                return icp_data
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            debug_print(f"❌ [ICPScraper] Error processing PDF: {e}")
            return {"source": f"PDF: {filename}", "parameters": {}, "status": "parse_error", "error": str(e)}
    
    def _format_corrections_needed(self, parameters: Dict) -> str:
        """Format parameters that need correction for enhanced query"""
        corrections = []
        for param_name, param_data in parameters.items():
            if param_data.get("needs_correction"):
                status = param_data["status"]
                element = param_data["element"]
                current = param_data["user_result"]
                target = param_data["recommended_range"]
                
                corrections.append(f"• {element}: {current} ({status.upper()}) → Target: {target}")
        
        return "\n".join(corrections) if corrections else "All parameters within optimal range"
    
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
            # Use configured client for ICP analysis
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

            # Call configured model
            response = self.client.chat.completions.create(
                model=self.model_name,
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