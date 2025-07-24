"""
Aquaforest RAG System - Main Application - Wersja 2.1 with Debug Control
Entry point for the conversational AI assistant
"""
import asyncio
import os
import time
from typing import Dict, Any, Optional
from workflow import app
from models import ConversationState
import config
from utils.logger import logger

class AquaforestAssistant:
    def __init__(self, analytics_instance=None):
        self.workflow = app
        self.analytics_instance = analytics_instance
        
    def process_query_sync(self, state: ConversationState, debug: bool = False) -> ConversationState:
        """
        Synchronous version for easier testing.
        Accepts the full conversation state and returns the updated state.
        """
        # Start timing
        start_time = time.time()
        
        # [NEW] Add analytics instance to state for per-session streaming
        if self.analytics_instance:
            state["analytics_instance"] = self.analytics_instance
        
        # Temporarily set TEST_ENV based on debug parameter
        original_test_env = os.environ.get("TEST_ENV", "false")
        if debug:
            os.environ["TEST_ENV"] = "true"
            config.TEST_ENV = True
        else:
            os.environ["TEST_ENV"] = "false"
            config.TEST_ENV = False
            
        try:
            if debug:
                logger.workflow_start()
                final_node_output = None
                for chunk in self.workflow.stream(state):
                    node_name = list(chunk.keys())[0]
                    if node_name != "__end__":
                        logger.workflow(f"Node: '{node_name}'", "SUB")
                        logger.separator("", 40, "-")
                        final_node_output = chunk[node_name]
                result = final_node_output
                if not result:
                     logger.error("Workflow: no output")
                     state["final_response"] = "I apologize, but an error occurred during the workflow."
                     return state
                logger.workflow_end()
            else:
                result = self.workflow.invoke(state)
            
            if "chat_history" not in result:
                result["chat_history"] = []
            result["chat_history"].append({"role": "user", "content": state["user_query"]})
            result["chat_history"].append({"role": "assistant", "content": result.get("final_response", "")})
            
            # Calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Display timing info
            if debug:
                logger.performance("Total execution time", execution_time)
                logger.separator("", 60, "-")
            
            return result
        except Exception as e:
            if debug:  # Only show errors in debug mode
                logger.error(f"Error: {str(e)[:30]}...")
                import traceback
                traceback.print_exc()
            state["final_response"] = "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
            
            # Calculate execution time even for errors
            end_time = time.time()
            execution_time = end_time - start_time
            if debug:
                logger.performance("Execution time (with error)", execution_time)
                logger.separator("", 60, "-")
                
            return state
        finally:
            # Restore original TEST_ENV value
            os.environ["TEST_ENV"] = original_test_env
            config.TEST_ENV = original_test_env.lower() == "true"

