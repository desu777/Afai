import { ChatRequest, ChatResponse } from '../types';

export class ChatAPI {
  private baseUrl: string;
  private authToken: string;

  constructor(baseUrl: string, authToken: string) {
    this.baseUrl = baseUrl;
    this.authToken = authToken;
  }

  async sendMessage(
    message: string,
    chatHistory: Array<{role: string; content: string}> = [],
    imageUrl?: string,
    sessionId?: string
  ): Promise<ChatResponse> {
    const request: ChatRequest = {
      message,
      chat_history: chatHistory,
      debug: false,
      image_url: imageUrl,
      session_id: sessionId,
      access_level: 'visionary_expert'
    };

    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Aquaforest-Auth': this.authToken,
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        headers: {
          'X-Aquaforest-Auth': this.authToken,
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}