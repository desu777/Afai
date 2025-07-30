import type { ChatRequest, ChatResponse, WorkflowUpdate } from '../types';

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

  async sendMessageStream(
    message: string,
    chatHistory: Array<{role: string; content: string}> = [],
    onUpdate: (update: WorkflowUpdate) => void,
    imageUrl?: string,
    sessionId?: string
  ): Promise<string> {
    // Fallback for older browsers that don't support ReadableStream
    if (!('ReadableStream' in window) || !window.ReadableStream) {
      const response = await this.sendMessage(message, chatHistory, imageUrl, sessionId);
      return response.response || '';
    }

    const request: ChatRequest = {
      message,
      chat_history: chatHistory,
      debug: false,
      image_url: imageUrl,
      session_id: sessionId,
      access_level: 'visionary_expert'
    };

    const response = await fetch(`${this.baseUrl}/chat/stream`, {
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

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body reader available');
    }

    const decoder = new TextDecoder();
    let finalResponse = '';
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6);
              if (jsonStr.trim()) {
                const update: WorkflowUpdate = JSON.parse(jsonStr);
                onUpdate(update);
                
                if (update.status === 'complete' && update.node === 'complete') {
                  finalResponse = update.message;
                }
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', e);
            }
          }
        }
      }

      // Process any remaining data in buffer
      if (buffer.trim() && buffer.startsWith('data: ')) {
        try {
          const jsonStr = buffer.slice(6);
          if (jsonStr.trim()) {
            const update: WorkflowUpdate = JSON.parse(jsonStr);
            onUpdate(update);
            if (update.status === 'complete' && update.node === 'complete') {
              finalResponse = update.message;
            }
          }
        } catch (e) {
          console.warn('Failed to parse final buffer data:', e);
        }
      }
      
    } finally {
      reader.releaseLock();
    }

    return finalResponse;
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