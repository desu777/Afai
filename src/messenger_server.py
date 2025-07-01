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

# 🚀 MESSAGE DEDUPLICATION CACHE
processed_messages = set()  # Simple in-memory cache for message IDs

def clean_processed_messages_cache():
    """Clean old messages from cache to prevent memory issues"""
    global processed_messages
    if len(processed_messages) > 1000:  # Keep last 500 messages
        # Convert to list, keep last 500, convert back to set
        processed_messages = set(list(processed_messages)[-500:])
        debug_print(f"🧹 [Cache] Cleaned message cache, now has {len(processed_messages)} entries", "🧹")

# 🚀 FACEBOOK MESSENGER MODELS
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

# 🚀 MESSENGER UTILITIES
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
            debug_print(f"✅ [Messenger] Message sent to {user_id}", "📤")
            return True
        else:
            debug_print(f"❌ [Messenger] Failed to send message: {response.status_code} {response.text}", "📤")
            return False
            
    except Exception as e:
        debug_print(f"❌ [Messenger] Error sending message: {e}", "📤")
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
        debug_print(f"❌ [Messenger] Signature verification failed: {e}", "🔐")
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
        chunks = split_long_message(message)
        debug_print(f"📤 [Messenger] Sending {len(chunks)} message chunk(s) to {user_id}", "📤")
        
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
        debug_print(f"❌ [Messenger] Error sending messages: {e}", "📤")
        return False

# 🚀 WEBHOOK HANDLERS
async def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"), 
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Webhook verification endpoint for Facebook"""
    # 🚫 Check if Messenger is enabled
    if not MESSENGER_ON:
        debug_print("🚫 [Webhook] Messenger integration is DISABLED (MESSENGER_ON=false)", "🚫")
        raise HTTPException(status_code=404, detail="Messenger integration disabled")
    
    debug_print(f"🔍 [Webhook] Verification request: mode={hub_mode}, token={hub_verify_token}", "🔐")
    
    if hub_mode == "subscribe" and hub_verify_token == MESSENGER_VERIFY_TOKEN:
        debug_print("✅ [Webhook] Verification successful!", "🔐")
        return int(hub_challenge)
    else:
        debug_print("❌ [Webhook] Verification failed!", "🔐")
        raise HTTPException(status_code=403, detail="Forbidden")

async def webhook_handler(request: Request, assistant: AquaforestAssistant):
    """Main webhook handler for Facebook Messenger"""
    # 🚫 Check if Messenger is enabled
    if not MESSENGER_ON:
        debug_print("🚫 [Webhook] Messenger integration is DISABLED (MESSENGER_ON=false)", "🚫")
        raise HTTPException(status_code=404, detail="Messenger integration disabled")
    
    try:
        # Get request body and signature
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        debug_print(f"📨 [Webhook] Received webhook request", "📥")
        
        # Verify signature (optional in development)
        if not TEST_ENV and not verify_webhook_signature(body, signature):
            debug_print("❌ [Webhook] Invalid signature", "🔐")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = MessengerWebhookData.parse_raw(body)
        
        debug_print(f"✅ [Webhook] Valid webhook data received: {webhook_data.object}", "📥")
        
        # Process each entry
        for entry in webhook_data.entry:
            debug_print(f"📋 [Webhook] Processing entry {entry.id}", "⚙️")
            
            for messaging_event in entry.messaging:
                # Only process text messages (skip delivery receipts, read receipts, etc.)
                if messaging_event.message and messaging_event.message.text:
                    # 🔍 CHECK FOR DUPLICATE MESSAGES
                    message_id = messaging_event.message.mid
                    if message_id in processed_messages:
                        debug_print(f"⏭️ [Webhook] Skipping duplicate message {message_id}", "🔄")
                        continue
                    
                    # Mark as processed immediately
                    processed_messages.add(message_id)
                    debug_print(f"✅ [Webhook] Processing new message {message_id}", "🆕")
                    
                    # Clean cache if needed
                    clean_processed_messages_cache()
                    
                    # 🚀 PROCESS ASYNCHRONOUSLY - don't wait for completion
                    import asyncio
                    task = asyncio.create_task(process_messenger_message(messaging_event, assistant))
                    debug_print(f"🚀 [Webhook] Started async processing for {message_id}", "🚀")
                    
                elif messaging_event.delivery:
                    debug_print(f"📨 [Webhook] Delivery receipt received", "📨")
                elif messaging_event.read:
                    debug_print(f"👁️ [Webhook] Read receipt received", "👁️")
                else:
                    debug_print(f"⏭️ [Webhook] Skipping non-text event", "⚙️")
        
        return {"status": "EVENT_RECEIVED"}
        
    except Exception as e:
        debug_print(f"❌ [Webhook] Error processing webhook: {e}", "🚨")
        # Return 200 to avoid Facebook retry loops
        return {"status": "ERROR", "message": str(e)}

async def process_messenger_message(messaging_event, assistant: AquaforestAssistant):
    """Process individual Messenger message with RAG - runs asynchronously"""
    message_id = messaging_event.message.mid
    try:
        user_id = messaging_event.sender.id
        message_text = messaging_event.message.text
        
        debug_print(f"💬 [Messenger] Processing message from {user_id}: '{message_text[:50]}...'", "🧠")
        
        # Create conversation state for RAG processing
        conversation_state: ConversationState = {
            "user_query": message_text,
            "detected_language": "en",  # Will be detected by intent detector
            "intent": "other",
            "product_names": [],
            "original_query": message_text,
            "optimized_queries": [],
            "search_results": [],
            "confidence": 0.0,
            "evaluation_reasoning": "",
            "iteration": 0,
            "final_response": "",
            "escalate": False,
            "domain_filter": None,
            "chat_history": [],  # TODO: Load user's chat history from database
            "context_cache": []
        }
        
        debug_print(f"🔄 [Messenger] Processing with RAG workflow", "⚙️")
        
        # Process with RAG system
        result_state = assistant.process_query_sync(conversation_state, debug=TEST_ENV)
        
        # Extract response
        ai_response = result_state.get("final_response", "Sorry, I couldn't process your request.")
        
        debug_print(f"✅ [Messenger] Generated response ({len(ai_response)} chars): '{ai_response[:100]}...'", "🤖")
        
        # Send response back to user
        success = send_messenger_messages(user_id, ai_response)
        
        if success:
            debug_print(f"🎉 [Messenger] Successfully handled message {message_id} from {user_id}", "✅")
        else:
            debug_print(f"❌ [Messenger] Failed to send response for {message_id} to {user_id}", "📤")
            
    except Exception as e:
        debug_print(f"❌ [Messenger] Error processing message {message_id}: {e}", "🚨")
        # Remove from processed cache so it can be retried
        if message_id in processed_messages:
            processed_messages.discard(message_id)
            debug_print(f"🔄 [Messenger] Removed {message_id} from cache for retry", "🔄")
        
        # Send error message to user
        error_msg = "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
        send_messenger_messages(messaging_event.sender.id, error_msg) 