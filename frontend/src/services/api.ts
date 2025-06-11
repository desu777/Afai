import { 
  ChatRequest, 
  ChatResponse, 
  ApiError, 
  FeedbackRequest, 
  FeedbackResponse,
  FeedbackSummaryResponse,
  AnalyticsSummaryResponse,
  AnalyticsQueryRequest,
  AnalyticsQueryResponse
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:2103';

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (import.meta.env.VITE_TEST_ENV === 'true') {
      console.log(`🔍 [API] Making request to: ${url}`, config);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      
      if (import.meta.env.VITE_TEST_ENV === 'true') {
        console.log(`✅ [API] Response received:`, data);
      }
      
      return data;
    } catch (error) {
      if (import.meta.env.VITE_TEST_ENV === 'true') {
        console.error(`❌ [API] Request failed:`, error);
      }
      
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        status: error instanceof Error && 'status' in error ? (error as any).status : undefined
      };
      
      throw apiError;
    }
  }

  async sendMessage(
    message: string, 
    chatHistory: Array<{role: string; content: string}> = [],
    debug: boolean = false
  ): Promise<ChatResponse> {
    const requestData: ChatRequest = {
      message,
      chat_history: chatHistory,
      debug
    };

    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  async healthCheck(): Promise<{status: string; debug_mode: boolean; timestamp: number}> {
    return this.request('/health');
  }

  async submitFeedback(feedback: FeedbackRequest): Promise<FeedbackResponse> {
    return this.request<FeedbackResponse>('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  // Admin Panel Methods
  async getFeedbackSummary(): Promise<FeedbackSummaryResponse> {
    return this.request<FeedbackSummaryResponse>('/feedback/summary');
  }

  async getAnalyticsSummary(): Promise<AnalyticsSummaryResponse> {
    return this.request<AnalyticsSummaryResponse>('/analytics/summary');
  }

  async getAnalyticsData(queryParams: AnalyticsQueryRequest): Promise<AnalyticsQueryResponse> {
    return this.request<AnalyticsQueryResponse>('/analytics/query', {
      method: 'POST',
      body: JSON.stringify(queryParams),
    });
  }

  async exportFeedbackCSV(startDate?: string, endDate?: string): Promise<Blob> {
    let url = `${API_BASE_URL}/feedback/export/csv`;
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (params.toString()) url += '?' + params.toString();

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to export feedback CSV`);
    }
    return response.blob();
  }

  async exportAnalyticsCSV(startDate?: string, endDate?: string): Promise<Blob> {
    let url = `${API_BASE_URL}/analytics/export/csv`;
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (params.toString()) url += '?' + params.toString();

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to export analytics CSV`);
    }
    return response.blob();
  }
}

export const apiService = new ApiService() 