def main():
    """Main entry point for testing"""
    assistant = AquaforestAssistant()
    
    # Always show interactive mode header (not dependent on TEST_ENV)
    print("\n" + "="*60)
    print("[AI] Aquaforest Assistant")
    print("="*60)
    print("\nCommands:")
    print("  • 'quit' or 'exit' - Exit the program")
    print("  • 'debug' - Toggle debug mode")
    print("  • 'new' - Start a new conversation")
    print("  • 'session' - Show session cache stats")
    print("  • 'cleanup' - Manual cleanup of expired sessions")
    print("  • 'help' - Show this help message")
    print("\n" + "="*60 + "\n")
    
    debug_mode = False
    query_count = 0
    
    def get_new_state() -> ConversationState:
        from session_manager import get_session_manager
        session_manager = get_session_manager()
        session_id = session_manager.generate_session_id()
        
        return {
            "user_query": "", "detected_language": "en", "intent": "other", "product_names": [],
            "original_query": "", "optimized_queries": [], "search_results": [],
            "iteration": 0, "final_response": "",
            "escalate": False, "domain_filter": None, "chat_history": [], "context_cache": [],
            "session_id": session_id, "extended_cache": None,  # [NEW] Session fields
            "image_url": None, "image_analysis": None,  # [NEW] Vision analysis fields
            "node_timings": {}, "routing_decisions": [], "total_execution_time": 0.0, "analytics_instance": None
        }

    conversation_state = get_new_state()
    print(f"[SESSION] Session ID: {conversation_state['session_id']}")

    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n[EXIT] Goodbye! Thank you for using Aquaforest AI Assistant.")
                break
                
            if user_input.lower() == 'debug':
                debug_mode = not debug_mode
                print(f"\n[{'DEBUG' if debug_mode else 'NORMAL'}] Debug mode is now {'ON' if debug_mode else 'OFF'}")
                print("-"*40)
                continue

            if user_input.lower() == 'new':
                conversation_state = get_new_state()
                print(f"\n[NEW] Starting new conversation...")
                print(f"[SESSION] Session ID: {conversation_state['session_id']}")
                print("-"*40)
                continue
                
            if user_input.lower() == 'session':
                from session_manager import get_session_manager
                session_manager = get_session_manager()
                extended_cache = session_manager.get_session_cache(conversation_state['session_id'])
                
                print(f"\n[CACHE] Session Cache Stats:")
                print(f"[SESSION] Session ID: {conversation_state['session_id']}")
                if extended_cache:
                    print(f"[DATA] Metadata items: {len(extended_cache.get('metadata', []))}")
                    print(f"[AI] Model responses: {len(extended_cache.get('model_responses', []))}")
                    print(f"[CONTEXT] Context fields: {len(extended_cache.get('conversation_context', {}))}")
                    print(f"[TIME] Last updated: {extended_cache.get('timestamp', 'unknown')}")
                else:
                    print("[ERROR] No cache found for this session")
                
                global_stats = session_manager.get_session_stats()
                print(f"\n[GLOBAL] Global Stats:")
                print(f"[STATS] Total sessions: {global_stats['total_sessions']}")
                print(f"[ACTIVE] Active sessions: {global_stats['active_sessions']}")
                print(f"[TTL] TTL: {global_stats['ttl_minutes']} minutes")
                print("-"*40)
                continue
                
            if user_input.lower() == 'cleanup':
                from session_manager import get_session_manager
                session_manager = get_session_manager()
                cleaned = session_manager.manual_cleanup()
                print(f"\n[CLEANUP] Manually cleaned {cleaned} expired sessions")
                print("-"*40)
                continue
                
            if user_input.lower() == 'help':
                print("\n[HELP] Available commands:")
                print("  • 'quit'/'exit' - Exit the program")
                print("  • 'debug' - Toggle debug mode (currently: {})".format('ON' if debug_mode else 'OFF'))
                print("  • 'new' - Start a new conversation")
                print("  • 'session' - Show session cache stats")
                print("  • 'cleanup' - Manual cleanup of expired sessions")
                print("  • 'help' - Show this help message")
                print("-"*40)
                continue

            if not user_input:
                continue
                
            # Manual cleanup every 10 queries
            query_count += 1
            if query_count % 10 == 0:
                from session_manager import get_session_manager
                session_manager = get_session_manager()
                cleaned = session_manager.manual_cleanup()
                if cleaned > 0 and debug_mode:
                    print(f"[CLEANUP] Cleaned {cleaned} expired sessions")
                
            conversation_state["user_query"] = user_input
            conversation_state["iteration"] = 0

            # [DEBUG] Session ID tracking zgodnie z rules (TEST_ENV)
            if config.TEST_ENV or debug_mode:
                session_id = conversation_state.get('session_id', 'NONE')
                logger.debug(f"Session: {session_id}")
                from session_manager import get_session_manager
                session_manager = get_session_manager()
                existing_cache = session_manager.get_session_cache(session_id)
                if existing_cache:
                    logger.debug(f"Cache: {len(existing_cache.get('metadata', []))} items", "SUB")
                else:
                    logger.debug("Cache: none", "SUB")

            print("\n[AI] Assistant: ", end="", flush=True)
            
            updated_state = assistant.process_query_sync(conversation_state, debug=debug_mode)
            
            conversation_state = updated_state
            
            if not debug_mode:
                # In non-debug mode, print response inline
                print(conversation_state.get("final_response", "No response generated."))
            else:
                # In debug mode, response is on new line for clarity
                print("\n" + conversation_state.get("final_response", "No response generated."))
                
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n[WARN] Interrupted by user. Type 'quit' to exit properly.")
            continue
        except Exception as e:
            if debug_mode:  # Only show errors in debug mode
                logger.error(f"Error: {str(e)[:30]}...")
                import traceback
                traceback.print_exc()
                print("\nTrying to continue...")
            else:
                print("\nAn error occurred. Trying to continue...")

if __name__ == "__main__":
    main()