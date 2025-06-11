import { useState } from 'react'
import { Message } from '../types'
import { apiService } from '../services/api'
import Header from './Header'
import MessageList from './MessageList'
import ChatInput from './ChatInput'

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'assistant',
      content: '🐠 Welcome! I\'m AF AI, your Aquaforest assistant. I can help you with aquarium products, dosing calculations, and problem solving in any language. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Convert messages to chat history format for API
      const chatHistory = messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Debug mode based on environment variable
      const debugMode = import.meta.env.VITE_TEST_ENV === 'true';

      if (debugMode) {
        console.log('🔍 [Chat] Sending message:', currentInput);
        console.log('🔍 [Chat] Chat history:', chatHistory);
      }

      // Send message to API
      const response = await apiService.sendMessage(currentInput, chatHistory, debugMode);

      if (debugMode) {
        console.log('✅ [Chat] Response received:', response);
      }

      // Add AI response
      const aiResponse: Message = {
        id: messages.length + 2,
        type: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiResponse]);

    } catch (error) {
      console.error('❌ [Chat] Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: messages.length + 2,
        type: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please try again or contact support@aquaforest.eu if the problem persists.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuerySelect = (query: string) => {
    setInputValue(query);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100">
      <Header />
      <MessageList 
        messages={messages} 
        isLoading={isLoading} 
        onQuerySelect={handleQuerySelect} 
      />
      <ChatInput
        inputValue={inputValue}
        isLoading={isLoading}
        onInputChange={setInputValue}
        onSend={handleSend}
      />
    </div>
  );
};

export default ChatInterface 