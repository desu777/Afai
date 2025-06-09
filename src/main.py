"""
Aquaforest RAG System - Main Application - Wersja 2.1 with Debug Control
Entry point for the conversational AI assistant
"""
import asyncio
import os
from typing import Dict, Any
from workflow import app
from models import ConversationState
import config

class AquaforestAssistant:
    def __init__(self):
        self.workflow = app
        
    def process_query_sync(self, state: ConversationState, debug: bool = False) -> ConversationState:
        """
        Synchronous version for easier testing.
        Accepts the full conversation state and returns the updated state.
        """
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
                print("\n" + "="*60)
                print("🚀 [WORKFLOW START]")
                print("="*60)
                final_node_output = None
                for chunk in self.workflow.stream(state):
                    node_name = list(chunk.keys())[0]
                    if node_name != "__end__":
                        print(f"\n📍 Executing node: '{node_name}'")
                        print("-"*40)
                        final_node_output = chunk[node_name]
                result = final_node_output
                if not result:
                     print("\n❌ [ERROR] Workflow did not produce any output.")
                     state["final_response"] = "I apologize, but an error occurred during the workflow."
                     return state
                print("\n" + "="*60)
                print("🏁 [WORKFLOW END]")
                print("="*60 + "\n")
            else:
                result = self.workflow.invoke(state)
            
            if "chat_history" not in result:
                result["chat_history"] = []
            result["chat_history"].append({"role": "user", "content": state["user_query"]})
            result["chat_history"].append({"role": "assistant", "content": result.get("final_response", "")})
            
            return result
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
            state["final_response"] = "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
            return state
        finally:
            # Restore original TEST_ENV value
            os.environ["TEST_ENV"] = original_test_env
            config.TEST_ENV = original_test_env.lower() == "true"

def main():
    """Main entry point for testing"""
    assistant = AquaforestAssistant()
    
    print("\n" + "="*60)
    print("🐠 Aquaforest AI Assistant - Interactive Mode")
    print("="*60)
    print("\nCommands:")
    print("  • 'quit' or 'exit' - Exit the program")
    print("  • 'debug' - Toggle debug mode")
    print("  • 'new' - Start a new conversation")
    print("  • 'help' - Show this help message")
    print("\n" + "="*60 + "\n")
    
    debug_mode = False
    
    def get_new_state() -> ConversationState:
        return {
            "user_query": "", "detected_language": "en", "intent": "other", "product_names": [],
            "original_query": "", "optimized_queries": [], "search_results": [],
            "confidence": 0.0, "evaluation_reasoning": "", "iteration": 0, "final_response": "",
            "escalate": False, "domain_filter": None, "chat_history": [], "context_cache": []
        }

    conversation_state = get_new_state()

    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thank you for using Aquaforest AI Assistant.")
                break
                
            if user_input.lower() == 'debug':
                debug_mode = not debug_mode
                print(f"\n{'🔍' if debug_mode else '🔒'} Debug mode is now {'ON' if debug_mode else 'OFF'}")
                print("-"*40)
                continue

            if user_input.lower() == 'new':
                print("\n🆕 Starting new conversation...")
                print("-"*40)
                conversation_state = get_new_state()
                continue
                
            if user_input.lower() == 'help':
                print("\n📖 Available commands:")
                print("  • 'quit'/'exit' - Exit the program")
                print("  • 'debug' - Toggle debug mode (currently: {})".format('ON' if debug_mode else 'OFF'))
                print("  • 'new' - Start a new conversation")
                print("  • 'help' - Show this help message")
                print("-"*40)
                continue

            if not user_input:
                continue
                
            conversation_state["user_query"] = user_input
            conversation_state["iteration"] = 0

            print("\n🤖 Assistant: ", end="", flush=True)
            
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
            print("\n\n⚠️  Interrupted by user. Type 'quit' to exit properly.")
            continue
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            print("\nTrying to continue...")

if __name__ == "__main__":
    main()