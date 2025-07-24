"""
Data Loader Module
JSON mapping data loading extracted from business_reasoner.py
"""
import json
from pathlib import Path
from typing import List, Dict
from config import debug_print, PRODUCTS_FILE_PATH, PRODUCTS_TURBO_FILE_PATH, DISABLE_BUSINESS_MAPPINGS, ENABLE_COMPETITORS_ONLY

class DataLoader:
    def __init__(self):
        # Load all data sources for comprehensive LLM analysis
        self.products_list = self._load_products_list()
        self.products_knowledge = self._load_products_knowledge()
        
        # Load mapping data based on configuration modes
        if ENABLE_COMPETITORS_ONLY:
            self._load_competitors_only()
            debug_print(f"[API] VERSION 4.1 COMPETITORS-ONLY initialized")
            debug_print(f"[DATA] Loaded {len(self.products_knowledge)} products")
            debug_print(f"[COMP] Competitors: {len(self.competitors_data.get('competitors', {}))}")
            debug_print("[WARN] Other mappings disabled - using LLM intelligence only")
        elif not DISABLE_BUSINESS_MAPPINGS:
            self._load_mapping_data()
            debug_print(f"[API] VERSION 4.1 REFACTORED initialized")
            debug_print(f"[DATA] Loaded {len(self.products_knowledge)} products")
            debug_print(f"[COMP] Competitors: {len(self.competitors_data.get('competitors', {}))}")
            debug_print(f"[SCENARIOS] Scenarios: {len(self.scenarios_data.get('tank_setup_scenarios', {}))}")
            debug_print(f"[TARGET] Use cases: {len(self.use_cases_data.get('use_cases', {}))}")
            debug_print(f"[GROUPS] Product groups: {len(self.product_groups_data.get('product_groups', {}))}")
        else:
            debug_print(f"[API] VERSION 4.1 MAPPINGS DISABLED - Pure LLM mode")
            debug_print(f"[DATA] Loaded {len(self.products_knowledge)} products")
            debug_print("[WARN] All mappings disabled - using pure LLM intelligence")
            self._initialize_fallback_mappings()

    def _load_products_list(self) -> List[str]:
        """Load simple product names list"""
        try:
            with open(PRODUCTS_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            debug_print(f"[ERROR] Error loading products list: {e}")
            return []
    
    def _load_products_knowledge(self) -> List[Dict]:
        """Load detailed product knowledge from products_turbo.json"""
        try:
            # Use configured path from config.py
            with open(PRODUCTS_TURBO_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                debug_print(f"[OK] Loaded products_turbo.json")
                return data
        except Exception as e:
            debug_print(f"[ERROR] Error loading products_turbo.json: {e}")
            return []
    
    def _load_mapping_data(self):
        """Load comprehensive mapping data from JSON files for LLM"""
        try:
            mapping_dir = Path(__file__).parent.parent.absolute() / "mapping"
            
            # Load competitors mapping
            with open(mapping_dir / "competitors.json", 'r', encoding='utf-8') as f:
                self.competitors_data = json.load(f)
                debug_print("[OK] Loaded competitors mapping")
            
            # Load scenarios mapping  
            with open(mapping_dir / "scenarios.json", 'r', encoding='utf-8') as f:
                self.scenarios_data = json.load(f)
                debug_print("[OK] Loaded scenarios mapping")
            
            # Load product groups mapping
            with open(mapping_dir / "products_groups.json", 'r', encoding='utf-8') as f:
                self.product_groups_data = json.load(f)
                debug_print("[OK] Loaded product groups mapping")
            
            # Load use cases mapping
            with open(mapping_dir / "use_cases.json", 'r', encoding='utf-8') as f:
                self.use_cases_data = json.load(f)
                debug_print("[OK] Loaded use cases mapping")
                
            debug_print(f"[API] Full LLM mapping system loaded successfully!")
            
        except Exception as e:
            debug_print(f"[ERROR] Failed to load mapping data: {e}")
            # Initialize empty mappings as fallback
            self._initialize_fallback_mappings()
    
    def _load_competitors_only(self):
        """Load only competitors mapping, initialize others as empty"""
        try:
            mapping_dir = Path(__file__).parent.parent.absolute() / "mapping"
            
            # Load only competitors mapping
            with open(mapping_dir / "competitors.json", 'r', encoding='utf-8') as f:
                self.competitors_data = json.load(f)
                debug_print("[OK] Loaded competitors mapping (ONLY)")
            
            # Initialize other mappings as empty
            self.scenarios_data = {"tank_setup_scenarios": {}}
            self.product_groups_data = {"product_groups": {}}
            self.use_cases_data = {"use_cases": {}}
            
            debug_print(f"[TARGET] Competitors-only mode: {len(self.competitors_data.get('competitors', {}))} competitor categories loaded")
            
        except Exception as e:
            debug_print(f"[ERROR] Failed to load competitors mapping: {e}")
            # Fallback to empty mappings
            self._initialize_fallback_mappings()
    
    def _initialize_fallback_mappings(self):
        """Initialize empty mappings if JSON loading fails"""
        debug_print("[WARN] Using empty fallback mappings")
        self.competitors_data = {"competitors": {}, "response_strategies": {}}
        self.scenarios_data = {"tank_setup_scenarios": {}}
        self.product_groups_data = {"product_groups": {}}
        self.use_cases_data = {"use_cases": {}}
        
    def validate_product_exists(self, product_name: str) -> bool:
        """Validate if product exists in knowledge base"""
        product_name_lower = product_name.lower()
        return any(prod.lower() == product_name_lower for prod in self.products_list)