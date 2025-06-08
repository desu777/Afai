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
    
    def process_query_sync(self, user_query: str, debug: bool = False) -> str:
        """Synchronous version for easier testing"""
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
            if debug:
                print("\n--- [WORKFLOW START] ---")
                result = {}
                final_chunk = None
                # Use stream to get step-by-step execution
                for chunk in self.workflow.stream(initial_state):
                    node_name = list(chunk.keys())[0]
                    print(f"-> Executed node: '{node_name}'")
                    final_chunk = chunk
                
                if final_chunk and "__end__" in final_chunk:
                    result = final_chunk["__end__"]
                else:
                    print("[ERROR] Workflow did not finish correctly.")
                    return "I apologize, but an error occurred during the workflow."

                print("--- [WORKFLOW END] ---\n")

            else:
                # Run the workflow without streaming logs
                result = self.workflow.invoke(initial_state)
            
            return result["final_response"]
        except Exception as e:
            print(f"Error processing query: {e}")
            import traceback
            traceback.print_exc()
            return "I apologize, but I encountered an error. Please try again or contact support@aquaforest.eu"

def main():
    """Main entry point for testing"""
    assistant = AquaforestAssistant()
    
    print("🐠 Aquaforest AI Assistant")
    print("Type 'quit' to exit, 'debug' to toggle debug mode\n")
    
    debug_mode = False
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
            
        if user_input.lower() == 'debug':
            debug_mode = not debug_mode
            print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
            continue
            
        if not user_input:
            continue
            
        print("\nAssistant: ", end="", flush=True)
        response = assistant.process_query_sync(user_input, debug=debug_mode)
        print(response)
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