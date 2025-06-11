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

export interface ApiError {
  message: string;
  status?: number;
} 