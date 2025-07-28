import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { FloatingButton } from './FloatingButton';
import { ChatInterface } from './ChatInterface';
import { ChatAPI } from '../services/api';
import { WidgetConfig } from '../types';
import '../styles/widget.css';

interface WidgetContainerProps extends WidgetConfig {}

export const WidgetContainer: React.FC<WidgetContainerProps> = ({
  apiToken,
  apiUrl,
  position = 'bottom-right',
  theme = 'aquaforest'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [api] = useState(() => new ChatAPI(apiUrl, apiToken));

  useEffect(() => {
    // Check API health on mount
    api.healthCheck().then(healthy => {
      if (!healthy) {
        console.warn('Aquaforest Chat API is not available');
      }
    });
  }, [api]);

  const toggleChat = () => {
    setIsOpen(prev => !prev);
  };

  return (
    <div className={`aquaforest-widget ${position} ${theme}`}>
      <AnimatePresence>
        {isOpen && (
          <ChatInterface 
            key="chat-interface"
            onClose={toggleChat} 
            api={api}
          />
        )}
      </AnimatePresence>
      
      <FloatingButton 
        isOpen={isOpen} 
        onClick={toggleChat}
        position={position}
      />
    </div>
  );
};