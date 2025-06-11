import { useState } from 'react'
import { Message } from '../types'
import { apiService } from '../services/api'
import Header from './Header'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import SplashScreen from './SplashScreen'

const ChatInterface: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessLevel, setAccessLevel] = useState<'test' | 'admin'>('test');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessageId = messages.length + 1;
    const userMessage: Message = {
      id: userMessageId,
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
        id: userMessageId + 1,
        type: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiResponse]);

    } catch (error) {
      console.error('❌ [Chat] Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: userMessageId + 1,
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

  const handleNewChat = () => {
    setMessages([]);
    setInputValue('');
    setIsLoading(false);
  };

  const handleAuthenticate = (level: 'test' | 'admin') => {
    setAccessLevel(level);
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return <SplashScreen onAuthenticate={handleAuthenticate} />;
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100">
      <Header onNewChat={handleNewChat} accessLevel={accessLevel} />
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