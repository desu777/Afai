export interface Message {
  id: string;
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
  access_level: 'visionary_expert';
}

export interface ChatResponse {
  response: string;
  success: boolean;
  error?: string;
  execution_time?: number;
  session_id?: string;
}

export interface WidgetConfig {
  apiToken: string;
  apiUrl: string;
  position?: 'bottom-right' | 'bottom-left';
  theme?: 'aquaforest' | 'custom';
}

export interface WidgetState {
  isOpen: boolean;
  currentView: 'welcome' | 'chat';
  messages: Message[];
  isLoading: boolean;
  error?: string;
  sessionId?: string;
}