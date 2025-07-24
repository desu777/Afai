"""
ICP Scraper Module - PDF analysis for ICP test results
Uses configured provider (Vertex AI) with OpenRouter fallback
"""
import re
import base64
from typing import Dict, List, Optional
from config import debug_print, TEST_ENV, ICP_API, ICP_MODEL, ICP_TEMPERATURE
import json
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader
import tempfile
import os

# Import factory for primary provider
from llm_client_factory import create_icp_analysis_client

class ICPScraper:
    """ICP PDF processor for Aquaforest Lab ICP test results"""
    
    def __init__(self):
        # Use factory for client creation - it handles fallback internally
        self.client, self.model_name = create_icp_analysis_client()
        
        # Keep fallback LLM for compatibility with existing code
        self.fallback_llm = ChatOpenAI(
            api_key=ICP_API,
            model=ICP_MODEL,
            base_url="https://openrouter.ai/api/v1",
            temperature=ICP_TEMPERATURE
        )
        
        if TEST_ENV:
            debug_print(f"[LAB] ICP client ready: {self.model_name}")
    
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM using configured client with temperature"""
        try:
            if TEST_ENV:
                debug_print(f"[>] Using client: {self.model_name}")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=ICP_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            debug_print(f"[X] Client failed: {e}")
            debug_print(f"[RTY] Using legacy fallback...")
            
            # Final fallback to legacy LLM
            response = self.fallback_llm.invoke(prompt)
            return response.content.strip()



    
    def robust_json_parse(self, text: str) -> dict:
        """Robust JSON parsing method copied from business_reasoner.llm_analyzer"""
        try:
            # Direct parse
            return json.loads(text)
        except Exception:
            # Strip code fences ```json ... ``` or ``` ... ```
            if "```" in text:
                # Keep everything between the first pair of fences that contains '{'
                blocks = text.split("```")
                for block in blocks:
                    if "{" in block and "}" in block:
                        candidate = block[block.find("{"): block.rfind("}")+1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            continue
            # Fallback: extract substring between first '{' and last '}'
            if "{" in text and "}" in text:
                candidate = text[text.find("{") : text.rfind("}")+1]
                try:
                    return json.loads(candidate)
                except Exception:
                    pass
            # Give up
            raise ValueError("Unable to parse JSON from LLM output")
    
    def _parse_json_response(self, response_content: str, source_type: str) -> dict:
        """Enhanced JSON parsing using robust_json_parse from business_reasoner"""
        try:
            result = self.robust_json_parse(response_content)
            debug_print(f"[OK] Successfully parsed {source_type} JSON")
            return result
        except Exception as e:
            debug_print(f"[X] {source_type} JSON parsing failed: {e}")
            debug_print(f"[?] Raw response: {response_content[:200]}")
            return None



    
    def _detect_aquarium_type(self, parameters: Dict) -> str:
        """Detect aquarium type based on parameter values"""
        try:
            # Look for key saltwater indicators
            ca_value = None
            mg_value = None
            
            for param_name, param_data in parameters.items():
                element = param_data.get("element", "").lower()
                user_result = param_data.get("user_result", "")
                
                # Extract numeric value
                def extract_number(text):
                    match = re.search(r'(\d+\.?\d*)', text.replace(',', '.'))
                    return float(match.group(1)) if match else None
                
                # Check for Calcium
                if "calcium" in element or "ca" in element:
                    ca_value = extract_number(user_result)
                
                # Check for Magnesium  
                if "magnesium" in element or "mg" in element:
                    mg_value = extract_number(user_result)
            
            # Saltwater detection logic
            if ca_value and mg_value:
                if ca_value > 300 and mg_value > 1000:
                    return "saltwater"
                else:
                    return "freshwater"
            elif ca_value and ca_value > 300:
                return "saltwater"  # High calcium usually indicates saltwater
            elif mg_value and mg_value > 1000:
                return "saltwater"  # High magnesium usually indicates saltwater
            
            # Default fallback
            return "unknown"
            
        except Exception as e:
            debug_print(f"[X] Error detecting aquarium type: {e}")
            return "unknown"
    
    def _analyze_icp_parameter_status(self, element: str, recommended_range: str, user_result: str) -> str:
        """Analyze if ICP parameter result is within recommended range"""
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
                    debug_print(f"[THK] Analysis: {element} = {result_val} (range: {min_val}-{max_val})")
                    
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
            
            debug_print(f"[!] Could not analyze: {element} - {recommended_range} vs {user_result}")
            return "unknown"
            
        except Exception as e:
            debug_print(f"[X] Error analyzing {element}: {e}")
            return "unknown"
    
    
    def process_pdf_icp_data(self, pdf_content: bytes, filename: str = "icp_results.pdf") -> Dict:
        """Process PDF ICP results using LangChain PyMuPDF"""
        try:
            debug_print(f"[DOC] Processing PDF: {filename}")
            
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
                debug_print(f"[LST] Extracted {len(full_text)} chars from PDF")
                
                # DEBUG: Log extracted PDF content for troubleshooting
                if TEST_ENV:
                    debug_print(f"[DOC] Content preview: {full_text[:300]}")
                    if len(full_text) > 300:
                        debug_print(f"[DOC] Content end: {full_text[-100:]}")
                
                # Use AI as Water Chemistry Diagnostician for PDF
                pdf_analysis_prompt = f"""
