"""
Environment loader for Aquaforest RAG System
Handles loading of environment variables from external or local .env files
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """
    Load environment variables from external .env file or fallback to local.
    
    Priority:
    1. ENV_FILE_PATH environment variable (for external .env location)
    2. Local .env file in project root
    3. No .env file (use system environment variables only)
    
    Returns:
        bool: True if .env file was loaded successfully, False otherwise
    """
    # Check for external .env file path via environment variable
    external_env_path = os.getenv("ENV_FILE_PATH")
    
    if external_env_path:
        external_path = Path(external_env_path)
        if external_path.exists() and external_path.is_file():
            load_dotenv(dotenv_path=external_path)
            
            # Debug info only in test environment
            if os.getenv("TEST_ENV", "false").lower() == "true":
                print(f"🔧 External .env loaded from: {external_path}")
            
            return True
        else:
            # Debug warning for missing external file
            if os.getenv("TEST_ENV", "false").lower() == "true":
                print(f"⚠️  External .env file not found at: {external_path}")
    
    # Fallback to local .env file in project root
    project_root = Path(__file__).parent.parent
    local_env_path = project_root / ".env"
    
    if local_env_path.exists():
        load_dotenv(dotenv_path=local_env_path)
        
        # Debug info only in test environment
        if os.getenv("TEST_ENV", "false").lower() == "true":
            print(f"🔧 Local .env loaded from: {local_env_path}")
        
        return True
    
    # No .env file found - use system environment variables only
    if os.getenv("TEST_ENV", "false").lower() == "true":
        print("🔧 No .env file found - using system environment variables only")
    
    return False


def get_env_info():
    """
    Get information about current environment configuration.
    
    Returns:
        dict: Environment configuration information
    """
    external_env_path = os.getenv("ENV_FILE_PATH")
    project_root = Path(__file__).parent.parent
    local_env_path = project_root / ".env"
    
    info = {
        "external_path": external_env_path,
        "external_exists": Path(external_env_path).exists() if external_env_path else False,
        "local_path": str(local_env_path),
        "local_exists": local_env_path.exists(),
        "active_source": None
    }
    
    # Determine active source
    if external_env_path and Path(external_env_path).exists():
        info["active_source"] = "external"
    elif local_env_path.exists():
        info["active_source"] = "local"
    else:
        info["active_source"] = "system"
    
    return info