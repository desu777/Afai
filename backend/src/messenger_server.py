"""
Facebook Messenger Integration Module
Dedicated module for handling Facebook Messenger webhooks and API calls
"""
import hmac
import hashlib
import requests
from typing import Optional
from fastapi import HTTPException, Request, Query
from pydantic import BaseModel, Field
from config import (
    debug_print, TEST_ENV, MESSENGER_ON,
    MESSENGER_PAGE_ACCESS_TOKEN, MESSENGER_VERIFY_TOKEN, FACEBOOK_API_VERSION
)
from models import ConversationState
from main import AquaforestAssistant

# [API] MESSAGE DEDUPLICATION CACHE
processed_messages = set()  # Simple in-memory cache for message IDs

def clean_processed_messages_cache():
    """Clean old messages from cache to prevent memory issues"""
    global processed_messages
    if len(processed_messages) > 1000:  # Keep last 500 messages
        # Convert to list, keep last 500, convert back to set
        processed_messages = set(list(processed_messages)[-500:])
        debug_print(f"[CLEANUP] [Cache] Cleaned message cache, now has {len(processed_messages)} entries", "[CLEANUP]")

# [NEW] MARKDOWN TO CLEAN TEXT CONVERTER
def convert_markdown_to_messenger_text(text: str) -> str:
    """Convert Markdown formatting to clean, readable text for Facebook Messenger"""
    if not text:
        return text
    
    import re
    
    # Convert headers - simple, clean formatting
    text = re.sub(r'^### (.+)$', r'▶ \1', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'📋 \1', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'🔹 \1', text, flags=re.MULTILINE)
    
    # Convert bold and italic - remove formatting, keep text clean
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Remove bold completely
    text = re.sub(r'\*(.+?)\*', r'\1', text)      # Remove italic completely
    
    # Convert inline code - just use quotes
    text = re.sub(r'`(.+?)`', r'"\1"', text)
    
    # Convert code blocks - simple format
    text = re.sub(r'```[\w]*\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    
    # Convert links - clean format
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1: \2', text)
    
    # Convert bullet points - minimal formatting
    text = re.sub(r'^- (.+)$', r'• \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\* (.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Convert numbered lists - clean numbers
    text = re.sub(r'^\d+\. (.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Clean up multiple newlines (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Clean up extra spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Convert horizontal rules - just remove them
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    
    # Remove any remaining markdown artifacts
    text = re.sub(r'\*+', '', text)  # Remove stray asterisks
    text = re.sub(r'#+\s*', '', text)  # Remove stray hashes
    
    return text.strip()

# [API] FACEBOOK MESSENGER MODELS
class MessengerUser(BaseModel):
    """Facebook Messenger user"""
    id: str

class MessengerMessage(BaseModel):
    """Facebook Messenger message"""
    mid: str
    text: Optional[str] = None
    timestamp: Optional[int] = None

class MessengerSender(BaseModel):
    """Facebook Messenger sender"""
    id: str

class MessengerRecipient(BaseModel):
    """Facebook Messenger recipient"""  
    id: str

class MessengerMessageEntry(BaseModel):
    """Facebook Messenger message entry"""
    sender: MessengerSender
    recipient: MessengerRecipient
    timestamp: Optional[int] = None
    message: Optional[MessengerMessage] = None
    delivery: Optional[dict] = None  # For delivery receipts
    read: Optional[dict] = None      # For read receipts

class MessengerWebhookEntry(BaseModel):
    """Facebook Messenger webhook entry"""
    id: str
    time: Optional[int] = None
    messaging: list[MessengerMessageEntry]

class MessengerWebhookData(BaseModel):
    """Facebook Messenger webhook data"""
    object: str
    entry: list[MessengerWebhookEntry]

# [API] MESSENGER UTILITIES
def send_messenger_message(user_id: str, message: str) -> bool:
    """Send message via Facebook Messenger API"""
    try:
        url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/me/messages"
        
        data = {
            "recipient": {"id": user_id},
            "message": {"text": message},
            "messaging_type": "RESPONSE"
        }
        
        headers = {
            "Authorization": f"Bearer {MESSENGER_PAGE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            debug_print(f"[OK] [Messenger] Message sent to {user_id}", "[STREAM]")
            return True
        else:
            debug_print(f"[ERROR] [Messenger] Failed to send message: {response.status_code} {response.text}", "[STREAM]")
            return False
            
    except Exception as e:
        debug_print(f"[ERROR] [Messenger] Error sending message: {e}", "[STREAM]")
        return False

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Facebook webhook signature"""
    try:
        # Facebook sends signature as 'sha256=<hash>'
        expected_signature = hmac.new(
            MESSENGER_VERIFY_TOKEN.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Remove 'sha256=' prefix from signature
        signature = signature.replace('sha256=', '')
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        debug_print(f"[ERROR] [Messenger] Signature verification failed: {e}", "[AUTH]")
        return False

def split_long_message(message: str, max_length: int = 1950) -> list[str]:
    """Intelligently split long messages into chunks"""
    if len(message) <= max_length:
        return [message]
    
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first
    paragraphs = message.split('\n\n')
    
    for paragraph in paragraphs:
        # If single paragraph is too long, split by sentences
        if len(paragraph) > max_length:
            sentences = paragraph.split('. ')
            for i, sentence in enumerate(sentences):
                # Add period back except for last sentence
                if i < len(sentences) - 1:
                    sentence += '. '
                
                if len(current_chunk + sentence) > max_length:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        # Even single sentence is too long, force split
                        chunks.append(sentence[:max_length] + "...")
                        current_chunk = "..." + sentence[max_length:]
                else:
                    current_chunk += sentence
        else:
            # Normal paragraph
            if len(current_chunk + '\n\n' + paragraph) > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += '\n\n' + paragraph
                else:
                    current_chunk = paragraph
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def send_messenger_messages(user_id: str, message: str) -> bool:
    """Send message(s) via Facebook Messenger API with intelligent splitting"""
    try:
        # [NEW] Convert Markdown to Messenger-friendly text
        cleaned_message = convert_markdown_to_messenger_text(message)
        debug_print(f"[LOG] [Messenger] Converted Markdown to plain text ({len(message)} chars to {len(cleaned_message)} chars)", "[LOG]")
        
        chunks = split_long_message(cleaned_message)
        debug_print(f"[STREAM] [Messenger] Sending {len(chunks)} message chunk(s) to {user_id}", "[STREAM]")
        
        all_success = True
        for i, chunk in enumerate(chunks):
            success = send_messenger_message(user_id, chunk)
            if not success:
                all_success = False
                break
            
            # Small delay between messages to maintain order
            if i < len(chunks) - 1:
                import time
                time.sleep(0.5)
        
        return all_success
        
    except Exception as e:
        debug_print(f"[ERROR] [Messenger] Error sending messages: {e}", "[STREAM]")
        return False

# [API] WEBHOOK HANDLERS
async def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"), 
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Webhook verification endpoint for Facebook"""
    # [INFO] Check if Messenger is enabled
    if not MESSENGER_ON:
        debug_print("[INFO] [Webhook] Messenger integration is DISABLED (MESSENGER_ON=false)", "[INFO]")
        raise HTTPException(status_code=404, detail="Messenger integration disabled")
    
    debug_print(f"[DEBUG] [Webhook] Verification request: mode={hub_mode}, token={hub_verify_token}", "[AUTH]")
    
    if hub_mode == "subscribe" and hub_verify_token == MESSENGER_VERIFY_TOKEN:
        debug_print("[OK] [Webhook] Verification successful!", "[AUTH]")
        return int(hub_challenge)
    else:
        debug_print("[ERROR] [Webhook] Verification failed!", "[AUTH]")
        raise HTTPException(status_code=403, detail="Forbidden")

async def webhook_handler(request: Request, assistant: AquaforestAssistant, 
                          load_history_func=None, save_message_func=None):
    """Main webhook handler for Facebook Messenger"""
    # [INFO] Check if Messenger is enabled
    if not MESSENGER_ON:
        debug_print("[INFO] [Webhook] Messenger integration is DISABLED (MESSENGER_ON=false)", "[INFO]")
        raise HTTPException(status_code=404, detail="Messenger integration disabled")
    
    try:
        # Get request body and signature
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        debug_print(f"[STREAM] [Webhook] Received webhook request", "[STREAM]")
        
        # Verify signature (optional in development)
        if not TEST_ENV and not verify_webhook_signature(body, signature):
            debug_print("[ERROR] [Webhook] Invalid signature", "[AUTH]")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = MessengerWebhookData.parse_raw(body)
        
        debug_print(f"[OK] [Webhook] Valid webhook data received: {webhook_data.object}", "[STREAM]")
        
        # Process each entry
        for entry in webhook_data.entry:
            debug_print(f"[INFO] [Webhook] Processing entry {entry.id}", "[CONFIG]")
            
            for messaging_event in entry.messaging:
                # Only process text messages (skip delivery receipts, read receipts, etc.)
                if messaging_event.message and messaging_event.message.text:
                    # [DEBUG] CHECK FOR DUPLICATE MESSAGES
                    message_id = messaging_event.message.mid
                    if message_id in processed_messages:
                        debug_print(f"[INFO] [Webhook] Skipping duplicate message {message_id}", "[PROCESS]")
                        continue
                    
                    # Mark as processed immediately
                    processed_messages.add(message_id)
                    debug_print(f"[OK] [Webhook] Processing new message {message_id}", "[NEW]")
                    
                    # Clean cache if needed
                    clean_processed_messages_cache()
                    
                    # [API] PROCESS ASYNCHRONOUSLY - don't wait for completion
                    import asyncio
                    task = asyncio.create_task(process_messenger_message(
                        messaging_event, assistant, load_history_func, save_message_func
                    ))
                    debug_print(f"[API] [Webhook] Started async processing for {message_id}", "[API]")
                    
                elif messaging_event.delivery:
                    debug_print(f"[STREAM] [Webhook] Delivery receipt received", "[STREAM]")
                elif messaging_event.read:
                    debug_print(f"[INFO] [Webhook] Read receipt received", "[INFO]")
                else:
                    debug_print(f"[INFO] [Webhook] Skipping non-text event", "[CONFIG]")
        
        return {"status": "EVENT_RECEIVED"}
        
    except Exception as e:
        debug_print(f"[ERROR] [Webhook] Error processing webhook: {e}", "[ALERT]")
        # Return 200 to avoid Facebook retry loops
        return {"status": "ERROR", "message": str(e)}

async def process_messenger_message(messaging_event, assistant: AquaforestAssistant, 
                                    load_history_func=None, save_message_func=None):
    """Process individual Messenger message with RAG - runs asynchronously"""
    message_id = messaging_event.message.mid
    try:
        user_id = messaging_event.sender.id
        message_text = messaging_event.message.text
        
        debug_print(f"[INFO] [Messenger] Processing message from {user_id}: '{message_text[:50]}...'", "[AI]")
        
        # [NEW] Load chat history for context (last exchange only)
        chat_history = []
        if load_history_func:
            chat_history = load_history_func(user_id)
            if chat_history:
                debug_print(f"[INFO] [Messenger] Using {len(chat_history)} messages for context", "[INFO]")
        
        # [NEW] Save user message to history
        if save_message_func:
            save_message_func(user_id, "user", message_text, message_id)
        
        # Create conversation state for RAG workflow
        conversation_state = {
            "user_query": message_text,
            "detected_language": "en",
            "intent": "other",
            "product_names": [],
            "original_query": "",
            "optimized_queries": [],
            "search_results": [],
            "iteration": 0,
            "final_response": "",
            "escalate": False,
            "domain_filter": None,
            "chat_history": chat_history,
            "context_cache": [],
            "image_url": None,  # [NEW] Vision analysis - TODO: add Messenger image support
            "image_analysis": None,  # [NEW] Will be filled by intent detector
            "node_timings": {},
            "routing_decisions": [],
            "total_execution_time": 0.0
        }
        
        debug_print(f"[PROCESS] [Messenger] Processing with RAG workflow", "[CONFIG]")
        
        # Process with RAG system
        result_state = assistant.process_query_sync(conversation_state, debug=TEST_ENV)
        
        # Extract response
        ai_response = result_state.get("final_response", "Sorry, I couldn't process your request.")
        
        debug_print(f"[OK] [Messenger] Generated response ({len(ai_response)} chars): '{ai_response[:100]}...'", "[AI]")
        
        # [NEW] Save assistant response to history
        if save_message_func:
            save_message_func(user_id, "assistant", ai_response)
        
        # Send response back to user
        success = send_messenger_messages(user_id, ai_response)
        
        if success:
            debug_print(f"[OK] [Messenger] Successfully handled message {message_id} from {user_id}", "[OK]")
        else:
            debug_print(f"[ERROR] [Messenger] Failed to send response for {message_id} to {user_id}", "[STREAM]")
            
    except Exception as e:
        debug_print(f"[ERROR] [Messenger] Error processing message {message_id}: {e}", "[ALERT]")
        # Remove from processed cache so it can be retried
        if message_id in processed_messages:
            processed_messages.discard(message_id)
            debug_print(f"[PROCESS] [Messenger] Removed {message_id} from cache for retry", "[PROCESS]")
        
        # Send error message to user
        error_msg = "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
        send_messenger_messages(messaging_event.sender.id, error_msg) 