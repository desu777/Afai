#!/usr/bin/env python3
"""Test ICP recommendations extraction with element separators"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.icp_scraper import ICPScraper

def test_icp_element_separators():
    """Test if recommendations are correctly extracted for individual elements"""
    
    scraper = ICPScraper()
    
    # Test with real-like ICP data with multiple elements having Zalecenia
    mock_raw_data = """
    PO4 Fosforany | 0 - 0.0300mg/l | 0.0331 mg/l | + 0.0331 mg/l | ⬆️ HIGH
    Zalecenia Uwaga! Poziom PO4 za wysoki, w celu obniżenia podmień wodę i użyj Phosphate Minus oraz NitraPhos Minus.
    Al Glin 0 - 0.0100 mg/l 0.0021 mg/l + 0.0021 mg/l
    Co Kobalt | 0.0001 - 0.0006mg/l | 0 mg/l | - 0.00035 mg/l | ⬇️ LOW
    Zalecenia Uwaga! Poziom kobaltu za niski. Pamiętaj, że maksymalna bezpieczna dawka dzienna wynosi 1 ml na 100 litrów wody. Popraw wynik stosując: Cobaltum Sugerowana dawka dla Twojego akwarium 8.05 ml
    Cr Chrom 0.0001 - 0.0004 mg/l 0 mg/l - 0.00025 mg/l
    Zalecenia Uwaga! Poziom chromu za niski. Pamiętaj, że maksymalna bezpieczna dawka dzienna wynosi 1 ml na 100 litrów wody. Popraw wynik stosując: Chromium Sugerowana dawka dla Twojego akwarium 5.75 ml
    Fe Żelazo 0.0020 - 0.0060 mg/l 0.0012 mg/l - 0.0028 mg/l
    Zalecenia Uwaga! Poziom żelaza za niski. Popraw wynik stosując: Ferrum Sugerowana dawka dla Twojego akwarium 32.2 ml
    Ca Wapń 380 - 460 mg/l 455 mg/l + 35 mg/l
    """
    
    print("🧪 Testing ICP recommendations extraction with element separators...")
    print(f"📋 Test data length: {len(mock_raw_data)} characters")
    
    recommendations = scraper.extract_icp_recommendations_text(mock_raw_data)
    
    print(f"\n✅ Found {len(recommendations)} individual recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec}")
        print("   " + "="*80)
    
    # Expected: Should find 4 separate recommendations (PO4, Co, Cr, Fe)
    print(f"\n🎯 Expected 4 recommendations, got {len(recommendations)}")
    
    if len(recommendations) >= 3:
        print("✅ SUCCESS: Found multiple individual recommendations!")
        
        # Check if they're properly separated
        has_po4 = any("PO4" in rec or "fosfor" in rec.lower() for rec in recommendations)
        has_cobalt = any("kobalt" in rec.lower() for rec in recommendations)
        has_chrome = any("chrom" in rec.lower() for rec in recommendations)
        has_iron = any("żelaz" in rec.lower() for rec in recommendations)
        
        print(f"   - PO4 recommendation: {'✅' if has_po4 else '❌'}")
        print(f"   - Cobalt recommendation: {'✅' if has_cobalt else '❌'}")
        print(f"   - Chrome recommendation: {'✅' if has_chrome else '❌'}")
        print(f"   - Iron recommendation: {'✅' if has_iron else '❌'}")
        
    else:
        print("❌ FAILED: Should have found at least 3 individual recommendations")

if __name__ == "__main__":
    test_icp_element_separators() 