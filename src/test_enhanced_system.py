#!/usr/bin/env python3
"""
Test script for Enhanced Aquaforest RAG System v3.0
Tests the new mapping system with competitor detection, scenarios, and use cases
"""

import sys
import os
sys.path.append('src')

from business_reasoner import BusinessReasoner
from models import ConversationState, Intent

def test_enhanced_system():
    print("🚀 Testing Enhanced Aquaforest RAG System v3.0")
    print("=" * 60)
    
    # Initialize business reasoner
    reasoner = BusinessReasoner()
    
    # Test 1: Competitor Detection
    print("\n🏢 TEST 1: Competitor Detection")
    print("-" * 40)
    
    state1 = {
        "user_query": "I'm using Marco Rock in my new tank, what AF products should I use?",
        "chat_history": [],
        "search_results": []
    }
    
    result1 = reasoner.analyze(state1)
    print(f"Query: {state1['user_query']}")
    print(f"Intent: {result1.get('intent', 'Not detected')}")
    print(f"Competitor Info: {result1.get('competitor_info', 'None')}")
    
    # Test 2: New Tank Setup Scenario
    print("\n📋 TEST 2: New Tank Setup Scenario")
    print("-" * 40)
    
    state2 = {
        "user_query": "Setting up a new reef tank, what products do I need for kickstart?",
        "chat_history": [],
        "search_results": []
    }
    
    result2 = reasoner.analyze(state2)
    print(f"Query: {state2['user_query']}")
    print(f"Scenario Info: {result2.get('scenario_info', 'None')}")
    print(f"Business Recommendations: {len(result2.get('business_recommendations', []))} items")
    
    # Test 3: Fish Feeding Use Case
    print("\n🐟 TEST 3: Fish Feeding Use Case")
    print("-" * 40)
    
    state3 = {
        "user_query": "What fish food do you recommend for marine fish?",
        "chat_history": [],
        "search_results": []
    }
    
    result3 = reasoner.analyze(state3)
    print(f"Query: {state3['user_query']}")
    print(f"Use Case Info: {result3.get('use_case_info', 'None')}")
    
    # Test 4: Water Chemistry Focus
    print("\n🧪 TEST 4: Water Chemistry Focus")  
    print("-" * 40)
    
    state4 = {
        "user_query": "My calcium and alkalinity are unstable, what components should I use?",
        "chat_history": [],
        "search_results": []
    }
    
    result4 = reasoner.analyze(state4)
    print(f"Query: {state4['user_query']}")
    print(f"Use Case Info: {result4.get('use_case_info', 'None')}")
    print(f"Business Recommendations: {len(result4.get('business_recommendations', []))} items")
    
    print("\n✅ Enhanced System Test Complete!")
    print("=" * 60)
    
    # Test mapping data loading
    print(f"\n📊 SYSTEM STATS:")
    print(f"- Competitors tracked: {len(reasoner.all_competitors)}")
    print(f"- Scenarios available: {len(reasoner.scenarios_data.get('tank_setup_scenarios', {}))}")
    print(f"- Use cases available: {len(reasoner.use_cases_data.get('use_cases', {}))}")
    print(f"- Product groups: {len(reasoner.product_groups_data.get('product_groups', {}))}")

if __name__ == "__main__":
    test_enhanced_system() 