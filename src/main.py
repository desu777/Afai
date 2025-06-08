"""
Aquaforest RAG System - Main Application - Wersja 2.0
Entry point for the conversational AI assistant
"""
import asyncio
from typing import Dict, Any
from workflow import app
from models import ConversationState

class AquaforestAssistant:
    def __init__(self):
        self.workflow = app
        
    def process_query_sync(self, state: ConversationState, debug: bool = False) -> ConversationState:
        """
        Synchronous version for easier testing.
        Accepts the full conversation state and returns the updated state.
        """
        try:
            if debug:
                print("\n--- [WORKFLOW START] ---")
                final_node_output = None
                for chunk in self.workflow.stream(state):
                    node_name = list(chunk.keys())[0]
                    if node_name != "__end__":
                        print(f"-> Executed node: '{node_name}'")
                        final_node_output = chunk[node_name]
                result = final_node_output
                if not result:
                     print("[ERROR] Workflow did not produce any output.")
                     state["final_response"] = "I apologize, but an error occurred during the workflow."
                     return state
                print("--- [WORKFLOW END] ---\n")
            else:
                result = self.workflow.invoke(state)
            
            if "chat_history" not in result:
                result["chat_history"] = []
            result["chat_history"].append({"role": "user", "content": state["user_query"]})
            result["chat_history"].append({"role": "assistant", "content": result.get("final_response", "")})
            
            return result
        except Exception as e:
            print(f"Error processing query: {e}")
            import traceback
            traceback.print_exc()
            state["final_response"] = "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
            return state

def main():
    """Main entry point for testing"""
    assistant = AquaforestAssistant()
    
    print("🐠 Aquaforest AI Assistant")
    print("Type 'quit' to exit, 'debug' to toggle debug mode, 'new' to start a new conversation\n")
    
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
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
            
        if user_input.lower() == 'debug':
            debug_mode = not debug_mode
            print(f"Debug mode is now {'ON' if debug_mode else 'OFF'}")
            continue

        if user_input.lower() == 'new':
            print("\n--- Starting new conversation ---")
            conversation_state = get_new_state()
            continue

        if not user_input:
            continue
            
        conversation_state["user_query"] = user_input
        conversation_state["iteration"] = 0

        print("\nAssistant: ", end="", flush=True)
        
        updated_state = assistant.process_query_sync(conversation_state, debug=debug_mode)
        
        conversation_state = updated_state
        
        print(conversation_state.get("final_response", "No response generated."))
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()