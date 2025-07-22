export interface Message {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  imageUrl?: string;
  fileName?: string;
  fileSize?: number;
  fileType?: 'image' | 'pdf';
}

export interface ChatRequest {
  message: string;
  chat_history: Array<{role: string; content: string}>;
  debug: boolean;
  image_url?: string;
  session_id?: string;
  access_level?: string;
}

export interface ChatResponse {
  response: string;
  success: boolean;
  error?: string;
  execution_time?: number;
  session_id?: string;
}

export interface FeedbackRequest {
  message_id?: number;
  rating?: number; // 1-5 stars
  comment: string;
  user_type: 'visionary_expert' | 'admin';
}

export interface FeedbackResponse {
  success: boolean;
  feedback_id?: number;
  message: string;
}

export interface ApiError {
  message: string;
  status?: number;
}

// Admin Panel Types
export interface FeedbackItem {
  id: number;
  message_id?: number;
  rating?: number;
  comment: string;
  user_type: string;
  created_at: string;
}

export interface FeedbackSummaryResponse {
  success: boolean;
  summary: {
    total_feedback: number;
    average_rating: number;
    rating_distribution: Record<number, number>;
    recent_feedback: FeedbackItem[];
  };
}

export interface AnalyticsItem {
  id: number;
  user_query: string;
  detected_language: string;
  intent_detector_decision: string;
  intent_confidence: number;
  business_reasoner_decision: string;
  business_corrections: string;
  query_optimizer_queries: string[];
  pinecone_results_count: number;
  pinecone_top_results: Array<{product: string; score: number}>;
  filter_decision: string;
  filtered_results_count: number;
  confidence_score: number;
  confidence_reasoning: string;
  final_response: string;
  total_execution_time: number;
  node_timings: Record<string, number>;
  escalated: boolean;
  created_at: string;
}

export interface AnalyticsSummaryResponse {
  success: boolean;
  summary: {
    total_queries: number;
    average_execution_time: number;
    confidence_distribution: {
      high_confidence: number;
      medium_confidence: number;
      low_confidence: number;
    };
    intent_distribution: Record<string, number>;
    language_distribution: Record<string, number>;
    escalation_rate: number;
  };
}

export interface AnalyticsQueryRequest {
  start_date?: string;
  end_date?: string;
  limit: number;
}

export interface AnalyticsQueryResponse {
  success: boolean;
  count: number;
  data: AnalyticsItem[];
}

// 🚀 NEW: Streaming workflow types
export interface WorkflowUpdate {
  node: string;
  status: 'processing' | 'complete' | 'error';
  message: string;
  elapsed_time: number;
}

// Response format types
export type ResponseFormat = 'visionary_expert' | 'ghostwriter';

export interface ResponseFormatOption {
  id: ResponseFormat;
  label: string;
  description: string;
} 