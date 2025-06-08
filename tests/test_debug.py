"""
Debug script to test individual components
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *
from src.models import ConversationState
from src.intent_detector import IntentDetector
from src.query_optimizer import QueryOptimizer
from src.pinecone_client import PineconeSearchClient

def test_intent_detection():
    """Test intent detection"""
    print("=== Testing Intent Detection ===")
    detector = IntentDetector()
    
    test_queries = [
        "Cześć!",
        "moje korale bieleją",
        "chcę współpracować",
        "jak produkujecie Ca plus?",
        "Red Sea jest lepszy?"
    ]
    
    for query in test_queries:
        state = {"user_query": query}
        result = detector.detect(state)
        print(f"Query: '{query}'")
        print(f"  Intent: {result.get('intent')}")
        print(f"  Language: {result.get('detected_language')}")
        print()

def test_query_optimization():
    """Test query optimization"""
    print("=== Testing Query Optimization ===")
    optimizer = QueryOptimizer()
    
    state = {
        "user_query": "moje korale bieleją",
        "detected_language": "pl"
    }
    
    result = optimizer.optimize(state)
    print(f"Original: {result['original_query']}")
    print(f"Optimized: {result['optimized_queries']}")
    print()

def test_pinecone_connection():
    """Test Pinecone connection"""
    print("=== Testing Pinecone Connection ===")
    try:
        client = PineconeSearchClient()
        print("✅ Pinecone connected successfully")
        print(f"Index: {PINECONE_INDEX_NAME}")
        
        # Get and print index statistics
        stats = client.index.describe_index_stats()
        print(f"✅ Index stats: {stats}")
        
        # Test embedding
        embedding = client._get_embedding("test query")
        print(f"✅ Embedding dimension: {len(embedding)}")
        
    except Exception as e:
        print(f"❌ Pinecone error: {e}")

def check_environment():
    """Check environment setup"""
    print("=== Environment Check ===")
    
    checks = [
        ("OPENAI_API_KEY", OPENAI_API_KEY),
        ("PINECONE_API_KEY", PINECONE_API_KEY),
        ("PINECONE_INDEX_NAME", PINECONE_INDEX_NAME),
        ("PRODUCTS_FILE_PATH", PRODUCTS_FILE_PATH)
    ]
    
    for name, value in checks:
        if value:
            print(f"✅ {name}: {'*' * 10} (set)")
        else:
            print(f"❌ {name}: NOT SET")
    
    # Check products file
    if os.path.exists(PRODUCTS_FILE_PATH):
        print(f"✅ Products file exists: {PRODUCTS_FILE_PATH}")
        import json
        with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
            products = json.load(f)
            print(f"   Found {len(products)} products")
    else:
        print(f"❌ Products file NOT FOUND: {PRODUCTS_FILE_PATH}")

if __name__ == "__main__":
    check_environment()
    print("\n" + "="*50 + "\n")
    
    try:
        test_intent_detection()
    except Exception as e:
        print(f"Intent detection failed: {e}")
    
    try:
        test_query_optimization()
    except Exception as e:
        print(f"Query optimization failed: {e}")
    
    try:
        test_pinecone_connection()
    except Exception as e:
        print(f"Pinecone connection failed: {e}")