"""
Enhanced Logging System for Aquaforest RAG Backend
Centralized, elegant logging with hierarchical structure and consistent formatting
"""
import os
import time
from typing import Optional, Dict, Any
from datetime import datetime

class AquaforestLogger:
    """
    Enhanced logger with elegant formatting and hierarchical structure
    """
    
    # Log categories with consistent ASCII icons
    CATEGORIES = {
        'CONFIGURATION': '[CONFIG]',
        'WORKFLOW': '[WORKFLOW]',
        'STREAMING': '[STREAM]',
        'SECURITY': '[AUTH]',
        'DATABASE': '[DB]',
        'ERROR': '[ERROR]',
        'PERFORMANCE': '[PERF]',
        'SESSION': '[SESSION]',
        'API': '[API]',
        'RATE_LIMIT': '[LIMIT]',
        'SEARCH': '[SEARCH]',
        'ANALYSIS': '[AI]',
        'CACHE': '[CACHE]',
        'DEBUG': '[DEBUG]'
    }
    
    # Indentation levels
    MAIN_LEVEL = ""
    SUB_LEVEL = "   "
    DETAIL_LEVEL = "      "
    
    def __init__(self, test_env: bool = None):
        """Initialize logger with TEST_ENV setting"""
        if test_env is None:
            self.test_env = os.getenv("TEST_ENV", "false").lower() == "true"
        else:
            self.test_env = test_env
            
        self.start_time = time.time()
        self.current_session = None
    
    def is_enabled(self) -> bool:
        """Check if logging is enabled"""
        return self.test_env
    
    def _format_timestamp(self) -> str:
        """Format current timestamp"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    def _get_emoji(self, category: str) -> str:
        """Get emoji for category"""
        return self.CATEGORIES.get(category.upper(), '[INFO]')
    
    def separator(self, title: str = "", width: int = 60, char: str = "="):
        """Print elegant separator with optional title"""
        if not self.is_enabled():
            return
            
        separator_line = char * width
        if title:
            print(f"\n{separator_line}")
            print(f"{title}")
            print(f"{separator_line}")
        else:
            print(f"{separator_line}")
    
    def header(self, title: str, width: int = 60):
        """Print section header with separators"""
        if not self.is_enabled():
            return
            
        self.separator(title, width)
    
    def log(self, category: str, message: str, level: str = "MAIN", 
            session_id: str = None, timing: float = None):
        """Main logging method with hierarchical formatting"""
        if not self.is_enabled():
            return
            
        emoji = self._get_emoji(category)
        
        # Determine indentation
        if level == "MAIN":
            indent = self.MAIN_LEVEL
        elif level == "SUB":
            indent = self.SUB_LEVEL
        elif level == "DETAIL":
            indent = self.DETAIL_LEVEL
        else:
            indent = self.MAIN_LEVEL
        
        # Format message with session if provided
        if session_id:
            formatted_message = f"{emoji} [{category}] Session {session_id} - {message}"
        else:
            formatted_message = f"{emoji} [{category}] {message}"
        
        # Add timing if provided
        if timing:
            formatted_message += f" ({timing:.3f}s)"
        
        # Print with indentation
        print(f"{indent}{formatted_message}")
    
    def configuration(self, message: str, level: str = "MAIN"):
        """Log configuration messages"""
        self.log("CONFIGURATION", message, level)
    
    def workflow(self, message: str, level: str = "MAIN", timing: float = None):
        """Log workflow messages"""
        self.log("WORKFLOW", message, level, timing=timing)
    
    def streaming(self, message: str, session_id: str = None, level: str = "MAIN"):
        """Log streaming messages"""
        self.log("STREAMING", message, level, session_id=session_id)
    
    def security(self, message: str, level: str = "MAIN"):
        """Log security messages"""
        self.log("SECURITY", message, level)
    
    def database(self, message: str, level: str = "MAIN"):
        """Log database messages"""
        self.log("DATABASE", message, level)
    
    def error(self, message: str, level: str = "MAIN"):
        """Log error messages"""
        self.log("ERROR", message, level)
    
    def performance(self, message: str, timing: float = None, level: str = "MAIN"):
        """Log performance messages"""
        self.log("PERFORMANCE", message, level, timing=timing)
    
    def session(self, message: str, session_id: str = None, level: str = "MAIN"):
        """Log session messages"""
        self.log("SESSION", message, level, session_id=session_id)
    
    def api(self, message: str, level: str = "MAIN"):
        """Log API messages"""
        self.log("API", message, level)
    
    def rate_limit(self, message: str, level: str = "MAIN"):
        """Log rate limiting messages"""
        self.log("RATE_LIMIT", message, level)
    
    def search(self, message: str, level: str = "MAIN"):
        """Log search messages"""
        self.log("SEARCH", message, level)
    
    def analysis(self, message: str, level: str = "MAIN"):
        """Log analysis messages"""
        self.log("ANALYSIS", message, level)
    
    def cache(self, message: str, level: str = "MAIN"):
        """Log cache messages"""
        self.log("CACHE", message, level)
    
    def debug(self, message: str, level: str = "MAIN"):
        """Log debug messages"""
        self.log("DEBUG", message, level)
    
    def node_start(self, node_name: str, message: str, session_id: str = None):
        """Log workflow node start"""
        elapsed = time.time() - self.start_time
        self.streaming(f"Node started: {node_name} - {message}", session_id, "SUB")
        self.debug(f"Node '{node_name}' elapsed time: {elapsed:.3f}s", "DETAIL")
    
    def node_complete(self, node_name: str, execution_time: float, session_id: str = None):
        """Log workflow node completion"""
        elapsed = time.time() - self.start_time
        self.streaming(f"Node completed: {node_name}", session_id, "SUB")
        self.performance(f"Node '{node_name}' execution time: {execution_time:.3f}s", execution_time, "DETAIL")
        self.debug(f"Total elapsed time: {elapsed:.3f}s", "DETAIL")
    
    def workflow_start(self):
        """Log workflow start with elegant separator"""
        if not self.is_enabled():
            return
            
        self.separator()
        self.workflow("WORKFLOW START", "MAIN")
        self.separator()
    
    def workflow_end(self, total_time: float = None):
        """Log workflow end with elegant separator"""
        if not self.is_enabled():
            return
            
        self.separator()
        self.workflow("WORKFLOW END", "MAIN")
        self.separator()
        
        if total_time:
            self.performance(f"Total execution time: {total_time:.3f} seconds")
            print("-" * 60)

# Global logger instance
logger = AquaforestLogger()

# Convenience functions for backward compatibility
def debug_print(message: str, emoji: str = "[DEBUG]", category: str = "DEBUG"):
    """Legacy debug_print function for backward compatibility"""
    logger.log(category, message.replace(emoji, "").strip())

def log_configuration(message: str, level: str = "MAIN"):
    """Log configuration message"""
    logger.configuration(message, level)

def log_workflow(message: str, level: str = "MAIN", timing: float = None):
    """Log workflow message"""
    logger.workflow(message, level, timing)

def log_streaming(message: str, session_id: str = None, level: str = "MAIN"):
    """Log streaming message"""
    logger.streaming(message, session_id, level)

def log_error(message: str, level: str = "MAIN"):
    """Log error message"""
    logger.error(message, level)

def log_performance(message: str, timing: float = None, level: str = "MAIN"):
    """Log performance message"""
    logger.performance(message, timing, level)