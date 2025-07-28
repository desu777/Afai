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
      content: "Hello, I'm Afai 🌊\n\nI'm your personal reef aquarium advisor, ready to help you with all your aquarist needs. Ask me anything about Aquaforest products, reef care, or marine life!",
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

    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
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

      // Convert file to base64 if present
      let imageUrl: string | undefined;
      if (file && file.type.startsWith('image/')) {
        imageUrl = await fileToBase64(file);
      }

      // Send message to API
      const response = await api.sendMessage(
        content,
        chatHistory,
        imageUrl,
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
          <button className="af-chat-header-close" onClick={onClose}>
            <ArrowLeft size={24} />
          </button>
          <div />
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
              
              {state.messages.length === 1 && state.messages[0].id === 'greeting' && (
                <motion.div 
                  className="af-message-action"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <button 
                    className="af-action-button"
                    onClick={() => {
                      const ackMessage: Message = {
                        id: 'ack',
                        type: 'user',
                        content: 'OK I got it',
                        timestamp: new Date()
                      };
                      setState(prev => ({
                        ...prev,
                        messages: [...prev.messages, ackMessage]
                      }));
                    }}
                  >
                    OK I got it
                  </button>
                </motion.div>
              )}
              
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