"""
LLM Analyzer Module
LLM analysis and JSON parsing extracted from business_reasoner.py
"""
import json
from typing import Dict
from models import ConversationState
from config import TEST_ENV, debug_print
from prompts import load_prompt_template

class LLMAnalyzer:
    def __init__(self, client, model_name, data_loader):
        self.client = client
        self.model_name = model_name
        self.data_loader = data_loader

    def create_comprehensive_llm_prompt(self, state: ConversationState) -> str:
        """Create comprehensive prompt using external template"""
        
        # Format conversation history
        chat_history = ""
        if state.get("chat_history"):
            recent_messages = state["chat_history"][-4:]
            chat_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages])
        
        # Try to load prompt from external template
        prompt = load_prompt_template(
            "business_reasoning",
            user_query=state['user_query'],
            detected_language=state.get('detected_language', 'en'),
            intent=state.get('intent', 'unknown'),
            chat_history=chat_history if chat_history else "No previous conversation context",
            icp_parameter_mapping=json.dumps(self.data_loader.product_groups_data.get("icp_corrections", {}).get("parameter_map", {}), indent=1, ensure_ascii=False),
            products_knowledge=json.dumps(self.data_loader.products_knowledge, indent=1, ensure_ascii=False),
            competitors_data=json.dumps(self.data_loader.competitors_data, indent=1, ensure_ascii=False),
            scenarios_data=json.dumps(self.data_loader.scenarios_data, indent=1, ensure_ascii=False),
            use_cases_data=json.dumps(self.data_loader.use_cases_data, indent=1, ensure_ascii=False),
            product_groups_data=json.dumps(self.data_loader.product_groups_data, indent=1, ensure_ascii=False)
        )
        
        # Fallback if template loading fails
        if not prompt:
            debug_print("⚠️ [BusinessReasoner] Using fallback hardcoded prompt")
            prompt = f"""
You are an Aquaforest business intelligence specialist.
Analyze this query: "{state['user_query']}"
Return JSON with product recommendations and business analysis.
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
        """Pure LLM analysis using all mapping data with GPT-4.1-mini"""
        
        try:
            # Create comprehensive prompt with all mapping data
            prompt = self.create_comprehensive_llm_prompt(state)
            
            # Call GPT-4.1-mini with JSON mode (more reliable than structured outputs)
            response = self.client.chat.completions.create(
                model=self.model_name,  # OpenRouter per-node model
                temperature=0.1,  # Low for consistency
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"}  # JSON mode
            )
            
            # Parse the JSON response
            raw_content = response.choices[0].message.content
            try:
                decision_data = json.loads(raw_content)
            except json.JSONDecodeError:
                # Fallback robust parsing for models that add prose or code fences
                decision_data = self.robust_json_parse(raw_content)
            
            debug_print(f"🤖 [BusinessReasoner] Full LLM analysis completed")
            
            if TEST_ENV:
                print(f"🧠 [DEBUG BusinessReasoner] Full LLM Response Summary:")
                print(f"   - Business interpretation: {decision_data.get('business_interpretation', 'N/A')[:100]}...")
                print(f"   - Detected scenario: {decision_data.get('detected_scenario', 'null')}")
                print(f"   - Detected use case: {decision_data.get('detected_use_case', 'null')}")
                print(f"   - Detected competitors: {decision_data.get('detected_competitors', [])}")
                
                reasoning = decision_data.get('reasoning_steps', {})
                print(f"   - Stage 1 products (direct): {reasoning.get('stage_1_products', 'N/A')[:50]}...")
                print(f"   - Stage 2 products (mapping): {reasoning.get('stage_2_products', 'N/A')[:50]}...")
                
                print(f"   - Total priority products: {len(decision_data.get('priority_products', []))}")
                print(f"   - Priority products: {decision_data.get('priority_products', [])}")
                print(f"   - Response strategy: {decision_data.get('response_strategy', 'direct')}")
                print(f"   - Confidence level: {decision_data.get('confidence_level', 0.0)}")
            
            return decision_data
            
        except json.JSONDecodeError as e:
            debug_print(f"❌ [BusinessReasoner] JSON parsing error: {e}")
            return {}
        except Exception as e:
            debug_print(f"❌ [BusinessReasoner] Full LLM analysis error: {e}")
            return {}