You are an expert marine water chemistry diagnostician for reef aquariums. Analyze the ICP test results from the PDF and create a professional diagnosis.

PDF Content: {full_text}

TASKS:
1. Extract ALL chemical parameters (Ca, Mg, KH, NO3, PO4, all trace elements like I, Fe, Zn, etc.)
2. Determine status of each parameter for reef aquarium: optimal/too_high/too_low
3. Create action list required for Business Reasoner
4. Return ONLY valid JSON - no explanations, no markdown

JSON FORMAT (extract ALL found parameters):
{{
    "metadata": {{
        "test_number": "ICP test number",
        "aquarium_info": "aquarium information",
        "test_date": "test date", 
        "aquarium_volume": "volume if provided",
        "aquarium_type": "saltwater/freshwater (detect based on parameters - if Ca>300mg/l and Mg>1000mg/l then saltwater, else freshwater)"
    }},
    "parameters": {{
        "Calcium": {{
            "element": "Calcium (Ca)",
            "recommended_range": "420-460 mg/l",
            "user_result": "measured value",
            "change": "change from previous test",
            "status": "optimal/too_high/too_low",
            "action_needed": "none/increase/decrease"
        }},
        "Iodine": {{
            "element": "Iodine (I)",
            "recommended_range": "0.055-0.07 mg/l", 
            "user_result": "measured value",
            "change": "change from previous test",
            "status": "optimal/too_high/too_low",
            "action_needed": "none/increase/decrease"
        }}
    }},
    "diagnosis": {{
        "optimal_count": "number of OK parameters",
        "problems_count": "number of parameters to fix",
        "priority_actions": [
            "Reduce nitrates (12→5 mg/l)",
            "Increase calcium (350→430 mg/l)"
        ]
    }}
}}

