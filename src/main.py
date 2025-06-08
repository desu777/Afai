"""
Aquaforest RAG System - Main Application
Entry point for the conversational AI assistant
"""
import asyncio
from typing import Dict, Any
from workflow import app
from models import ConversationState

class AquaforestAssistant:
    def __init__(self):
        self.workflow = app
        
    async def process_query(self, user_query: str) -> str:
        """Process a single user query"""
        # Initialize state
        initial_state: ConversationState = {
            "user_query": user_query,
            "detected_language": "en",
            "intent": "other",
            "product_names": [],
            "original_query": user_query,
            "optimized_queries": [],
            "search_results": [],
            "confidence": 0.0,
            "iteration": 0,
            "final_response": "",
            "escalate": False,
            "domain_filter": None
        }
        
        try:
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            return result["final_response"]
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"
    
    def process_query_sync(self, state: ConversationState, debug: bool = False) -> ConversationState:
        """
        Synchronous version for easier testing.
        Accepts the full conversation state and returns the updated state.
        """
        try:
            # The user query is already in the state passed to this method
            if debug:
                print("\n--- [WORKFLOW START] ---")
                final_chunk = None
                # Use stream to get step-by-step execution
                for chunk in self.workflow.stream(state):
                    node_name = list(chunk.keys())[0]
                    print(f"-> Executed node: '{node_name}'")
                    final_chunk = chunk
                
                if final_chunk and "__end__" in final_chunk:
                    result = final_chunk["__end__"]
                else:
                    print("[ERROR] Workflow did not finish correctly.")
                    state["final_response"] = "I apologize, but an error occurred during the workflow."
                    return state

                print("--- [WORKFLOW END] ---\n")

            else:
                # Run the workflow without streaming logs
                result = self.workflow.invoke(state)
            
            # Before returning, update the chat history with the latest turn
            result["chat_history"].append({"role": "user", "content": state["user_query"]})
            result["chat_history"].append({"role": "assistant", "content": result["final_response"]})
            
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
            "user_query": "",
            "detected_language": "en",
            "intent": "other",
            "product_names": [],
            "original_query": "",
            "optimized_queries": [],
            "search_results": [],
            "confidence": 0.0,
            "iteration": 0,
            "final_response": "",
            "escalate": False,
            "domain_filter": None,
            "chat_history": [],
            "context_cache": []
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
            
        # Update state for the new turn
        conversation_state["user_query"] = user_input
        # Reset iteration count for the new turn
        conversation_state["iteration"] = 0

        print("\nAssistant: ", end="", flush=True)
        
        # Process the query using the current state and get the updated state back
        updated_state = assistant.process_query_sync(conversation_state, debug=debug_mode)
        
        # The new state for the next turn is the result of the previous one
        conversation_state = updated_state
        
        print(conversation_state.get("final_response", "No response generated."))
        print("\n" + "-"*50 + "\n")

async def async_main():
    """Async version for production use"""
    assistant = AquaforestAssistant()
    
    # Example async processing
    queries = [
        "Mam problem z azotanami i koralowce brązowieją",
        "What can I use to reduce phosphates naturally?",
        "Hello!",
        "Jak obliczyć dawkowanie Ca plus?",
    ]
    
    tasks = [assistant.process_query(q) for q in queries]
    results = await asyncio.gather(*tasks)
    
    for query, response in zip(queries, results):
        print(f"Q: {query}")
        print(f"A: {response}\n")

if __name__ == "__main__":
    # Run in interactive mode
    main()
    
    # Or run async examples
    # asyncio.run(async_main())