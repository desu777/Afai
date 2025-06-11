export interface Message {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  chat_history: Array<{role: string; content: string}>;
  debug: boolean;
}

export interface ChatResponse {
  response: string;
  success: boolean;
  error?: string;
  execution_time?: number;
}

export interface FeedbackRequest {
  message_id?: number;
  rating?: number; // 1-5 stars
  comment: string;
  user_type: 'test' | 'admin';
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