Extract ALL parameters from PDF. Return only JSON.
"""
                
                response = self._invoke_llm(pdf_analysis_prompt)
                
                # DEBUG: Log raw AI response for troubleshooting
                if TEST_ENV:
                    debug_print(f"[AI] Response length: {len(response)} chars")
                    debug_print(f"[AI] Response preview: {response[:200]}")
                    if len(response) > 200:
                        debug_print(f"[AI] Response end: {response[-100:]}")
                
                # Try to parse JSON with enhanced handling
                structured_data = self._parse_json_response(response, "PDF")
                if structured_data is None:
                    return {"source": f"PDF: {filename}", "parameters": {}, "status": "json_parse_error", "error": f"Could not parse JSON from response: {response[:200]}"}
                
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
                
                # Fallback aquarium type detection if AI didn't set it properly
                metadata = structured_data.get("metadata", {})
                if not metadata.get("aquarium_type") or metadata.get("aquarium_type") == "unknown":
                    metadata["aquarium_type"] = self._detect_aquarium_type(structured_data.get("parameters", {}))
                    debug_print(f"[?] Auto-detected aquarium type: {metadata['aquarium_type']}")
                
                icp_data = {
                    "source": f"PDF: {filename}",
                    "parameters": structured_data.get("parameters", {}),
                    "metadata": structured_data.get("metadata", {}),
                    "raw_data": full_text,
                    "status": "success",
                    "debug_info": {
                        "processing_method": "pymupdf",
                        "llm_analysis": self.model_name,
                        "provider": "configured"
                    }
                }
                
                debug_print(f"[OK] Processed PDF with {len(icp_data['parameters'])} parameters")
                return icp_data
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            debug_print(f"[X] Error processing PDF: {e}")
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
    

    def format_icp_data_for_llm(self, parameters: Dict, metadata: Dict = None, diagnosis: Dict = None) -> str:
        """Format ICP data as water diagnostician report for BusinessReasoner"""
        lines = []
        
        # AQUARIUM INFO
        if metadata:
            aquarium_info = metadata.get("aquarium_info", "")
            test_date = metadata.get("test_date", "")
            test_number = metadata.get("test_number", "")
            
            # Extract volume from aquarium_info (e.g., "Domowe 1150 LPS")
            volume_match = re.search(r'(\d+)', aquarium_info) if aquarium_info else None
            volume = volume_match.group(1) if volume_match else "unknown"
            
            lines.append(f"[LAB] DIAGNOZA ICP #{test_number}")
            lines.append(f"[DATE] Data: {test_date} | [HOME] Akwarium: {volume}L")
            lines.append("")
        
        # SUMMARY STATISTICS
        if diagnosis:
            optimal_count = diagnosis.get("optimal_count", 0)
            problems_count = diagnosis.get("problems_count", 0)
            lines.append(f"[STATS] PODSUMOWANIE: [OK] {optimal_count} OK | [!] {problems_count} problemów")
            lines.append("")
        
        # CATEGORIZE PARAMETERS
        optimal_params = []
        too_high_params = []
        too_low_params = []
        
        for param_name, data in parameters.items():
            element = data.get("element", param_name)
            user_result = data.get("user_result", "")
            recommended = data.get("recommended_range", "")
            status = data.get("status", "unknown")
            action_needed = data.get("action_needed", "none")
            
            # Format element name: "PO4Fosforany" → "PO4"
            if element:
                match = re.match(r'^([A-Za-z0-9]+)', element)
                element_short = match.group(1) if match else element
            else:
                element_short = param_name
            
            param_info = f"{element_short} ({user_result} | cel: {recommended})"
            
            if status == "optimal":
                optimal_params.append(param_info)
            elif status == "too_high" and action_needed == "decrease":
                too_high_params.append(param_info)
            elif status == "too_low" and action_needed == "increase":
                too_low_params.append(param_info)
        
        # OPTIMAL PARAMETERS
        if optimal_params:
            lines.append("[OK] PARAMETRY OPTYMALNE:")
            for param in optimal_params:
                lines.append(f"   • {param}")
            lines.append("")
        
        # PARAMETERS TO FIX
        if too_high_params:
            lines.append("[X] ZA WYSOKIE (wymagają obniżenia):")
            for param in too_high_params:
                lines.append(f"   • {param}")
            lines.append("")
        
        if too_low_params:
            lines.append("[!] ZA NISKIE (wymagają podwyższenia):")
            for param in too_low_params:
                lines.append(f"   • {param}")
            lines.append("")
        
        # PRODUCT SELECTION INSTRUCTIONS FOR BUSINESS REASONER
        lines.append("[SHOP] PRODUKTY DO DOBRANIA:")
        
        if too_high_params:
            for param in too_high_params:
                element_name = param.split(" (")[0]
                if "NO3" in element_name or "Azot" in element_name:
                    lines.append(f"[-] Obniżyć azotany: Dobierz wszystkie produkty na obniżenie azotanów!")
                elif "PO4" in element_name or "Fosfor" in element_name:
                    lines.append(f"[-] Obniżyć fosforany: Dobierz wszystkie produkty na obniżenie fosforanów!")
                else:
                    lines.append(f"[-] Obniżyć {element_name}: Dobierz produkty na obniżenie {element_name}!")
        
        if too_low_params:
            for param in too_low_params:
                element_name = param.split(" (")[0]
                if "Ca" in element_name or "Wapń" in element_name:
                    lines.append(f"[+] Podwyższyć wapń: Dobierz wszystkie produkty na podwyższenie wapnia!")
                elif "Mg" in element_name or "Magnez" in element_name:
                    lines.append(f"[+] Podwyższyć magnez: Dobierz wszystkie produkty na podwyższenie magnezu!")
                elif "KH" in element_name or "Alkalinity" in element_name:
                    lines.append(f"[+] Podwyższyć KH: Dobierz wszystkie produkty na podwyższenie alkaliczności!")
                else:
                    lines.append(f"[+] Podwyższyć {element_name}: Dobierz produkty na podwyższenie {element_name}!")
        
        if not too_high_params and not too_low_params:
            lines.append("[OK] Wszystkie parametry w normie - dobierz produkty do utrzymania stabilności!")
        
        return "\n".join(lines)





def format_icp_data_for_llm(parameters: Dict, metadata: Dict = None) -> str:
    """Convenience function for backward compatibility"""
    scraper = ICPScraper()
    return scraper.format_icp_data_for_llm(parameters, metadata) 