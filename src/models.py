"""
Data models for Aquaforest RAG System
Defines all TypedDict and Pydantic models
"""
from typing import TypedDict, List, Dict, Literal, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class Intent(str, Enum):
    GREETING = "greeting"
    BUSINESS = "business"
    PRODUCT_QUERY = "product_query"
    PURCHASE_INQUIRY = "purchase_inquiry"
    COMPETITOR = "competitor"
    CENSORED = "censored"
    FOLLOW_UP = "follow_up"
    SUPPORT = "support"
    OTHER = "other"

class Domain(str, Enum):
    SEAWATER = "seawater"
    FRESHWATER = "freshwater"
    UNIVERSAL = "universal"

class ConversationState(TypedDict):
    """State object that flows through the LangGraph workflow"""
    # Core fields
    user_query: str
    detected_language: str
    intent: Intent
    product_names: List[str]
    original_query: str
    optimized_queries: List[str]
    search_results: List[Dict[str, Any]]
    confidence: float
    evaluation_reasoning: str
    iteration: int
    final_response: str
    escalate: bool
    domain_filter: Optional[Domain]
    chat_history: List[Dict[str, str]]
    context_cache: List[Dict[str, Any]]
    
    # Analytics fields
    node_timings: Dict[str, float]  # Tracks execution time for each node
    routing_decisions: List[Dict[str, str]]  # Tracks routing decisions
    total_execution_time: float  # Total workflow execution time
    
    # Optional fields added during workflow
    business_analysis: Optional[Dict[str, Any]]
    requested_category: Optional[str]
    category_products: Optional[List[str]]
    identified_problem: Optional[str]
    recommended_solutions: Optional[List[str]]
    maintenance_solutions: Optional[List[str]]
    solution_note: Optional[str]
    comparison_products: Optional[List[str]]
    filter_reasoning: Optional[str]
    domain_warning: Optional[str]
    purchase_product: Optional[str]
    context_warning: Optional[str]
    knowledge_assessment: Optional[str]
    domain_assessment: Optional[str]
    category_coverage: Optional[str]

class SearchResult(BaseModel):
    """Pinecone search result with metadata"""
    id: str
    score: float
    metadata: Dict[str, Any]
    
    @property
    def product_name(self) -> str:
        return self.metadata.get("product_name", "")
    
    @property
    def domain(self) -> str:
        return self.metadata.get("domain", "")
    
    @property
    def content_type(self) -> str:
        return self.metadata.get("content_type", "")

class IntentDetectionResult(BaseModel):
    """Result from intent detection"""
    intent: Intent
    language: str
    confidence: float = Field(ge=0, le=1)

class ProductInfo(BaseModel):
    """Product information from search results"""
    content_type: str
    domain: Domain
    product_name: str
    title_en: str
    title_pl: Optional[str] = None
    full_content_en: str
    full_content_pl: Optional[str] = None
    dosage_amount: Optional[str] = None
    dosage_volume: Optional[str] = None
    dosage_frequency: Optional[str] = None
    dosage_timing: Optional[str] = None
    compatible_products: List[str] = Field(default_factory=list)
    sizes_available: List[str] = Field(default_factory=list)
    url_en: str
    url_pl: Optional[str] = None
    score: float = Field(ge=0, le=1)

class QueryOptimizationResult(BaseModel):
    """Result from query optimization"""
    original_query: str
    optimized_queries: List[str]
    detected_products: List[str]
    detected_problems: List[str]