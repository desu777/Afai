import { useState } from 'react'
import { Message, WorkflowUpdate } from '../types'
import { apiService } from '../services/api'
import Sidebar from './Sidebar'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import SplashScreen from './SplashScreen'
import AdminFeedbackPanel from './AdminFeedbackPanel'
import AdminAnalyticsPanel from './AdminAnalyticsPanel'
import ExamplesPanel from './ExamplesPanel'
import UpdatesPanel from './UpdatesPanel'

const ChatInterface: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const [accessLevel, setAccessLevel] = useState<'test' | 'admin'>('test');
  const [activeView, setActiveView] = useState<'chat' | 'feedback' | 'analytics' | 'examples' | 'updates'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentWorkflowUpdate, setCurrentWorkflowUpdate] = useState<WorkflowUpdate | undefined>(undefined);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

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
    setCurrentWorkflowUpdate(undefined);

    try {
      // Convert messages to chat history format for API
      const chatHistory = messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Debug mode based on environment variable
      const debugMode = import.meta.env.VITE_TEST_ENV === 'true';

      if (debugMode) {
        console.log('🔍 [Chat] Sending streaming message:', currentInput);
        console.log('🔍 [Chat] Chat history:', chatHistory);
      }

      // 🚀 Use streaming API with workflow updates
      const finalResponse = await apiService.sendMessageStream(
        currentInput, 
        chatHistory, 
        debugMode,
        (update: WorkflowUpdate) => {
          if (debugMode) {
            console.log('📡 [Chat] Workflow update received:', update);
            console.log('🔄 [Chat] Setting currentWorkflowUpdate state...');
          }
          setCurrentWorkflowUpdate(update);
          if (debugMode) {
            console.log('✅ [Chat] currentWorkflowUpdate state updated');
          }
        }
      );

      if (debugMode) {
        console.log('✅ [Chat] Final response received:', finalResponse ? finalResponse.substring(0, 100) + '...' : 'EMPTY');
      }

      // 🆕 Check if we have a valid response
      const responseContent = finalResponse && finalResponse.trim() 
        ? finalResponse 
        : 'I apologize, but I encountered an issue processing your request. Please try again.';

      // Add AI response
      const aiResponse: Message = {
        id: userMessageId + 1,
        type: 'assistant',
        content: responseContent,
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
      setCurrentWorkflowUpdate(undefined);
    }
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

  const handleViewChange = (view: 'chat' | 'feedback' | 'analytics' | 'examples' | 'updates') => {
    setActiveView(view);
    
    // If switching to chat, treat as new chat
    if (view === 'chat') {
      handleNewChat();
    }
  };

  const handleExampleSelect = (example: string) => {
    setInputValue(example);
    setActiveView('chat');
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
      className={`flex h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100 transition-all duration-500 ease-out ${
        isTransitioning ? 'opacity-0 transform translate-y-4' : 'opacity-100 transform translate-y-0'
      }`}
    >
      <Sidebar 
        accessLevel={accessLevel} 
        onViewChange={handleViewChange}
        activeView={activeView}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={setIsSidebarCollapsed}
      />
      
      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${
        isSidebarCollapsed ? 'md:ml-0' : 'md:ml-0'
      } ml-0`}>
        {/* Conditional Rendering based on activeView */}
        {activeView === 'chat' && (
          <>
            <MessageList 
              messages={messages} 
              isLoading={isLoading} 
              currentWorkflowUpdate={currentWorkflowUpdate}
              inputValue={inputValue}
              onInputChange={setInputValue}
              onSend={handleSend}
            />
            {(messages.length > 0 || isLoading) && (
              <ChatInput
                inputValue={inputValue}
                isLoading={isLoading}
                onInputChange={setInputValue}
                onSend={handleSend}
                hasMessages={true}
              />
            )}
          </>
        )}
        
        {activeView === 'feedback' && accessLevel === 'admin' && (
          <AdminFeedbackPanel accessLevel={accessLevel} />
        )}
        
        {activeView === 'analytics' && accessLevel === 'admin' && (
          <AdminAnalyticsPanel accessLevel={accessLevel} />
        )}
        
        {activeView === 'examples' && (
          <ExamplesPanel onExampleSelect={handleExampleSelect} />
        )}
        
        {activeView === 'updates' && (
          <UpdatesPanel />
        )}
      </div>
    </div>
  );
};

export default ChatInterface 