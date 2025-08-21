"""
Follow-up Handler Module
Follow-up question processing extracted from response_formatter.py
"""
import json
from models import ConversationState
from config import TEST_ENV, RESPONSE_FORMATTER_TEMPERATURE
from prompts import load_prompt_template
from llm_client_factory import create_response_formatter_client
from prompt_saver import log_prompt_if_enabled

def create_follow_up_prompt(state: ConversationState) -> str:
    """Creates a prompt to answer a follow-up question using cached context and external template"""
    lang = state.get("detected_language", "en")
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])
    
    if TEST_ENV:
        print(f"\n[PROCESS] FH prompt: {lang}")
        print(f"[CACHE] FH cache: {len(state.get('context_cache', []))} items")
    
    # Check if follow-up is about dosage
    is_dosage_followup = any(word in state["user_query"].lower() 
                           for word in ["dawkowanie", "ile", "how much", "dosage", "oblicz"])
    
    # Format cached metadata
    cached_full_metadata = []
    if state.get("context_cache"):
        for i, meta in enumerate(state.get("context_cache", [])):
            metadata_json = json.dumps(meta, indent=2, ensure_ascii=False)
            cached_full_metadata.append(f"""Cached Item {i+1}:
COMPLETE METADATA:
{metadata_json}

""")
    
    cached_context_formatted = "".join(cached_full_metadata)
    
    dosage_followup_note = "The user might be asking about dosage. Use dosage information from cached metadata if available." if is_dosage_followup else ""

    # Try to load prompt from template
    prompt = load_prompt_template(
        "response_followup",
        chat_history_formatted=chat_history_formatted,
        user_query=state['user_query'],
        cached_context_formatted=cached_context_formatted,
        dosage_followup_note=dosage_followup_note,
        language=lang
    )
    
    # Fallback to simple prompt if template fails
    if not prompt:
        if TEST_ENV:
            print("[WARN] FH fallback prompt")
        prompt = f"""
Answer follow-up question: "{state['user_query']}"
Based on conversation history and cached product information.
Respond in {lang} language.
"""
    
    return prompt

def handle_follow_up(state: ConversationState) -> ConversationState:
    """Handle follow-up questions using cached metadata"""
    if TEST_ENV:
        print(f"\n[PROCESS] FH handling follow-up")
        
    try:
        client, model_name = create_response_formatter_client()
        prompt = create_follow_up_prompt(state)
        
        # Log prompt to file if enabled
        log_prompt_if_enabled("followup_handler", prompt, state, model_name, RESPONSE_FORMATTER_TEMPERATURE)
        
        response = client.chat.completions.create(
            model=model_name,
            temperature=RESPONSE_FORMATTER_TEMPERATURE,
            messages=[{"role": "system", "content": prompt}]
        )
        state["final_response"] = response.choices[0].message.content
        
        if TEST_ENV:
            print(f"[OK] FH response generated")
            
    except Exception as e:
        if TEST_ENV:
            print(f"[ERROR] FH handling: {str(e)[:30]}")
        
        # Import here to avoid circular imports
        from .response_formatter import ResponseFormatter
        formatter = ResponseFormatter()
        state["final_response"] = formatter._handle_error(e, state)
        
    return state

def escalate_to_human(state: ConversationState) -> ConversationState:
    """Escalate without automatically adding support contact"""
    if TEST_ENV:
        print(f"\n[ALERT] FH escalating")
    state["escalate"] = True
    
    # Create a custom prompt for escalation that doesn't include contact info
    lang = state.get("detected_language", "en")
    user_query = state.get("user_query", "")
    
    escalation_prompt = f"""
You are AF AI. This query needs special handling.
User asked: "{user_query}"

Generate a helpful response that:
1. Acknowledges you found some information but it might not be exactly what they're looking for
2. Share what relevant information you DID find (if any)
3. Suggest they rephrase their question or provide more details
4. DO NOT automatically provide support contact information unless they specifically ask for it

Be helpful and apologetic about not finding perfect matches.

Respond in {lang} language.
"""
    
    try:
        client, model_name = create_response_formatter_client()
        
        # Log prompt to file if enabled
        log_prompt_if_enabled("followup_handler_escalation", escalation_prompt, state, model_name, RESPONSE_FORMATTER_TEMPERATURE)
        
        response = client.chat.completions.create(
            model=model_name,
            temperature=RESPONSE_FORMATTER_TEMPERATURE,
            messages=[{"role": "system", "content": escalation_prompt}]
        )
        state["final_response"] = response.choices[0].message.content
    except Exception as e:
        if TEST_ENV:
            print(f"[ERROR] FH escalation: {str(e)[:30]}")
        # Import here to avoid circular imports
        from .response_formatter import ResponseFormatter
        formatter = ResponseFormatter()
        state["final_response"] = formatter._handle_error(e, state)
    
    return state