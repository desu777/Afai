import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { FloatingButton } from './FloatingButton';
import { ChatInterface } from './ChatInterface';
import { ChatAPI } from '../services/api';
import type { WidgetConfig } from '../types';
import { useIsMobile } from '../hooks/useIsMobile';
import '../styles/widget.css';

interface WidgetContainerProps extends WidgetConfig {}

// Widget state persistence constants
const WIDGET_STATE_KEY = 'af_widget_state';
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds

interface WidgetStateData {
  isOpen: boolean;
  timestamp: number;
}

export const WidgetContainer: React.FC<WidgetContainerProps> = ({
  apiToken,
  apiUrl,
  position = 'bottom-right',
  theme = 'aquaforest'
}) => {
  // Detect if user is on mobile device
  const isMobile = useIsMobile();
  
  // Initialize widget state with persistence check
  const getInitialState = (): boolean => {
    try {
      const stored = localStorage.getItem(WIDGET_STATE_KEY);
      if (stored) {
        const data: WidgetStateData = JSON.parse(stored);
        const now = Date.now();
        
        // Check if the stored state is within session timeout
        if (now - data.timestamp < SESSION_TIMEOUT) {
          return data.isOpen;
        } else {
          // Session expired, clear storage
          localStorage.removeItem(WIDGET_STATE_KEY);
        }
      }
    } catch (error) {
      // Ignore localStorage errors (e.g., private browsing)
      console.debug('Widget state persistence unavailable');
    }
    
    // Default behavior: closed on mobile, open on desktop
    return !isMobile;
  };
  
  const [isOpen, setIsOpen] = useState(getInitialState);
  const [api] = useState(() => new ChatAPI(apiUrl, apiToken));

  useEffect(() => {
    // Check API health on mount
    api.healthCheck().then(healthy => {
      if (!healthy) {
        console.warn('Aquaforest Chat API is not available');
      }
    });
  }, [api]);

  // Handle device type changes (window resize)
  useEffect(() => {
    // Only update if there's no recent manual user action
    try {
      const stored = localStorage.getItem(WIDGET_STATE_KEY);
      if (!stored) {
        // No stored preference, apply default behavior for new device type
        setIsOpen(!isMobile);
      }
      // If there is a stored preference, keep it (user manually set it)
    } catch (error) {
      // Fallback to default behavior
      setIsOpen(!isMobile);
    }
  }, [isMobile]);

  const toggleChat = () => {
    setIsOpen(prev => {
      const newState = !prev;
      
      // Save user preference with timestamp
      try {
        const stateData: WidgetStateData = {
          isOpen: newState,
          timestamp: Date.now()
        };
        localStorage.setItem(WIDGET_STATE_KEY, JSON.stringify(stateData));
      } catch (error) {
        // Ignore localStorage errors
        console.debug('Could not persist widget state');
      }
      
      return newState;
    });
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