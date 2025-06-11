import { useState, useEffect } from 'react'
import { Message } from '../types'
import { apiService } from '../services/api'
import Header from './Header'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import SplashScreen from './SplashScreen'
import AdminFeedbackPanel from './AdminFeedbackPanel'
import AdminAnalyticsPanel from './AdminAnalyticsPanel'

const ChatInterface: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const [accessLevel, setAccessLevel] = useState<'test' | 'admin'>('test');
  const [activeView, setActiveView] = useState<'chat' | 'feedback' | 'analytics'>('chat');
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
    setActiveView('chat');
  };

  const handleAuthenticate = (level: 'test' | 'admin') => {
    setIsTransitioning(true);
    
    // Start fade out splash
    setTimeout(() => {
      setAccessLevel(level);
      setIsAuthenticated(true);
      setShowSplash(false);
      
      // Small delay before fade in main interface
      setTimeout(() => {
        setIsTransitioning(false);
      }, 150);
    }, 300);
  };

  const handleViewChange = (view: 'chat' | 'feedback' | 'analytics') => {
    setActiveView(view);
    
    // If switching to chat, treat as new chat
    if (view === 'chat') {
      handleNewChat();
    }
  };

  // Show splash screen during transition or when not authenticated
  if (!isAuthenticated || showSplash) {
    return (
      <div 
        className={`transition-all duration-300 ease-out ${
          isTransitioning ? 'opacity-0 transform scale-95' : 'opacity-100 transform scale-100'
        }`}
      >
        <SplashScreen onAuthenticate={handleAuthenticate} />
      </div>
    );
  }

  return (
    <div 
      className={`flex flex-col h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100 transition-all duration-500 ease-out ${
        isTransitioning ? 'opacity-0 transform translate-y-4' : 'opacity-100 transform translate-y-0'
      }`}
    >
      <Header 
        onNewChat={handleNewChat} 
        accessLevel={accessLevel} 
        onViewChange={handleViewChange}
        activeView={activeView}
      />
      
      {/* Conditional Rendering based on activeView */}
      {activeView === 'chat' && (
        <>
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
        </>
      )}
      
      {activeView === 'feedback' && accessLevel === 'admin' && (
        <AdminFeedbackPanel accessLevel={accessLevel} />
      )}
      
      {activeView === 'analytics' && accessLevel === 'admin' && (
        <AdminAnalyticsPanel accessLevel={accessLevel} />
      )}
    </div>
  );
};

export default ChatInterface 