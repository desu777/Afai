"""
LLM Analyzer Module
LLM analysis and JSON parsing extracted from business_reasoner.py
Uses configured provider (Vertex AI) with OpenRouter fallback
"""
import json
import time  # For LLM performance monitoring
from typing import Dict
from models import ConversationState
from config import TEST_ENV, debug_print, BUSINESS_REASONER_TEMPERATURE
from prompts import load_prompt_template
from prompt_saver import log_prompt_if_enabled
from .prompt_formatter import PromptDataFormatter

class LLMAnalyzer:
    def __init__(self, client, model_name, data_loader):
        self.client = client
        self.model_name = model_name
        self.data_loader = data_loader
        self.formatter = PromptDataFormatter()

    def create_comprehensive_llm_prompt(self, state: ConversationState) -> str:
        """Create comprehensive prompt using external template"""
        
        # Format conversation history
        chat_history = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages])
        
        # Format data using XML-structured formatters instead of JSON dumps
        formatted_products = self.formatter.format_products_catalog(
            self.data_loader.products_knowledge
        )
        
        formatted_competitors = self.formatter.format_competitors_map(
            self.data_loader.competitors_data
        )
        
        # Keep smaller data as JSON for now (can be optimized later)
        icp_parameter_mapping = json.dumps(
            self.data_loader.product_groups_data.get("icp_corrections", {}).get("parameter_map", {}), 
            indent=1, 
            ensure_ascii=False
        )
        scenarios_data = json.dumps(self.data_loader.scenarios_data, indent=1, ensure_ascii=False)
        use_cases_data = json.dumps(self.data_loader.use_cases_data, indent=1, ensure_ascii=False)
        product_groups_data = json.dumps(self.data_loader.product_groups_data, indent=1, ensure_ascii=False)
        
        # Try to load prompt from external template
        prompt = load_prompt_template(
            "business_reasoning",
            user_query=state['user_query'],
            detected_language=state.get('detected_language', 'en'),
            intent=state.get('intent', 'unknown'),
            chat_history=chat_history if chat_history else "No previous conversation context",
            icp_parameter_mapping=icp_parameter_mapping,
            products_knowledge=formatted_products,
            competitors_data=formatted_competitors,
            scenarios_data=scenarios_data,
            use_cases_data=use_cases_data,
            product_groups_data=product_groups_data
        )
        
        # Fallback if template loading fails
        if not prompt:
            debug_print("[!] Using fallback prompt with XML formatting")
            prompt = f"""You are an Aquaforest business intelligence specialist.

USER QUERY: {state['user_query']}
DETECTED LANGUAGE: {state.get('detected_language', 'en')}
INTENT: {state.get('intent', 'unknown')}

CONVERSATION HISTORY:
{chat_history if chat_history else "No previous conversation"}

PRODUCT CATALOG:
{formatted_products}

COMPETITOR MAPPINGS:
{formatted_competitors}

INSTRUCTIONS:
1. Analyze the user query and provide relevant product recommendations
2. If competitors are mentioned, acknowledge them and redirect to AF alternatives
3. Return response in JSON format with: recommended_products, reasoning, category_detected
"""

        return prompt
    
    def robust_json_parse(self, text: str) -> Dict:
        """Attempt to extract and parse a JSON object from arbitrary LLM output."""
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
    
    def analyze_with_full_llm(self, state: ConversationState) -> Dict:
        """Pure LLM analysis using all mapping data with configured temperature"""
        
        try:
            # Create comprehensive prompt with all mapping data
            prompt = self.create_comprehensive_llm_prompt(state)
            
            # Measure LLM response time
            start_time = time.time()
            
            # Call configured client with temperature parameter
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=BUSINESS_REASONER_TEMPERATURE,
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            # Calculate response time and log performance
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Log performance to console if TEST_ENV enabled
            if TEST_ENV:
                print(f"[LLM_PERF] business_reasoner: {response_time_ms:.2f}ms (model: {self.model_name})")
            
            # Update prompt file with response time if SAVE_PROMPT enabled
            from config import SAVE_PROMPT
            if SAVE_PROMPT:
                log_prompt_if_enabled("business_reasoner", prompt, state, self.model_name, BUSINESS_REASONER_TEMPERATURE, response_time_ms)
            
            # Parse the JSON response
            raw_content = response.choices[0].message.content
            try:
                decision_data = json.loads(raw_content)
            except json.JSONDecodeError:
                # Fallback robust parsing for models that add prose or code fences
                decision_data = self.robust_json_parse(raw_content)
            
            debug_print(f"[AI] Analysis complete")
            
            if TEST_ENV:
                print(f"[BRAIN] LLM Summary:")
                print(f"   - Business: {decision_data.get('business_interpretation', 'N/A')[:50]}...")
                print(f"   - Scenario: {decision_data.get('detected_scenario', 'null')}")
                print(f"   - Use case: {decision_data.get('detected_use_case', 'null')}")
                print(f"   - Competitors: {decision_data.get('detected_competitors', [])}")
                
                reasoning = decision_data.get('reasoning_steps', {})
                print(f"   - Stage 1: {reasoning.get('stage_1_products', 'N/A')[:30]}...")
                print(f"   - Stage 2: {reasoning.get('stage_2_products', 'N/A')[:30]}...")
                
                print(f"   - Priority: {len(decision_data.get('priority_products', []))}")
                print(f"   - Strategy: {decision_data.get('response_strategy', 'direct')}")
                print(f"   - Confidence: {decision_data.get('confidence_level', 0.0)}")
            
            return decision_data
            
        except json.JSONDecodeError as e:
            debug_print(f"[X] JSON parse error: {e}")
            return {}
        except Exception as e:
            debug_print(f"[X] LLM analysis error: {e}")
            return {}