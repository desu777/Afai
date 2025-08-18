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

// Bubble session constants
const BUBBLE_SESSION_KEY = 'af_bubble_session';
const BUBBLE_HIDDEN_KEY = 'af_bubble_hidden_until';

interface WidgetStateData {
  isOpen: boolean;
  timestamp: number;
  userClosedChat?: boolean; // Czy user świadomie zamknął czat
}

interface BubbleSessionData {
  firstPageUrl: string;
  entryTime: number;
  hiddenUntil?: number;
  pageViews: number;
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
  
  // Helper function - ukryj dymek na 30 minut
  const hideBubbleFor30Min = () => {
    const hideUntil = Date.now() + SESSION_TIMEOUT;
    try {
      sessionStorage.setItem(BUBBLE_HIDDEN_KEY, hideUntil.toString());
    } catch (error) {
      console.debug('Could not set bubble hidden state');
    }
  };

  // State kontrolujący wyświetlanie dymku "Ask Afai" z inteligentną logiką sesji
  const [showBubble, setShowBubble] = useState<boolean>(() => {
    const now = Date.now();
    
    // Sprawdź czy dymek jest ukryty (30 min timeout)
    try {
      const hiddenUntil = sessionStorage.getItem(BUBBLE_HIDDEN_KEY);
      if (hiddenUntil && parseInt(hiddenUntil) > now) {
        return false; // Dymek ukryty
      }
      
      // Sprawdź czy user zamknął czat w localStorage
      const stored = localStorage.getItem(WIDGET_STATE_KEY);
      if (stored) {
        const data: WidgetStateData = JSON.parse(stored);
        if (data.userClosedChat && (now - data.timestamp < SESSION_TIMEOUT)) {
          return false;
        }
      }
      
      // Sprawdź sesję nawigacji
      const sessionData = sessionStorage.getItem(BUBBLE_SESSION_KEY);
      if (sessionData) {
        const session: BubbleSessionData = JSON.parse(sessionData);
        
        // Jeśli to nie pierwsza strona w sesji - ukryj
        if (session.pageViews > 1) {
          hideBubbleFor30Min();
          return false;
        }
      } else {
        // Pierwsza wizyta - utwórz sesję
        const newSession: BubbleSessionData = {
          firstPageUrl: window.location.href,
          entryTime: now,
          pageViews: 1
        };
        sessionStorage.setItem(BUBBLE_SESSION_KEY, JSON.stringify(newSession));
      }
    } catch (error) {
      console.debug('Session storage error');
    }
    
    return true; // Domyślnie pokazuj dymek
  });

  useEffect(() => {
    // Check API health on mount
    api.healthCheck().then(healthy => {
      if (!healthy) {
        console.warn('Aquaforest Chat API is not available');
      }
    });
  }, [api]);

  // Detekcja nawigacji - sprawdź czy user przeszedł na nową stronę
  useEffect(() => {
    try {
      const sessionData = sessionStorage.getItem(BUBBLE_SESSION_KEY);
      if (sessionData) {
        const session: BubbleSessionData = JSON.parse(sessionData);
        const currentUrl = window.location.href;
        
        // Sprawdź czy to zmiana strony
        if (currentUrl !== session.firstPageUrl) {
          // User nawiguje - zwiększ licznik i ukryj dymek
          session.pageViews += 1;
          sessionStorage.setItem(BUBBLE_SESSION_KEY, JSON.stringify(session));
          
          if (session.pageViews > 1) {
            hideBubbleFor30Min();
            setShowBubble(false);
          }
        }
      }
    } catch (error) {
      console.debug('Session navigation detection error');
    }
  }, []); // Tylko przy mount (każde załadowanie strony)

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

  // Timer 12 sekund - ukryj dymek gdy user spędza czas na stronie
  useEffect(() => {
    if (!showBubble || !isMobile || isOpen) return;
    
    // Timer 12 sekund
    const timer = setTimeout(() => {
      // User spędził 12s na stronie - ukryj dymek na 30 minut
      hideBubbleFor30Min();
      setShowBubble(false);
    }, 12000);
    
    return () => clearTimeout(timer);
  }, [showBubble, isMobile, isOpen]);

  // Reset showBubble po 30 minutach jeśli jest ukryty
  useEffect(() => {
    if (!showBubble) {
      const timer = setTimeout(() => {
        setShowBubble(true); // Reset po 30 minutach
      }, SESSION_TIMEOUT);
      
      return () => clearTimeout(timer);
    }
  }, [showBubble]);

  const toggleChat = () => {
    setIsOpen(prev => {
      const newState = !prev;
      
      // Save user preference with timestamp
      try {
        const stateData: WidgetStateData = {
          isOpen: newState,
          timestamp: Date.now(),
          userClosedChat: prev === true && newState === false // User właśnie zamknął czat
        };
        localStorage.setItem(WIDGET_STATE_KEY, JSON.stringify(stateData));
        
        // Jeśli user zamknął czat, ukryj dymek na 30 minut
        if (prev === true && newState === false && isMobile) {
          hideBubbleFor30Min();
          setShowBubble(false);
        }
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
        showCallToAction={isMobile && !isOpen && showBubble}
      />
    </div>
  );
};