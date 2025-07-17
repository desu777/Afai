#!/bin/bash
# Aquaforest RAG Backend Startup Script for WSL/Linux
# Sets external .env path and starts the server

echo "============================================"
echo "     Aquaforest RAG Backend Server"
echo "============================================"
echo ""

# Set external .env file path (WSL format)
export ENV_FILE_PATH="/mnt/c/Users/kubas/Desktop/env/aquaforest/.env"

# Check if external .env file exists
if [ -f "$ENV_FILE_PATH" ]; then
    echo "[INFO] External .env file found: $ENV_FILE_PATH"
else
    echo "[WARNING] External .env file not found: $ENV_FILE_PATH"
    echo "[INFO] Will try to use local .env or system environment variables"
fi

echo ""
echo "[INFO] Starting Python server..."
echo "[INFO] ENV_FILE_PATH: $ENV_FILE_PATH"
echo ""

# Start the Python server
python3 src/server.py

# Handle errors
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "[ERROR] Server failed to start. Error code: $exit_code"
    echo "[INFO] Check that all required environment variables are set"
    echo "[INFO] and that all Python dependencies are installed"
    echo ""
    read -p "Press any key to continue..."
fi