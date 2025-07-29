import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { WelcomeScreen } from './WelcomeScreen';
import { MessageBubble } from './MessageBubble';
import { InputField } from './InputField';
import { ProgressIndicator } from './ProgressIndicator';
import { Message, WidgetState, WorkflowUpdate } from '../types';
import { ChatAPI } from '../services/api';

interface ChatInterfaceProps {
  onClose: () => void;
  api: ChatAPI;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ onClose, api }) => {
  const [state, setState] = useState<WidgetState>({
    isOpen: true,
    currentView: 'welcome',
    messages: [],
    isLoading: false,
    currentWorkflowUpdate: undefined,
    sessionId: undefined
  });
  const [userScrolledUp, setUserScrolledUp] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start',
      inline: 'nearest'
    });
  };

  // Detect user scroll position
  useEffect(() => {
    const container = document.querySelector('.af-messages-container');
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isAtBottom = scrollHeight - scrollTop <= clientHeight + 100; // 100px buffer
      setUserScrolledUp(!isAtBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Intelligent scroll behavior - only scroll when user sends messages
  useEffect(() => {
    if (state.messages.length === 0) return;
    
    const lastMessage = state.messages[state.messages.length - 1];
    
    // FIXED: Only auto-scroll when user sends a new message, NOT when AI responds
    const shouldAutoScroll = lastMessage.type === 'user' && !userScrolledUp;
    
    if (shouldAutoScroll) {
      // Scroll immediately after user sends a question
      const timeoutId = setTimeout(() => {
        scrollToBottom();
      }, 0);
      
      return () => clearTimeout(timeoutId);
    }
    
    // When AI responds - DON'T scroll, let user read from the beginning
    
  }, [state.messages.length, userScrolledUp, state.isLoading]);

  // Additional scroll when loading starts to show progress indicator
  useEffect(() => {
    if (state.isLoading && state.messages.length > 0) {
      scrollToBottom(); // Show progress indicator immediately
    }
  }, [state.isLoading]);

  const handleStart = () => {
    // Add initial greeting message
    const greetingMessage: Message = {
      id: 'greeting',
      type: 'assistant',
      content: "Upload a **photo** to identify pests or diseases, attach **ICP results in PDF** for detailed analysis, or simply ask a question to instantly receive a ready-to-implement plan.\n\nYou're getting **early access** to Afai – our breakthrough AI assistant, now in public Beta. This means you're among the first people in the world to use it! Please be patient with any imperfections. **Your feedback is crucial** as we work together to perfect this revolutionary tool.",
      timestamp: new Date()
    };
    
    setState(prev => ({ 
      ...prev, 
      currentView: 'chat',
      messages: [greetingMessage]
    }));
  };

  const handleSendMessage = async (content: string, file?: File) => {
    if (!content.trim() && !file) return;

    // Handle file conversion - exactly like frontend
    let imageUrlForMessage: string | undefined;
    let fileName: string | undefined;
    let fileSize: number | undefined;
    let fileType: 'image' | 'pdf' | undefined;
    
    if (file) {
      try {
        imageUrlForMessage = await fileToBase64(file);
        fileName = file.name;
        fileSize = file.size;
        fileType = file.type.startsWith('image/') ? 'image' : 'pdf';
      } catch (error) {
        // If base64 conversion fails, still create message with file info
        fileName = file.name;
        fileSize = file.size;
        fileType = file.type.startsWith('image/') ? 'image' : 'pdf';
      }
    }

    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
      imageUrl: imageUrlForMessage,
      fileName: fileName,
      fileSize: fileSize,
      fileType: fileType
    };

    // Add user message and set loading
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      currentWorkflowUpdate: undefined,
      error: undefined
    }));

    try {
      // Convert messages to chat history
      const chatHistory = state.messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Use streaming API with workflow updates
      const response = await api.sendMessageStream(
        content,
        chatHistory,
        (update: WorkflowUpdate) => {
          setState(prev => ({
            ...prev,
            currentWorkflowUpdate: update
          }));
        },
        userMessage.imageUrl,
        state.sessionId
      );

      // Create assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response || 'I apologize, but I encountered an issue processing your request. Please try again.',
        timestamp: new Date()
      };

      // Update state with response
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
        currentWorkflowUpdate: undefined,
        sessionId: prev.sessionId
      }));

    } catch (error) {
      console.error('Chat error:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        currentWorkflowUpdate: undefined,
        error: 'Failed to send message. Please try again.'
      }));
    }
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  return (
    <motion.div
      className="af-chat-window"
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      transition={{ type: 'spring', damping: 20, stiffness: 200 }}
    >
      {state.currentView === 'chat' && (
        <div className="af-chat-header">
          <div className="af-chat-header-content">
            <span className="af-chat-header-title">Meet Afai</span>
            <div className="af-chat-header-icon">
              <div className="af-circle">
                <div className="af-wave-inner"></div>
              </div>
            </div>
          </div>
        </div>
      )}

      <AnimatePresence mode="wait">
        {state.currentView === 'welcome' ? (
          <WelcomeScreen key="welcome" onStart={handleStart} onClose={onClose} />
        ) : (
          <div key="chat" className="af-chat-interface">
            <div className="af-messages-container">
              {state.messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              
              {state.isLoading && (
                <motion.div 
                  className="af-message assistant"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="af-message-wrapper">
                    <div className="af-message-bubble">
                      {state.currentWorkflowUpdate ? (
                        <ProgressIndicator currentUpdate={state.currentWorkflowUpdate} />
                      ) : (
                        <div className="af-loading-dots">
                          <div className="af-loading-dot" />
                          <div className="af-loading-dot" />
                          <div className="af-loading-dot" />
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
              
              {state.error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  style={{
                    padding: '8px 16px',
                    background: '#FEE2E2',
                    color: '#DC2626',
                    borderRadius: '8px',
                    fontSize: '14px',
                    margin: '8px 0'
                  }}
                >
                  {state.error}
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
            
            <InputField 
              onSendMessage={handleSendMessage} 
              disabled={state.isLoading}
              onClose={onClose}
            />
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};