import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { WelcomeScreen } from './WelcomeScreen';
import { MessageBubble } from './MessageBubble';
import { InputField } from './InputField';
import { Message, WidgetState } from '../types';
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
    sessionId: undefined
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages]);

  const handleStart = () => {
    // Add initial greeting message
    const greetingMessage: Message = {
      id: 'greeting',
      type: 'assistant',
      content: "Talk to Afai in any language. Ask questions about your reef, send ICP test results in PDF files, or add photos to show problems. Afai will help you solve them.",
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

    // Convert file to base64 if present
    let imageUrl: string | undefined;
    if (file) {
      imageUrl = await fileToBase64(file);
    }

    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
      imageUrl,
      fileName: file?.name,
      fileSize: file?.size,
      fileType: file?.type.startsWith('image/') ? 'image' : 'pdf'
    };

    // Add user message and set loading
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: undefined
    }));

    try {
      // Convert messages to chat history
      const chatHistory = state.messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Send message to API with file if present
      const response = await api.sendMessage(
        content,
        chatHistory,
        userMessage.imageUrl,
        state.sessionId
      );

      // Create assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      // Update state with response
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
        sessionId: response.session_id || prev.sessionId
      }));

    } catch (error) {
      console.error('Chat error:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
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
                  <div className="af-message-bubble">
                    <div className="af-loading-dots">
                      <div className="af-loading-dot" />
                      <div className="af-loading-dot" />
                      <div className="af-loading-dot" />
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