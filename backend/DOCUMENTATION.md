# Aquaforest RAG Backend Documentation

This document provides a comprehensive overview of the Aquaforest RAG (Retrieval-Augmented Generation) backend system. It details the architecture, individual components, and the overall workflow of the application.

## 1. High-Level Architecture

The backend is a sophisticated AI system built with Python and FastAPI, designed to serve as an intelligent assistant for Aquaforest products. It leverages a Retrieval-Augmented Generation (RAG) architecture, which means it retrieves relevant information from a knowledge base before generating a response. This ensures that the answers are not only contextually aware but also factually grounded in the provided data.

The system is designed to be highly modular and configurable, with a clear separation of concerns. It uses a stateful graph-based workflow engine (`LangGraph`) to orchestrate the complex process of handling a user's query, from initial intent detection to the final response generation.

### Key Features:

*   **Modular RAG Pipeline**: The core logic is broken down into distinct, reusable components (nodes in a graph), such as intent detection, query optimization, business reasoning, and response formatting.
*   **Flexible LLM Integration**: The system is not tied to a single Large Language Model (LLM) provider. It supports both OpenRouter and Google's Vertex AI (Gemini models), with the ability to configure different models for different tasks (e.g., a fast model for intent detection, a powerful model for business reasoning).
*   **Vector Search with Pinecone**: It uses Pinecone as a vector database for efficient and scalable similarity search, allowing it to quickly find the most relevant product information.
*   **Stateful Conversations**: The system maintains conversation state, including session-based caching, to handle follow-up questions intelligently and provide a more natural conversational experience.
*   **Robust Security**: It includes essential security features like rate limiting, IP filtering, and authentication to protect the API from abuse.
*   **Built-in Analytics**: The application tracks key metrics and workflow data, saving them to a SQLite database for monitoring and analysis.
*   **Developer-Friendly**: The project includes a command-line interface for interactive testing and debugging.

## 2. Core Components & File Descriptions

This section provides a detailed description of each major file and module in the `backend/src` directory.

### 2.1. Main Application & Server

#### `main.py`

*   **Purpose**: This file serves as the main entry point for the application's core logic and also provides a command-line interface (CLI) for interactive testing and debugging.
*   **Key Components**:
    *   **`AquaforestAssistant` class**: This class encapsulates the entire RAG workflow. Its `process_query_sync` method takes the current conversation state and executes the `LangGraph` workflow to produce a response.
    *   **`main()` function**: When the script is run directly (`python -m src.main`), this function provides an interactive chat session in the terminal. It allows developers to test the chatbot, toggle debug mode, manage sessions, and see detailed logs without needing to run the full web server.
*   **Workflow**: The CLI simulates a user conversation, maintaining the conversation state between turns and passing it to the `AquaforestAssistant` for processing.

#### `server.py`

*   **Purpose**: This file sets up and runs the FastAPI web server, which exposes the AI assistant's functionality as a REST API for the frontend.
*   **Key Components**:
    *   **FastAPI App Initialization**: It creates a FastAPI application instance using the `create_app` factory function from `core/app_factory.py`.
    *   **Pydantic Models**: It defines the data structures for API requests and responses (e.g., `ChatRequest`, `ChatResponse`, `FeedbackRequest`) using Pydantic, which ensures data validation.
    *   **Endpoint Setup**: It imports and sets up all the different API endpoints from the `endpoints/` directory (chat, session, feedback, analytics, etc.), applying the appropriate rate limiting rules to each.
    *   **Global Instances**: It initializes global instances of the `AquaforestAssistant` and `WorkflowAnalytics`.
*   **Execution**: Running this file (`python -m src.server`) starts the Uvicorn server, making the API accessible on port 2103.

#### `core/app_factory.py`

*   **Purpose**: This module acts as a factory for creating and configuring the FastAPI application instance. This separation of concerns keeps `server.py` clean and focused on defining endpoints.
*   **Key Functions**:
    *   **`create_app()`**: This function is responsible for:
        1.  Initializing the `FastAPI` application.
        2.  Configuring CORS (Cross-Origin Resource Sharing) middleware to allow the frontend to communicate with the API.
        3.  Setting up all security-related middleware in the correct order, including authentication, rate limiting, and security headers.
        4.  Initializing the database connection on startup.
    *   **`run_server()`**: A convenience function that starts the Uvicorn web server with the correct settings (host, port, reload, etc.).

### 2.2. Configuration

#### `env_loader.py`

*   **Purpose**: This utility module is responsible for loading environment variables into the application. It's designed to be flexible for different environments.
*   **Functionality**: It automatically finds and loads a `.env` file. It first checks for a path specified in an `ENV_FILE_PATH` environment variable, which is useful for production deployments where the configuration might be stored outside the project directory. If that's not found, it falls back to a local `.env` file in the project root. This allows developers to have their own local configuration without affecting the production setup.

#### `config.py`

*   **Purpose**: This is the central configuration file for the entire application. It acts as a single source of truth for all settings.
*   **Functionality**:
    *   It imports and executes `load_environment()` from `env_loader.py` to ensure all environment variables are loaded at startup.
    *   It reads all the environment variables (e.g., API keys, database settings, model names, feature flags) and stores them in Python constants.
    *   It performs validation checks at startup to ensure that all required environment variables are set, preventing runtime errors. For example, it will raise an error if `PINECONE_API_KEY` is missing.
    *   It includes logic to print a summary of the loaded configuration when in debug mode, which is very helpful for development.

### 2.3. RAG Workflow

#### `workflow.py`

*   **Purpose**: This is the heart of the RAG system. It defines the entire conversational logic as a state machine using the `LangGraph` library.
*   **Key Components**:
    *   **`ConversationState`**: A typed dictionary that defines the structure of the data that flows through the graph. It holds everything from the user's query and chat history to intermediate results like detected intent, search results, and final response.
    *   **Nodes**: Each function in this file (e.g., `detect_intent_and_language`, `business_reasoner`, `search_products_k20`, `format_final_response`) represents a node in the graph—a single step in the processing pipeline.
    *   **`timing_wrapper`**: A decorator that wraps each node to measure its execution time and capture analytics data.
    *   **Edges and Conditional Edges**: The file defines the connections between the nodes. `add_edge` creates a direct link, while `add_conditional_edges` creates decision points in the graph (e.g., `route_intent`), allowing the workflow to branch based on the current state.
    *   **`create_workflow()`**: This function assembles all the nodes and edges into a compiled, executable `StateGraph`.
*   **Workflow Logic**:
    1.  The graph starts at the `detect_intent` node.
    2.  Based on the intent, it conditionally routes to different paths: simple intents go directly to formatting a response, while product-related queries go through the full RAG pipeline.
    3.  The pipeline involves business reasoning, query optimization, searching Pinecone, and finally, formatting the response.
    4.  It also includes a sophisticated path for handling follow-up questions by checking a session cache first.


